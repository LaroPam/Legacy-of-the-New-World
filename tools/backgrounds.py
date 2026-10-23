#!/usr/bin/env python3
"""Prepare chapter backgrounds for the quest book.

  python tools/backgrounds.py            # art/backgrounds/*.png -> kubejs/assets/nasledie/textures/backgrounds/
  python tools/backgrounds.py --check    # every source has a prepared background in the expected brightness

Sources are the author's generated pictures (16:9). They keep their own resolution and every pixel: the only change
is an even darkening, every channel multiplied by one factor so the picture's mean brightness drops to MEAN
(darker pictures stay as they are). The author asked for this after a gamma curve, blur and vignette had spoilt the
pictures. A .png.mcmeta turns on smooth scaling: FTB stretches the background to the screen. The theme uses the
results as per-chapter `background` (see tools/apply_palettes.py and docs/BACKGROUND_PROMPTS.md).
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/backgrounds'
TARGET = ROOT / 'kubejs/assets/nasledie/textures/backgrounds'
MEAN = 0.18           # mean brightness after darkening (0..1)
MCMETA = {'texture': {'blur': True}}  # smooth scaling to the screen, like FTB Quests shape textures


def luminance(image):
    return ImageStat.Stat(image.convert('L')).mean[0] / 255


def factor(source):
    return min(1.0, MEAN / max(luminance(source), 1e-6))


def prepare(path):
    source = Image.open(path).convert('RGB')
    k = factor(source)
    return source.point(lambda v: round(v * k)), luminance(source), k


def check():
    problems = []
    sources = sorted(SOURCE.glob('*.png'))
    for path in sources:
        target = TARGET / path.name
        if not target.exists():
            problems.append(f'{path.name}: not prepared')
            continue
        mcmeta = target.with_name(target.name + '.mcmeta')
        if not mcmeta.exists() or json.loads(mcmeta.read_text()) != MCMETA:
            problems.append(f'{path.name}: missing or different {mcmeta.name}')
        image, source = Image.open(target), Image.open(path)
        if image.size != source.size:
            problems.append(f'{path.name}: size {image.size}, the source is {source.size}')
        if luminance(image) > MEAN + 0.01:
            problems.append(f'{path.name}: brightness {luminance(image):.2f} above {MEAN}')
    extra = sorted(p.name for p in TARGET.glob('*') if not (SOURCE / p.name.removesuffix('.mcmeta')).exists())
    problems += [f'{name}: prepared file without a source' for name in extra]
    for line in problems:
        print('ERROR', line)
    print(f'{len(sources)} backgrounds: ' + ('ok' if not problems else f'{len(problems)} problems'))
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    if args.check:
        return check()
    TARGET.mkdir(parents=True, exist_ok=True)
    for path in sorted(SOURCE.glob('*.png')):
        image, before, k = prepare(path)
        image.save(TARGET / path.name, optimize=True)
        (TARGET / (path.name + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print(f'{path.name:24} {image.size[0]}x{image.size[1]}  brightness {before:.2f} -> {luminance(image):.2f}  x{k:.2f}')
    return check()


if __name__ == '__main__':
    sys.exit(main())
