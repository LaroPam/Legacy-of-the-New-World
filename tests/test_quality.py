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

    def test_shape_mask_without_alpha_is_detected(self):
        import io
        from PIL import Image
        grey, rgba = io.BytesIO(), io.BytesIO()
        Image.new('L', (4, 4), 255).save(grey, 'PNG')
        Image.new('RGBA', (4, 4), (255, 255, 255, 0)).save(rgba, 'PNG')
        shapes = {f'kubejs/assets/ftbquests/textures/shapes/crown/{part}.png': rgba.getvalue()
                  for part in ('shape', 'outline', 'background')}
        theme = {'kubejs/assets/ftbquests/ftb_quests_theme.txt': b'extra_quest_shapes: crown'}
        self.assertNotIn('shape_texture_opaque', self.codes(self.report(extra={**theme, **shapes})))
        shapes['kubejs/assets/ftbquests/textures/shapes/crown/shape.png'] = grey.getvalue()
        self.assertIn('shape_texture_opaque', self.codes(self.report(extra={**theme, **shapes})))

    def test_theme_icon_that_is_not_a_resource_location_is_detected(self):
        theme = b'[*]\ncontainer_slot: hollow_rectangle:#526C8C + color=#24374B\n'
        r = self.report(extra={'kubejs/assets/ftbquests/ftb_quests_theme.txt': theme})
        self.assertIn('theme_icon_invalid', self.codes(r))

    def test_missing_theme_background_is_detected(self):
        theme = b'[*]\nbackground: nasledie:textures/backgrounds/bg_missing.png\n'
        r = self.report(extra={'kubejs/assets/ftbquests/ftb_quests_theme.txt': theme,
                               'kubejs/assets/nasledie/textures/backgrounds/bg_other.png': b''})
        self.assertIn('theme_texture_missing', self.codes(r))

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


class IconNavigationTests(unittest.TestCase):
    def chapter(self, icons):
        return {REF: {'quests': [dict(id=str(i), **({'icon': icon} if icon is not None else {}))
                                for i, icon in enumerate(icons)]}}

    def test_dominant_icon_is_rejected_even_if_inherited_by_completed_chapter(self):
        source = self.chapter(['minecraft:compass'] * 8)
        issues = quality.icon_variety_issues(source)
        self.assertEqual([i['code'] for i in issues], ['dominant_quest_icon'])
        errors, warnings = quality.classify_quality(issues, issues, 'nasledie_defense',
            {'completed_chapters': ['nasledie_defense']})
        self.assertEqual(len(errors), 1)
        self.assertEqual(warnings, [])

    def test_small_thematic_group_and_task_derived_icons_are_allowed(self):
        icons = ['minecraft:compass'] * 3 + [None] * 5
        self.assertEqual(quality.icon_variety_issues(self.chapter(icons)), [])
        self.assertEqual(quality.icon_variety_issues(self.chapter(['minecraft:compass'] * 4)), [])

    def test_stack_count_variants_do_not_hide_dominant_item(self):
        icons = [{'id': 'minecraft:compass', 'Count': i + 1} for i in range(8)]
        issues = quality.icon_variety_issues(self.chapter(icons))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['count'], 8)


class ContentAdditionTests(unittest.TestCase):
    ADDITION = '''{id:"0000000000000010" title:"Expedition" description:["Explore the vault"]
      x:6d y:0d size:1d dependencies:["0000000000000005"]
      tasks:[{id:"0000000000000011" type:"advancement" advancement:"test:treasure"}]
      rewards:[{id:"0000000000000012" type:"xp" xp:200}]}'''

    def scope(self, body=None):
        return {'quest_additions': {'nasledie_defense': [
            {'snbt': body or self.ADDITION, 'reason': 'Continue an expedition with a new action'}]}}

    def report(self, extra=None, source=SOURCE, scope=None):
        import apply_polish
        current = apply_polish.append_quests(source.decode(), [extra or self.ADDITION]).encode()
        return quality.evaluate({REF: current}, {REF: SOURCE}, scope=scope or self.scope())

    def codes(self, report):
        return {e['code'] for e in report['errors']}

    def test_exact_addition_passes_and_reproduces_with_new_design(self):
        import apply_polish
        design = {'chapter': {}, 'quests': {'0000000000000010': {'values': {'title': 'Open the vault'}}}}
        output = apply_polish.render(SOURCE.decode(), design, {}, [self.ADDITION]).encode()
        result = quality.evaluate({REF: output}, {REF: SOURCE}, scope=self.scope())
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['counts']['quests'], 3)
        self.assertFalse(result['summary']['release_ready'])

    def test_addition_cannot_weaken_original_reward_guard(self):
        r = self.report(source=SOURCE.replace(b'xp: 10', b'xp: 11'))
        self.assertIn('mechanics_changed', self.codes(r))

    def test_changed_new_task_or_reward_is_not_an_allowed_addition(self):
        for old, new in [('xp:200', 'xp:999'), ('test:treasure', 'test:unrelated'),
                         ('0000000000000005', '0000000000000002')]:
            with self.subTest(old=old):
                self.assertIn('quest_addition_mismatch', self.codes(self.report(extra=self.ADDITION.replace(old, new))))

    def test_new_quest_cannot_reuse_an_existing_task_id(self):
        invalid = self.ADDITION.replace('0000000000000011', '0000000000000003')
        self.assertIn('quest_addition_reused_id', self.codes(self.report(extra=invalid, scope=self.scope(invalid))))

    def test_old_quest_cannot_be_redeclared_as_an_addition(self):
        invalid = self.ADDITION.replace('0000000000000010', '0000000000000002')
        result = quality.evaluate({REF: SOURCE}, {REF: SOURCE}, scope=self.scope(invalid))
        self.assertIn('quest_addition_reused_id', self.codes(result))

    def test_missing_new_quest_is_detected(self):
        result = quality.evaluate({REF: SOURCE}, {REF: SOURCE}, scope=self.scope())
        self.assertIn('quest_addition_mismatch', self.codes(result))
        self.assertIn('id_inventory_changed', self.codes(result))

    def test_undeclared_added_quest_is_rejected(self):
        import apply_polish
        current = apply_polish.append_quests(SOURCE.decode(), [self.ADDITION]).encode()
        result = quality.evaluate({REF: current}, {REF: SOURCE})
        self.assertIn('quest_addition_mismatch', self.codes(result))

    def test_new_advancement_requires_exact_hash_and_cannot_replace_old_data(self):
        import hashlib
        name = 'kubejs/data/nasledie/advancements/alpha43/treasure.json'
        raw = b'{"criteria":{"loot":{"trigger":"minecraft:player_generates_container_loot","conditions":{"loot_table":"test:treasure"}}}}'
        scope = {'file_additions': {name: {'sha256': hashlib.sha256(raw).hexdigest(), 'reason': 'Specific new loot action'}}}
        before = {REF: SOURCE}
        self.assertEqual(quality.evaluate({**before, name: raw}, before, scope=scope)['errors'], [])
        self.assertIn('file_addition_mismatch', self.codes(quality.evaluate({**before, name: raw+b'\n'}, before, scope=scope)))
        self.assertIn('file_addition_mismatch', self.codes(quality.evaluate(before, before, scope=scope)))
        old = {**before, name: raw}
        self.assertIn('file_addition_mismatch', self.codes(quality.evaluate(old, old, scope=scope)))


