#!/usr/bin/env python3
"""Render schematic PNG previews of chapters (layout, shapes, item icons, titles).

  python tools/preview.py OUT_DIR [--jars JAR_DIR] [chapter ...]
  python tools/preview.py OUT_DIR --screen --jars JAR_DIR [chapter ...]

An approximation of the FTB Quests screen: positions, sizes, shapes and dependency lines are real;
fonts, frames and colours are not. Item icons are taken from the mod JARs when --jars is given
(blocks and 3D items as one flat texture of their model).

--screen draws what the quest map looks like on a 1920x1080 screen (GUI scale 3): the chapter background and
colours from the theme, quest shapes from the FTB Quests JAR and kubejs, quest buttons and lines sized as in
FTB Quests 2001.4.22 (button 1.5 x zoom, spacing zoom x quest_spacing / 4, line zoom x 0.17 x 3/4). The zoom is
the default 16, or lower if the chapter would not fit. Progress is simulated: the first two steps of every
branch are completed, the next available, the rest locked. Interface buttons and tooltips are not drawn.
"""
import argparse
import functools
import io
import json
from pathlib import Path
import re
import zipfile

from PIL import Image, ImageDraw, ImageFont

import apply_palettes
import curves
import quest_frames
import questbook

UNIT = 56
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BG = (24, 28, 36)
LINE = (120, 150, 190)
SHAPE_FILL = {'star': (210, 170, 60), 'crown': (220, 120, 60), 'shield': (170, 70, 70), 'scroll': (150, 120, 80),
              'heart': (200, 90, 130), 'gear': (110, 130, 150)}


class Icons:
    """Flat item icons from the JARs: the item model's layer0, else a face of its block model."""
    FACES = ('layer0', 'front', 'side', 'all', 'texture', 'top', 'wool', 'particle')

    def __init__(self, jars):
        self.files, self.cache = {}, {}
        for jar in sorted(Path(jars).glob('*.jar')) if jars else []:
            archive = zipfile.ZipFile(jar)
            for name in archive.namelist():
                if re.match(r'assets/[^/]+/(textures|models)/.+\.(png|json)$', name):
                    self.files.setdefault(name, archive)

    def read(self, name):
        archive = self.files.get(name)
        return archive.read(name) if archive else None

    def model_texture(self, ns, path):
        textures, model = {}, f'{ns}:item/{path}'
        for _ in range(8):  # follow parents, the child's textures win
            mns, _, mpath = model.partition(':') if ':' in model else ('minecraft', '', model)
            data = self.read(f'assets/{mns}/models/{mpath}.json')
            if not data:
                break
            data = json.loads(data)
            textures = {**data.get('textures', {}), **textures}
            model = data.get('parent', '')
            if not model:
                break
        for face in self.FACES:
            ref = textures.get(face)
            for _ in range(4):
                if ref and ref.startswith('#'):
                    ref = textures.get(ref[1:])
            if ref:
                tns, _, tpath = ref.partition(':') if ':' in ref else ('minecraft', '', ref)
                if f'assets/{tns}/textures/{tpath}.png' in self.files:
                    return f'assets/{tns}/textures/{tpath}.png'
        return None

    def get(self, ident):
        if ident in self.cache:
            return self.cache[ident]
        ns, _, path = str(ident).partition(':')
        candidates = [self.model_texture(ns, path)]
        candidates += [f'assets/{ns}/textures/{kind}/{path}{suffix}.png' for kind in ('item', 'block')
                       for suffix in ('', '_front', '_side', '_top')]
        image = None
        for name in candidates:
            data = name and self.read(name)
            if data:
                image = Image.open(io.BytesIO(data)).convert('RGBA')
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


SCREEN, GUI_SCALE = (1920, 1080), 3
NODE_FILL = (0x21, 0x21, 0x21)  # Color4I.DARK_GRAY, under every quest shape


class Screen:
    """Theme, shapes and backgrounds for --screen previews."""

    def __init__(self, root, jars):
        self.root = root
        self.theme = apply_palettes.sections((root / apply_palettes.THEME).read_text())
        self.ftbq = next((zipfile.ZipFile(j) for j in sorted(Path(jars).glob('ftb-quests-*.jar'))), None) if jars else None
        self.shapes = {}

    def prop(self, chapter_id, key):
        return self.theme.get(chapter_id, {}).get(key) or self.theme['*'].get(key)

    def color(self, chapter_id, key):
        value = self.prop(chapter_id, key).lstrip('#')
        return tuple(int(value[i:i + 2], 16) for i in range(len(value) - 6, len(value), 2))

    def background(self, chapter_id):
        value = self.prop(chapter_id, 'background').split(';')[0].strip()
        ns, _, path = value.partition(':')
        if ns == 'color' or not path.endswith('.png'):
            return Image.new('RGB', SCREEN, BG)
        return Image.open(self.root / 'kubejs/assets' / ns / path).convert('RGB').resize(SCREEN, Image.BILINEAR)

    @functools.lru_cache(maxsize=None)
    def texture(self, value):
        """A theme texture like ftbquests:textures/gui/dependency.png from kubejs or the FTB Quests JAR."""
        ns, _, path = value.split(';')[0].strip().partition(':')
        local = self.root / 'kubejs/assets' / ns / path
        if local.exists():
            return Image.open(local).convert('RGBA')
        entry = f'assets/{ns}/{path}'
        if self.ftbq and entry in self.ftbq.namelist():
            return Image.open(io.BytesIO(self.ftbq.read(entry))).convert('RGBA')
        return Image.new('RGBA', (1, 1), (255, 255, 255, 255))

    def shape(self, name, part):
        if (name, part) not in self.shapes:
            local = self.root / f'kubejs/assets/ftbquests/textures/shapes/{name}/{part}.png'
            entry = f'assets/ftbquests/textures/shapes/{name}/{part}.png'
            if local.exists():
                image = Image.open(local)
            elif self.ftbq and entry in self.ftbq.namelist():
                image = Image.open(io.BytesIO(self.ftbq.read(entry)))
            else:
                image = None
            self.shapes[name, part] = image.convert('RGBA') if image else None
        return self.shapes[name, part]


