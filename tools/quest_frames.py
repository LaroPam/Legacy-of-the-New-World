#!/usr/bin/env python3
"""Turn the author's medallion pictures into FTB Quests shapes, one per quest type.

  python tools/quest_frames.py            # art/frames/frame_<type>.png -> kubejs/assets/ftbquests/textures/shapes/<type>/
  python tools/quest_frames.py --check    # every type has its three textures, masks with alpha

FTB Quests 2001.4.22 draws a quest button from three textures of its shape: shape.png filled with #212121,
background.png on top at alpha 150/255, outline.png tinted with the quest state colour (locked, available,
started, completed), then the item icon in the middle 2/3 of the button times the quest's icon_scale.
Every type uses the same round medallion. The picture is cut out of its black background (ornaments that stick
out of the ring stay), the dark recess in its middle is found and centred, and darkened a little more so the icon
reads; the outline is a thin white ring around the recess that FTB colours by quest state. Quests get
icon_scale ICON_SCALE, so the icon stays inside the recess. Preparing needs numpy; --check needs only Pillow.
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/frames'
TARGET = ROOT / 'kubejs/assets/ftbquests/textures/shapes'
TYPES = {  # shape name: (picture, what it marks)
    'step': ('frame_step.png', 'обычный шаг'),
    'expedition': ('frame_expedition.png', 'экспедиция'),
    'milestone': ('frame_milestone.png', 'веха, особое достижение'),
    'trial': ('frame_trial.png', 'опасное испытание'),
    'tech': ('frame_tech.png', 'техника и стройка'),
    'boss': ('frame_boss.png', 'босс, кульминация'),
    'home': ('frame_home.png', 'дом, люди, торговля'),
}
SIZE = 256
WORK = 1024            # pictures are cut at this size, then scaled down for smooth edges
ICON_SCALE = 0.75
RECESS = 0.72          # every picture is scaled so its dark recess spans this share of the button
# a square icon's corners reach 2/3 * ICON_SCALE * sqrt(2) of the button: 0.71 < RECESS, so icons stay inside
RECESS_SHADE = 0.6     # brightness kept in the middle of the recess, where the icon sits
RIM = 0.03             # state rim width around the recess, share of the button
BLEND, FILL = 150 / 255, 0x21 / 255  # FTB: background alpha, shape fill (Color4I.DARK_GRAY)
MCMETA = {'texture': {'blur': True}}


def measure(picture):
    """Centre and radius of the dark recess, in pixels."""
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
    return cx, cy, edge(*profile(cx, cy))


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


def render(picture):
    """shape, background and outline textures of one medallion."""
    import numpy as np
    picture = picture.convert('RGB')
    cx, cy, recess = measure(picture)
    half = recess / RECESS  # ornaments beyond the button are cut softly along its circle
    work = picture.crop((round(cx - half), round(cy - half), round(cx + half), round(cy + half))).resize((WORK, WORK), Image.LANCZOS)
    rgb = np.asarray(work, dtype=np.float32) / 255
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    alpha, inside = silhouette(lum)
    share = RECESS / 2  # recess radius as a share of the button width
    yy, xx = np.mgrid[0:WORK, 0:WORK]
    r = np.sqrt((yy - WORK / 2) ** 2 + (xx - WORK / 2) ** 2) / WORK
    edge = np.clip((0.5 - r) / 0.015, 0, 1)
    alpha, inside = alpha * edge, inside * edge
    shade = RECESS_SHADE + (1 - RECESS_SHADE) * np.clip((r - share * 0.55) / (share * 0.45), 0, 1)
    rgb = rgb * shade[..., None]
    # FTB draws the background at alpha 150/255 over the #212121 fill: undo that blend so the frame keeps its colours.
    rgb = (rgb - (1 - BLEND) * FILL) / BLEND
    def texture(rgb, a):
        data = np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).astype('uint8')
        return Image.fromarray(data, 'RGBA').resize((SIZE, SIZE), Image.LANCZOS)
    white = np.ones_like(rgb)
    background = texture(rgb, alpha)
    shape = texture(white, inside)
    outline = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    outline.putalpha(ring(share * 2, RIM))
    return {'shape.png': shape, 'background.png': background, 'outline.png': outline}


def check():
    problems = []
    for name, (picture, _) in TYPES.items():
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
    for name, (picture, _) in TYPES.items():
        source = SOURCE / picture
        if not source.exists():
            print(f'skip {name}: no art/frames/{picture}')
            continue
        (TARGET / name).mkdir(parents=True, exist_ok=True)
        parts = render(Image.open(source))
        for part, image in parts.items():
            image.save(TARGET / name / part, optimize=True)
            (TARGET / name / (part + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print('prepared', name)
    return check()


if __name__ == '__main__':
    sys.exit(main())
