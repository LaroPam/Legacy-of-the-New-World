#!/usr/bin/env python3
"""Index ids from the pack's JAR files into references/registry.json and references/names_ru.json.

Static evidence only: item models, entity lang keys, data-pack structures/biomes/advancements.
An id found this way can still be missing at runtime (e.g. disabled by config); an id absent from
a covered namespace is almost certainly a typo.

  python tools/build_registry.py JAR_DIR [--vanilla-ru ru_ru.json]
"""
import argparse
import io
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'items': r'assets/([^/]+)/models/item/(.+)\.json$',
    'advancement': r'data/([^/]+)/advancements/(.+)\.json$',
    'structures': r'data/([^/]+)/worldgen/structure/(.+)\.json$',
    'biomes': r'data/([^/]+)/worldgen/biome/(.+)\.json$',
    'blocks': r'assets/([^/]+)/blockstates/(.+)\.json$',
    'loot_tables': r'data/([^/]+)/loot_tables/(.+)\.json$',
    'recipes': r'data/([^/]+)/recipes/(.+)\.json$',
}
LANG = r'assets/([^/]+)/lang/(en_us|ru_ru)\.json$'


def text(component):
    if isinstance(component, dict):
        return component.get('translate', component.get('text'))
    return component


def scan(archive, out, langs, depth=0):
    for name in archive.namelist():
        if name.endswith('.jar') and depth < 2:
            try:
                scan(zipfile.ZipFile(io.BytesIO(archive.read(name))), out, langs, depth + 1)
            except zipfile.BadZipFile:
                pass
            continue
        match = re.match(LANG, name)
        if match:
            try:
                langs[match[2]].update(json.loads(archive.read(name).decode('utf-8', 'replace')))
            except ValueError:
                pass
            continue
        for kind, pattern in PATTERNS.items():
            match = re.match(pattern, name)
            if not match:
                continue
            ident = f'{match[1]}:{match[2]}'
            out[kind].add(ident)
            if kind == 'advancement':
                try:
                    body = json.loads(archive.read(name))
                except ValueError:
                    break
                display = body.get('display') or {}
                out['advancement_info'][ident] = {'title': text(display.get('title')),
                                                  'description': text(display.get('description'))}
                items = sorted({i for c in (body.get('criteria') or {}).values()
                                if isinstance(c, dict) and c.get('trigger') == 'minecraft:inventory_changed'
                                for p in ((c.get('conditions') or {}).get('items') or []) if isinstance(p, dict)
                                for i in (p.get('items') or [])})
                if items:
                    out['advancement_items'][ident] = items
            break


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('jars', type=Path)
    parser.add_argument('--vanilla-ru', type=Path)
    args = parser.parse_args()
    out = {k: set() for k in PATTERNS}
    out['advancement_info'], out['advancement_items'] = {}, {}
    langs = {'en_us': {}, 'ru_ru': {}}
    jars = sorted(args.jars.glob('*.jar'))
    for jar in jars:
        scan(zipfile.ZipFile(jar), out, langs)
    if args.vanilla_ru:
        langs['ru_ru'].update(json.loads(args.vanilla_ru.read_text(encoding='utf-8')))
    out['entities'] = {f'{m[1]}:{m[2]}' for lang in langs.values() for key in lang
                       for m in [re.match(r'entity\.([a-z0-9_]+)\.([a-z0-9_]+)$', key)] if m}
    out['effects'] = {f'{m[1]}:{m[2]}' for lang in langs.values() for key in lang
                      for m in [re.match(r'effect\.([a-z0-9_]+)\.([a-z0-9_]+)$', key)] if m}
    kinds = ('items', 'entities', 'structures', 'biomes', 'advancement', 'blocks', 'loot_tables', 'recipes', 'effects')
    registry = {kind: sorted(out[kind]) for kind in kinds}
    registry['namespaces'] = {kind: sorted({i.split(':')[0] for i in out[kind]}) for kind in kinds}
    registry['advancement_items'] = out['advancement_items']
    registry['sources'] = [jar.name for jar in jars]
    (ROOT / 'references' / 'registry.json').write_text(json.dumps(registry, ensure_ascii=False, indent=0) + '\n')

    def name(prefixes, ident):
        ns, path = ident.split(':', 1)
        for prefix in prefixes:
            key = f'{prefix}.{ns}.{path.replace("/", ".")}'
            for lang in ('ru_ru', 'en_us'):
                if key in langs[lang]:
                    return langs[lang][key]
        return None
    names = {
        'items': {i: name(('item', 'block'), i) for i in registry['items']},
        'entities': {i: name(('entity',), i) for i in registry['entities']},
        'advancements': {i: {k: langs['ru_ru'].get(v, langs['en_us'].get(v, v)) if v else None
                             for k, v in info.items()} for i, info in sorted(out['advancement_info'].items())
                         if info['title']},
        'biomes': {i: name(('biome',), i) for i in registry['biomes']},
        'structures': {i: name(('structure', 'structure_name'), i) for i in registry['structures']},
    }
    (ROOT / 'references' / 'names_ru.json').write_text(json.dumps(names, ensure_ascii=False, indent=0) + '\n')
    print({k: len(registry[k]) for k in kinds}, len(jars), 'jars')


if __name__ == '__main__':
    main()
