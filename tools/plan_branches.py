#!/usr/bin/env python3
"""Compile reviewed narrative routes to exact dependency fixes and layout values."""
import json
from pathlib import Path
import ftb_snbt_lib as snbt
import quality

root=Path(__file__).resolve().parents[1]
inventory=json.loads((root/'reviews/semantic_inventory.json').read_text())
plans=json.loads((root/'reviews/branch_plans.json').read_text())
scope=json.loads((root/'reviews/polish_scope.json').read_text())
for name, plan in plans['chapters'].items():
    rows=[q for q in inventory['quests'] if Path(q['chapter']).stem==name]
    by_id={q['id']:q for q in rows}
    ids=[q['id'] for q in rows]
    baseline=snbt.loads(quality.git(root,'show',scope['baseline_commit']+':'+quality.CHAPTER_ROOT+name+'.snbt').decode())
    original={str(q['id']):q for q in baseline['quests']}
    coverage=[i for branch in plan['branches'] for i in branch['nodes']]
    if sorted(coverage)!=list(range(len(rows))):
        raise ValueError('Routes must cover every quest exactly once: '+name)
    design_path=root/'reviews/chapters'/(name+'.json')
    design=json.loads(design_path.read_text())
    compiled_dependencies={}
    for branch in plan['branches']:
        previous=branch['after']
        for index in branch['nodes']:
            quest=rows[index]
            before=quest['dependencies']
            after=[] if previous is None else [ids[previous]]
            if str(index) in plan.get('dependency_overrides', {}):
                after=[ids[i] for i in plan['dependency_overrides'][str(index)]]
            compiled_dependencies[quest['id']]=after
            reason='Ветка «'+branch['name']+'»: '+branch['goal']+' Последовательность шагов ведёт к этому результату; ID, условия и награды сохранены.'
            if before!=after:
                scope['quest_fixes'][quest['id']]={'dependencies':{'before':original[quest['id']].get('dependencies'),'after':after,'reason':reason}}
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
    used_after={dep for deps in compiled_dependencies.values() for dep in deps}
    plan['metrics']={'quests':len(rows),'terminal_quests_before':len(set(ids)-used_before),
                     'terminal_quests_after':len(set(ids)-used_after),'routes':len(plan['branches'])}
    print(name,plan['metrics'])
(root/'reviews/branch_plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
(root/'reviews/polish_scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n')
