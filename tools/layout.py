#!/usr/bin/env python3
"""Rewrite quest coordinates in a chapter source from polar positions (radius, angle in degrees).

  python tools/layout.py CHAPTER SPEC.yaml

SPEC: {quests: {key: [r, deg]}, links: {quest_ref: [r, deg]}}. Angle 0 points right, 90 points down
(FTB y grows downwards). Only x/y lines are touched; the rest of the YAML stays as written.
"""
import math
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def cartesian(r, deg):
    a = math.radians(deg)
    return round(r * math.cos(a), 2), round(r * math.sin(a), 2)


def apply(text, spec):
    for key, (r, deg) in spec.get('quests', {}).items():
        x, y = cartesian(r, deg)
        start = text.index(f'  - key: {key}\n')
        end = text.find('\n  - ', start + 1)
        end = len(text) if end == -1 else end
        block = text[start:end]
        block = re.sub(r'(?m)^    x: .*$', f'    x: {x}', block, count=1)
        block = re.sub(r'(?m)^    y: .*$', f'    y: {y}', block, count=1)
        text = text[:start] + block + text[end:]
    for ref, (r, deg) in spec.get('links', {}).items():
        x, y = cartesian(r, deg)
        text, count = re.subn(r'\{quest: ' + re.escape(ref) + r', x: [-\d.]+, y: [-\d.]+',
                              f'{{quest: {ref}, x: {x}, y: {y}', text)
        if count != 1:
            raise ValueError(f'link {ref} not found exactly once')
    return text


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    chapter, spec_path = sys.argv[1], Path(sys.argv[2])
    path = ROOT / 'src' / 'chapters' / f'nasledie_{chapter}.yaml'
    spec = yaml.safe_load(spec_path.read_text(encoding='utf-8'))
    path.write_text(apply(path.read_text(encoding='utf-8'), spec), encoding='utf-8')
    print('laid out', chapter)


if __name__ == '__main__':
    main()
