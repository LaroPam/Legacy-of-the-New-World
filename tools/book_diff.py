#!/usr/bin/env python3
"""Compare quest IDs of two questbook trees and print a Markdown change log appendix.

  python tools/book_diff.py BASE_DIR [CURRENT_DIR]

Each directory holds config/ftbquests/quests/chapters/*.snbt (BASE_DIR is e.g. `git archive <commit>` unpacked).
Lists removed quests, quests that kept their ID but changed their checks, and quests moved between chapters.
"""
from collections import Counter
from pathlib import Path
import sys

import ftb_snbt_lib as snbt

CHAPTERS = Path('config/ftbquests/quests/chapters')


def target(task):
    item = task.get('item')
    if item is not None and not isinstance(item, str):
        item = item.get('id')
    for key in ('advancement', 'entity', 'structure', 'stat', 'biome', 'dimension'):
        if task.get(key) is not None:
            return str(task.get(key))
    return str(item or '')


def load(root):
    quests = {}
    for path in sorted(Path(root, CHAPTERS).glob('*.snbt')):
        data = snbt.loads(path.read_text(encoding='utf-8'))
        for quest in data.get('quests', []):
            tasks = [f"{task.get('type')} {target(task)}".strip() for task in quest.get('tasks', [])]
            quests[str(quest['id'])] = {'chapter': path.stem.removeprefix('nasledie_'),
                                        'title': str(quest.get('title', '')), 'tasks': tasks}
    return quests


def cell(text):
    return str(text).replace('|', '\\|')


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    base, current = load(argv[0]), load(argv[1] if len(argv) > 1 else '.')
    removed = [k for k in base if k not in current]
    added = [k for k in current if k not in base]
    kept = [k for k in current if k in base]
    changed = [k for k in kept if base[k]['tasks'] != current[k]['tasks']]
    moved = [k for k in kept if base[k]['chapter'] != current[k]['chapter']]
    print(f'База: {len(base)} квестов, сейчас: {len(current)}. Сохранено ID: {len(kept)}, удалено: {len(removed)}, '
          f'новых: {len(added)}, перенесено между главами: {len(moved)}, сохранили ID при новой проверке: {len(changed)}.')
    print('\nНовые квесты по главам: ' + ', '.join(f'{c} {n}' for c, n in Counter(current[k]['chapter'] for k in added).most_common()))
    print('\n### Удалённые квесты\n\n| ID | Глава | Название | Проверка |\n|---|---|---|---|')
    for k in sorted(removed, key=lambda k: (base[k]['chapter'], base[k]['title'])):
        print(f"| `{k}` | {base[k]['chapter']} | {cell(base[k]['title'])} | {cell('; '.join(base[k]['tasks']))} |")
    print('\n### ID сохранён, проверка уточнена\n\n| ID | Глава | Название | Было | Стало |\n|---|---|---|---|---|')
    for k in sorted(changed, key=lambda k: (current[k]['chapter'], current[k]['title'])):
        print(f"| `{k}` | {current[k]['chapter']} | {cell(current[k]['title'])} | {cell('; '.join(base[k]['tasks']))} | "
              f"{cell('; '.join(current[k]['tasks']))} |")
    print('\n### Перенесены в другую главу\n\n| ID | Было | Стало | Название |\n|---|---|---|---|')
    for k in sorted(moved, key=lambda k: (base[k]['chapter'], current[k]['chapter'])):
        print(f"| `{k}` | {base[k]['chapter']} | {current[k]['chapter']} | {cell(current[k]['title'])} |")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
