#!/usr/bin/env python3
"""Turn the author's medallion pictures into FTB Quests shapes, one per quest type.

  python tools/quest_frames.py            # art/frames/frame_<type>.png -> kubejs/assets/ftbquests/textures/shapes/<type>/
  python tools/quest_frames.py --check    # every type has its three textures, masks with alpha

FTB Quests 2001.4.22 draws a quest button from three textures of its shape: shape.png filled with #212121,
background.png on top at alpha 150/255, outline.png tinted with the quest state colour (locked, available,
started, completed), then the item icon in the middle 2/3 of the button times the quest's icon_scale.
Every type uses the same round medallion: the picture is cut to a circle and its middle darkened so the icon
reads, the outline is a thin white rim that FTB colours by state. Quests get icon_scale ICON_SCALE, so even a
square block icon stays inside the inner disc (its corners reach 2/3 * ICON_SCALE / sqrt(2) of the radius).
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

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
SS = 4                 # supersampling for smooth circle edges
INNER = 0.74           # diameter share of the darkened inner disc that holds the icon
INNER_SHADE = 0.45     # brightness kept in the middle of the disc
RIM = 0.035            # outline width, share of the diameter
ICON_SCALE = 0.75
MCMETA = {'texture': {'blur': True}}


def disc(diameter_share, blur=0.0):
    """White disc on transparent black, antialiased, as an L mask of SIZE."""
    big = SIZE * SS
    mask = Image.new('L', (big, big), 0)
    r = big * diameter_share / 2
    ImageDraw.Draw(mask).ellipse([big / 2 - r, big / 2 - r, big / 2 + r, big / 2 + r], fill=255)
    mask = mask.resize((SIZE, SIZE), Image.LANCZOS)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur else mask


def medallion_crop(image):
    """Square crop around the medallion: the generator draws it on black, not always edge to edge."""
    image = image.convert('RGB')
    lit = image.convert('L').point(lambda v: 255 if v > 24 else 0)
    box = lit.getbbox() or (0, 0, image.width, image.height)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    half = max(box[2] - box[0], box[3] - box[1]) / 2
    return image.crop((round(cx - half), round(cy - half), round(cx + half), round(cy + half))).resize((SIZE, SIZE), Image.LANCZOS)


def render(picture):
    outer = disc(1.0)
    art = medallion_crop(picture)
    # Darken the inner disc smoothly so any icon reads on it; the ornament stays at the edge.
    inner = disc(INNER, blur=SIZE * 0.02)
    shade = inner.point(lambda v: round(255 - (255 - 255 * INNER_SHADE) * v / 255))
    art = ImageChops.multiply(art, Image.merge('RGB', [shade] * 3))
    background = art.convert('RGBA')
    background.putalpha(outer)
    shape = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    shape.putalpha(outer)
    rim = ImageChops.subtract(outer, disc(1.0 - 2 * RIM))
    outline = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    outline.putalpha(rim)
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
        for part, image in render(Image.open(source)).items():
            image.save(TARGET / name / part, optimize=True)
            (TARGET / name / (part + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print('prepared', name)
    return check()


if __name__ == '__main__':
    sys.exit(main())
