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

Custom conditions live next to the quest: a task `{type: criteria, title: ..., kill: entity}` (or placed,
bred, tamed, trade, loot, ride, effect, used_item, used_on_block, crafted, obtain, granted, criteria)
generates kubejs/data/nasledie/advancements/q/<chapter>/<key>.json and an advancement task for it.
`any_of: [...]` combines several shorthands with OR. `granted: true` is for script-granted goals.

Chapter `links: [{quest: ref, x, y, shape, size}]` shows a quest of another chapter in this one.
src/chapter_groups.yaml lists chapter groups.
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
GROUPS = ROOT / 'src' / 'chapter_groups.yaml'
OUT = ROOT / 'config' / 'ftbquests' / 'quests' / 'chapters'
GROUP_FILE = OUT.parent / 'chapter_groups.snbt'
ADV_DIR = ROOT / 'kubejs' / 'data' / 'nasledie' / 'advancements' / 'q'
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


def location(structure):
    return {'structure': structure}


def criterion(spec):
    """One shorthand condition -> advancement criterion."""
    kinds = [k for k in SHORTHANDS if k in spec]
    if len(kinds) != 1:
        raise ValueError(f'Criteria task needs exactly one condition, got {sorted(spec)}')
    kind, value = kinds[0], spec[kinds[0]]
    if kind == 'kill':
        entity = {'type': value}
        if spec.get('in_structure'):
            entity['location'] = location(spec['in_structure'])
        conditions = {'entity': entity}
        if spec.get('player_effect'):
            conditions['player'] = [{'condition': 'minecraft:entity_properties', 'entity': 'this',
                                     'predicate': {'effects': {spec['player_effect']: {}}}}]
        return {'trigger': 'minecraft:player_killed_entity', 'conditions': conditions}
    if kind == 'placed':
        return {'trigger': 'minecraft:placed_block', 'conditions': {'location': [
            {'condition': 'minecraft:block_state_property', 'block': value}]}}
    if kind == 'bred':
        return {'trigger': 'minecraft:bred_animals', 'conditions': {'child': {'type': value}}}
    if kind == 'tamed':
        return {'trigger': 'minecraft:tame_animal', 'conditions': {'entity': {'type': value}}}
    if kind == 'trade':
        return {'trigger': 'minecraft:villager_trade', 'conditions': {'item': {'items': [value]}}}
    if kind == 'loot':
        return {'trigger': 'minecraft:player_generates_container_loot', 'conditions': {'loot_table': value}}
    if kind == 'ride':
        return {'trigger': 'minecraft:started_riding', 'conditions': {'player': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'vehicle': {'type': value}}}]}}
    if kind == 'effect':
        return {'trigger': 'minecraft:effects_changed', 'conditions': {'effects': {value: {}}}}
    if kind == 'used_item':
        return {'trigger': 'minecraft:using_item', 'conditions': {'item': {'items': [value]}}}
    if kind == 'used_on_block':
        return {'trigger': 'minecraft:item_used_on_block', 'conditions': {'location': [
            {'condition': 'minecraft:match_tool', 'predicate': {'items': [value]}}]}}
    if kind == 'crafted':
        return {'trigger': 'minecraft:recipe_crafted', 'conditions': {'recipe_id': value}}
    if kind == 'obtain':
        items = value if isinstance(value, list) else [value]
        return {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': items}]}}
    if kind == 'consumed':
        return {'trigger': 'minecraft:consume_item', 'conditions': {'item': {'items': [value]}}}
    if kind == 'in_structure_tick':
        return {'trigger': 'minecraft:location', 'conditions': {'player': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'location': location(value)}}]}}
    if kind == 'granted':
        return {'trigger': 'minecraft:impossible'}
    raise AssertionError(kind)


SHORTHANDS = ('kill', 'placed', 'bred', 'tamed', 'trade', 'loot', 'ride', 'effect', 'used_item', 'used_on_block',
              'crafted', 'obtain', 'consumed', 'in_structure_tick', 'granted')


def advancement_body(task):
    if 'criteria' in task:
        criteria = task['criteria']
        requirements = task.get('requirements') or [[name] for name in criteria]
    elif 'any_of' in task:
        criteria = {f'c{i}': criterion(spec) for i, spec in enumerate(task['any_of'])}
        requirements = [list(criteria)]
    elif 'all_of' in task:
        criteria = {f'c{i}': criterion(spec) for i, spec in enumerate(task['all_of'])}
        requirements = [[name] for name in criteria]
    else:
        criteria = {'done': criterion(task)}
        requirements = [['done']]
    return {'criteria': criteria, 'requirements': requirements}


def build_task(task, seed, generated=None, path=None):
    if task.get('type') == 'criteria':
        if not task.get('title'):
            raise ValueError(f'{path}: criteria task needs a title')
        rel = f'q/{path}'
        generated[ADV_DIR.parent / (rel + '.json')] = json.dumps(advancement_body(task), ensure_ascii=False, indent=2) + '\n'
        task = {k: v for k, v in task.items() if k in ('id', 'title')}
        task.update({'type': 'advancement', 'advancement': f'nasledie:{rel}'})

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


