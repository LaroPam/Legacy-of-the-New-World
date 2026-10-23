#!/usr/bin/env python3
"""Turn the author's medallion pictures into FTB Quests shapes, one per quest type.

  python tools/quest_frames.py            # art/frames/frame_<type>.png -> kubejs/assets/ftbquests/textures/shapes/<type>/
  python tools/quest_frames.py --check    # every type has its three textures, masks with alpha

FTB Quests 2001.4.22 draws a quest button from three textures of its shape: shape.png filled with #212121,
background.png on top at alpha 150/255, outline.png tinted with the quest state colour (locked, available,
started, completed), then the item icon in the middle 2/3 of the button times the quest's icon_scale.
Every type uses the same round medallion. The whole picture is fitted into the button, ornaments that stick out
of the ring included, and cut out of its black background. The empty recess in its middle is filled with a glow in
the type's colour (violet for milestones, red for trials...); the outline is a thin white ring around the recess
that FTB colours by quest state. Quests get questbook.ICON_SCALE, small enough for the icon to stay inside every
recess. Preparing needs numpy; --check needs only Pillow.
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from questbook import ICON_SCALE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/frames'
TARGET = ROOT / 'kubejs/assets/ftbquests/textures/shapes'
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
    """shape, background and outline textures of one medallion and its recess diameter as a share of the button."""
    import numpy as np
    picture = picture.convert('RGB')
    cx, cy, recess, reach = measure(picture)
    half = reach * 1.02  # the whole medallion fits, nothing is cut
    work = picture.crop((round(cx - half), round(cy - half), round(cx + half), round(cy + half))).resize((WORK, WORK), Image.LANCZOS)
    rgb = np.asarray(work, dtype=np.float32) / 255
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    alpha, inside = silhouette(lum)
    share = recess / half / 2  # recess radius as a share of the button width
    yy, xx = np.mgrid[0:WORK, 0:WORK]
    r = np.sqrt((yy - WORK / 2) ** 2 + (xx - WORK / 2) ** 2) / WORK / share  # 1 at the recess edge
    # The recess becomes a glow in the type's colour: a soft core, brighter towards the rim like light inside a lens.
    t = np.clip((r - 0.55) / 0.45, 0, 1)
    light = GLOW_CORE + (GLOW_EDGE - GLOW_CORE) * t * t * (3 - 2 * t)
    lens = light[..., None] * (np.array(glow, dtype=np.float32) / 255)[None, None, :]
    fill = np.clip((1.0 - r) / 0.06, 0, 1)[..., None]  # recess fully glow, blending into the ring at its edge
    # FTB draws the background at alpha 150/255 over the #212121 fill: undo that blend so colours stay as drawn.
    rgb = rgb * (1 - fill) + lens * fill
    rgb = (rgb - (1 - BLEND) * FILL) / BLEND
    def texture(rgb, a):
        data = np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).astype('uint8')
        return Image.fromarray(data, 'RGBA').resize((SIZE, SIZE), Image.LANCZOS)
    white = np.ones_like(rgb)
    background = texture(rgb, np.maximum(alpha, fill[..., 0]))
    shape = texture(white, np.maximum(inside, fill[..., 0]))
    outline = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    outline.putalpha(ring(share * 2, RIM))
    return {'shape.png': shape, 'background.png': background, 'outline.png': outline}, share * 2


def check():
    problems = []
    for name, (picture, _, _) in TYPES.items():
        if not (SOURCE / picture).exists():
            problems.append(f'{name}: picture art/frames/{picture} is missing')
        for part in ('shape.png', 'background.png', 'outline.png'):
            path = TARGET / name / part
            if not path.exists():
                problems.append(f'{name}/{part}: not prepared')
                continue
            image = Image.open(path)
            if image.mode != 'RGBA' or image.size != (SIZE, SIZE):
                problems.append(f'{name}/{part}: {image.mode} {image.size}, expected RGBA {SIZE}x{SIZE}')
            meta = path.with_name(part + '.mcmeta')
            if not meta.exists() or json.loads(meta.read_text()) != MCMETA:
                problems.append(f'{name}/{part}.mcmeta: missing or different')
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
        parts, recess = render(Image.open(source), glow)
        if recess < ICON_REACH:
            print(f'ERROR {name}: recess {recess:.2f} of the button, a square icon needs {ICON_REACH:.2f}')
        for part, image in parts.items():
            image.save(TARGET / name / part, optimize=True)
            (TARGET / name / (part + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print(f'prepared {name}: recess {recess:.2f} of the button, icon needs {ICON_REACH:.2f}')
    return check()


if __name__ == '__main__':
    sys.exit(main())
