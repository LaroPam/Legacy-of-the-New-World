import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import curves


def chapter(*quests):
    data = {'quests': [dict(q, _chapter='c') for q in quests]}
    return data, {q['_id']: data['quests'][i] for i, q in enumerate(quests)}


def dep(ref, chapter):
    return ref


class CurveTests(unittest.TestCase):
    def test_curve_through_another_quest_is_found(self):
        data, every = chapter({'_id': 'A', 'x': 0, 'y': 0}, {'_id': 'B', 'x': 2, 'y': 0},
                              {'_id': 'C', 'x': 4, 'y': 0, 'deps': ['A']})
        self.assertEqual(curves.crossings('c', data, dep, every), [('A', 'C', 'B')])

    def test_branch_enters_along_its_row(self):
        # B sits right above A and its row continues to the right: the curve must arrive moving right, not up.
        data, every = chapter({'_id': 'A', 'x': 0, 'y': 0}, {'_id': 'B', 'x': 0, 'y': -3, 'deps': ['A']},
                              {'_id': 'C', 'x': 3, 'y': -3, 'deps': ['B']})
        _, paths = curves.curves('c', data, dep, every)
        (x0, y0), (x1, y1) = paths[('A', 'B')][-2:]
        self.assertGreater(x1 - x0, abs(y1 - y0))

    def test_completed_overlay_waits_for_its_prerequisite(self):
        data, every = chapter({'_id': 'A', 'x': 0, 'y': 0}, {'_id': 'B', 'x': 3, 'y': 0, 'deps': ['A']})
        colours = {'dependency_line_uncompleted_color': '#112233', 'dependency_line_completed_color': '#445566'}
        entries, files = curves.chapter_images('c', data, dep, every, colours, 1.05)
        self.assertEqual([e.get('dependency') for e in entries], [None, 'A'])
        self.assertEqual([e['color'] for e in entries], [0x112233, 0x445566])
        self.assertEqual(len(files), 4)  # two PNGs with their .mcmeta


if __name__ == '__main__':
    unittest.main()
