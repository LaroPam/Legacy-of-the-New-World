#!/usr/bin/env python3
"""Prepare chapter backgrounds for the quest book.

  python tools/backgrounds.py            # art/backgrounds/*.png -> kubejs/assets/nasledie/textures/backgrounds/
  python tools/backgrounds.py --check    # every source has a prepared 16:9 background in the expected brightness

Sources are the author's generated pictures (16:9). Each one is brought to a common dark brightness so quest
icons and dependency lines stay readable: a gamma curve on luminance darkens midtones and keeps hues, highlights
are compressed, pixel noise blurred (more in the middle, where the quest map sits by default), a soft vignette
added, and a still bright middle darkened further. Daylight scenes that need strong darkening get a "day for
night" grade, otherwise they turn grey: more saturation and a cool tint in the shadows. Preparing needs numpy; --check needs only Pillow. The theme uses the
results as per-chapter `background` (see tools/apply_palettes.py and docs/BACKGROUND_PROMPTS.md).
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/backgrounds'
TARGET = ROOT / 'kubejs/assets/nasledie/textures/backgrounds'
SIZE = (1600, 900)
MEAN = 0.14           # target mean luminance (sRGB, 0..1)
MEAN_RANGE = (0.07, 0.17)
MIDDLE_MAX = 0.15     # the middle, where the quest map sits by default, is darkened down to this luminance
MIDDLE_VALUE_MAX = 0.26  # ... and this mean max(R, G, B): saturated red lava is dim by luminance, yet bright
KNEE = 0.6            # luminance above this is compressed (bright clouds, sand, sun)
# "day for night", in full from gamma 3: saturation, cool tint and the luminance below which the tint applies
NIGHT_SATURATION = 1.4
NIGHT_TINT = (0.86, 0.96, 1.24)
NIGHT_SHADOWS = 0.35
BLUR_EDGE, BLUR_MIDDLE = 1.0, 2.5
VIGNETTE = 0.35       # corners darkened by this share
MCMETA = {'texture': {'blur': True}}  # smooth scaling to the screen, like FTB Quests shape textures


def luminance(image):
    return ImageStat.Stat(image.convert('L')).mean[0] / 255


def radial(size, inner, blur):
    """White ellipse in the middle (inner = share of width/height), soft edges, black corners."""
    w, h = size
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).ellipse([w * (1 - inner) / 2, h * (1 - inner) / 2, w * (1 + inner) / 2, h * (1 + inner) / 2], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur))


def tone(image, gamma):
    """Gamma on luminance only: darkens midtones more than highlights and keeps each pixel's hue."""
    import numpy as np  # needed only to prepare pictures, not for --check
    weights = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    rgb = np.asarray(image, dtype=np.float32) / 255
    lum = rgb @ weights
    target = lum ** gamma
    target = np.where(target < KNEE, target, KNEE + (target - KNEE) * 0.4)
    rgb = rgb * (target / np.maximum(lum, 1e-4))[..., None]
    night = min(1.0, max(0.0, (gamma - 1) / 2))
    rgb = target[..., None] + (rgb - target[..., None]) * (1 + (NIGHT_SATURATION - 1) * night)
    shadows = (1 - np.clip(target / NIGHT_SHADOWS, 0, 1))[..., None] * night
    rgb = rgb * (1 + (np.array(NIGHT_TINT, dtype=np.float32) - 1) * shadows)
    rgb = rgb * (target / np.maximum(rgb @ weights, 1e-4))[..., None]  # the tint must not change brightness
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype('uint8'), 'RGB')


def process(image, gamma):
    image = tone(image.convert('RGB').resize(SIZE, Image.LANCZOS), gamma)
    edge, middle = image.filter(ImageFilter.GaussianBlur(BLUR_EDGE)), image.filter(ImageFilter.GaussianBlur(BLUR_MIDDLE))
    image = Image.composite(middle, edge, radial(SIZE, 0.6, 120))
    keep = radial(SIZE, 1.15, 220).point(lambda v: int(255 * (1 - VIGNETTE) + v * VIGNETTE))
    return Image.composite(image, Image.new('RGB', SIZE, (0, 0, 0)), keep)


def calm_middle(image):
    """Darken a bright middle (sand, clouds, lava) so icons and lines stay readable there."""
    import numpy as np
    mask = radial(SIZE, 0.5, 90)
    weight = np.asarray(mask, dtype=np.float32) / 255
    for _ in range(5):  # the shade fades towards the edges, so one pass falls short of the limits
        rgb = np.asarray(image, dtype=np.float32) / 255
        lum = (rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32) * weight).sum() / weight.sum()
        value = (rgb.max(axis=2) * weight).sum() / weight.sum()
        factor = min(1.0, MIDDLE_MAX / lum, MIDDLE_VALUE_MAX / value)
        if factor > 0.99:
            break
        shade = mask.point(lambda v: int(255 * (1 - (1 - factor) * v / 255)))
        image = Image.composite(image, Image.new('RGB', SIZE, (0, 0, 0)), shade)
    return image


def prepare(path):
    source = Image.open(path)
    lo, hi = 0.8, 6.0
    for _ in range(14):  # gamma that brings the finished picture to the target brightness
        gamma = (lo + hi) / 2
        if luminance(process(source, gamma)) > MEAN:
            lo = gamma
        else:
            hi = gamma
    result = calm_middle(process(source, gamma))
    return result, luminance(source.convert('RGB')), luminance(result), gamma


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
        image = Image.open(target)
        if image.size != SIZE:
            problems.append(f'{path.name}: size {image.size}, expected {SIZE}')
        mean = luminance(image)
        if not MEAN_RANGE[0] <= mean <= MEAN_RANGE[1]:
            problems.append(f'{path.name}: brightness {mean:.2f} outside {MEAN_RANGE}')
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
        image, before, after, gamma = prepare(path)
        image.save(TARGET / path.name, optimize=True)
        (TARGET / (path.name + '.mcmeta')).write_text(json.dumps(MCMETA, indent=2) + '\n')
        print(f'{path.name:24} brightness {before:.2f} -> {after:.2f}  gamma {gamma:.2f}')
    return check()


if __name__ == '__main__':
    sys.exit(main())
