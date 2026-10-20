#!/usr/bin/env python3
"""Print retained per-quest evidence for focused editing; never changes game data."""
import argparse
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('chapter')
p.add_argument('--start', type=int, default=0)
p.add_argument('--limit', type=int, default=25)
p.add_argument('--cache', type=Path, default=Path('/workspace/.onboarding/artifacts'))
a = p.parse_args()
supplement_path = root/'reviews/supplemental_advancements.json'
supplement = json.loads(supplement_path.read_text()) if supplement_path.exists() else {}
rows = [q for q in json.loads((root/'reviews/semantic_inventory.json').read_text())['quests']
        if Path(q['chapter']).stem == 'nasledie_' + a.chapter]
for index, q in enumerate(rows[a.start:a.start+a.limit], a.start):
    print(f'\n{index} {q["id"]} | {q["title"]} | {q["icon"]}')
    print('TASK', json.dumps([{k:v for k,v in t.items() if k != 'id'} for t in q['tasks']], ensure_ascii=False))
    for name,evidence in q['advancement_evidence'].items():
        evidence = supplement.get(name, evidence)
        body = evidence.get('body', {})
        print('CONDITION', name, json.dumps({k:body[k] for k in ('criteria','requirements') if k in body},ensure_ascii=False))
        display = body.get('display', {})
        print('MOD_ICON', display.get('icon'))
        source = a.cache/(evidence.get('source') or '')
        if source.is_file():
            with zipfile.ZipFile(source) as z:
                for lang in [n for n in z.namelist() if n.endswith('/lang/en_us.json')]:
                    try:
                        translations = json.loads(z.read(lang))
                    except (ValueError, UnicodeError):
                        continue
                    terms = [translations.get(display.get(k, {}).get('translate', '')) for k in ('title','description') if isinstance(display.get(k), dict)]
                    if any(terms): print('MOD_TEXT', json.dumps(terms,ensure_ascii=False))
    print('DEPS', q['dependencies'])
    if not q['advancement_evidence'] or any(not supplement.get(n, e).get('body') for n, e in q['advancement_evidence'].items()):
        print('OLD_TEXT', ' / '.join(q['description']))
