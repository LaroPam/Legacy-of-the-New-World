#!/usr/bin/env python3
"""Smooth dependency curves for the quest book, drawn as chapter images under the quest buttons.

FTB Quests 2001.4.22 draws dependencies only as straight lines. The book hides them (default_hide_dependency_lines,
and the theme makes the hover-only lines transparent) and draws its own curves instead:

- every dependency is a cubic Bezier curve: it leaves the prerequisite towards the quest and enters the quest
  straight on when the path continues that way, else along the branch the path turns into, so a row that starts
  above its column bends into it smoothly instead of meeting it at a right angle;
- one image per chapter holds all curves in the chapter's uncompleted line colour (order -2);
- one image per prerequisite holds its outgoing curves in the completed colour (order -1) and has the
  prerequisite as `dependency`: FTB shows it only once that quest is completed.

FTB facts used (bytecode of 2001.4.22): chapter images are added to the quest panel before the quest buttons, so
they lie under them; an image without `click` ignores the mouse unless the editor is on; an element at (x, y)
is centred at (x - minX) * (button + spacing) and an image of width w is button * w wide, so one grid unit is
(1 + quest_spacing / 6) image units; all quests are created before chapters read their images, so a
`dependency` in another chapter resolves.
"""
import io
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PALETTES = ROOT / 'reviews' / 'chapter_palettes.json'
TEXTURES = ROOT / 'kubejs' / 'assets' / 'nasledie' / 'textures' / 'curves'
PX = 40            # texture pixels per grid unit
WIDTH = 0.11       # curve width in grid units (FTB's line at thickness 0.24 is 0.10)
SAMPLES = 48
NODE_RADIUS = 0.5 / 1.175  # a size-1 quest button in grid units (button / (button + spacing)) / 2
MCMETA = json.dumps({'texture': {'blur': True}}, indent=2) + '\n'


def norm(v):
    length = math.hypot(*v)
    return (v[0] / length, v[1] / length) if length else (0.0, 0.0)


def graph(name, data, dependency, every):
    """Nodes {id: (x, y, size)} of the chapter (quests and links) and its dependency edges (prerequisite, quest)."""
    nodes = {q['_id']: (float(q.get('x', 0)), float(q.get('y', 0)), float(q.get('size', 1))) for q in data['quests']}
    for link in data.get('links', []):
        nodes[dependency(link['quest'], name)] = (float(link['x']), float(link['y']), float(link.get('size', 1)))
    edges = []
    for ident in nodes:
        quest = every[ident]
        if quest.get('hide_dependency_lines'):
            continue
        for dep in quest.get('deps', []):
            source = dependency(dep, quest['_chapter'])
            if source in nodes and source != ident:
                edges.append((source, ident))
    return nodes, edges


def branches(nodes, edges):
    """Unit directions of each node's outgoing edges."""
    out = {}
    for a, b in edges:
        out.setdefault(a, []).append(norm((nodes[b][0] - nodes[a][0], nodes[b][1] - nodes[a][1])))
    return out


def entry(d, outgoing):
    """Direction to enter a quest in: straight on if the path continues that way, else along the branch it turns
    into (a row starting above its column is entered from the side), unless that would turn back."""
    if not outgoing or any(c[0] * d[0] + c[1] * d[1] > 0.9 for c in outgoing):
        return d
    best = max(outgoing, key=lambda c: c[0] * d[0] + c[1] * d[1])
    return best if best[0] * d[0] + best[1] * d[1] > -0.2 else d


def departure(d, incoming):
    """Direction to leave a quest in: towards the next one, but a side branch first follows the path it leaves
    (like a railway switch) instead of breaking off at a right angle."""
    if incoming and abs(incoming[0] * d[0] + incoming[1] * d[1]) < 0.3:
        return norm((d[0] + incoming[0] * 0.75, d[1] + incoming[1] * 0.75))
    return d


