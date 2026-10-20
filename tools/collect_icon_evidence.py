#!/usr/bin/env python3
"""Collect exact model/texture hashes for deliberately selected replacement icons."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def collect(identifier, jar, registration):
    namespace, name = identifier.split(':', 1)
    model = f'assets/{namespace}/models/item/{name}.json'
    with zipfile.ZipFile(jar) as z:
        models, textures = {}, {}
        def visit(path):
            if path in models:
                return
            raw = z.read(path)
            body = json.loads(raw)
            models[path] = hashlib.sha256(raw).hexdigest()
            for value in body.get('textures', {}).values():
                if value.startswith('#'):
                    continue
                ns, local = value.split(':', 1) if ':' in value else ('minecraft',value)
                texture = f'assets/{ns}/textures/{local}.png'
                if texture in z.namelist():
                    textures[texture] = hashlib.sha256(z.read(texture)).hexdigest()
            parent = body.get('parent', '')
            ns, local = parent.split(':', 1) if ':' in parent else ('minecraft',parent)
            parent_path = f'assets/{ns}/models/{local}.json'
            if parent and parent_path in z.namelist():
                visit(parent_path)
        visit(model)
        if not textures:
            raise ValueError('No resolved texture evidence for '+identifier)
    return {'kind':'minecraft_builtin' if namespace=='minecraft' else 'forge_item_registration',
            'source_file':jar.name,'source_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),
            'registration_evidence':registration,'model':model,'model_sha256':models[model],
            'model_chain':models,'textures':[{'path':p,'sha256':h} for p,h in sorted(textures.items())]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path('/workspace/.onboarding/artifacts'))
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    specifications=json.loads((root/'reviews/icon_sources.json').read_text())
    result={'scope':'Introduced icons: exact static item registration/model/texture evidence; not game rendering.', 'items':{}}
    for identifier, spec in specifications.items():
        jar=a.cache/spec['jar']
        if hashlib.sha256(jar.read_bytes()).hexdigest()!=spec['sha256']:
            raise ValueError('Source JAR hash mismatch: '+str(jar))
        result['items'][identifier]=collect(identifier,jar,spec['registration'])
    (root/'reviews/polish_icon_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Saved icon evidence:',len(result['items']))


if __name__=='__main__':
    main()
