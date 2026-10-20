"""Mutation tests: changes that must never pass a presentation-only review."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
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

    def test_multi_chapter_scope_still_protects_rewards(self):
        second = SOURCE.replace(b'000000000000000', b'000000000000001')
        before = {REF: SOURCE, OTHER: second}
        scope = {'presentation_chapters': ['nasledie_defense', 'other']}
        after = {**before, OTHER: second.replace(b'First', b'Reviewed')}
        self.assertEqual(quality.evaluate(after, before, scope=scope)['errors'], [])
        after[OTHER] = after[OTHER].replace(b'xp: 10', b'xp: 11')
        self.assertIn('mechanics_changed', self.codes(quality.evaluate(after, before, scope=scope)))

    def test_exact_approved_file_fix_does_not_allow_further_change(self):
        import hashlib
        name = 'kubejs/data/test/advancements/a.json'
        old = b'{"criteria":{"a":{"trigger":"minecraft:impossible"}}}'
        new = b'{"criteria":{"a":{"trigger":"minecraft:tick"}}}'
        before, after = {REF: SOURCE, name: old}, {REF: SOURCE, name: new}
        scope = {'file_fixes': {name: {'before_sha256': hashlib.sha256(old).hexdigest(),
                 'after_sha256': hashlib.sha256(new).hexdigest(), 'reason': 'Approved exact fix'}}}
        self.assertEqual(quality.evaluate(after, before, scope=scope)['errors'], [])
        after[name] = new + b'\n'
        self.assertIn('protected_file_changed', self.codes(quality.evaluate(after, before, scope=scope)))

    def test_completed_chapter_cannot_retain_technical_prose(self):
        source = SOURCE.replace(b'Explore', b'Use minecraft:diamond')
        scope = {'completed_chapters': ['nasledie_defense']}
        self.assertIn('technical_prose', self.codes(quality.evaluate({REF:source}, {REF:source}, scope=scope)))

    def test_reviewed_dependency_change_is_exact_and_still_checks_cycles(self):
        scope = {'quest_fixes': {'0000000000000005': {'dependencies': {
            'before':['0000000000000002'], 'after':[], 'reason':'Independent optional route'}}}}
        new = SOURCE.replace(b'dependencies: ["0000000000000002"]', b'dependencies: []')
        self.assertEqual(quality.evaluate({REF:new}, {REF:SOURCE}, scope=scope)['errors'], [])
        cycle = SOURCE.replace(b'dependencies: ["0000000000000002"]', b'dependencies: ["0000000000000005"]')
        self.assertIn('approved_fix_mismatch', self.codes(quality.evaluate({REF:cycle}, {REF:SOURCE}, scope=scope)))
        scope['quest_fixes']['0000000000000005']['dependencies']['after'] = ['0000000000000005']
        self.assertIn('dependency_cycle', self.codes(quality.evaluate({REF:cycle}, {REF:SOURCE}, scope=scope)))

    def test_dependency_approval_cannot_exempt_reward_changes(self):
        scope = {'quest_fixes': {'0000000000000002': {'rewards': {
            'before':[], 'after':[], 'reason':'Invalid attempt to exempt rewards'}}}}
        new = SOURCE.replace(b'xp: 10', b'xp: 11')
        codes = self.codes(quality.evaluate({REF:new}, {REF:SOURCE}, scope=scope))
        self.assertIn('approved_fix_mismatch', codes)
        self.assertIn('mechanics_changed', codes)

    def test_add_dependency_to_original_root_preserves_absent_field(self):
        import apply_polish
        # Reverse this tiny route: remove the old edge, then attach the old root.
        fixes = {
            '0000000000000005': {'dependencies': {'before': ['0000000000000002'], 'after': [], 'reason': 'New route start'}},
            '0000000000000002': {'dependencies': {'before': None, 'after': ['0000000000000005'], 'reason': 'Join existing expedition'}},
        }
        design = {'chapter': {}, 'quests': {}}
        result = apply_polish.render(SOURCE.decode(), design, fixes).encode()
        scope = {'quest_fixes': fixes}
        self.assertEqual(quality.evaluate({REF: result}, {REF: SOURCE}, scope=scope)['errors'], [])
        altered = result.replace(b'xp: 10', b'xp: 11')
        self.assertIn('mechanics_changed', self.codes(quality.evaluate({REF: altered}, {REF: SOURCE}, scope=scope)))

    def test_advancement_condition_change_is_protected(self):
        name = 'kubejs/data/test/advancements/a.json'
        before = {REF: SOURCE, name: b'{"criteria":{"a":{"trigger":"minecraft:tick"}}}'}
        after = {**before, name: b'{"criteria":{"a":{"trigger":"minecraft:impossible"}}}'}
        self.assertIn('protected_file_changed', self.codes(quality.evaluate(after, before)))

    def test_new_prose_leak_is_blocked(self):
        self.assertIn('technical_prose', self.codes(self.report(SOURCE.replace(b'Explore', b'Use minecraft:diamond'))))

    def test_overlap_is_blocked(self):
        self.assertIn('node_overlap', self.codes(self.report(SOURCE.replace(b'x: 3d', b'x: 0.2d'))))

    def test_new_icon_needs_exact_evidence(self):
        bad = SOURCE.replace(b'title: "First"', b'title: "First" icon: "invented:thing"')
        self.assertIn('new_icon_unverified', self.codes(self.report(bad)))

    def test_model_name_alone_does_not_validate_registration(self):
        current = SOURCE.replace(b'title: "First"', b'title: "First" icon: "invented:thing"')
        evidence = {'items':{'invented:thing':{'model':'assets/invented/models/item/thing.json'}}}
        report = quality.evaluate({REF:current}, {REF:SOURCE}, icon_evidence=evidence)
        self.assertIn('new_icon_unverified', self.codes(report))

    def test_cycle_detected_even_without_changed_baseline(self):
        source = SOURCE.replace(b'title: "First"', b'dependencies:["0000000000000005"] title:"First"')
        self.assertIn('dependency_cycle', self.codes(quality.evaluate({REF:source}, {REF:source})))

    def test_missing_shape_resource_is_detected(self):
        r = self.report(extra={'kubejs/assets/ftbquests/ftb_quests_theme.txt': b'extra_quest_shapes: crown'})
        self.assertIn('shape_texture_missing', self.codes(r))

    def test_duplicate_json_keys_are_rejected(self):
        r = self.report(extra={'kubejs/data/test/advancements/a.json': b'{"criteria":{},"criteria":{}}'})
        self.assertIn('parse', self.codes(r))

    def test_original_gameplay_defect_cannot_be_called_release_ready(self):
        path = 'kubejs/data/test/advancements/a.json'
        files = {REF:SOURCE, path:b'{"criteria":{"a":{"trigger":"minecraft:player_killed_entity","conditions":{"entity":{"type":"test:missing"}}}}}'}
        evidence = {'namespace':'test','entities':['test:real'],'source':'fixture exact registry','source_sha256':'a'*64}
        report = quality.evaluate(files, files, entity_evidence=evidence)
        self.assertEqual(len(report['gameplay_blockers']), 1)
        self.assertFalse(report['summary']['release_ready'])
        self.assertEqual(report['errors'], [])
        self.assertIn('unregistered_entity_predicate', {i['code'] for i in report['warnings']})


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
