import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import ftb_snbt_lib as snbt  # noqa: E402
import questbook  # noqa: E402
import validate  # noqa: E402

CHAPTER = """
chapter: {filename: test_a, id: 0000000000000A01, group: 842B4DB4DBD349A0, title: Тест, icon: minecraft:book,
          order_index: 0, default_quest_shape: circle}
quests:
  - key: start
    title: Начало
    x: 0
    y: 0
    icon: minecraft:book
    tasks: [{type: advancement, advancement: minecraft:story/root}]
    rewards: [{type: xp, xp: 10}, {type: book, title: Запись 1, pages: [Первая страница]}]
  - key: next
    title: Дальше
    x: 2.5
    y: 0
    deps: [start]
    tasks: [{type: item, item: minecraft:diamond}]
    rewards: [{type: item, item: minecraft:emerald, count: 3}]
"""
OTHER = """
chapter: {filename: test_b, id: 0000000000000B01, group: 842B4DB4DBD349A0, title: Другая, icon: minecraft:map, order_index: 1}
quests:
  - key: far
    title: Далеко
    deps: [test_a/next]
    tasks: [{type: kill, entity: minecraft:zombie}]
    rewards: [{type: item, item: minecraft:diamond}]
"""


def build(*sources):
    with tempfile.TemporaryDirectory() as tmp:
        for i, text in enumerate(sources):
            name = 'test_a' if i == 0 else 'test_b'
            (Path(tmp) / (name + '.yaml')).write_text(text, encoding='utf-8')
        return {n: snbt.loads(t) for n, t in questbook.build_all(Path(tmp)).items()}


class QuestbookBuild(unittest.TestCase):
    def test_ids_types_and_dependencies(self):
        out = build(CHAPTER, OTHER)
        start, nxt = out['test_a']['quests']
        self.assertEqual(str(start['id']), questbook.make_id('test_a/start'))
        self.assertEqual([str(d) for d in nxt['dependencies']], [str(start['id'])])
        self.assertIsInstance(nxt['x'], snbt.Double)
        self.assertIsInstance(nxt['tasks'][0]['count'], snbt.Long)
        self.assertEqual(int(nxt['rewards'][0]['item']['Count']), 3)
        self.assertIsInstance(nxt['rewards'][0]['item']['Count'], snbt.Byte)
        far = out['test_b']['quests'][0]
        self.assertEqual(str(far['dependencies'][0]), str(nxt['id']))

    def test_ids_are_stable(self):
        first, second = build(CHAPTER), build(CHAPTER)
        self.assertEqual(snbt.dumps(first['test_a']), snbt.dumps(second['test_a']))

    def test_book_reward_is_readable_written_book(self):
        book = build(CHAPTER)['test_a']['quests'][0]['rewards'][1]['item']
        self.assertEqual(str(book['id']), 'minecraft:written_book')
        self.assertEqual(json.loads(str(book['tag']['pages'][0])), {'text': 'Первая страница'})
        self.assertEqual(str(book['tag']['author']), questbook.BOOK_AUTHOR)

    def test_unknown_dependency_fails(self):
        with self.assertRaises(ValueError):
            build(CHAPTER.replace('deps: [start]', 'deps: [missing]'))

    def test_duplicate_key_fails(self):
        with self.assertRaises(ValueError):
            build(CHAPTER.replace('key: next', 'key: start'))


class Validation(unittest.TestCase):
    def files(self, *sources):
        out = build(*sources)
        files = {f'config/ftbquests/quests/chapters/{n}.snbt': snbt.dumps(c).encode() for n, c in out.items()}
        files['config/ftbquests/quests/chapter_groups.snbt'] = b'{chapter_groups: [{id: "842B4DB4DBD349A0", title: "G"}]}'
        return files

    def codes(self, files, registry=None):
        return {e['code'] for e in validate.evaluate(files, registry or {})['errors']}

    def test_reward_that_completes_another_quest(self):
        self.assertIn('reward_completes_task', self.codes(self.files(CHAPTER, OTHER), {'namespaces': {}}))

    def test_clean_chapter(self):
        self.assertEqual(self.codes(self.files(CHAPTER)), set())

    def test_registry_unknown_item(self):
        registry = {'namespaces': {'items': ['minecraft']}, 'items': ['minecraft:book', 'minecraft:diamond']}
        self.assertIn('unknown_items', self.codes(self.files(CHAPTER), registry))

    def test_overlapping_nodes(self):
        self.assertIn('node_overlap', self.codes(self.files(CHAPTER.replace('x: 2.5', 'x: 0.3'))))

    def test_checkmark_with_item_reward(self):
        text = CHAPTER.replace('{type: item, item: minecraft:diamond}', '{type: checkmark}')
        self.assertIn('manual_task_item_reward', self.codes(self.files(text)))


if __name__ == '__main__':
    unittest.main()
