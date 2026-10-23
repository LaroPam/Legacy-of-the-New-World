import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import quality
from validate import quest_issues


def book(task):
    quest = {'id': 'AAAAAAAAAAAAAAAA', 'shape': 'circle', 'description': ['Шаг.'], 'tasks': [task], 'rewards': []}
    return {quality.CHAPTER_ROOT + 'test.snbt': {'quests': [quest]}}


class CountedTaskTests(unittest.TestCase):
    def codes(self, task):
        errors, _ = quest_issues(book(task))
        return [e['code'] for e in errors]

    def test_kill_task_without_value_is_rejected(self):
        # FTB KillTask.readData uses getLong("value"): a missing key is a goal of zero kills.
        self.assertIn('count_missing', self.codes({'id': 'B', 'type': 'kill', 'entity': 'minecraft:zombie'}))

    def test_kill_task_with_value_passes(self):
        self.assertNotIn('count_missing', self.codes({'id': 'B', 'type': 'kill', 'entity': 'minecraft:zombie', 'value': 1}))

    def test_stat_task_without_value_is_rejected(self):
        self.assertIn('count_missing', self.codes({'id': 'B', 'type': 'stat', 'stat': 'minecraft:jump'}))


class WrittenBookTests(unittest.TestCase):
    def codes(self, tag):
        data = book({'id': 'B', 'type': 'checkmark'})
        quest = next(iter(data.values()))['quests'][0]
        quest['rewards'] = [{'id': 'R', 'type': 'item', 'item': {'id': 'minecraft:written_book', 'Count': 1, 'tag': tag}}]
        return [e['code'] for e in quest_issues(data)[0]]

    def test_title_over_32_chars_is_rejected(self):
        # The 1.20.1 client renders such a book as "Invalid book tag".
        self.assertIn('book_invalid', self.codes({'title': 'Я' * 33, 'author': 'Линд', 'pages': ['{"text":"x"}']}))

    def test_valid_book_passes(self):
        self.assertNotIn('book_invalid', self.codes({'title': 'Я' * 32, 'author': 'Линд', 'pages': ['{"text":"x"}']}))


if __name__ == '__main__':
    unittest.main()
