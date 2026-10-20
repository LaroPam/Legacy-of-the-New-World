#!/usr/bin/env python3
"""Optional browser smoke test for the offline report, NOT a Minecraft test.

Requires Playwright and Chromium. In the cloud these are already available in
the system Python. set_content loads our generated document without file URLs.
"""
import hashlib
import json
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
document = root/'reports/visual/index.html'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1680,'height':1200}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(document.read_text(), wait_until='load')
    assert 'Охота и артиллерия' in page.locator('#chapter option:checked').inner_text()
    assert page.locator('#chapter option').count() == 18
    assert page.locator('#before [data-quest-id]').count() == 25
    assert page.locator('#after [data-quest-id]').count() == 25
    page.locator('#quest-list').select_option('9B6EFB1C669C7CFA')
    assert 'Топор Тысячи Металлов' in page.locator('#after-detail').inner_text()
    page.locator('#only-changed').check()
    assert page.locator('#quest-list option').count() == 25
    page.locator('#labels').uncheck()
    page.screenshot(path=str(root/'reports/visual/reference-comparison.png'), full_page=False)
    page.locator('#labels').check()
    page.locator('#actual').click()
    page.locator('#locate').click()
    page.locator('#chapter').select_option(index=0)
    assert page.locator('#before [data-quest-id]').count() == 4
    for i in range(18):
        page.locator('#chapter').select_option(index=i)
        page.wait_for_function("document.querySelector('#palette-name').textContent === current.palette.name")
        expected_count = page.evaluate("current.after.quests.length")
        assert page.locator('#after [data-quest-id]').count() == expected_count
        for state in ['locked', 'not_started', 'started', 'completed']:
            page.locator('#quest-state').select_option(state)
            color = page.evaluate("current.palette.properties['quest_' + document.querySelector('#quest-state').value + '_color']")
            assert set(page.locator('#after .quest-frame').evaluate_all("(els)=>els.map(el=>el.getAttribute('stroke'))")) == {color}
    page.locator('#chapter').select_option(index=2)
    page.locator('#quest-state').select_option('not_started')
    page.locator('#quest-list').select_option('1D1395D17D6238DB')
    assert 'Первая цель — небольшая пекарня' in page.locator('#after-detail').inner_text()
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(root/'reports/visual/create-comparison.png'), full_page=True)
    assert not errors, errors
    report = {'scope':'Browser report smoke test only; Minecraft not run',
              'html_sha256':hashlib.sha256(document.read_bytes()).hexdigest(),
              'chapters':18, 'reference_nodes_per_side':25, 'changed_quests':25,
              'checks':['default reference selection','all chapter options','both diagrams','quest detail','changed filter','label toggle','zoom','locate','all 18 chapter node counts','all 72 chapter/state palettes','Create roadmap'],
              'javascript_errors':errors, 'result':'passed'}
    (root/'reports/browser_smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    browser.close()
    print(json.dumps(report,ensure_ascii=False))
