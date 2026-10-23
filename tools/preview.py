#!/usr/bin/env python3
"""Render schematic PNG previews of chapters (layout, shapes, item icons, titles).

  python tools/preview.py OUT_DIR [--jars JAR_DIR] [chapter ...]

An approximation of the FTB Quests screen: positions, sizes, shapes and dependency lines are real;
fonts, frames and colours are not. Item icons are taken from the mod JARs when --jars is given.
"""
import argparse
import io
import json
from pathlib import Path
import re
import zipfile

from PIL import Image, ImageDraw, ImageFont

import questbook

UNIT = 56
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BG = (24, 28, 36)
LINE = (120, 150, 190)
SHAPE_FILL = {'star': (210, 170, 60), 'crown': (220, 120, 60), 'shield': (170, 70, 70), 'scroll': (150, 120, 80),
              'heart': (200, 90, 130), 'gear': (110, 130, 150)}


class Icons:
    def __init__(self, jars):
        self.index, self.cache = {}, {}
        for jar in sorted(Path(jars).glob('*.jar')) if jars else []:
            archive = zipfile.ZipFile(jar)
            for name in archive.namelist():
                match = re.match(r'assets/([^/]+)/textures/(item|block)/(.+)\.png$', name)
                if match:
                    self.index.setdefault((match[1], match[3]), (archive, name))

    def get(self, ident):
        if ident in self.cache:
            return self.cache[ident]
        ns, _, path = str(ident).partition(':')
        image = None
        for candidate in (path, path + '_front', path + '_side', path + '_top', path.replace('_block', '')):
            entry = self.index.get((ns, candidate))
            if entry:
                image = Image.open(io.BytesIO(entry[0].read(entry[1]))).convert('RGBA')
                image = image.crop((0, 0, image.width, image.width)).resize((32, 32), Image.NEAREST)
                break
        self.cache[ident] = image
        return image


def shape_points(kind, cx, cy, r):
    if kind == 'diamond':
        return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    if kind in ('square', 'rsquare', 'scroll', 'gear'):
        return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
    if kind == 'shield':
        return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r * 0.2), (cx, cy + r), (cx - r, cy + r * 0.2)]
    if kind == 'star':
        import math
        return [(cx + (r if i % 2 == 0 else r * 0.5) * math.sin(i * math.pi / 5),
                 cy - (r if i % 2 == 0 else r * 0.5) * math.cos(i * math.pi / 5)) for i in range(10)]
    return None


def render(name, data, ids, icons, out, every):
    quests = data['quests']
    links = data.get('links', [])
    xs = [float(q.get('x', 0)) for q in quests] + [float(l['x']) for l in links]
    ys = [float(q.get('y', 0)) for q in quests] + [float(l['y']) for l in links]
    minx, maxx, miny, maxy = min(xs) - 1.5, max(xs) + 1.5, min(ys) - 1.5, max(ys) + 2
    width, height = int((maxx - minx) * UNIT), int((maxy - miny) * UNIT) + 40
    image = Image.new('RGB', (width, height), BG)
    draw = ImageDraw.Draw(image)
    font, small = ImageFont.truetype(FONT, 13), ImageFont.truetype(FONT, 10)
    pos = lambda x, y: ((float(x) - minx) * UNIT, (float(y) - miny) * UNIT + 40)
    draw.text((10, 8), f"{data['chapter']['title']}  ({len(quests)} кв.)", fill=(230, 230, 230), font=font)
    # Links stand in for the linked quest: FTB draws dependency lines to and from them.
    by_id = {q['_id']: q for q in quests}
    linked = {questbook.dependency(l['quest'], name, ids): l for l in links}
    nodes = dict(by_id, **linked)
    for target_id, q in list(by_id.items()) + [(i, every[i]) for i in linked]:
        here = nodes[target_id]
        if q.get('hide_dependency_lines'):
            continue
        for dep in q.get('deps', []):
            other = nodes.get(questbook.dependency(dep, q['_chapter'], ids))
            if other:
                draw.line([pos(other['x'], other['y']), pos(here['x'], here['y'])], fill=LINE, width=2)
    entries = [(q, False) for q in quests] + [(dict(l, title='→ ' + str(l['quest'])), True) for l in links]
    for q, is_link in entries:
        cx, cy = pos(q['x'], q['y'])
        size = float(q.get('size', data['chapter'].get('default_quest_size', 1)))
        r = size * UNIT * 0.45
        kind = q.get('shape', data['chapter'].get('default_quest_shape', 'circle'))
        fill = SHAPE_FILL.get(kind, (70, 90, 120))
        if q.get('optional'):
            fill = tuple(int(c * 0.6) for c in fill)
        outline = (255, 255, 255) if not is_link else (120, 220, 120)
        points = shape_points(kind, cx, cy, r)
        if points:
            draw.polygon(points, fill=fill, outline=outline)
        else:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=2)
        icon = icons.get(q.get('icon', '')) if not is_link else None
        if icon:
            image.paste(icon, (int(cx - 16), int(cy - 16)), icon)
        title = str(q.get('title', ''))
        for i, line in enumerate(wrap(title, 18)):
            w = draw.textlength(line, font=small)
            draw.text((cx - w / 2, cy + r + 2 + i * 11), line, fill=(220, 220, 220), font=small)
    image.save(out / f'{name}.png')


def wrap(text, width):
    words, lines, line = text.split(), [], ''
    for word in words:
        if len(line) + len(word) + 1 > width and line:
            lines.append(line)
            line = word
        else:
            line = (line + ' ' + word).strip()
    return lines + [line] if line else lines


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('out', type=Path)
    parser.add_argument('chapters', nargs='*')
    parser.add_argument('--jars')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    chapters = questbook.load_sources()
    ids = questbook.resolve_ids(chapters)
    every = {}
    for chapter, data in chapters.items():
        for quest in data['quests']:
            quest['_chapter'] = chapter
            every[quest['_id']] = quest
    icons = Icons(args.jars)
    for name, data in chapters.items():
        if not args.chapters or name.removeprefix('nasledie_') in args.chapters:
            render(name, data, ids, icons, args.out, every)
            print('rendered', name)


if __name__ == '__main__':
    main()
