import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from apply_palettes import sections, validate, COLORS, texture_file


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


class BackgroundTests(unittest.TestCase):
    CHAPTERS = {'chapter': {'id': '1234567890ABCDEF'}}

    def theme(self, background):
        return '[*]\n[1234567890ABCDEF]\n' + '\n'.join(
            f'{key}: #{index + 1:06X}' for index, key in enumerate(COLORS)) + f'\nbackground: {background}\n'

    def test_chapter_background_must_be_a_texture(self):
        validate(self.theme('nasledie:textures/backgrounds/bg_chapter.png'), self.CHAPTERS)
        for value in ('color:transparent', '#000000', 'nasledie:backgrounds/bg.png'):
            with self.assertRaises(ValueError):
                validate(self.theme(value), self.CHAPTERS)

    def test_missing_background_file_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        validate(self.theme('nasledie:textures/backgrounds/bg_life.png'), self.CHAPTERS, root)
        with self.assertRaises(ValueError):
            validate(self.theme('nasledie:textures/backgrounds/bg_nowhere.png'), self.CHAPTERS, root)

    def test_texture_file_maps_to_kubejs_assets(self):
        self.assertEqual(texture_file('nasledie:textures/backgrounds/bg_x.png; color=#FFFFFF'),
                         'kubejs/assets/nasledie/textures/backgrounds/bg_x.png')
        self.assertIsNone(texture_file('color:transparent'))
