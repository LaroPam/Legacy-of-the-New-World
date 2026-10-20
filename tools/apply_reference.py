#!/usr/bin/env python3
"""Apply reviewed presentation values by SNBT field spans, preserving all other bytes."""
import argparse
import json
from pathlib import Path

import ftb_snbt_lib as snbt
import quality


def whitespace(text, pos):
    while pos < len(text):
        if text[pos].isspace() or text[pos] == ',':
            pos += 1
        elif text.startswith('//', pos) or text[pos] == '#':
            end = text.find('\n', pos)
            pos = len(text) if end < 0 else end + 1
        else:
            return pos
    return pos


def quoted_end(text, pos):
    quote = text[pos]
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
        elif text[pos] == quote:
            return pos + 1
        else:
            pos += 1
    raise ValueError('Unclosed quoted string')


def value_end(text, pos):
    if text[pos] in '\"\'':
        return quoted_end(text, pos)
    if text[pos] in '{[':
        closing = '}' if text[pos] == '{' else ']'
        pos = whitespace(text, pos + 1)
        while pos < len(text) and text[pos] != closing:
            pos = whitespace(text, value_end(text, pos))
        if pos >= len(text):
            raise ValueError('Unclosed SNBT container')
        return pos + 1
    end = pos
    while end < len(text) and not text[end].isspace() and text[end] not in ',]}{[\"\'':
        end += 1
    if end == pos:
        raise ValueError(f'Unexpected token at {pos}')
    return end


def field_spans(text, pos):
    if text[pos] != '{':
        raise ValueError('Expected compound')
    fields = {}
    pos = whitespace(text, pos + 1)
    while text[pos] != '}':
        if text[pos] in '\"\'':
            end = quoted_end(text, pos)
            key = text[pos + 1:end - 1]
        else:
            end = pos
            while text[end] != ':' and not text[end].isspace():
                end += 1
            key = text[pos:end]
        pos = whitespace(text, end)
        if text[pos] != ':':
            raise ValueError('Expected colon')
        start = whitespace(text, pos + 1)
        end = value_end(text, start)
        if key in fields:
            raise ValueError('Duplicate field: ' + key)
        fields[key] = (start, end)
        pos = whitespace(text, end)
    return fields


def render_value(key, value):
    if key == 'description':
        return '[\n' + '\n'.join('                ' + json.dumps(line, ensure_ascii=False) for line in value) + '\n            ]'
    if key in ('x', 'y', 'size'):
        return f'{float(value):.2f}d'
    return json.dumps(value, ensure_ascii=False)


def transform(text, design):
    root = field_spans(text, whitespace(text, 0))
    edits = []
    def change(spans, values):
        for key, value in values.items():
            if key not in quality.PRESENTATION:
                raise ValueError('Protected field in design: ' + key)
            if key not in spans:
                raise ValueError('This patcher only changes existing fields: ' + key)
            start, end = spans[key]
            edits.append((start, end, render_value(key, value)))
    change(root, design['chapter'])
    pos = whitespace(text, root['quests'][0] + 1)
    found = set()
    while text[pos] != ']':
        end = value_end(text, pos)
        quest = snbt.loads(text[pos:end])
        ident = str(quest['id'])
        if ident in design['quests']:
            change(field_spans(text, pos), design['quests'][ident]['values'])
            found.add(ident)
        pos = whitespace(text, end)
    if found != set(design['quests']):
        raise ValueError('Design contains missing quest IDs')
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Require working file to match the reviewed output, without writing')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    design = json.loads((root/'reviews/reference_design.json').read_text())
    name = quality.CHAPTER_ROOT + 'nasledie_defense.snbt'
    baseline = quality.git(root, 'show', f'{design["baseline_commit"]}:{name}').decode()
    result = transform(baseline, design)
    before, after = snbt.loads(baseline), snbt.loads(result)
    if quality.canonical(quality.protected_body(before)) != quality.canonical(quality.protected_body(after)):
        raise ValueError('Protected game data would change')
    target = root/name
    current = target.read_text()
    if args.check:
        if current != result:
            raise SystemExit('Working chapter differs from reproducible reference design')
        print('Reference design matches the chapter exactly')
        return
    if current not in (baseline, result):
        raise ValueError('Unexpected existing edits: refusing to overwrite')
    if current != result:
        target.write_text(result)
    changes = []
    before_quests = {str(q['id']):q for q in before['quests']}
    for q in after['quests']:
        old = before_quests[str(q['id'])]
        fields = {k:{'before':old.get(k), 'after':q.get(k)} for k in quality.PRESENTATION if old.get(k)!=q.get(k)}
        if fields:
            changes.append({'id':str(q['id']), 'title':str(q['title']), 'fields':fields,
                            'reason':design['quests'][str(q['id'])]['reason']})
    report = {'baseline_commit':design['baseline_commit'], 'file':name,
              'chapter_fields':{k:{'before':before.get(k),'after':after.get(k)} for k in quality.PRESENTATION if before.get(k)!=after.get(k)},
              'quests':changes,'protected_data':'identical including IDs, tasks, rewards, dependencies, optional and order',
              'gameplay_test':'not run; grove_watch contains pre-existing entity ID defects'}
    (root/'reviews/reference_changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Applied/reproduced presentation changes for {len(changes)} quests; protected data identical')


if __name__ == '__main__':
    main()