def bezier(a, b, ta, tb):
    """Leave a along ta, enter b along tb; the end handle is shorter so a turn does not overshoot."""
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    p1 = (a[0] + ta[0] * dist * 0.5, a[1] + ta[1] * dist * 0.5)
    p2 = (b[0] - tb[0] * dist * 0.35, b[1] - tb[1] * dist * 0.35)
    points = []
    for i in range(SAMPLES + 1):
        t = i / SAMPLES
        u = 1 - t
        points.append((u ** 3 * a[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * b[0],
                       u ** 3 * a[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * b[1]))
    return points


def curves(name, data, dependency, every):
    """{(prerequisite, quest): [points in grid units]} for one chapter."""
    nodes, edges = graph(name, data, dependency, every)
    out = branches(nodes, edges)
    paths, arrivals = {}, {}
    for a, b in edges:
        d = norm((nodes[b][0] - nodes[a][0], nodes[b][1] - nodes[a][1]))
        arrivals.setdefault(b, []).append(entry(d, out.get(b)))
    for a, b in edges:
        d = norm((nodes[b][0] - nodes[a][0], nodes[b][1] - nodes[a][1]))
        incoming = arrivals[a][0] if len(arrivals.get(a, [])) == 1 else None
        paths[(a, b)] = bezier(nodes[a][:2], nodes[b][:2], departure(d, incoming), entry(d, out.get(b)))
    return nodes, paths


def draw(paths):
    """White soft strokes for the paths, the image's centre and size in grid units."""
    margin = WIDTH * 2
    xs = [p[0] for path in paths for p in path]
    ys = [p[1] for path in paths for p in path]
    x0, y0, x1, y1 = min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin
    ss = 2
    size = (max(1, round((x1 - x0) * PX)), max(1, round((y1 - y0) * PX)))
    mask = Image.new('L', (size[0] * ss, size[1] * ss), 0)
    pen = ImageDraw.Draw(mask)
    width = max(1, round(WIDTH * PX * ss * 0.8))
    for path in paths:
        pen.line([((x - x0) * PX * ss, (y - y0) * PX * ss) for x, y in path], fill=255, width=width, joint='curve')
    mask = mask.filter(ImageFilter.GaussianBlur(WIDTH * PX * ss * 0.12)).resize(size, Image.LANCZOS)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    image.putalpha(mask)
    return image, ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0)


def color_int(value):
    value = value.lstrip('#')
    return int(value[-6:], 16)


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


def chapter_images(name, data, dependency, every, colours, spacing):
    """Chapter image entries (plain dicts) and {path: bytes or text} of the textures they use."""
    nodes, paths = curves(name, data, dependency, every)
    if not paths:
        return [], {}
    scale = 1 + spacing / 6  # image units per grid unit
    short = name.removeprefix('nasledie_')
    entries, files = [], {}

    def add(image_paths, file_name, colour, order, source=None):
        image, (cx, cy), (w, h) = draw(image_paths)
        path = TEXTURES / short / file_name
        files[path] = png(image)
        files[path.with_name(file_name + '.mcmeta')] = MCMETA
        entry = {'x': cx, 'y': cy, 'width': w * scale, 'height': h * scale, 'rotation': 0.0,
                 'image': f'nasledie:textures/curves/{short}/{file_name}',
                 'color': color_int(colours[colour]), 'alpha': 255, 'order': order}
        if source:
            entry['dependency'] = source
        entries.append(entry)

    add(list(paths.values()), 'base.png', 'dependency_line_uncompleted_color', -2)
    for source in sorted({a for a, _ in paths}):
        add([p for (a, _), p in sorted(paths.items()) if a == source], f'{source.lower()}.png',
            'dependency_line_completed_color', -1, source)
    return entries, files


def crossings(name, data, dependency, every):
    """Curves that pass through a quest other than their two ends: [(prerequisite, quest, crossed)]."""
    nodes, paths = curves(name, data, dependency, every)
    found = []
    for (a, b), path in paths.items():
        for other, (x, y, size) in nodes.items():
            if other in (a, b):
                continue
            reach = NODE_RADIUS * size * 0.9 + WIDTH / 2
            if any(math.hypot(px - x, py - y) < reach for px, py in path):
                found.append((a, b, other))
    return found


def palettes():
    """{chapter: line colours} (the chapter palette, else the global one) and the theme's quest spacing."""
    design = json.loads(PALETTES.read_text(encoding='utf-8'))
    colours = {name: entry['properties'] for name, entry in design['chapters'].items()}
    return colours, design['global'], float(design['global'].get('quest_spacing', 1))
