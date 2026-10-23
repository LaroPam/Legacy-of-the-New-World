#!/usr/bin/env python3
"""Turn the author's medallion pictures into quest medallions, one per quest type.

  python tools/quest_frames.py            # art/frames/frame_<type>.png -> FTB shape textures and frame images
  python tools/quest_frames.py --check    # every type has its textures, masks with alpha

FTB Quests 2001.4.22 draws a quest button from three textures of its shape: shape.png filled with #212121,
background.png on top at alpha 150/255, outline.png tinted with the quest state colour, then the item icon in the
middle 2/3 of the button times the quest's icon_scale; a black layer at alpha 100 over shape.png darkens quests
whose dependencies are not complete. A background at alpha 150 can never be brighter than ~64 %, so the frame
itself is not part of the shape:

- the frame (the author's picture fitted whole into the button, cut out of its black background, recess empty) is a
  chapter image under the quest button at full brightness: a dimmed copy always, the bright one appears once the
  quest's prerequisite is completed (`dependency`), so locked quests look dimmed and open or done ones bright;
- the shape keeps the recess: shape.png is opaque there and 5/255 over the frame (FTB counts clicks where the mask
  alpha is at least 5, so the whole medallion stays clickable while the dark fill stays invisible),
  background.png is a glow in the type's colour, outline.png a thin white ring around the recess that FTB colours
  by quest state.

Quests get ICON_SCALE, small enough for the icon to stay inside every recess. Preparing needs numpy; --check and
frame_images() only Pillow.
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/frames'
TARGET = ROOT / 'kubejs/assets/ftbquests/textures/shapes'
FRAMES = ROOT / 'kubejs/assets/nasledie/textures/frames'
TYPES = {  # shape name: (picture, what it marks, glow colour of the recess)
    'step': ('frame_step.png', 'обычный шаг', (120, 170, 255)),
    'expedition': ('frame_expedition.png', 'экспедиция', (255, 165, 60)),
    'milestone': ('frame_milestone.png', 'веха, особое достижение', (185, 105, 255)),
    'trial': ('frame_trial.png', 'опасное испытание', (255, 55, 45)),
    'tech': ('frame_tech.png', 'техника и стройка', (60, 220, 255)),
    'boss': ('frame_boss.png', 'босс, кульминация', (255, 125, 40)),
    'home': ('frame_home.png', 'дом, люди, торговля', (95, 230, 120)),
}
SIZE = 256
WORK = 1024            # pictures are cut at this size, then scaled down for smooth edges
ICON_SCALE = 0.6       # quests' icon_scale (tools/questbook.py)
DIM = 0.6              # brightness of a locked quest's frame, like FTB's black overlay at alpha 100
CLICKABLE = 5 / 255    # shape.png alpha over the frame: FTB's click test needs at least 5
ICON_REACH = 2 / 3 * ICON_SCALE * 2 ** 0.5  # diameter a square icon's corners span, share of the button
GLOW_CORE, GLOW_EDGE = 0.30, 0.62  # glow brightness on screen (FTB caps the background near 0.64) in the middle, at the rim
RIM = 0.03             # state rim width around the recess, share of the button
BLEND, FILL = 150 / 255, 0x21 / 255  # FTB: background alpha, shape fill (Color4I.DARK_GRAY)
MCMETA = {'texture': {'blur': True}}


def measure(picture):
    """Centre and radius of the dark recess and how far the medallion reaches, ornaments included, in pixels."""
    import numpy as np  # needed only to prepare pictures, not for --check
    lum = np.asarray(picture.convert('L'), dtype=np.float32) / 255
    ys, xs = np.nonzero(lum > 0.12)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    half = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2
    angles = np.linspace(0, 2 * np.pi, 720, endpoint=False)

    def profile(cx, cy):
        radii = np.arange(0, half, 2.0)
        px = np.clip((cx + radii[:, None] * np.cos(angles)).astype(int), 0, lum.shape[1] - 1)
        py = np.clip((cy + radii[:, None] * np.sin(angles)).astype(int), 0, lum.shape[0] - 1)
        return radii, lum[py, px].mean(axis=1)

    def edge(radii, mean):  # going out from the middle, the last dark circle before the ring's brightest one
        peak = radii[np.argmax(mean)]
        return radii[(radii < peak) & (mean < mean.max() / 2)].max() + 2

    for _ in range(2):
        recess = edge(*profile(cx, cy))
        yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
        dark = ((yy - cy) ** 2 + (xx - cx) ** 2 < (0.9 * recess) ** 2) & (lum < 0.3)
        cy, cx = yy[dark].mean(), xx[dark].mean()
    lit_y, lit_x = np.nonzero(lum > 0.05)
    reach = np.sqrt((lit_y - cy) ** 2 + (lit_x - cx) ** 2).max()
    return cx, cy, edge(*profile(cx, cy)), reach


def silhouette(lum):
    """Opaque inside the medallion (recess and dark metal included), soft glow outside, black background clear."""
    import numpy as np
    from PIL import ImageDraw as Draw
    lit = Image.fromarray(((lum > 0.03) * 255).astype('uint8'))
    outside = lit.copy()
    for corner in ((0, 0), (lit.width - 1, 0), (0, lit.height - 1), (lit.width - 1, lit.height - 1)):
        if outside.getpixel(corner) == 0:
            Draw.floodfill(outside, corner, 128)
    inside = np.asarray(outside) != 128
    glow = np.clip((lum - 0.03) / 0.12, 0, 1)
    return np.maximum(inside.astype(np.float32), glow), inside


def ring(diameter_share, width_share):
    big = SIZE * 4
    mask = Image.new('L', (big, big), 0)
    draw = ImageDraw.Draw(mask)
    outer, inner = big * (diameter_share / 2 + width_share), big * diameter_share / 2
    draw.ellipse([big / 2 - outer, big / 2 - outer, big / 2 + outer, big / 2 + outer], fill=255)
    draw.ellipse([big / 2 - inner, big / 2 - inner, big / 2 + inner, big / 2 + inner], fill=0)
    return mask.resize((SIZE, SIZE), Image.LANCZOS)


def render(picture, glow):
    """Shape textures, frame image (bright, dim) of one medallion and its recess diameter as a share of the button."""
    import numpy as np
    picture = picture.convert('RGB')
    cx, cy, recess, reach = measure(picture)
    half = reach * 1.02  # the whole medallion fits, nothing is cut
    work = picture.crop((round(cx - half), round(cy - half), round(cx + half), round(cy + half))).resize((WORK, WORK), Image.LANCZOS)
    art = np.asarray(work, dtype=np.float32) / 255
    lum = art @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    alpha, inside = silhouette(lum)
    share = recess / half / 2  # recess radius as a share of the button width
    yy, xx = np.mgrid[0:WORK, 0:WORK]
    r = np.sqrt((yy - WORK / 2) ** 2 + (xx - WORK / 2) ** 2) / WORK / share  # 1 at the recess edge
    fill = np.clip((1.0 - r) / 0.06, 0, 1)  # the recess, blending into the ring at its edge
    # The recess glows in the type's colour: a soft core, brighter towards the rim like light inside a lens.
    t = np.clip((r - 0.55) / 0.45, 0, 1)
    light = GLOW_CORE + (GLOW_EDGE - GLOW_CORE) * t * t * (3 - 2 * t)
    lens = light[..., None] * (np.array(glow, dtype=np.float32) / 255)[None, None, :]
    lens = (lens - (1 - BLEND) * FILL) / BLEND  # FTB blends the background at 150/255 over #212121: undo it

    def texture(rgb, a):
        data = np.dstack([np.clip(rgb, 0, 1) * 255, np.clip(a, 0, 1) * 255]).astype('uint8')
        return Image.fromarray(data, 'RGBA').resize((SIZE, SIZE), Image.LANCZOS)

    white = np.ones_like(art)
    frame_alpha = np.maximum(alpha, inside) * (1 - fill)
    outline = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    outline.putalpha(ring(share * 2, RIM))
    shape = texture(white, np.maximum(fill, inside * CLICKABLE))
    # LANCZOS rings below CLICKABLE next to the opaque recess and at the rim: hold the floor where the medallion is.
    covered = np.asarray(Image.fromarray((inside * 255).astype('uint8')).resize((SIZE, SIZE), Image.BILINEAR)) >= 128
    mask = np.asarray(shape.getchannel('A'))
    shape.putalpha(Image.fromarray(np.where(covered, np.maximum(mask, round(CLICKABLE * 255)), mask).astype('uint8')))
    shapes = {'shape.png': shape, 'background.png': texture(lens, fill), 'outline.png': outline}
    frames = {'': texture(art, frame_alpha), '_dim': texture(art * DIM, frame_alpha)}
    return shapes, frames, share * 2


def node_type(quest, data, link=None):
    return (link or {}).get('shape') or quest.get('shape') or data['chapter'].get('default_quest_shape', 'step')


def frame_images(name, data, dependency, every, chapters):
    """Chapter image entries for the frames of a chapter's quests and links: dimmed always, bright once the quest's
    prerequisite is completed (the deepest one when all are needed: likely the last to be done; each of them when
    fewer are enough, so the frame never stays dim because of a prerequisite the players skipped)."""
    depth = {}

    def prerequisites(quest):
        return [p for p in (dependency(d, quest['_chapter']) for d in quest.get('deps', [])) if p in every]

    def deep(ident, seen=()):
        if ident not in depth:
            depth[ident] = 1 + max((deep(p, seen + (ident,)) for p in prerequisites(every[ident]) if p not in seen),
                                   default=-1)
        return depth[ident]

    def brighten_after(quest, prereqs):
        needed = int(quest.get('min_required_dependencies', 0) or 0)
        if str(quest.get('dependency_requirement', '')).startswith('one_') or 0 < needed < len(prereqs):
            return sorted(set(prereqs))
        return [max(prereqs, key=lambda p: (deep(p), p))]

    nodes = [(q, q, None) for q in data['quests']]
    nodes += [(every[dependency(l['quest'], name)], None, l) for l in data.get('links', [])]
    entries = []
    for quest, own, link in nodes:
        place = link or own
        kind = node_type(quest, chapters[quest['_chapter']], link)
        if kind not in TYPES:
            continue
        prereqs = prerequisites(quest)
        size = float(place.get('size', data['chapter'].get('default_quest_size', 1)))
        base = {'x': float(place.get('x', 0)), 'y': float(place.get('y', 0)), 'width': size, 'height': size,
                'rotation': 0.0, 'color': 0xFFFFFF, 'alpha': 255}
        if prereqs:
            entries.append(dict(base, image=f'nasledie:textures/frames/{kind}_dim.png', order=0))
            entries += [dict(base, image=f'nasledie:textures/frames/{kind}.png', order=1, dependency=p)
                        for p in brighten_after(quest, prereqs)]
        else:
            entries.append(dict(base, image=f'nasledie:textures/frames/{kind}.png', order=1))
    return entries


def check():
    problems = []
    for name, (picture, _, _) in TYPES.items():
        if not (SOURCE / picture).exists():
            problems.append(f'{name}: picture art/frames/{picture} is missing')
        for part in ('shape.png', 'background.png', 'outline.png', 'frame.png', 'frame_dim.png'):
            path = TARGET / name / part if not part.startswith('frame') else FRAMES / part.replace('frame', name)
            if not path.exists():
                problems.append(f'{path.relative_to(ROOT)}: not prepared')
                continue
            image = Image.open(path)
            if image.mode != 'RGBA' or image.size != (SIZE, SIZE):
                problems.append(f'{path.relative_to(ROOT)}: {image.mode} {image.size}, expected RGBA {SIZE}x{SIZE}')
            meta = path.with_name(path.name + '.mcmeta')
            if not meta.exists() or json.loads(meta.read_text()) != MCMETA:
                problems.append(f'{meta.relative_to(ROOT)}: missing or different')
    for line in problems:
        print('ERROR', line)
    print(f'{len(TYPES)} quest frames: ' + ('ok' if not problems else f'{len(problems)} problems'))
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    if args.check:
        return check()
    for name, (picture, _, glow) in TYPES.items():
        source = SOURCE / picture
        if not source.exists():
            print(f'skip {name}: no art/frames/{picture}')
            continue
        (TARGET / name).mkdir(parents=True, exist_ok=True)
        FRAMES.mkdir(parents=True, exist_ok=True)
        parts, frames, recess = render(Image.open(source), glow)
        for suffix, image in frames.items():
            image.save(FRAMES / f'{name}{suffix}.png', optimize=True)
            (FRAMES / f'{name}{suffix}.png.mcmeta').write_text(json.dumps(MCMETA, indent=2) + '\n')
        if recess < ICON_REACH:
            print(f'ERROR {name}: recess {recess:.2f} of the button, a square icon needs {ICON_REACH:.2f}')
        for part, image in parts.items():
            image.save(TARGET / name / part, optimize=True)
            (TARGET / name / (part + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print(f'prepared {name}: recess {recess:.2f} of the button, icon needs {ICON_REACH:.2f}')
    return check()


if __name__ == '__main__':
    sys.exit(main())
