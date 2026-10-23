import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import quest_frames


def chapter(*quests, links=()):
    data = {'chapter': {'default_quest_shape': 'step'}, 'quests': [dict(q, _chapter='c') for q in quests],
            'links': list(links)}
    return data, {q['_id']: q for q in data['quests']}


def dep(ref, chapter):
    return ref


class FrameTests(unittest.TestCase):
    def test_open_quest_frame_is_always_bright(self):
        data, every = chapter({'_id': 'A', 'x': 1, 'y': 2, 'shape': 'boss'})
        entries = quest_frames.frame_images('c', data, dep, every, {'c': data})
        self.assertEqual([(e['image'], e.get('dependency')) for e in entries],
                         [('nasledie:textures/frames/boss.png', None)])

    def test_locked_frame_brightens_after_the_deepest_prerequisite(self):
        # C needs A and B; B comes after A, so it is the one likely done last.
        data, every = chapter({'_id': 'A'}, {'_id': 'B', 'deps': ['A']}, {'_id': 'C', 'deps': ['A', 'B']})
        entries = [e for e in quest_frames.frame_images('c', data, dep, every, {'c': data}) if e['x'] == 0][-2:]
        self.assertEqual([(e['image'], e['order'], e.get('dependency')) for e in entries],
                         [('nasledie:textures/frames/step_dim.png', 0, None),
                          ('nasledie:textures/frames/step.png', 1, 'B')])

    def test_link_uses_its_own_place_and_shape(self):
        data, every = chapter({'_id': 'A'}, links=[{'quest': 'A', 'x': 5, 'y': 6, 'shape': 'home'}])
        entries = quest_frames.frame_images('c', data, dep, every, {'c': data})
        self.assertIn(('nasledie:textures/frames/home.png', 5.0, 6.0), [(e['image'], e['x'], e['y']) for e in entries])


if __name__ == '__main__':
    unittest.main()
