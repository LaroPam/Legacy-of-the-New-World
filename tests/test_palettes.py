import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from apply_palettes import sections, validate, COLORS


class ThemeParsingTests(unittest.TestCase):
    def test_missing_global_selector_rejects_old_silent_failure(self):
        with self.assertRaises(ValueError):
            sections('quest_not_started_color: #FF8800\n')

    def test_id_selector_is_not_a_tag_selector(self):
        with self.assertRaises(ValueError):
            sections('[#1234567890ABCDEF]\nquest_started_color: #FF8800\n')

    def test_repeated_selector_is_rejected(self):
        with self.assertRaises(ValueError):
            sections('[*]\nbackground: color:transparent\n[*]\n')

    def test_palette_cannot_target_quest_instead_of_chapter(self):
        text = '[*]\n[1234567890ABCDEF]\n' + '\n'.join(
            f'{key}: #{index + 1:06X}' for index, key in enumerate(COLORS))
        validate(text, {'chapter': {'id': '1234567890ABCDEF'}})
        with self.assertRaises(ValueError):
            validate(text, {'chapter': {'id': '0234567890ABCDEF'}})
