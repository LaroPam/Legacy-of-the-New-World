#!/usr/bin/env python3
"""Package current questbook files, verify ZIP bytes and apply its patch to the baseline."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

import quality


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    scope = json.loads((root/'reviews/polish_scope.json').read_text())
    current, baseline, commit = quality.snapshots(root, scope['baseline_commit'])
    report = json.loads((root/'reports/quality.json').read_text())
    if report['summary']['errors']:
        raise ValueError('Static quality report contains errors')
    if report.get('input_sha256') != {name: sha(data) for name, data in current.items()}:
        raise ValueError('Static quality report does not match current game files')
    if quality.git(root, 'diff', '--name-only', 'HEAD', '--', *quality.INPUT_ROOTS).strip():
        raise ValueError('Commit the tested game inputs before packaging')
    head = quality.git(root, 'rev-parse', 'HEAD').decode().strip()
    patch = quality.git(root, 'diff', '--binary', commit, '--', *quality.INPUT_ROOTS)
    with tempfile.TemporaryDirectory(prefix='nasledie-patch-') as temp:
        work = Path(temp)
        for name, data in baseline.items():
            target = work/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        subprocess.run(['git', 'apply', '--check', '-'], cwd=work, input=patch, check=True)
        subprocess.run(['git', 'apply', '-'], cwd=work, input=patch, check=True)
        restored = {p.relative_to(work).as_posix(): p.read_bytes()
                    for prefix in quality.INPUT_ROOTS for p in (work/prefix).rglob('*') if p.is_file()}
        if restored != current:
            raise ValueError('Applying patch does not reproduce current files')
    manifest = {
        'purpose': 'Full questbook test candidate; not a modpack or gameplay-validated release',
        'baseline_commit': commit, 'source_commit': head,
        'gameplay_test': 'not run', 'release_ready': False,
        'counts': report['counts'], 'static_summary': report['summary'],
        'game_files': {name: sha(data) for name, data in sorted(current.items())},
        'patch_applied_to_baseline_and_compared': True,
    }
    files = dict(current)
    files['README_CANDIDATE.md'] = (root/'docs/CANDIDATE_INSTALL.md').read_bytes()
    for name in ['docs/KNOWN_LIMITS.md', 'docs/CHAPTER_ROUTES_AND_COLORS.md',
                 'docs/USABILITY_PASS.md', 'docs/EXPEDITION_ACTIONS.md',
                 'docs/REWARD_REVIEW.md', 'reports/quality.json']:
        files[name] = (root/name).read_bytes()
    files['SOURCE.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode()
    target = root/'reports/questbook-candidate.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None or set(z.namelist()) != set(files):
            raise ValueError('ZIP failed CRC or file-list comparison')
        if any(z.read(name) != data for name, data in files.items()):
            raise ValueError('ZIP differs from source files')
    (root/'reports/questbook-candidate.patch').write_bytes(patch)
    manifest.update(zip_sha256=sha(target.read_bytes()), patch_sha256=sha(patch),
                    zip_entries=len(files), zip_bytes_match_sources=True)
    (root/'reports/questbook-candidate-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'zip': str(target), 'game_files': len(current),
                      'patch_files': len([name for name in set(baseline) | set(current)
                                         if baseline.get(name) != current.get(name)]),
                      'zip_sha256': manifest['zip_sha256'], 'patch_reproduces_sources': True}))


if __name__ == '__main__':
    main()
