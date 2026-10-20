#!/usr/bin/env python3
"""Materialize baseline audit context; ambiguous semantics remain editorial review items."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

import quality


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/workspace/.onboarding/artifacts'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    _, files, sha = quality.snapshots(root, quality.BASELINE)
    parsed, errors = quality.parse_files(files)
    if errors:
        raise ValueError(errors)
    evidence = json.loads((root/'reviews/artifact_evidence.json').read_text())
    findings = json.loads((root/'reviews/editorial_findings.json').read_text())['quests']
    model_sources, advancement_sources, archives = {}, {}, {}
    # Use retained successful evidence; do not retry downloads or rerun completed CRC checks.
    for entry in evidence['artifacts']:
        path = args.cache/entry['file']
        if path.exists():
            archives[entry['file']] = zipfile.ZipFile(path)
        for item in entry['item_model_assets']:
            model_sources.setdefault(item, []).append(entry['file'])
        for item in entry['advancement_json']:
            advancement_sources.setdefault(item, []).append(entry['file'])
    vanilla = args.cache/'minecraft-client-1.20.1.jar'
    if vanilla.exists():
        z = zipfile.ZipFile(vanilla)
        archives[vanilla.name] = z
        for path in z.namelist():
            if match := re.fullmatch(r'assets/minecraft/models/item/(.+)\.json', path):
                model_sources.setdefault('minecraft:'+match[1], []).append(vanilla.name)
            if match := re.fullmatch(r'data/minecraft/advancements/(.+)\.json', path):
                advancement_sources.setdefault('minecraft:'+match[1], []).append(vanilla.name)

    def advancement(ident):
        local = quality.local_advancement(ident, parsed)
        if local is not None:
            return {'source':'repository', 'body':local}
        namespace, path = ident.split(':', 1)
        for jar in advancement_sources.get(ident, []):
            if jar in archives:
                body = json.loads(archives[jar].read(f'data/{namespace}/advancements/{path}.json'))
                return {'source':jar, 'body':body}
        return {'source':None, 'status':'unavailable_in_downloaded_artifacts'}

    rows = list(quality.quest_rows(parsed))
    icons = Counter(str(q.get('icon','')) for _,_,q in rows)
    prose = {p['location'].split('#')[-1]:p['patterns'] for p in quality.prose_issues(parsed)}
    geometry_issues, geometry = quality.geometry(parsed)
    records, summaries = [], []
    for name, chapter in sorted(quality.chapters(parsed).items(), key=lambda v:int(v[1].get('order_index',0))):
        chapter_records = []
        for q in chapter['quests']:
            ident, icon = str(q['id']), str(q.get('icon',''))
            tasks = json.loads(json.dumps(q['tasks']))
            sources = {}
            for t in tasks:
                if t['type']=='advancement':
                    sources[t['advancement']] = advancement(t['advancement'])
            contextual_targets = []
            for t in tasks:
                if t['type']=='item':
                    contextual_targets.append(str(t['item']))
                elif t['type']=='advancement':
                    body = sources[t['advancement']].get('body', {})
                    if display_icon := body.get('display',{}).get('icon',{}).get('item'):
                        contextual_targets.append(display_icon)
            manual = findings.get(ident, [])
            icon_findings = [f for f in manual if f['kind'] in ('icon','asset')]
            objective = '; '.join(str(t.get('advancement') or t.get('structure') or t.get('item') or t.get('entity') or t.get('biome') or t.get('stat') or t['type']) for t in tasks)
            if icon_findings:
                status = 'mismatch' if any(f['status']=='confirmed' for f in icon_findings) else 'review'
                reason = ' '.join(f['message'] for f in icon_findings)
            elif icon in contextual_targets:
                status = 'supported_by_objective'
                reason = f'Значок {icon} совпадает с предметом цели или значком точного достижения ({objective}). Это свидетельство связи с условием, не автоматическая оценка художественного качества.'
            else:
                status = 'review'
                reason = f'Цель «{q["title"]}» проверяется через {objective}; значок {icon} требует редакторской оценки связи с действием. Несовпадение строк само по себе не считается ошибкой.'
            description_issues = [{'kind':'pattern', 'patterns':prose[ident]}] if ident in prose else []
            text = '\n'.join(q.get('description',[]))
            if '…' in text or '...' in text:
                description_issues.append({'kind':'ellipsis_review','message':'Проверить, завершена ли инструкция; многоточие может быть художественным приёмом, а не обрывом.'})
            description_issues += [f for f in manual if f['kind']=='description']
            record = {
                'id':ident, 'chapter':name, 'title':str(q['title']), 'icon':icon,
                'icon_status':status, 'icon_reason':reason,
                'icon_model_sources':model_sources.get(icon, []), 'icon_global_occurrences':icons[icon],
                'description':list(q.get('description',[])), 'description_issues':description_issues,
                'tasks':tasks, 'advancement_evidence':sources,
                'rewards':json.loads(json.dumps(q['rewards'])),
                'reward_notes':[f for f in manual if f['kind']=='reward'],
                'dependency_notes':[f for f in manual if f['kind'] in ('dependency','duplicate','mechanic')],
                'dependencies':list(q.get('dependencies',[])), 'editorial_findings':manual,
                'review_scope':'Context inventory + retained editorial findings; supported_by_objective does not mean final approval. Review entries remain unresolved.',
            }
            records.append(record); chapter_records.append(record)
        geometry_problems = [p for p in geometry_issues if p['location'].split('#')[0]==name]
        long_edges = sum(p['code']=='edge_long' for p in geometry_problems)
        bad_prose = sum(bool(r['description_issues']) for r in chapter_records)
        mismatch = sum(r['icon_status']=='mismatch' for r in chapter_records)
        unresolved = sum(r['icon_status']=='review' for r in chapter_records)
        score = 2 if bad_prose>len(chapter_records)/2 or mismatch else 3
        summaries.append({'file':name, 'title':str(chapter['title']), 'quests':len(chapter_records),
                          'score_1_to_5':score,
                          'assessment':'Предварительная оценка по статическим признакам: 2 — требуется существенная редактура; 3 — требуется точечная редактура. Не оценка отображения в игре.',
                          'icons_mismatch':mismatch,'icons_review':unresolved,'descriptions_flagged':bad_prose,
                          'long_edges':long_edges,'geometry':geometry[name], 'issues':geometry_problems})
    output = {'baseline_commit':sha,
              'method':'All 478 baseline quests are inventoried with full task conditions and available exact-JAR evidence. Semantic decisions use action context and retained auditor findings; no keyword-only icon rejection. Ambiguities are review, not defects.',
              'limitations':['No final editorial approval for unresolved icon entries','Item model assets do not establish runtime registration','No game test'],
              'chapters':summaries,'quests':records}
    (root/'reviews/semantic_inventory.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    lines=['# Аудит оформления Alpha 42','',f'База `{sha}`. Все 18 глав и 478 квестов представлены в `reviews/semantic_inventory.json`.',
           'В каждой карточке: исходный текст, значок, задачи, доступные условия из точного JAR, награды и замечания.',
           'Это полный реестр проверки, но не заявление, что все спорные значки одобрены. Неопределённость сохранена явно.','',
           '| Глава | Квесты | Явные ошибки значков | Значки для оценки | Тексты с замечаниями | Связи >8 ед. | Оценка /5 |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for s in summaries:
        lines.append(f'| {s["title"]} | {s["quests"]} | {s["icons_mismatch"]} | {s["icons_review"]} | {s["descriptions_flagged"]} | {s["long_edges"]} | {s["score_1_to_5"]} |')
    lines += ['', 'Оценка предварительная, по данным: массовый служебный текст или явные ошибки значков дают 2/5; остальные главы 3/5 до визуальной проверки. Это не измерение эстетики интерфейса.',
              '', '## Конкретные редакторские находки', '']
    for r in records:
        if not r['editorial_findings']:continue
        lines += [f'### {r["title"]} — `{r["id"]}`',f'Файл: `{r["chapter"]}`.']
        lines += [f'- **{f["kind"]} / {f["status"]}:** {f["message"]}' for f in r['editorial_findings']]
        lines.append('')
    lines += ['## Геометрия и интерфейс','',
              'Ни одна исходная глава не имеет найденных пересечений прямых связей или заходов в диски посторонних узлов в принятой модели. Это не опровергает неудобство графов: обнаружены длинные связи, большие габариты и неравномерность.',
              'Порог 8 единиц — редакторский сигнал, а не ограничение FTB. Формы и подписи в игре проверяются отдельно.',
              'Задачи и награды раскладываются двумя колонками Java-интерфейса; подробности в `FTB_UI_CAPABILITIES.md`.',
              '', '## Эталон и следующий этап','',
              'Эталон — «Военное дело»: 25 квестов, 29 задач, 52 награды; бои, экспедиции, монтаж и составные испытания.',
              'Задачи, награды и зависимости сохраняются. Слабые связи (артиллерия после Пастецвета, роща и зал стража в одной цепи) требуют отдельного согласования, не скрытого изменения ради геометрии.',
              'Остальные 17 глав не изменяются до оценки эталона. Пересмотр наград остаётся отдельной Alpha 43.']
    (root/'docs/POLISH_AUDIT.md').write_text('\n'.join(lines)+'\n')
    for z in archives.values():z.close()
    print(json.dumps({'quests':len(records),'chapters':len(summaries),'icon_status':dict(Counter(r['icon_status'] for r in records)),'descriptions_flagged':sum(bool(r['description_issues']) for r in records)},ensure_ascii=False))


if __name__=='__main__':main()
