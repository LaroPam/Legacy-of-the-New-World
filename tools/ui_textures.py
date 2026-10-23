#!/usr/bin/env python3
"""Generate interface textures for the quest book theme.

  python tools/ui_textures.py            # write kubejs/assets/nasledie/textures/gui/*.png
  python tools/ui_textures.py --check    # the files match a fresh render

dependency_soft.png replaces FTB's dependency.png (arrow chevrons). FTB Quests 2001.4.22 draws a dependency as a
quad: u runs along the line (one texture width per two line thicknesses, scrolled by the line speed), v across it,
and multiplies the texture, alpha included, by the line colour. A texture without a pattern along u and with a soft
falloff across v gives a smooth line with rounded edges.
"""
import argparse
import io
import json
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'kubejs/assets/nasledie/textures/gui'
MCMETA = {'texture': {'blur': True}}
SIZE = 64


def smoothstep(edge0, edge1, x):
    t = min(1.0, max(0.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def dependency_soft():
    """Opaque core, soft edges and a slightly brighter middle, the same along the whole line."""
    image = Image.new('RGBA', (SIZE, SIZE))
    for y in range(SIZE):
        d = abs((y + 0.5) / SIZE - 0.5) * 2  # 0 in the middle of the line, 1 at its edges
        alpha = 1 - smoothstep(0.35, 1.0, d)
        shade = 1 - 0.18 * smoothstep(0.0, 0.9, d)
        pixel = (round(255 * shade),) * 3 + (round(255 * alpha),)
        for x in range(SIZE):
            image.putpixel((x, y), pixel)
    return image


TEXTURES = {'dependency_soft.png': dependency_soft}


def encoded(image):
    data = io.BytesIO()
    image.save(data, 'PNG', optimize=True)
    return data.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    problems = []
    for name, render in TEXTURES.items():
        path, meta = TARGET / name, TARGET / (name + '.mcmeta')
        data, meta_text = encoded(render()), json.dumps(MCMETA, indent=2) + '\n'
        if args.check:
            if not path.exists() or Image.open(path).tobytes() != Image.open(io.BytesIO(data)).tobytes():
                problems.append(f'{name}: differs from a fresh render')
            if not meta.exists() or meta.read_text() != meta_text:
                problems.append(f'{name}.mcmeta: missing or different')
        else:
            TARGET.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            meta.write_text(meta_text)
    for line in problems:
        print('ERROR', line)
    print(f'{len(TEXTURES)} interface textures: ' + ('ok' if not problems else f'{len(problems)} problems'))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
