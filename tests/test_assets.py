import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def strict(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f'duplicate keys: {keys}')
    return dict(pairs)


class LangOverrideTests(unittest.TestCase):
    """kubejs/assets/<mod>/lang/ru_ru.json override single keys of the mods' Russian translations."""

    def test_overrides_are_flat_unique_strings(self):
        files = sorted(ROOT.glob('kubejs/assets/*/lang/ru_ru.json'))
        self.assertTrue(files)
        for path in files:
            data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=strict)
            for key, value in data.items():
                self.assertIsInstance(value, str, f'{path.name}: {key}')
                self.assertTrue(value.strip(), f'{path}: {key}')
                # Either a key of that mod or the project's own nasledie.* key.
                self.assertTrue(key.startswith('nasledie.') or path.parts[-3] in key.split('.')[:2],
                                f'{path}: key {key} belongs to another mod')


if __name__ == '__main__':
    unittest.main()
