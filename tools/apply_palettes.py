#!/usr/bin/env python3
"""Render and validate chapter ID selectors for FTB Quests 2001.4.22."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import ftb_snbt_lib as snbt

THEME = 'kubejs/assets/ftbquests/ftb_quests_theme.txt'
STATES = ('quest_locked_color', 'quest_not_started_color',
          'quest_started_color', 'quest_completed_color')
COLORS = (*STATES, 'dependency_line_completed_color',
          'dependency_line_uncompleted_color', 'dependency_line_requires_color',
          'dependency_line_required_for_color', 'quest_view_border', 'quest_view_title',
          'tasks_text_color', 'rewards_text_color',
          'selected_chapter_highlight_1', 'selected_chapter_highlight_2')


def sections(text):
    """Strict subset of ThemeLoader syntax used here; reject silently ignored lines."""
    result, current = {}, None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('//'):
            continue
        if re.fullmatch(r'\[(?:\*|[0-9A-F]{16})\]', line):
            selector = line[1:-1]
            if selector in result:
                raise ValueError(f'Duplicate selector at line {number}')
            current = result[selector] = {}
        elif current is None or ':' not in line:
            raise ValueError(f'Ignored or invalid theme line {number}: {line}')
        else:
            key, value = (part.strip() for part in line.split(':', 1))
            if not key or not value or key in current:
                raise ValueError(f'Empty or duplicate property at line {number}')
            current[key] = value
    return result


def validate(text, chapters):
    parsed = sections(text)
    ids = {chapter['id'] for chapter in chapters.values()}
    if len(ids) != len(chapters) or set(parsed) != ids | {'*'}:
        raise ValueError('Theme selectors must cover each chapter exactly once')
    accents = []
    for ident in ids:
        properties = parsed[ident]
        if set(properties) != set(COLORS):
            raise ValueError(f'Unexpected or missing chapter color properties: {ident}')
        if any(not re.fullmatch(r'#[0-9A-F]{6}(?:[0-9A-F]{2})?', v)
               for v in properties.values()):
            raise ValueError(f'Invalid color: {ident}')
        if len({properties[k] for k in STATES}) != 4:
            raise ValueError(f'Quest states have identical colors: {ident}')
        accents.append(properties['quest_not_started_color'])
    if len(set(accents)) != len(accents):
        raise ValueError('Chapter accent colors must differ')
    return parsed


def render(design, chapters):
    if set(design['chapters']) != set(chapters):
        raise ValueError('Palette chapter filenames do not match current chapters')
    lines = ['// Generated from reviews/chapter_palettes.json',
             '// FTB Quests 2001.4.22: [*] is required before global properties.', '[*]']
    lines += [f'{key}: {value}' for key, value in design['global'].items()]
    for name, entry in design['chapters'].items():
        if entry['id'] != chapters[name]['id']:
            raise ValueError(f'Palette targets a different chapter ID: {name}')
        lines += ['', '// ' + name + ' — ' + entry['name'], '[' + entry['id'] + ']']
        lines += [f'{key}: {value}' for key, value in entry['properties'].items()]
    text = '\n'.join(lines) + '\n'
    validate(text, chapters)
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    design = json.loads((root/'reviews/chapter_palettes.json').read_text())
    chapters = {p.stem: snbt.loads(p.read_text())
                for p in (root/'config/ftbquests/quests/chapters').glob('*.snbt')}
    target = root/THEME
    output = render(design, chapters)
    current = target.read_text()
    if args.check:
        validate(current, chapters)
        if current != output:
            raise ValueError('Theme differs from reviewed palettes')
    else:
        if current != output and hashlib.sha256(target.read_bytes()).hexdigest() != design['previous_sha256']:
            raise ValueError('Unexpected existing theme edits; refusing to overwrite')
        target.write_text(output)
    print(f'{len(chapters)} chapter palettes: ' + ('match theme' if args.check else 'applied'))


if __name__ == '__main__':
    main()
