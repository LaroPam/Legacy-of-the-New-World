#!/usr/bin/env python3
"""Compile reviewed narrative routes to exact dependency fixes and layout values."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
inventory=json.loads((root/'reviews/semantic_inventory.json').read_text())
plans=json.loads((root/'reviews/branch_plans.json').read_text())
scope=json.loads((root/'reviews/polish_scope.json').read_text())
for name, plan in plans['chapters'].items():
    rows=[q for q in inventory['quests'] if Path(q['chapter']).stem==name]
    by_id={q['id']:q for q in rows}
    ids=[q['id'] for q in rows]
    coverage=[i for branch in plan['branches'] for i in branch['nodes']]
    if sorted(coverage)!=list(range(len(rows))):
        raise ValueError('Routes must cover every quest exactly once: '+name)
    design_path=root/'reviews/chapters'/(name+'.json')
    design=json.loads(design_path.read_text())
    for branch in plan['branches']:
        previous=branch['after']
        for index in branch['nodes']:
            quest=rows[index]
            before=quest['dependencies']
            after=[] if previous is None else [ids[previous]]
            reason='Ветка «'+branch['name']+'»: '+branch['goal']+' Последовательность шагов ведёт к этому результату; ID, условия и награды сохранены.'
            if before!=after:
                scope['quest_fixes'][quest['id']]={'dependencies':{'before':before,'after':after,'reason':reason}}
            else:
                scope['quest_fixes'].pop(quest['id'],None)
            entry=design['quests'][quest['id']]
            entry['branch']=branch['name']
            entry['branch_goal']=branch['goal']
            xy=plan['positions'][str(index)]
            entry['values'].update(x=xy[0]*2.5,y=xy[1]*2.5)
            previous=index
    design['layout_reason']=plan['layout_reason']
    design_path.write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n')
    used_before={d for q in rows for d in q['dependencies']}
    used_after={ids[b['after']] for b in plan['branches'] if b['after'] is not None}
    used_after.update(ids[i] for b in plan['branches'] for i in b['nodes'][:-1])
    plan['metrics']={'quests':len(rows),'terminal_quests_before':len(set(ids)-used_before),
                     'terminal_quests_after':len(set(ids)-used_after),'routes':len(plan['branches'])}
    print(name,plan['metrics'])
(root/'reviews/branch_plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
(root/'reviews/polish_scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n')
