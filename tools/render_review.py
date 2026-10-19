#!/usr/bin/env python3
"""Build an offline, explicitly schematic before/after questbook review.

This reads Git and the working tree. It never updates quest data or Git history.
Requires ftb-snbt-lib; all other dependencies are in the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap

try:
    import ftb_snbt_lib as snbt
except ImportError as exc:
    raise SystemExit("Install the repository's pinned ftb-snbt-lib dependency first.") from exc


BASELINE = "f68124fb33597aa13b4b6a8dd8c6dde7c879b188"
CHAPTER_DIR = Path("config/ftbquests/quests/chapters")
PIXELS_PER_UNIT = 64
MARGIN = 128
FORMAT_CODE = re.compile(r"§[0-9a-fk-or]", re.IGNORECASE)


def plain(value: object) -> str:
    return FORMAT_CODE.sub("", str(value))


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True
    )
    return result.stdout.decode("utf-8")


def parse_chapter(source: str, label: str) -> dict:
    """Round-trip into JSON primitives, without normalizing IDs or field values."""
    chapter = json.loads(json.dumps(snbt.loads(source), ensure_ascii=False))
    seen = set()
    for quest in chapter.get("quests", []):
        ident = str(quest["id"])
        if ident in seen:
            raise ValueError(f"Duplicate quest ID in {label}: {ident}")
        seen.add(ident)
        for axis in ("x", "y"):
            if not math.isfinite(float(quest.get(axis, 0))):
                raise ValueError(f"Non-finite {axis} in {label}: {ident}")
    return chapter


def quest_map(chapter: dict) -> dict[str, dict]:
    return {str(quest["id"]): quest for quest in chapter.get("quests", [])}


def shared_bounds(before: dict, after: dict) -> tuple[float, float, float, float]:
    quests = before.get("quests", []) + after.get("quests", [])
    xs = [float(quest.get("x", 0)) * PIXELS_PER_UNIT for quest in quests] or [0]
    ys = [float(quest.get("y", 0)) * PIXELS_PER_UNIT for quest in quests] or [0]
    return (
        min(xs) - MARGIN,
        min(ys) - MARGIN,
        max(xs) - min(xs) + MARGIN * 2,
        max(ys) - min(ys) + MARGIN * 2,
    )


def frame(shape: str, radius: float, color: str) -> str:
    """Draw schematic frames, never claim to render FTB custom shape textures."""
    attrs = f'fill="#152532" stroke="{color}" stroke-width="2.4"'
    if shape in {"square", "scroll"}:
        rounding = radius * (0.1 if shape == "square" else 0.35)
        return f'<rect x="{-radius:.2f}" y="{-radius:.2f}" width="{2*radius:.2f}" height="{2*radius:.2f}" rx="{rounding:.2f}" {attrs}/>'
    points = []
    if shape == "star":
        for index in range(10):
            angle = math.pi * index / 5 - math.pi / 2
            length = radius * (1 if index % 2 == 0 else 0.53)
            points.append((math.cos(angle) * length, math.sin(angle) * length))
    elif shape == "shield":
        points = [(-radius, -radius), (radius, -radius), (radius * .8, radius * .3), (0, radius), (-radius * .8, radius * .3)]
    elif shape == "crown":
        points = [(-radius, -radius*.6), (-radius*.45, 0), (0, -radius), (radius*.45, 0), (radius, -radius*.6), (radius*.7, radius*.7), (-radius*.7, radius*.7)]
    elif shape == "gear":
        for index in range(24):
            angle = math.pi * index / 12
            length = radius * (1 if index % 3 in (0, 1) else .78)
            points.append((math.cos(angle) * length, math.sin(angle) * length))
    if points:
        coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        return f'<polygon points="{coordinates}" {attrs}/>'
    return f'<circle r="{radius:.2f}" {attrs}/>'


def svg_for(chapter: dict, other: dict, bounds: tuple, prefix: str, numbers: dict) -> str:
    """Use real coordinates and direct dependency lines, with no auto-layout."""
    esc = html.escape
    quests, other_quests = quest_map(chapter), quest_map(other)
    x_min, y_min, width, height = bounds
    viewbox = " ".join(f"{value:.2f}" for value in bounds)
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" width="{width:.2f}" height="{height:.2f}" role="img" aria-labelledby="{prefix}-title" data-quest-count="{len(quests)}">',
        f'<title id="{prefix}-title">{esc(plain(chapter.get("title", "Отсутствующая глава")))} — схема SNBT, не скриншот игры</title>',
        f'<defs><marker id="{prefix}-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#77939f" stroke-width="1.2"/></marker></defs>',
        '<g fill="none" stroke="#24404d" stroke-width="0.7" opacity="0.55" aria-hidden="true">',
    ]
    for x in range(math.ceil(x_min / PIXELS_PER_UNIT), math.floor((x_min + width) / PIXELS_PER_UNIT) + 1):
        px = x * PIXELS_PER_UNIT
        pieces.append(f'<path d="M {px} {y_min:.2f} v {height:.2f}"/>')
    for y in range(math.ceil(y_min / PIXELS_PER_UNIT), math.floor((y_min + height) / PIXELS_PER_UNIT) + 1):
        py = y * PIXELS_PER_UNIT
        pieces.append(f'<path d="M {x_min:.2f} {py} h {width:.2f}"/>')
    pieces.append('</g><g class="dependencies" fill="none" stroke="#77939f" stroke-width="1.6">')
    for ident, quest in quests.items():
        target_x = float(quest.get("x", 0)) * PIXELS_PER_UNIT
        target_y = float(quest.get("y", 0)) * PIXELS_PER_UNIT
        for dependency in quest.get("dependencies", []):
            source = quests.get(str(dependency))
            if not source:
                continue
            source_x = float(source.get("x", 0)) * PIXELS_PER_UNIT
            source_y = float(source.get("y", 0)) * PIXELS_PER_UNIT
            distance = math.hypot(target_x - source_x, target_y - source_y)
            if distance == 0:
                continue
            source_r = 20 * float(source.get("size", 1)) + 3
            target_r = 20 * float(quest.get("size", 1)) + 6
            ux, uy = (target_x - source_x) / distance, (target_y - source_y) / distance
            x1, y1 = source_x + ux * source_r, source_y + uy * source_r
            x2, y2 = target_x - ux * target_r, target_y - uy * target_r
            hidden = quest.get("hide_dependency_lines", chapter.get("default_hide_dependency_lines", False))
            dashed = ' stroke-dasharray="5 5" opacity="0.5"' if hidden else ""
            pieces.append(f'<path data-from="{esc(str(dependency))}" data-to="{esc(ident)}" d="M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}" marker-end="url(#{prefix}-arrow)"{dashed}><title>{esc(str(dependency))} → {esc(ident)}{"; скрытая линия показана пунктиром для аудита" if hidden else ""}</title></path>')
    pieces.append('</g><g class="quests" font-family="system-ui, sans-serif" text-anchor="middle">')
    for ident, quest in quests.items():
        x = float(quest.get("x", 0)) * PIXELS_PER_UNIT
        y = float(quest.get("y", 0)) * PIXELS_PER_UNIT
        radius = 20 * float(quest.get("size", 1))
        shape = str(quest.get("shape", chapter.get("default_quest_shape", "circle")))
        changed = other_quests.get(ident) != quest
        color = "#83b8ca" if quest.get("optional", False) else "#e8c97d"
        title = plain(quest.get("title", ident))
        icon = str(quest.get("icon", "не задан явно"))
        lines = textwrap.wrap(title, width=25, break_long_words=False) or [ident]
        if len(lines) > 2:
            lines = [lines[0], lines[1].rstrip(" .…") + "…"]
        pieces.append(f'<g data-quest-id="{esc(ident)}" tabindex="0" role="button" aria-label="{esc(title)}" transform="translate({x:.2f},{y:.2f})" style="cursor:pointer">')
        pieces.append(f'<title>{esc(title)}\nID: {esc(ident)}\nЗначок: {esc(icon)}\nФорма: {esc(shape)}\nx={quest.get("x",0)}, y={quest.get("y",0)}\n{"Есть изменения" if changed else "Без изменений"}</title>')
        if changed:
            pieces.append(f'<circle class="change-ring" r="{radius+6:.2f}" fill="none" stroke="#ed9f69" stroke-width="1.6" stroke-dasharray="3 3"/>')
        pieces.append(f'<circle class="selection-ring" r="{radius+10:.2f}" fill="none" stroke="#f4f7fc" stroke-width="3" visibility="hidden"/>')
        pieces.append(frame(shape, radius, color))
        pieces.append(f'<text y="4" font-size="11" fill="#edf2f5" pointer-events="none">{numbers[ident]:02d}</text>')
        for index, line in enumerate(lines):
            pieces.append(f'<text class="quest-label" y="{radius+24+index*16:.2f}" font-size="12" fill="#e2edf0" paint-order="stroke" stroke="#12202b" stroke-width="3" stroke-linejoin="round" pointer-events="none">{esc(line)}</text>')
        pieces.append('</g>')
    pieces.append('</g></svg>')
    return "\n".join(pieces)


HTML = r'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Наследие нового мира — обзор схем глав</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#101a23;color:#e2edf0}*{box-sizing:border-box}body{margin:0}button,select,input{font:inherit;color:inherit;background:#1c303f;border:1px solid #466170;border-radius:6px;padding:.45rem .65rem}button{cursor:pointer}button:hover{background:#304955}a{color:#9bd1e9}header{padding:1.1rem 1.5rem;border-bottom:1px solid #334856}h1{font-size:1.5rem;margin:0 0 .5rem}p{line-height:1.5}header p{margin:.35rem 0;color:#adc2ce}.notice{color:#f1cd8d}main{padding:1rem 1.5rem}.toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:.5rem;margin:.6rem 0}.toolbar select{max-width:100%}.meta,.legend{font-size:.85rem;color:#adc2ce}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}.panel{min-width:0;border:1px solid #334856;border-radius:8px;overflow:hidden;background:#12202b}.panel h2{margin:0;padding:.75rem;font-size:1rem;border-bottom:1px solid #334856}.canvas{height:60vh;min-height:280px;overflow:auto;position:relative;touch-action:pan-x pan-y;cursor:grab}.canvas.dragging{cursor:grabbing}.canvas svg{display:block;max-width:none}.canvas svg .selected .selection-ring{visibility:visible}.hide-labels .quest-label{display:none}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.details{padding:1rem;min-width:0;background:#162733;border:1px solid #334856;border-radius:8px}.details h3{margin-top:0}.details p{white-space:pre-wrap}.details h4{color:#a8ccd9;margin-bottom:.4rem}.details ul{padding-left:1.2rem}.details li{margin:.5rem 0;overflow-wrap:anywhere}.description p{margin:.4rem 0}.code,code{font-family:ui-monospace,monospace;font-size:.82rem;overflow-wrap:anywhere}pre{white-space:pre-wrap;word-break:break-word;background:#0c1720;padding:.75rem;border-radius:5px;font-size:.8rem;line-height:1.5;max-height:35rem;overflow:auto}.changed{color:#f6b886}.status{font-size:.9rem;color:#b8cbd5}.empty{color:#c1a798}.search{width:min(30rem,100%)}#quest-list{width:min(45rem,100%)}.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.5rem}.summary span{padding:.65rem;background:#172a37;border-radius:6px}footer{padding:1rem 1.5rem;color:#adc2ce;font-size:.85rem;border-top:1px solid #334856}@media(max-width:850px){.comparison,.detail-grid{grid-template-columns:1fr}.canvas{height:45vh}main,header{padding:1rem}}@media print{.toolbar{display:none}.canvas{height:auto;overflow:visible}.canvas svg{width:100%!important;height:auto!important}body{background:white;color:black}.comparison{grid-template-columns:1fr}.details,.panel{break-inside:avoid}}
</style></head><body>
<header><h1>Наследие нового мира · сравнение глав</h1>
<p class="notice"><strong>Статическая схема из SNBT. Это не Minecraft и не скриншот FTB Quests.</strong></p>
<p>Настоящие координаты, размеры и зависимости. Номера заменяют значки предметов; рамки условны. Цвет: золотой — обязательный квест, голубой — optional. Пунктирное оранжевое кольцо — изменённая запись.</p>
<p class="meta" id="source-info"></p></header>
<main>
<div class="toolbar"><label for="chapter">Глава</label><select id="chapter"></select></div>
<div class="summary" id="summary"></div>
<div class="toolbar"><button id="fit">Вписать обе схемы</button><button id="zoom-out" aria-label="Уменьшить масштаб">−</button><button id="zoom-in" aria-label="Увеличить масштаб">+</button><button id="actual">100%</button><span id="scale" class="meta"></span><label><input id="labels" type="checkbox" checked> Подписи</label><label><input id="sync-pan" type="checkbox" checked> Вместе перемещать</label></div>
<p class="legend">Единица SNBT = 64 px при 100%. Общие границы и одинаковый масштаб у пары; сравнение не подгоняет главы по отдельности. Перетаскивайте пустое место или пользуйтесь полосами прокрутки. Скрытые в данных линии показаны пунктиром для аудита.</p>
<div class="comparison"><section class="panel"><h2 id="before-title">Alpha 42 · до</h2><div id="before" class="canvas"></div></section><section class="panel"><h2 id="after-title">Рабочие файлы · после</h2><div id="after" class="canvas"></div></section></div>
<p id="chapter-notes" class="status"></p>
<div class="toolbar"><label for="search">Поиск</label><input id="search" class="search" placeholder="Название, Quest ID или значок"><label><input id="only-changed" type="checkbox"> Только изменённые</label></div>
<div class="toolbar"><label for="quest-list">Квест</label><select id="quest-list"></select><button id="locate">К выбранному узлу</button></div>
<p id="diff-fields" class="status"></p><div class="detail-grid"><article id="before-detail" class="details"></article><article id="after-detail" class="details"></article></div>
<details><summary>Настройки главы и данные, которые схема не визуализирует</summary><div class="detail-grid"><pre id="before-settings"></pre><pre id="after-settings"></pre></div></details>
</main><footer>HTML полностью автономен: работает из файла без сети и сервера. SVG каждой главы лежат рядом в папке с её именем. Геометрия линий, шрифты, хитбоксы, текстуры форм, доступность и статусы выполнения требуют отдельной проверки в FTB Quests установленной версии. Схема не проверяет зачёт задач, награды или сохранение прогресса.</footer>
<script id="review-data" type="application/json">__DATA__</script>
<script>
'use strict';
const DATA=JSON.parse(document.getElementById('review-data').textContent);
const $=id=>document.getElementById(id), panels=[$('before'),$('after')];
const clean=value=>String(value??'').replace(/§[0-9a-fk-or]/gi,'');
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const colors={0:'#aaa',1:'#7878ff',2:'#55aa55',3:'#55aaaa',4:'#dd7777',5:'#cc77cc',6:'#ffaa00',7:'#aaa',8:'#888',9:'#8888ff',a:'#55ff55',b:'#55ffff',c:'#ff7777',d:'#ff55ff',e:'#ffff55',f:'#fff'};
function formatted(value){let result='',color=null,bold=false,italic=false;for(const part of String(value??'').split(/(§[0-9a-fk-or])/gi)){if(/^§[0-9a-fk-or]$/i.test(part)){const code=part[1].toLowerCase();if(code==='r'){color=null;bold=false;italic=false;}else if(code==='l')bold=true;else if(code==='o')italic=true;else if(colors[code]){color=colors[code];bold=false;italic=false;}}else{const style=[color?'color:'+color:'',bold?'font-weight:700':'',italic?'font-style:italic':''].filter(Boolean).join(';');result+='<span'+(style?' style="'+style+'"':'')+'>'+esc(part)+'</span>';}}return result;}
function equal(a,b){if(a===b)return true;if(a===null||b===null||typeof a!=='object'||typeof b!=='object')return false;if(Array.isArray(a)!==Array.isArray(b))return false;const ak=Object.keys(a).sort(),bk=Object.keys(b).sort();return ak.length===bk.length&&ak.every((key,index)=>key===bk[index]&&equal(a[key],b[key]));}
let current=null,selected=null,scale=1,scrolling=false;
function mapping(chapter){return Object.fromEntries((chapter.quests||[]).map(q=>[String(q.id),q]));}
function getMaps(){return [mapping(current.before),mapping(current.after)];}
function entrySummary(entry){const type=entry.type||'не указан';if(type==='item'){const item=entry.item||{};const itemId=typeof item==='string'?item:(item.id||'?');const amount=entry.count??(typeof item==='object'?item.Count:undefined)??1;return amount+' × '+itemId;}if(type==='xp')return (entry.xp??'?')+' XP';if(type==='xp_levels')return (entry.xp_levels??entry.levels??'?')+' уровней XP';const keys=['advancement','structure','biome','entity','dimension','stage','stat','title'];return type+(keys.filter(k=>entry[k]!==undefined).map(k=>' · '+k+': '+entry[k]).join(''));}
function entryList(entries){if(!entries?.length)return '<p class="empty">Нет записей.</p>';return '<ul>'+entries.map(entry=>'<li>'+esc(entrySummary(entry))+'<div class="code">ID '+esc(entry.id||'—')+'</div><details><summary>Все поля</summary><pre>'+esc(JSON.stringify(entry,null,2))+'</pre></details></li>').join('')+'</ul>';}
function card(quest,chapter,version){if(!quest)return '<h3>'+esc(version)+'</h3><p class="empty">Квест отсутствует в этой версии.</p>';const descriptions=Array.isArray(quest.description)?quest.description:[quest.description||''];const dependencies=(quest.dependencies||[]).join(', ')||'нет';return '<h3>'+esc(version)+' · '+formatted(quest.title||quest.id)+'</h3><p class="code">Quest ID: '+esc(quest.id)+'</p><p>Координаты: '+esc(quest.x??0)+', '+esc(quest.y??0)+' · размер: '+esc(quest.size??1)+' · форма: '+esc(quest.shape??chapter.default_quest_shape??'circle')+' · optional: '+esc(quest.optional??false)+'</p><p class="code">Значок: '+esc(typeof quest.icon==='object'?JSON.stringify(quest.icon):quest.icon||'не задан явно')+'</p><p class="code">Зависимости: '+esc(dependencies)+'</p><div class="description">'+descriptions.map(line=>'<p>'+formatted(line)+'</p>').join('')+'</div><h4>Задачи ('+(quest.tasks||[]).length+')</h4>'+entryList(quest.tasks)+'<h4>Награды ('+(quest.rewards||[]).length+')</h4>'+entryList(quest.rewards)+'<details><summary>Полная запись квеста</summary><pre>'+esc(JSON.stringify(quest,null,2))+'</pre></details>';}
function selectQuest(id){selected=id;const [a,b]=getMaps();panels.forEach(panel=>panel.querySelectorAll('[data-quest-id]').forEach(node=>node.classList.toggle('selected',node.dataset.questId===id)));$('quest-list').value=id||'';$('before-detail').innerHTML=card(a[id],current.before,'Alpha 42');$('after-detail').innerHTML=card(b[id],current.after,'Рабочие файлы');const keys=[...new Set([...Object.keys(a[id]||{}),...Object.keys(b[id]||{})])].sort().filter(key=>!equal(a[id]?.[key],b[id]?.[key]));$('diff-fields').textContent=id?(keys.length?'Изменённые поля: '+keys.join(', '):'Запись квеста совпадает с базой.'):'';$('diff-fields').classList.toggle('changed',keys.length>0);}
function populateQuests(){const [a,b]=getMaps(),term=$('search').value.trim().toLocaleLowerCase('ru'),onlyChanged=$('only-changed').checked;const ids=current.ids.filter(id=>{const searchable=JSON.stringify([id,a[id]?.title,b[id]?.title,a[id]?.icon,b[id]?.icon]).toLocaleLowerCase('ru');return (!term||searchable.includes(term))&&(!onlyChanged||!equal(a[id],b[id]));});$('quest-list').replaceChildren(...ids.map(id=>{const q=b[id]||a[id],option=document.createElement('option');option.value=id;option.textContent=String(current.numbers[id]).padStart(2,'0')+' · '+clean(q.title||id)+(!equal(a[id],b[id])?' · изменён':'');return option;}));if(ids.includes(selected))selectQuest(selected);else if(ids.length)selectQuest(ids[0]);else{selectQuest(null);$('diff-fields').textContent='Нет квестов, соответствующих поиску.';}}
function applyScale(next,center=true){const old=scale;scale=Math.max(.04,Math.min(4,next));panels.forEach(panel=>{const svg=panel.querySelector('svg'),x=(panel.scrollLeft+panel.clientWidth/2)/old,y=(panel.scrollTop+panel.clientHeight/2)/old;svg.style.width=current.bounds[2]*scale+'px';svg.style.height=current.bounds[3]*scale+'px';if(center){panel.scrollLeft=x*scale-panel.clientWidth/2;panel.scrollTop=y*scale-panel.clientHeight/2;}});$('scale').textContent=Math.round(scale*100)+'% · одинаково до / после';}
function fit(){const target=Math.min(...panels.map(panel=>Math.min((panel.clientWidth-18)/current.bounds[2],(panel.clientHeight-18)/current.bounds[3])));applyScale(target,false);panels.forEach(panel=>{panel.scrollLeft=0;panel.scrollTop=0;});}
function loadChapter(){current=DATA.chapters[Number($('chapter').value)];selected=null;$('search').value='';panels[0].innerHTML=current.before_svg;panels[1].innerHTML=current.after_svg;$('before-title').textContent='Alpha 42 · '+clean(current.before.title||'глава отсутствует');$('after-title').textContent='Рабочие файлы · '+clean(current.after.title||'глава отсутствует');const [a,b]=getMaps(),changed=current.ids.filter(id=>!equal(a[id],b[id])).length;$('summary').innerHTML=['Квесты: '+Object.keys(a).length+' → '+Object.keys(b).length,'Изменённых записей: '+changed,'Задачи: '+count(current.before,'tasks')+' → '+count(current.after,'tasks'),'Награды: '+count(current.before,'rewards')+' → '+count(current.after,'rewards')].map(text=>'<span>'+esc(text)+'</span>').join('');const settings=chapter=>Object.fromEntries(Object.entries(chapter).filter(([key])=>key!=='quests'));$('before-settings').textContent=JSON.stringify(settings(current.before),null,2);$('after-settings').textContent=JSON.stringify(settings(current.after),null,2);$('chapter-notes').textContent='Файл: '+current.file+'. Связи между главами, quest_links и декоративные изображения не рисуются; исходные данные доступны ниже. Размеры и формы узлов показаны условно.';populateQuests();requestAnimationFrame(fit);history.replaceState(null,'','#'+current.slug);}
function count(chapter,key){return (chapter.quests||[]).reduce((n,q)=>n+(q[key]||[]).length,0);}
$('source-info').textContent='База: '+DATA.baseline+' · рабочий HEAD: '+DATA.head+' · SHA256 прочитанных SNBT: '+DATA.source_digest+'. Снимок включает несохранённые в Git изменения файлов.';
DATA.chapters.forEach((chapter,index)=>{const option=document.createElement('option');option.value=index;option.textContent=String(index+1).padStart(2,'0')+' · '+clean(chapter.after.title||chapter.before.title);$('chapter').append(option);});
const initial=DATA.chapters.findIndex(chapter=>chapter.slug===decodeURIComponent(location.hash.slice(1)));if(initial>=0)$('chapter').value=initial;
$('chapter').addEventListener('change',loadChapter);$('search').addEventListener('input',populateQuests);$('only-changed').addEventListener('change',populateQuests);$('quest-list').addEventListener('change',event=>selectQuest(event.target.value));$('zoom-in').onclick=()=>applyScale(scale*1.25);$('zoom-out').onclick=()=>applyScale(scale/1.25);$('actual').onclick=()=>applyScale(1);$('fit').onclick=fit;$('labels').onchange=()=>document.body.classList.toggle('hide-labels',!$('labels').checked);
$('locate').onclick=()=>{if(!selected)return;const maps=getMaps();panels.forEach((panel,index)=>{const quest=maps[index][selected];if(!quest)return;panel.scrollLeft=(Number(quest.x||0)*64-current.bounds[0])*scale-panel.clientWidth/2;panel.scrollTop=(Number(quest.y||0)*64-current.bounds[1])*scale-panel.clientHeight/2;});};
panels.forEach((panel,index)=>{let drag=null,suppressClick=false;panel.addEventListener('click',event=>{if(suppressClick){suppressClick=false;return;}const node=event.target.closest('[data-quest-id]');if(node)selectQuest(node.dataset.questId);});panel.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){const node=event.target.closest('[data-quest-id]');if(node){event.preventDefault();selectQuest(node.dataset.questId);}}});panel.addEventListener('pointerdown',event=>{if(event.button!==0||event.target.closest('[data-quest-id]'))return;drag={x:event.clientX,y:event.clientY,left:panel.scrollLeft,top:panel.scrollTop};panel.setPointerCapture(event.pointerId);panel.classList.add('dragging');});panel.addEventListener('pointermove',event=>{if(!drag)return;const dx=event.clientX-drag.x,dy=event.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)suppressClick=true;panel.scrollLeft=drag.left-dx;panel.scrollTop=drag.top-dy;});const stop=()=>{drag=null;panel.classList.remove('dragging');};panel.addEventListener('pointerup',stop);panel.addEventListener('pointercancel',stop);panel.addEventListener('scroll',()=>{if(!$('sync-pan').checked||scrolling)return;scrolling=true;panels[1-index].scrollLeft=panel.scrollLeft;panels[1-index].scrollTop=panel.scrollTop;requestAnimationFrame(()=>scrolling=false);});});
loadChapter();
</script></body></html>
'''


def build(root: Path, baseline: str, output: Path) -> dict:
    baseline = git(root, "rev-parse", "--verify", baseline + "^{commit}").strip()
    head = git(root, "rev-parse", "HEAD").strip()
    old_files = git(root, "ls-tree", "-r", "--name-only", baseline, "--", CHAPTER_DIR.as_posix()).splitlines()
    old_files = {name for name in old_files if name.endswith(".snbt")}
    new_files = {path.relative_to(root).as_posix() for path in (root / CHAPTER_DIR).glob("*.snbt")}
    files = sorted(old_files | new_files)
    if not files:
        raise ValueError("No chapter SNBT files found in the baseline or working tree")
    chapters = []
    digest = hashlib.sha256()
    for filename in files:
        before_text = git(root, "show", f"{baseline}:{filename}") if filename in old_files else "{}"
        after_text = (root / filename).read_text(encoding="utf-8") if filename in new_files else "{}"
        digest.update(filename.encode("utf-8") + b"\0" + after_text.encode("utf-8") + b"\0")
        before, after = parse_chapter(before_text, filename), parse_chapter(after_text, filename)
        bounds = shared_bounds(before, after)
        ids = list(dict.fromkeys([*quest_map(before), *quest_map(after)]))
        numbers = {ident: index + 1 for index, ident in enumerate(ids)}
        slug = Path(filename).stem
        chapter = {"file": filename, "slug": slug, "before": before, "after": after,
                   "bounds": bounds, "ids": ids, "numbers": numbers,
                   "before_sha256": hashlib.sha256(before_text.encode("utf-8")).hexdigest(),
                   "after_sha256": hashlib.sha256(after_text.encode("utf-8")).hexdigest()}
        chapter["before_svg"] = svg_for(before, after, bounds, slug + "-before", numbers)
        chapter["after_svg"] = svg_for(after, before, bounds, slug + "-after", numbers)
        chapters.append(chapter)
    chapters.sort(key=lambda entry: (entry["after"].get("order_index", entry["before"].get("order_index", 0)), entry["slug"]))
    data = {"baseline": baseline, "head": head, "source_digest": digest.hexdigest(),
            "pixels_per_unit": PIXELS_PER_UNIT, "chapters": chapters}
    output.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        folder = output / chapter["slug"]
        folder.mkdir(exist_ok=True)
        for version in ("before", "after"):
            (folder / f"{version}.svg").write_text(chapter[f"{version}_svg"], encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    (output / "index.html").write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
    manifest = {key: value for key, value in data.items() if key != "chapters"}
    manifest["chapters"] = [{key: chapter[key] for key in ("file", "slug", "before_sha256", "after_sha256", "bounds")} for chapter in chapters]
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE, help="Git commit to compare with the working tree")
    parser.add_argument("--output", type=Path, default=Path("reports/visual"), help="Output directory, relative to the repository root")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root")
    args = parser.parse_args()
    root = args.repo.resolve()
    output = args.output.resolve() if args.output.is_absolute() else root / args.output
    data = build(root, args.baseline, output)
    total = sum(len(chapter["after"].get("quests", [])) for chapter in data["chapters"])
    print(f"Generated {len(data['chapters'])} chapter comparisons, {total} current quests: {output / 'index.html'}")
    print("Static schematic only; no Minecraft client or server was tested.")


if __name__ == "__main__":
    main()
