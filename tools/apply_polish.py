#!/usr/bin/env python3
"""Reproduce individually reviewed chapter designs and exact approved dependencies."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

import ftb_snbt_lib as snbt
import apply_reference
import quality


def render(source, design, fixes):
    result = apply_reference.transform(source, design)
    fields = apply_reference.field_spans(result, apply_reference.whitespace(result, 0))
    pos = apply_reference.whitespace(result, fields['quests'][0] + 1)
    edits = []
    while result[pos] != ']':
        end = apply_reference.value_end(result, pos)
        quest = snbt.loads(result[pos:end])
        for key, fix in fixes.get(str(quest['id']), {}).items():
            if key != 'dependencies' or quest.get(key) != fix['before']:
                raise ValueError('Dependency fix differs from baseline')
            spans = apply_reference.field_spans(result, pos)
            if key in spans:
                edits.append((*spans[key], json.dumps(fix['after'])))
            else:
                line_start = result.rfind('\n', 0, end - 1) + 1
                closing_indent = result[line_start:end - 1]
                if not closing_indent.strip():
                    edits.append((line_start, end - 1, closing_indent + '    dependencies: ' +
                                  json.dumps(fix['after']) + '\n' + closing_indent))
                else:
                    edits.append((end - 1, end - 1, '\n            dependencies: ' +
                                  json.dumps(fix['after']) + '\n        '))
        pos = apply_reference.whitespace(result, end)
    for start, end, value in sorted(edits, reverse=True):
        result = result[:start] + value + result[end:]
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('chapters', nargs='*', help='Short names, e.g. prolog life; default all saved designs')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    scope = json.loads((root/'reviews/polish_scope.json').read_text())
    designs = root/'reviews/chapters'
    paths = [designs/('nasledie_'+name+'.json') for name in args.chapters] if args.chapters else sorted(designs.glob('*.json'))
    for path in paths:
        design = json.loads(path.read_text())
        if design['baseline_commit'] != scope['baseline_commit']:
            raise ValueError('Design baseline mismatch')
        name = quality.CHAPTER_ROOT + path.stem + '.snbt'
        source = quality.git(root, 'show', f'{scope["baseline_commit"]}:{name}').decode()
        output = render(source, design, scope['quest_fixes'])
        before, after = snbt.loads(source), snbt.loads(output)
        guarded = deepcopy(after)
        for q in guarded['quests']:
            for key, fix in scope['quest_fixes'].get(str(q['id']), {}).items():
                if fix['before'] is None:
                    q.pop(key, None)
                else:
                    q[key] = fix['before']
        if quality.canonical(quality.protected_body(before)) != quality.canonical(quality.protected_body(guarded)):
            raise ValueError('Protected data changed outside exact approved fixes')
        target = root/name
        if args.check:
            if target.read_text() != output:
                raise ValueError('Working file differs from reviewed design: '+name)
        else:
            current = target.read_text()
            committed = quality.git(root, 'show', 'HEAD:'+name).decode()
            if current not in (source, output, committed):
                raise ValueError('Unexpected uncommitted edits: '+name)
            target.write_text(output)
            old_quests = {str(q['id']):q for q in before['quests']}
            changes = []
            for q in after['quests']:
                old = old_quests[str(q['id'])]
                fields = {k:{'before':old.get(k),'after':q.get(k)} for k in sorted(set(old)|set(q)) if old.get(k)!=q.get(k)}
                changes.append({'id':str(q['id']), 'title':str(q['title']), 'fields':fields,
                                'review':design['quests'][str(q['id'])]['reason']})
            report = {'baseline_commit':scope['baseline_commit'],'file':name,'chapter_fields':{k:{'before':before.get(k),'after':after.get(k)} for k in quality.PRESENTATION if before.get(k)!=after.get(k)},'quests':changes,'gameplay_test':'not run'}
            out = root/'reviews/changes'/path.name
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(path.stem, 'matches design' if args.check else 'applied', len(after['quests']))


if __name__ == '__main__':
    main()