class AdvancementConditionTests(unittest.TestCase):
    def duplicates(self, criteria, second='second'):
        parsed = {REF: {'id': '1', 'quests': [
            {'id': '2', 'tasks': [{'id': '3', 'type': 'advancement', 'advancement': 'test:first'}]},
            {'id': '4', 'tasks': [{'id': '5', 'type': 'advancement', 'advancement': 'test:'+second}]},
        ]}}
        for name in ['first', 'second']:
            parsed['kubejs/data/test/advancements/'+name+'.json'] = {'criteria': criteria}
        return quality.duplicate_conditions(parsed)

    def test_separately_granted_impossible_targets_are_distinct(self):
        self.assertEqual(self.duplicates({'done': {'trigger': 'minecraft:impossible'}}), [])

    def test_repeated_impossible_target_still_collides(self):
        self.assertEqual(len(self.duplicates({'done': {'trigger': 'minecraft:impossible'}}, 'first')), 1)

    def test_natural_or_mixed_identical_conditions_still_collide(self):
        natural = {'obtained': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': ['minecraft:clock']}]}}}
        for criteria in [natural, {**natural, 'manual': {'trigger': 'minecraft:impossible'}}]:
            with self.subTest(criteria=criteria):
                self.assertEqual(len(self.duplicates(criteria)), 1)


class ScriptAdditionTests(unittest.TestCase):
    NAME = 'kubejs/server_scripts/nasledie_factory_trials.js'
    RAW = b'ServerEvents.tick(function(event) {});'

    def report(self, current=None, baseline=None, name=None, fields=None):
        import hashlib
        declaration = {'sha256': hashlib.sha256(self.RAW).hexdigest(), 'reason': 'Observed production cycle',
                       'evidence': 'reviews/factory_trial_evidence.json', 'tests': 'tests/factory_trials.test.cjs'}
        declaration.update(fields or {})
        return quality.evaluate(current if current is not None else {REF: SOURCE, self.NAME: self.RAW},
                                baseline if baseline is not None else {REF: SOURCE},
                                scope={'script_additions': {name or self.NAME: declaration}})

    def test_exact_reviewed_script_is_allowed(self):
        self.assertEqual(self.report()['errors'], [])

    def test_missing_changed_or_existing_script_is_rejected(self):
        for current, baseline in [({REF: SOURCE}, None),
                                  ({REF: SOURCE, self.NAME: self.RAW+b'\n'}, None),
                                  ({REF: SOURCE, self.NAME: self.RAW}, {REF: SOURCE, self.NAME: self.RAW})]:
            with self.subTest(current=current, baseline=baseline):
                codes = {e['code'] for e in self.report(current, baseline)['errors']}
                self.assertIn('script_addition_mismatch', codes)

    def test_arbitrary_code_or_missing_review_metadata_is_rejected(self):
        for name, fields in [('kubejs/startup_scripts/unrelated.js', {}),
                             (self.NAME, {'tests': ''}), (self.NAME, {'evidence': ''}), (self.NAME, {'reason': ''})]:
            with self.subTest(name=name, fields=fields):
                self.assertIn('script_addition_mismatch', {e['code'] for e in self.report(name=name, fields=fields)['errors']})

    def test_undeclared_script_is_rejected(self):
        r = quality.evaluate({REF: SOURCE, self.NAME: self.RAW}, {REF: SOURCE})
        self.assertIn('protected_file_changed', {e['code'] for e in r['errors']})


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