BOOK_TITLE_MAX = 32


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
        if len(nbt['title']) > BOOK_TITLE_MAX:
            # WrittenBookItem.makeSureTagIsValid: a longer title makes the client show "Invalid book tag".
            raise ValueError(f'Book title longer than {BOOK_TITLE_MAX} characters: {nbt["title"]}')
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


def sentence(line):
    """An unquoted YAML line containing ": " parses as a one-key mapping; restore the sentence."""
    if isinstance(line, dict) and len(line) == 1:
        key, value = next(iter(line.items()))
        return f'{key}: {value}'
    return line


def build_chapter(name, data, names, generated):
    chapter = {k: tag(v, k) for k, v in data['chapter'].items()}
    links = []
    for i, link in enumerate(data.get('links', [])):
        body = {'id': snbt.String(link.get('id') or make_id(f'{name}/link/{link["quest"]}')),
                'linked_quest': snbt.String(dependency(link['quest'], name, names)),
                'x': snbt.Double(float(link['x'])), 'y': snbt.Double(float(link['y']))}
        for key in ('shape', 'size'):
            if key in link:
                body[key] = tag(link[key], key)
        links.append(snbt.Compound(body))
    chapter['quest_links'] = snbt.List(links)
    quests = []
    for quest in data['quests']:
        ident = quest['_id']
        text = quest.get('description', [])
        if isinstance(text, list):
            text = quest['description'] = [sentence(line) for line in text]
        if not isinstance(quest.get('title', ''), str) or not isinstance(text, list) or not all(isinstance(s, str) for s in text):
            raise ValueError(f'{name}/{quest.get("key") or ident}: title and description lines must be plain strings '
                             '(quote YAML lines that contain ": ")')
        body = {'id': snbt.String(ident)}
        for key, value in quest.items():
            if key in ('key', 'id', '_id', 'deps', 'tasks', 'rewards', 'note'):
                continue
            body[key] = tag(value, key)
        body.setdefault('description', snbt.List([]))
        if quest.get('deps'):
            body['dependencies'] = snbt.List([snbt.String(dependency(d, name, names)) for d in quest['deps']])
        stem = (quest.get('key') or ident.lower()).replace('-', '_')
        tasks = quest.get('tasks', [])
        body['tasks'] = snbt.List([
            build_task(t, f'{ident}/task/{i}', generated,
                       f'{name.removeprefix("nasledie_")}/{stem}' + (f'_{i + 1}' if len(tasks) > 1 else ''))
            for i, t in enumerate(tasks)])
        body['rewards'] = snbt.List([build_reward(r, f'{ident}/reward/{i}') for i, r in enumerate(quest.get('rewards', []))])
        quests.append(snbt.Compound(ordered(body, QUEST_ORDER)))
    chapter['quests'] = snbt.List(quests)
    return snbt.Compound(ordered(chapter, CHAPTER_ORDER + ('quest_links', 'quests')))


def build_all(src=SRC, groups=GROUPS):
    """Return {path: text} for every generated file."""
    chapters = load_sources(src)
    names = resolve_ids(chapters)
    generated = {}
    entries = yaml.safe_load(groups.read_text(encoding='utf-8')) if groups.exists() else []
    group_ids = {}
    for entry in entries:
        entry['id'] = entry.get('id') or make_id('group/' + entry['key'])
        group_ids[entry.pop('key')] = entry['id']
    for data in chapters.values():
        group = data['chapter'].get('group')
        if group and not HEX.match(str(group)):
            if group not in group_ids:
                raise ValueError(f'Unknown chapter group {group}')
            data['chapter']['group'] = group_ids[group]
    for name, data in chapters.items():
        generated[OUT / (name + '.snbt')] = snbt.dumps(build_chapter(name, data, names, generated)) + '\n'
    if groups.exists():
        generated[GROUP_FILE] = snbt.dumps(snbt.Compound({'chapter_groups': tag(entries)})) + '\n'
    return generated


def managed(path):
    return path.parent == OUT or path == GROUP_FILE or ADV_DIR in path.parents


def existing_files():
    files = set(OUT.glob('*.snbt')) | (set(ADV_DIR.rglob('*.json')) if ADV_DIR.exists() else set())
    return files | ({GROUP_FILE} if GROUP_FILE.exists() and GROUPS.exists() else set())


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
    existing = existing_files()
    if args.command == 'check':
        bad = [p for p, text in built.items() if not p.exists() or p.read_text(encoding='utf-8') != text]
        bad += sorted(existing - set(built))
        if bad:
            print('Out of date or unexpected generated files (run tools/questbook.py build):',
                  ', '.join(str(p.relative_to(ROOT)) for p in bad))
            return 1
        print('Generated files match sources:', len(built))
        return 0
    for stale in existing - set(built):
        stale.unlink()
        print('removed', stale.relative_to(ROOT))
    for path, text in built.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8')
    print('built', sum(p.parent == OUT for p in built), 'chapters,', len(built), 'files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
