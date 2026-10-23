#!/usr/bin/env python3
"""Static validation of the whole questbook (no baseline): structure, ids, layout, registries, rewards.

Errors fail CI. Warnings are review hints. Nothing here proves in-game behaviour.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

import quality
import questbook

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'references' / 'registry.json'
# Issues inherited from Alpha 42 that the Alpha 43 rework must remove; new ones always fail.
KNOWN = ROOT / 'references' / 'known_issues.json'
SHAPES = {'circle', 'square', 'rsquare', 'diamond', 'pentagon', 'hexagon', 'octagon', 'heart', 'gear',
          'crown', 'laurel', 'scroll', 'shield', 'coin', 'star', 'ribbon', 'none', 'default'}
TASK_FIELDS = {'item': 'item', 'kill': 'entity', 'structure': 'structure', 'biome': 'biome', 'advancement': 'advancement'}
LONG_TEXT = 900
VANILLA_HINT = 'minecraft'


def collect_files():
    files = {}
    for base in (questbook.OUT.parent, ROOT / 'kubejs'):
        for path in base.rglob('*'):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    return files


def problem(code, location, message, **details):
    return {'code': code, 'location': location, 'message': message, **details}


def known(kind, ident, registry, local_advancements):
    """True/False when the namespace is covered by the registry index, None when it cannot be judged."""
    ident = str(ident)
    if ident.startswith('#'):
        return None
    namespace = ident.split(':', 1)[0]
    if kind == 'advancement' and ident in local_advancements:
        return True
    entries = registry.get(kind, {})
    if namespace not in registry.get('namespaces', {}).get(kind, []):
        return None
    return ident in entries


TAG_DIRS = {'structures': 'worldgen/structure', 'items': 'items', 'entities': 'entity_types', 'biomes': 'worldgen/biome'}


def tag_issues(parsed, registry):
    """Local tags must list ids that exist."""
    errors = []
    for name, body in parsed.items():
        for kind, folder in TAG_DIRS.items():
            if name.startswith('kubejs/data/') and f'/tags/{folder}/' in name:
                for value in body.get('values', []):
                    value = value.get('id') if isinstance(value, dict) else value
                    if known(kind, value, registry, set()) is False:
                        errors.append(problem('unknown_' + kind, name, 'Tag member is not in the installed mods', id=value))
    return errors


def registry_issues(parsed, registry, local_advancements):
    errors, unknown = [], Counter()
    def check(kind, ident, location):
        if str(ident).startswith('#nasledie:'):
            ns, path = str(ident)[1:].split(':', 1)
            if f'kubejs/data/{ns}/tags/{TAG_DIRS[kind]}/{path}.json' not in parsed:
                errors.append(problem('unknown_tag', location, 'Local tag file is missing', id=str(ident)))
            return
        result = known(kind, ident, registry, local_advancements)
        if result is False:
            errors.append(problem('unknown_' + kind, location, f'{kind} id is not in the installed mods', id=str(ident)))
        elif result is None:
            unknown[kind] += 1
    for name, _, quest in quality.quest_rows(parsed):
        location = f"{name}#{quest.get('id')}"
        icon = quest.get('icon')
        if isinstance(icon, str) and icon:
            check('items', icon, location + '/icon')
        for task in quest.get('tasks', []):
            kind = str(task.get('type'))
            field = TASK_FIELDS.get(kind)
            if field and task.get(field) is not None:
                value = task[field]
                value = value.get('id') if hasattr(value, 'get') else value
                check({'item': 'items', 'kill': 'entities', 'structure': 'structures', 'biome': 'biomes',
                       'advancement': 'advancement'}[kind], value, location + '/task')
        for reward in quest.get('rewards', []):
            if str(reward.get('type')) == 'item':
                check('items', reward['item'].get('id'), location + '/reward')
    return errors, unknown


ADV_KEYS = {'type': 'entities', 'block': 'blocks', 'structure': 'structures', 'loot_table': 'loot_tables',
            'recipe_id': 'recipes', 'parent': 'advancement'}


def advancement_issues(parsed, registry, local_advancements):
    """Check ids referenced inside local KubeJS advancements."""
    errors = []
    def walk(value, location, key=None):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == 'items' and isinstance(v, list) and all(isinstance(i, str) for i in v):
                    for item in v:
                        check('items', item, location)
                elif k == 'effects' and isinstance(v, dict):
                    for effect in v:
                        check('effects', effect, location)
                    walk(v, location, k)
                elif k in ADV_KEYS and isinstance(v, str) and ':' in v:
                    check(ADV_KEYS[k], v, location)
                else:
                    walk(v, location, k)
        elif isinstance(value, list):
            for v in value:
                walk(v, location, key)
    def check(kind, ident, location):
        if known(kind, ident, registry, local_advancements) is False:
            errors.append(problem('unknown_' + kind, location, f'{kind} id inside advancement is not in the installed mods', id=ident))
    for name, body in parsed.items():
        if name.startswith('kubejs/data/') and '/advancements/' in name:
            walk(body, name)
    return errors


def unused_advancements(parsed, local_advancements, files):
    used = {str(t.get('advancement')) for _, _, q in quality.quest_rows(parsed) for t in q.get('tasks', [])}
    scripts = '\n'.join(v.decode('utf-8', 'replace') for k, v in files.items() if k.endswith('.js'))
    return [problem('unused_advancement', a, 'Local advancement is not used by any quest or script')
            for a in sorted(local_advancements) if a not in used and a not in scripts]


def reward_conflicts(parsed, registry):
    """A reward must not hand out an item that some item task or inventory advancement asks the player to obtain."""
    wanted = defaultdict(list)
    adv_items = registry.get('advancement_items', {})
    for name, _, quest in quality.quest_rows(parsed):
        for task in quest.get('tasks', []):
            if str(task.get('type')) == 'item':
                item = task.get('item')
                item = str(item.get('id') if hasattr(item, 'get') else item)
                wanted[item].append(str(quest.get('id')))
            if str(task.get('type')) == 'advancement':
                path = 'kubejs/data/{}/advancements/{}.json'.format(*str(task.get('advancement')).split(':', 1))
                items = adv_items.get(str(task.get('advancement')), [])
                if path in parsed:
                    items = [i for c in parsed[path].get('criteria', {}).values()
                             if c.get('trigger') == 'minecraft:inventory_changed'
                             for p in c.get('conditions', {}).get('items', [])
                             for i in p.get('items', [])]
                for item in items:
                    wanted[item].append(str(quest.get('id')))
    issues = []
    for name, _, quest in quality.quest_rows(parsed):
        for reward in quest.get('rewards', []):
            if str(reward.get('type')) != 'item':
                continue
            item = str(reward['item'].get('id'))
            targets = [q for q in wanted.get(item, []) if q != str(quest.get('id'))]
            if targets:
                issues.append(problem('reward_completes_task', f"{name}#{quest.get('id')}",
                                      'Reward item is also the goal of another quest', item=item, quests=sorted(set(targets))))
    return issues


def quest_issues(parsed):
    errors, warnings = [], []
    for name, _, quest in quality.quest_rows(parsed):
        location = f"{name}#{quest.get('id')}"
        if str(quest.get('shape', 'default')) not in SHAPES:
            errors.append(problem('shape_unknown', location, 'Unknown quest shape', shape=str(quest.get('shape'))))
        if not quest.get('tasks'):
            errors.append(problem('no_tasks', location, 'Quest has no tasks'))
        for reward in quest.get('rewards', []):
            item = reward.get('item') if str(reward.get('type')) == 'item' else None
            if item is not None and str(item.get('id')) == 'minecraft:written_book':
                title = str(item.get('tag', {}).get('title', ''))
                if not title or len(title) > 32 or 'author' not in item.get('tag', {}):
                    # WrittenBookItem.makeSureTagIsValid (1.20.1): title of 1..32 characters and an author.
                    errors.append(problem('book_invalid', location, 'Written book needs a title of 1-32 chars and an author',
                                          title=title))
        for task in quest.get('tasks', []):
            # KillTask/StatTask read `value` with getLong/getInt: a missing key means a goal of 0.
            if str(task.get('type')) in ('kill', 'stat') and int(task.get('value', 0)) < 1:
                errors.append(problem('count_missing', location, 'Kill/stat task needs value >= 1', task=str(task.get('id'))))
        text = '\n'.join(map(str, quest.get('description', [])))
        if not text.strip():
            warnings.append(problem('no_description', location, 'Quest has no description'))
        if len(text) > LONG_TEXT:
            warnings.append(problem('long_description', location, 'Description reads like a manual', chars=len(text)))
        manual = [t for t in quest.get('tasks', []) if str(t.get('type')) == 'checkmark']
        items = [r for r in quest.get('rewards', []) if str(r.get('type')) == 'item'
                 and str(r['item'].get('id')) != 'minecraft:written_book']
        if manual and items:
            errors.append(problem('manual_task_item_reward', location, 'Checkmark quest must not give item rewards'))
        ids = Counter(str(r['item'].get('id')) for r in quest.get('rewards', []) if str(r.get('type')) == 'item')
        for item, count in ids.items():
            if count > 1:
                errors.append(problem('duplicate_reward_item', location, 'Same item appears in several rewards of one quest', item=item))
    return errors, warnings


def with_links(parsed):
    """Treat quest links as nodes for layout checks."""
    # FTB draws dependency lines to and from a link exactly as for the linked quest, so a link node
    # carries the linked quest's id and dependencies.
    # Quests with hide_dependency_lines draw no lines, so their dependencies are left out of the layout check.
    view = dict(parsed)
    every = {str(q.get('id')): q for _, _, q in quality.quest_rows(parsed)}
    for name, chapter in quality.chapters(parsed).items():
        links = chapter.get('quest_links', [])
        hidden = any(q.get('hide_dependency_lines') for q in chapter.get('quests', []))
        if links or hidden:
            copy = dict(chapter)
            copy['quests'] = [dict(q, dependencies=[]) if q.get('hide_dependency_lines') else q
                              for q in chapter.get('quests', [])] + [
                {'id': str(link.get('linked_quest')), 'x': link.get('x'), 'y': link.get('y'), 'size': link.get('size', 1),
                 'dependencies': every.get(str(link.get('linked_quest')), {}).get('dependencies', [])} for link in links]
            view[name] = copy
    return view


def issue_key(issue):
    return (issue['code'], issue['location'], str(issue.get('id', issue.get('item', ''))))


def evaluate(files, registry):
    parsed, errors = quality.parse_files(files)
    warnings = []
    errors += quality.integrity(parsed)
    errors += quality.resource_checks(files, parsed)
    geometry, metrics = quality.geometry(with_links(parsed))
    errors += [g for g in geometry if g['code'] != 'edge_long']
    warnings += [g for g in geometry if g['code'] == 'edge_long']
    warnings += quality.duplicate_conditions(parsed)
    warnings += quality.prose_issues(parsed)
    warnings += quality.icon_variety_issues(parsed)
    q_errors, q_warnings = quest_issues(parsed)
    errors += q_errors
    warnings += q_warnings
    local = {f"{p.split('/')[2]}:{p.split('/advancements/', 1)[1][:-5]}" for p in parsed
             if p.startswith('kubejs/data/') and '/advancements/' in p}
    unknown = Counter()
    warnings += unused_advancements(parsed, local, files)
    if registry:
        r_errors, unknown = registry_issues(parsed, registry, local)
        errors += r_errors
        errors += advancement_issues(parsed, registry, local)
        errors += tag_issues(parsed, registry)
        errors += reward_conflicts(parsed, registry)
    return {'counts': quality.inventory(parsed), 'errors': errors, 'warnings': warnings,
            'unknown_registry_namespaces': dict(unknown), 'geometry': metrics,
            'scope': 'Static checks only; Minecraft was not run.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--strict', action='store_true', help='fail on warnings too')
    parser.add_argument('--write-known', action='store_true', help='record current errors as inherited (rarely needed)')
    args = parser.parse_args(argv)
    registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else None
    if questbook.main(['check']):
        return 1
    report = evaluate(collect_files(), registry)
    keys = sorted({issue_key(e) for e in report['errors']})
    if args.write_known:
        KNOWN.write_text(json.dumps(keys, ensure_ascii=False, indent=1) + '\n')
    known_keys = {tuple(k) for k in json.loads(KNOWN.read_text())} if KNOWN.exists() else set()
    report['inherited'] = [e for e in report['errors'] if issue_key(e) in known_keys]
    report['errors'] = [e for e in report['errors'] if issue_key(e) not in known_keys]
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    for item in report['errors']:
        print('ERROR', item['code'], item['location'], {k: v for k, v in item.items() if k not in ('code', 'location', 'message')})
    codes = Counter(w['code'] for w in report['warnings'])
    print(json.dumps({'counts': {k: report['counts'][k] for k in ('chapters', 'quests', 'tasks', 'rewards')},
                      'errors': len(report['errors']), 'inherited': len(report['inherited']), 'warnings': dict(codes),
                      'unknown': report['unknown_registry_namespaces']}, ensure_ascii=False))
    return 1 if report['errors'] or (args.strict and report['warnings']) else 0


if __name__ == '__main__':
    sys.exit(main())
