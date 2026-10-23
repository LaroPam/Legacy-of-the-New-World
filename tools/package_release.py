#!/usr/bin/env python3
"""Package a questbook release: installable ZIP, patch against the declared base and a manifest.

  python tools/package_release.py [--base bf2a0d9] [--name alpha43]

Refuses to package uncommitted or untracked game files or a book with validator errors. The patch is
applied to the base files in a temporary directory and must reproduce the packaged files byte for byte.
Output: reports/<name>/nasledie-<name>.zip, <name>.patch, manifest.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality  # noqa: E402
import validate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ['docs/ALPHA43_TEST_CHECKLIST.md', 'docs/ALPHA43_CHANGELOG.md', 'docs/KNOWN_LIMITS.md', 'docs/STORY.md',
        'docs/REWARD_POLICY.md']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def install_text(name, head, base, counts):
    return f"""# Наследие нового мира — {name}

Файлы квестбука (не сборка модов). Коммит `{head[:12]}`, база `{base[:12]}`.
{counts['chapters']} глав, {counts['quests']} квестов, {counts['tasks']} задач, {counts['rewards']} наград.
Статическая проверка пройдена; **игровой тест ещё не проводился**.

## Установка (на обоих компьютерах)

1. Сделайте копию мира, если он дорог. Для проверки лучше новый мир.
2. Удалите папки `.minecraft/config/ftbquests/quests/` (целиком: FTB перезаписывает её при сохранении)
   и `.minecraft/kubejs/data/nasledie/`.
3. Скопируйте `config/` и `kubejs/` из архива в `.minecraft/` с заменой.
4. Полностью перезапустите игру.

Что проверить — `docs/ALPHA43_TEST_CHECKLIST.md`; известные ограничения — `docs/KNOWN_LIMITS.md`.
""".encode()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='bf2a0d9')
    parser.add_argument('--name', default='alpha43')
    args = parser.parse_args(argv)

    dirty = quality.git(ROOT, 'status', '--porcelain', '--untracked-files=all', '--', *quality.INPUT_ROOTS)
    if dirty.strip():
        raise SystemExit('Commit the game files before packaging:\n' + dirty.decode())
    current, baseline, base = quality.snapshots(ROOT, args.base)
    registry = json.loads(validate.REGISTRY.read_text())
    report = validate.evaluate(validate.collect_files(), registry)
    if report['errors']:
        raise SystemExit(f"Validator errors: {len(report['errors'])}")
    head = quality.git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    patch = quality.git(ROOT, 'diff', '--binary', base, 'HEAD', '--', *quality.INPUT_ROOTS)

    with tempfile.TemporaryDirectory(prefix='nasledie-release-') as temp:
        work = Path(temp)
        for name, data in baseline.items():
            (work/name).parent.mkdir(parents=True, exist_ok=True)
            (work/name).write_bytes(data)
        subprocess.run(['git', 'init', '-q'], cwd=work, check=True)
        subprocess.run(['git', 'apply', '-'], cwd=work, input=patch, check=True)
        restored = {p.relative_to(work).as_posix(): p.read_bytes()
                    for prefix in quality.INPUT_ROOTS for p in (work/prefix).rglob('*') if p.is_file()}
    if restored != current:
        raise SystemExit('Applying the patch to the base does not reproduce the packaged files')

    warnings = sorted({w['code'] for w in report['warnings']})
    manifest = {
        'name': args.name, 'source_commit': head, 'base_commit': base,
        'gameplay_test': 'not run', 'counts': report['counts'],
        'validator': {'errors': 0, 'warnings': len(report['warnings']), 'warning_codes': warnings},
        'patch_applied_to_base_and_compared': True,
        'game_files': {name: sha(data) for name, data in sorted(current.items())},
    }
    files = dict(current)
    files['INSTALL.md'] = install_text(args.name, head, base, report['counts'])
    for name in DOCS:
        files[name] = (ROOT/name).read_bytes()
    files['SOURCE.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()

    out = ROOT/'reports'/args.name
    out.mkdir(parents=True, exist_ok=True)
    archive = out/f'nasledie-{args.name}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), data)
    with zipfile.ZipFile(archive) as z:
        if any(z.read(name) != data for name, data in files.items()):
            raise SystemExit('ZIP contents differ from the packaged files')
    (out/f'{args.name}.patch').write_bytes(patch)
    manifest['archive_sha256'] = sha(archive.read_bytes())
    manifest['patch_sha256'] = sha(patch)
    (out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{archive.relative_to(ROOT)}: {len(files)} files, sha256 {manifest['archive_sha256']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
