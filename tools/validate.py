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


def registry_issues(parsed, registry, local_advancements):
    errors, unknown = [], Counter()
    def check(kind, ident, location):
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


def issue_key(issue):
    return (issue['code'], issue['location'], str(issue.get('id', issue.get('item', ''))))


def evaluate(files, registry):
    parsed, errors = quality.parse_files(files)
    warnings = []
    errors += quality.integrity(parsed)
    errors += quality.resource_checks(files, parsed)
    geometry, metrics = quality.geometry(parsed)
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
    if registry:
        r_errors, unknown = registry_issues(parsed, registry, local)
        errors += r_errors
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
