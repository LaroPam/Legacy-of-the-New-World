#!/usr/bin/env python3
"""Deterministic preview archive containing only the edited chapter and review notes."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
baseline = 'f68124fb33597aa13b4b6a8dd8c6dde7c879b188'
name = 'config/ftbquests/quests/chapters/nasledie_defense.snbt'
source = (root/name).read_bytes()
readme = '''ВИЗУАЛЬНЫЙ ОБРАЗЕЦ — НЕ ГОТОВЫЙ РЕЛИЗ

Эталонная глава «Охота и артиллерия»: 25 квестов / 29 задач / 52 награды.
Архив содержит только одну главу и эти заметки. Моды и остальные главы не включены.
Предназначен для копии уже существующей Alpha 42. Перед просмотром в игре сохраните
свою прежнюю главу и используйте тестовую копию мира. Сервер/клиент здесь не проверялись.

ID, задачи, награды, зависимости и optional сохранены. Изменены только оформление
и пользовательские тексты. Файл главы располагается по исходному пути config/ftbquests/quests/chapters/.

ИЗВЕСТНЫЙ ИСХОДНЫЙ ДЕФЕКТ: «Караул солнечной рощи» содержит два условия с отсутствующими
типами существ Mowzie. Они не исправлялись без отдельного согласования. Поэтому этот
образец предназначен для оценки оформления и не объявляется готовым к прохождению.

Подробности: docs/REFERENCE_CHAPTER.md, docs/POLISH_AUDIT.md, reports/visual/index.html
в рабочей ветке polish/reference-chapter репозитория. Остальные 17 глав ждут оценки автора.
'''
manifest = {'baseline_commit':baseline, 'chapter':name, 'chapter_sha256':hashlib.sha256(source).hexdigest(),
            'purpose':'visual reference for author review; not gameplay-ready release'}
files = {name:source, 'README_REFERENCE.txt':readme.encode(), 'SOURCE.json':(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()}
target = root/'reports/reference-preview.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for filename,data in sorted(files.items()):
        info = zipfile.ZipInfo(filename,date_time=(1980,1,1,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info,data)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert z.read(name) == source
patch = subprocess.check_output(['git','diff','--binary',baseline,'--',name],cwd=root)
(root/'reports/reference-preview.patch').write_bytes(patch)
manifest['zip_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
manifest['patch_sha256'] = hashlib.sha256(patch).hexdigest()
(root/'reports/reference-preview-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest,ensure_ascii=False))
