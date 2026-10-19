"""Mutation tests: changes that must never pass a presentation-only review."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('quality', Path(__file__).resolve().parents[1] / 'tools/quality.py')
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)
REF = quality.CHAPTER_ROOT + 'nasledie_defense.snbt'
OTHER = quality.CHAPTER_ROOT + 'other.snbt'
SOURCE = b'''{
 id: "0000000000000001"
 quests: [
  { id: "0000000000000002" title: "First" description: ["Explore"] x: 0d y: 0d size: 1d
    tasks: [{id: "0000000000000003" type: "item" item: "minecraft:diamond" count: 1L consume_items: false}]
    rewards: [{id: "0000000000000004" type: "xp" xp: 10}] }
  { id: "0000000000000005" title: "Second" description: ["Return"] x: 3d y: 0d size: 1d
    dependencies: ["0000000000000002"]
    tasks: [{id: "0000000000000006" type: "checkmark"}] rewards: [] }
 ]
}'''


class PreservationTests(unittest.TestCase):
    def report(self, source=SOURCE, extra=None):
        before = {REF: SOURCE, **(extra or {})}
        after = {**before, REF: source}
        return quality.evaluate(after, before)

    def codes(self, report):
        return {e['code'] for e in report['errors']}

    def test_cosmetic_changes_pass_without_claiming_gameplay(self):
        r = self.report(SOURCE.replace(b'First', b'New title').replace(b'x: 3d', b'x: 2.5d'))
        self.assertEqual(r['errors'], [])
        self.assertIn('gameplay_unverified', {e['code'] for e in r['unknown']})

    def test_reward_amount_change_is_blocked(self):
        self.assertIn('mechanics_changed', self.codes(self.report(SOURCE.replace(b'xp: 10', b'xp: 11'))))

    def test_task_target_change_is_blocked(self):
        self.assertIn('protected_quest_field', self.codes(self.report(SOURCE.replace(b'minecraft:diamond', b'minecraft:emerald'))))

    def test_task_id_replacement_is_blocked(self):
        self.assertIn('id_inventory_changed', self.codes(self.report(SOURCE.replace(b'0000000000000003', b'0000000000000009'))))

    def test_dependency_deletion_is_blocked(self):
        self.assertIn('mechanics_changed', self.codes(self.report(SOURCE.replace(b'dependencies: ["0000000000000002"]', b'dependencies: []'))))

    def test_numeric_type_change_is_blocked(self):
        self.assertIn('mechanics_changed', self.codes(self.report(SOURCE.replace(b'count: 1L', b'count: 1'))))

    def test_other_chapter_presentation_is_protected(self):
        before = {REF: SOURCE, OTHER: b'{id:"0000000000000011" quests:[] title:"Other"}'}
        after = {**before, OTHER: before[OTHER].replace(b'Other', b'Changed')}
        self.assertIn('protected_file_changed', self.codes(quality.evaluate(after, before)))

    def test_advancement_condition_change_is_protected(self):
        name = 'kubejs/data/test/advancements/a.json'
        before = {REF: SOURCE, name: b'{"criteria":{"a":{"trigger":"minecraft:tick"}}}'}
        after = {**before, name: b'{"criteria":{"a":{"trigger":"minecraft:impossible"}}}'}
        self.assertIn('protected_file_changed', self.codes(quality.evaluate(after, before)))

    def test_new_prose_leak_is_blocked(self):
        self.assertIn('technical_prose', self.codes(self.report(SOURCE.replace(b'Explore', b'Use minecraft:diamond'))))

    def test_overlap_is_blocked(self):
        self.assertIn('node_overlap', self.codes(self.report(SOURCE.replace(b'x: 3d', b'x: 0.2d'))))

    def test_cycle_detected_even_without_changed_baseline(self):
        source = SOURCE.replace(b'title: "First"', b'dependencies:["0000000000000005"] title:"First"')
        self.assertIn('dependency_cycle', self.codes(quality.evaluate({REF:source}, {REF:source})))

    def test_missing_shape_resource_is_detected(self):
        r = self.report(extra={'kubejs/assets/ftbquests/ftb_quests_theme.txt': b'extra_quest_shapes: crown'})
        self.assertIn('shape_texture_missing', self.codes(r))

    def test_duplicate_json_keys_are_rejected(self):
        r = self.report(extra={'kubejs/data/test/advancements/a.json': b'{"criteria":{},"criteria":{}}'})
        self.assertIn('parse', self.codes(r))


class GeometryTests(unittest.TestCase):
    def test_intersection_not_just_exact_center(self):
        self.assertAlmostEqual(quality.distance_to_segment((2, .2), (0, 0), (4, 0)), .2)
        body = {REF:{'quests':[
            {'id':'a','x':0,'y':0,'size':1},
            {'id':'b','x':4,'y':0,'size':1,'dependencies':['a']},
            {'id':'c','x':2,'y':.2,'size':1},
        ]}}
        problems, _ = quality.geometry(body)
        self.assertIn('edge_through_node', {p['code'] for p in problems})

    def test_crossing_and_collinear_overlap(self):
        self.assertEqual(quality.segment_crossing((0,0),(4,4),(0,4),(4,0)), 'crossing')
        self.assertEqual(quality.segment_crossing((0,0),(4,0),(2,0),(5,0)), 'collinear_overlap')
        self.assertIsNone(quality.segment_crossing((0,0),(2,0),(2,0),(3,1)))


if __name__ == '__main__':
    unittest.main()