def tinted(image, color, size, alpha=255):
    """ImageIcon.withColor: multiply the texture by a colour, then scale it to the button."""
    if size:
        image = image.resize((size, size), Image.BILINEAR)
    r, g, b, a = image.split()
    channels = [c.point(lambda v, k=k: v * k // 255) for c, k in zip((r, g, b), color)]
    return Image.merge('RGBA', (*channels, a.point(lambda v: v * alpha // 255)))


def line_strip(texture, start, end, width, color):
    """A dependency line as FTB draws it: one texture width per two line widths along it, v across it."""
    import math
    length = math.dist(start, end)
    tile = texture.resize((max(1, round(2 * width)), max(1, round(width))), Image.BILINEAR)
    strip = Image.new('RGBA', (max(1, round(length)), tile.height))
    for x in range(0, strip.width, tile.width):
        strip.paste(tile, (x, 0))
    strip = tinted(strip, color[:3], None, color[3] if len(color) > 3 else 255)
    angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))
    strip = strip.rotate(-angle, resample=Image.BICUBIC, expand=True)
    middle = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    return strip, (round(middle[0] - strip.width / 2), round(middle[1] - strip.height / 2))


def progress(quests, ids, name):
    """Simulated progress: steps at depth 0-1 completed, their followers available, the rest locked."""
    by_id = {q['_id']: q for q in quests}
    depth = {}

    def walk(ident, seen=()):
        if ident not in depth:
            deps = [questbook.dependency(d, name, ids) for d in by_id[ident].get('deps', [])]
            local = [d for d in deps if d in by_id and d not in seen]
            depth[ident] = 1 + max((walk(d, seen + (ident,)) for d in local), default=-1)
        return depth[ident]

    state = {}
    for ident in by_id:
        if walk(ident) < 2:
            state[ident] = 'completed'
    for ident, q in by_id.items():
        if ident not in state:
            deps = [questbook.dependency(d, name, ids) for d in q.get('deps', [])]
            state[ident] = 'not_started' if all(state.get(d) == 'completed' for d in deps if d in by_id) else 'locked'
    return state


def straight_lines(screen, chapter_id, nodes, every, ids, state, pos, zoom):
    """FTB's own dependency lines, for chapters without curves."""
    hi = 2  # lines are drawn at double resolution and scaled down, like a smooth GPU quad
    lines = Image.new('RGBA', (SCREEN[0] * hi, SCREEN[1] * hi), (0, 0, 0, 0))
    texture = screen.texture(screen.prop(chapter_id, 'dependency_line_texture') or 'ftbquests:textures/gui/dependency.png')
    thickness = float(screen.prop(chapter_id, 'dependency_line_thickness') or 0.17)
    width = zoom * thickness * 0.75 * GUI_SCALE * hi
    for ident, node in nodes.items():
        quest = every[ident]
        if quest.get('hide_dependency_lines'):
            continue
        for dep in quest.get('deps', []):
            other = nodes.get(questbook.dependency(dep, quest['_chapter'], ids))
            if other:
                done = state.get(questbook.dependency(dep, quest['_chapter'], ids)) == 'completed'
                key = 'dependency_line_completed_color' if done else 'dependency_line_uncompleted_color'
                a, b = pos(other), pos(node)
                strip, at = line_strip(texture, (a[0] * hi, a[1] * hi), (b[0] * hi, b[1] * hi), width,
                                       screen.color(chapter_id, key) + (255,))
                lines.alpha_composite(strip, (max(at[0], 0), max(at[1], 0)), (max(-at[0], 0), max(-at[1], 0)))
    lines = lines.resize(SCREEN, Image.LANCZOS)
    return lines


def draw_images(image, name, data, ids, every, chapters, state, pos, button, screen):
    """Chapter images as FTB draws them, by order: curves, then frames; one with a `dependency` once it is done."""
    resolve = lambda ref, ch: questbook.dependency(ref, ch, ids)  # noqa: E731
    entries, files = [], {}
    if data['chapter'].get('curves', True):
        colours, global_colours, spacing = curves.palettes()
        entries, files = curves.chapter_images(name, data, resolve, every, colours.get(name, global_colours), spacing)
    entries = entries + quest_frames.frame_images(name, data, resolve, every, chapters)
    for entry in sorted(entries, key=lambda e: e['order']):
        if entry.get('dependency') and state.get(entry['dependency']) != 'completed':
            continue
        prefix = 'nasledie:textures/curves/'
        if entry['image'].startswith(prefix):  # curves as just generated, which may not be built yet
            texture = Image.open(io.BytesIO(files[curves.TEXTURES / entry['image'][len(prefix):]])).convert('RGBA')
        else:
            texture = screen.texture(entry['image'])
        size = (max(1, round(entry['width'] * button)), max(1, round(entry['height'] * button)))
        colour = ((entry['color'] >> 16) & 255, (entry['color'] >> 8) & 255, entry['color'] & 255)
        layer = tinted(texture.resize(size, Image.BILINEAR), colour, None, entry['alpha'])
        x, y = pos({'x': entry['x'], 'y': entry['y']})
        image.alpha_composite(layer, (round(x - size[0] / 2), round(y - size[1] / 2)))


def render_screen(name, data, ids, icons, out, every, screen):
    chapter_id = data['chapter']['id']
    quests, links = data['quests'], data.get('links', [])
    by_id = {q['_id']: q for q in quests}
    linked = {questbook.dependency(l['quest'], name, ids): l for l in links}
    nodes = dict(by_id, **linked)
    spacing = float(screen.prop(chapter_id, 'quest_spacing') or 1)
    xs = [float(n['x']) for n in nodes.values()]
    ys = [float(n['y']) for n in nodes.values()]
    for zoom in (16, 12, 8, 4):
        unit = (zoom * 1.5 + zoom * spacing / 4) * GUI_SCALE
        if (max(xs) - min(xs) + 1) * unit <= SCREEN[0] and (max(ys) - min(ys) + 1) * unit <= SCREEN[1]:
            break
    button = zoom * 1.5 * GUI_SCALE
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    pos = lambda n: (SCREEN[0] / 2 + (float(n['x']) - cx) * unit, SCREEN[1] / 2 + (float(n['y']) - cy) * unit)

    image = screen.background(chapter_id).convert('RGBA')
    state = progress(quests, ids, name)
    if not data['chapter'].get('curves', True):
        image.alpha_composite(straight_lines(screen, chapter_id, nodes, every, ids, state, pos, zoom))
    draw_images(image, name, data, ids, every, screen.chapters, state, pos, button, screen)


    default_shape = data['chapter'].get('default_quest_shape', 'circle')
    for ident, node in nodes.items():
        quest = every[ident]
        # A link has its own size (QuestLink: 1 when unset), a quest falls back to the chapter default.
        default = 1 if ident in linked else data['chapter'].get('default_quest_size', 1)
        size = round(button * float(node.get('size', default)))
        x, y = pos(node)
        corner = (round(x - size / 2), round(y - size / 2))
        kind = node.get('shape') or quest.get('shape') or default_shape
        color = screen.color(chapter_id, f"quest_{state.get(ident, 'not_started')}_color")
        if screen.shape(kind, 'shape'):
            image.alpha_composite(tinted(screen.shape(kind, 'shape'), NODE_FILL, size), corner)
            image.alpha_composite(tinted(screen.shape(kind, 'background'), (255, 255, 255), size, 150), corner)
            image.alpha_composite(tinted(screen.shape(kind, 'outline'), color, size), corner)
        icon = icons.get(quest.get('icon', ''))
        if icon:
            side = round(size * 2 / 3 * float(quest.get('icon_scale', questbook.ICON_SCALE)))
            image.alpha_composite(icon.resize((side, side), Image.NEAREST), (round(x - side / 2), round(y - side / 2)))
        if state.get(ident) == 'locked' and screen.shape(kind, 'shape'):  # FTB darkens a locked quest over its shape
            image.alpha_composite(tinted(screen.shape(kind, 'shape'), (0, 0, 0), size, 100), corner)
    caption = ImageDraw.Draw(image)
    caption.text((12, SCREEN[1] - 24), f"{data['chapter']['title']} — zoom {zoom}, GUI 3, 1920x1080",
                 fill=(200, 200, 200), font=ImageFont.truetype(FONT, 14))
    image.convert('RGB').save(out / f'{name}.png')


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
    parser.add_argument('--screen', action='store_true', help='1920x1080 quest map over the chapter background')
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
    screen = Screen(Path(__file__).resolve().parents[1], args.jars) if args.screen else None
    if screen:
        screen.chapters = chapters
    for name, data in chapters.items():
        if not args.chapters or name.removeprefix('nasledie_') in args.chapters:
            if screen:
                render_screen(name, data, ids, icons, args.out, every, screen)
            else:
                render(name, data, ids, icons, args.out, every)
            print('rendered', name)


if __name__ == '__main__':
    main()
