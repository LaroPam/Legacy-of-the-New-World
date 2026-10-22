#!/usr/bin/env python3
"""Build FTB Quests SNBT from the readable chapter sources in src/chapters/*.yaml.

  python tools/questbook.py build    write config/ftbquests/quests/chapters/*.snbt
  python tools/questbook.py check    fail if the SNBT differs from a fresh build
  python tools/questbook.py import   one-time conversion of existing SNBT into sources

Source format (one YAML file per chapter):

  chapter: {id, filename, group, title, icon, order_index, ...}   # chapter fields
  quests:
    - key: first_camp            # readable name; dependencies may use it
      id: 0123456789ABCDEF       # optional; generated from filename/key when absent
      title: ...
      description: [...]
      x: 0; y: 0; icon; shape; size; optional
      deps: [other_key, chapter_filename/key, 0123456789ABCDEF]
      tasks:   [{type: advancement, advancement: ...}, ...]
      rewards: [{type: xp, xp: 100}, {type: item, item: id, count: 2},
                {type: book, title: ..., pages: [...]}]

Task/reward ids are generated from the quest id and position unless given explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import ftb_snbt_lib as snbt
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'chapters'
OUT = ROOT / 'config' / 'ftbquests' / 'quests' / 'chapters'
HEX = re.compile(r'^[0-9A-F]{16}$')
BOOK_AUTHOR = 'Первая экспедиция'

CHAPTER_ORDER = ('filename', 'id', 'group', 'title', 'icon', 'order_index', 'default_hide_dependency_lines',
                 'default_quest_shape', 'default_quest_size', 'progression_mode', 'subtitle', 'images')
QUEST_ORDER = ('id', 'title', 'subtitle', 'description', 'x', 'y', 'icon', 'shape', 'size', 'optional',
               'dependencies', 'dependency_requirement', 'hide_dependency_lines', 'tasks', 'rewards')
DOUBLE_KEYS = {'x', 'y', 'size', 'default_quest_size'}


def make_id(seed):
    value = hashlib.sha256(('nasledie:' + seed).encode()).hexdigest()[:16].upper()
    return value if value.strip('0') else '1' + value[1:]


def tag(value, key=None):
    """Convert plain YAML data into typed SNBT tags."""
    if isinstance(value, snbt.Base):
        return value
    if isinstance(value, bool):
        return snbt.Bool(value)
    if key in DOUBLE_KEYS:
        return snbt.Double(float(value))
    if isinstance(value, int):
        return snbt.Integer(value)
    if isinstance(value, float):
        return snbt.Double(value)
    if isinstance(value, str):
        return snbt.String(value)
    if isinstance(value, list):
        return snbt.List([tag(v) for v in value])
    if isinstance(value, dict):
        return snbt.Compound({k: tag(v, k) for k, v in value.items()})
    raise TypeError(f'Unsupported value {value!r}')


def plain(value):
    """Convert SNBT tags into plain YAML data (import only)."""
    if isinstance(value, snbt.Bool):
        return bool(value)
    if isinstance(value, (snbt.Byte, snbt.Short, snbt.Integer, snbt.Long)):
        return int(value)
    if isinstance(value, (snbt.Float, snbt.Double)):
        return float(value)
    if isinstance(value, snbt.String):
        return str(value)
    if isinstance(value, snbt.List):
        return [plain(v) for v in value]
    if isinstance(value, snbt.Compound):
        return {str(k): plain(v) for k, v in value.items()}
    raise TypeError(f'Unsupported tag {value!r}')


def ordered(data, order):
    keys = [k for k in order if k in data] + [k for k in data if k not in order]
    return {k: data[k] for k in keys}


def build_task(task, seed):
    task = dict(task)
    ident = task.pop('id', None) or make_id(seed)
    kind = task.pop('type')
    body = {'id': snbt.String(ident), 'type': snbt.String(kind)}
    for key, value in task.items():
        if kind == 'item' and key == 'count':
            body[key] = snbt.Long(value)
        else:
            body[key] = tag(value, key)
    if kind == 'item':
        body.setdefault('count', snbt.Long(1))
        body.setdefault('consume_items', snbt.Bool(False))
    return snbt.Compound(body)


def item_stack(item, count=1, nbt=None):
    stack = {'Count': snbt.Byte(count), 'id': snbt.String(item)}
    if nbt is not None:
        stack['tag'] = snbt.loads(nbt) if isinstance(nbt, str) else tag(nbt)
    return snbt.Compound(stack)


def build_reward(reward, seed):
    reward = dict(reward)
    ident = reward.pop('id', None) or make_id(seed)
    kind = reward.pop('type')
    body = {'id': snbt.String(ident)}
    if kind == 'book':
        pages = [json.dumps({'text': page}, ensure_ascii=False) for page in reward.pop('pages')]
        nbt = {'title': reward.pop('title'), 'author': reward.pop('author', BOOK_AUTHOR), 'pages': pages}
        if 'lore' in reward:
            nbt['display'] = {'Lore': [json.dumps({'text': line, 'italic': True}, ensure_ascii=False)
                                       for line in reward.pop('lore')]}
        body['type'] = snbt.String('item')
        body['item'] = item_stack('minecraft:written_book', 1, nbt)
    elif kind == 'item':
        body['type'] = snbt.String('item')
        body['item'] = item_stack(reward.pop('item'), reward.pop('count', 1), reward.pop('nbt', None))
    else:
        body['type'] = snbt.String(kind)
    for key, value in reward.items():
        body[key] = tag(value, key)
    return snbt.Compound(body)


def load_sources(src=SRC):
    chapters = {}
    for path in sorted(src.glob('*.yaml')):
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        name = data['chapter']['filename']
        if name != path.stem:
            raise ValueError(f'{path.name}: filename must match the file stem')
        chapters[name] = data
    return chapters


def resolve_ids(chapters):
    """Map every way of naming a quest (id, key, chapter/key) to its id."""
    names, seen = {}, {}
    for name, data in chapters.items():
        for quest in data['quests']:
            key = quest.get('key')
            ident = quest.get('id') or make_id(f'{name}/{key}')
            if not key and not quest.get('id'):
                raise ValueError(f'{name}: quest without key or id: {quest.get("title")}')
            if not HEX.match(ident):
                raise ValueError(f'{name}: bad id {ident}')
            if ident in seen:
                raise ValueError(f'Duplicate quest id {ident} in {name} and {seen[ident]}')
            seen[ident] = name
            quest['_id'] = ident
            names[(name, ident)] = ident
            if key:
                if (name, key) in names:
                    raise ValueError(f'{name}: duplicate key {key}')
                names[(name, key)] = ident
    return names


def dependency(ref, chapter, names):
    ref = str(ref)
    if HEX.match(ref):
        return ref
    if '/' in ref:
        other, key = ref.split('/', 1)
        target = names.get((other, key))
    else:
        target = names.get((chapter, ref))
    if not target:
        raise ValueError(f'{chapter}: unknown dependency {ref}')
    return target


def build_chapter(name, data, names):
    chapter = {k: tag(v, k) for k, v in data['chapter'].items()}
    chapter.setdefault('quest_links', snbt.List([]))
    quests = []
    for quest in data['quests']:
        ident = quest['_id']
        body = {'id': snbt.String(ident)}
        for key, value in quest.items():
            if key in ('key', 'id', '_id', 'deps', 'tasks', 'rewards', 'note'):
                continue
            body[key] = tag(value, key)
        body.setdefault('description', snbt.List([]))
        if quest.get('deps'):
            body['dependencies'] = snbt.List([snbt.String(dependency(d, name, names)) for d in quest['deps']])
        body['tasks'] = snbt.List([build_task(t, f'{ident}/task/{i}') for i, t in enumerate(quest.get('tasks', []))])
        body['rewards'] = snbt.List([build_reward(r, f'{ident}/reward/{i}') for i, r in enumerate(quest.get('rewards', []))])
        quests.append(snbt.Compound(ordered(body, QUEST_ORDER)))
    chapter['quests'] = snbt.List(quests)
    return snbt.Compound(ordered(chapter, CHAPTER_ORDER + ('quest_links', 'quests')))


def build_all(src=SRC):
    chapters = load_sources(src)
    names = resolve_ids(chapters)
    return {name: snbt.dumps(build_chapter(name, data, names)) + '\n' for name, data in chapters.items()}


def import_sources():
    SRC.mkdir(parents=True, exist_ok=True)
    for path in sorted(OUT.glob('*.snbt')):
        data = plain(snbt.load(path.open(encoding='utf-8')))
        quests = []
        for quest in data.pop('quests'):
            q = {'id': quest.pop('id')}
            deps = quest.pop('dependencies', None)
            tasks, rewards = quest.pop('tasks', []), quest.pop('rewards', [])
            q.update(quest)
            if deps:
                q['deps'] = deps
            q['tasks'] = tasks
            q['rewards'] = []
            for reward in rewards:
                if reward.get('type') == 'item':
                    stack = reward.pop('item')
                    reward['item'] = stack['id']
                    if stack.get('Count', 1) != 1:
                        reward['count'] = stack['Count']
                    if 'tag' in stack:
                        reward['nbt'] = stack['tag']
                q['rewards'].append(reward)
            quests.append(q)
        if not data.get('quest_links'):
            data.pop('quest_links', None)
        text = yaml.safe_dump({'chapter': data, 'quests': quests}, allow_unicode=True, sort_keys=False, width=110)
        (SRC / (path.stem + '.yaml')).write_text(text, encoding='utf-8')
        print('imported', path.stem, len(quests))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('build', 'check', 'import'))
    args = parser.parse_args(argv)
    if args.command == 'import':
        import_sources()
        return 0
    built = build_all()
    existing = {p.stem for p in OUT.glob('*.snbt')}
    if args.command == 'check':
        bad = sorted(n for n, text in built.items() if (OUT / (n + '.snbt')).read_text(encoding='utf-8') != text
                     if (OUT / (n + '.snbt')).exists()) + sorted((existing ^ set(built)))
        if bad:
            print('Out of date or unexpected SNBT (run tools/questbook.py build):', ', '.join(bad))
            return 1
        print('SNBT matches sources:', len(built), 'chapters')
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in existing - set(built):
        (OUT / (stale + '.snbt')).unlink()
        print('removed', stale)
    for name, text in built.items():
        (OUT / (name + '.snbt')).write_text(text, encoding='utf-8')
    print('built', len(built), 'chapters')
    return 0


if __name__ == '__main__':
    sys.exit(main())
