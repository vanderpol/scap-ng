"""Focused conversion, stability and independent-oracle gates for six cases."""
from pathlib import Path
import copy
import hashlib
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import yaml

from convert_board_pilot_v02 import (ROOT, PACKAGE, PLAN, convert_case, generated_files,
                                     dump, execution_form)
from test_board_samples_v02 import run_case
from assessment_expression import load_assessments


class BoardConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text(encoding='utf-8'))
        cls.manifest = json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'))
        cls.sources = load_assessments(PACKAGE/'content')

    def test_committed_outputs_are_actual_existing_converter_output(self):
        self.assertEqual(len(self.plan['cases']), 6)
        self.assertEqual({c['name'] for c in self.plan['cases']}, {s['name'] for s in self.manifest['samples']})
        for case in self.plan['cases']:
            with self.subTest(case=case['name']):
                for relative, output in generated_files(case).items():
                    self.assertEqual((PACKAGE/relative).read_bytes(), output.encode('utf-8'), relative)

    def test_both_forms_obey_independent_source_oracles(self):
        for sample in self.manifest['samples']:
            mechanical = yaml.safe_load((PACKAGE/sample['mechanical']).read_text(encoding='utf-8'))
            native = {'assessment': self.sources[sample['assessment_id']]}
            self.assertEqual(execution_form(mechanical), execution_form(native))
            sources = {**self.sources, sample['assessment_id']:mechanical['assessment']}
            cases = json.loads((PACKAGE/sample['expected']).read_text(encoding='utf-8'))['cases']
            for case in cases:
                with self.subTest(sample=sample['name'], case=case['id']):
                    for inputs in (sources, self.sources):
                        result, model = run_case(inputs, sample['name'], case)
                        self.assertEqual(result['outcome'], case['expected']['outcome'])
                        self.assertEqual(model.test_results, case['expected']['test_outcomes'])
                        if 'record_outcomes' in case['expected']:
                            self.assertEqual([r['outcome'] for r in model.record_results], case['expected']['record_outcomes'])

    def test_conversion_is_byte_deterministic_across_two_runs(self):
        with tempfile.TemporaryDirectory(prefix='board-stability-') as temporary:
            directories = [Path(temporary)/'first-conversion', Path(temporary)/'second-conversion']
            for seed, directory in zip(('11', '97'), directories):
                process = subprocess.run([sys.executable, str(ROOT/'tools/convert_board_pilot_v02.py'),
                                          '--output', str(directory)], cwd=ROOT, capture_output=True, text=True,
                                         env={**os.environ, 'PYTHONHASHSEED':seed, 'PYTHONDONTWRITEBYTECODE':'1'})
                self.assertEqual(process.returncode, 0, process.stdout+process.stderr)
            files = [sorted(p.relative_to(directory).as_posix() for p in directory.rglob('*.yaml')) for directory in directories]
            self.assertEqual(len(files[0]), 12)
            self.assertEqual(files[0], files[1])
            for relative in files[0]:
                self.assertEqual((directories[0]/relative).read_bytes(), (directories[1]/relative).read_bytes())

    def test_unrelated_source_and_node_order_do_not_rename_content(self):
        for case in self.plan['cases']:
            original = ET.parse(PACKAGE/case['source_extract']).getroot()
            reordered = copy.deepcopy(original)
            # Reverse object/state/variable declarations without changing the
            # Definition's executable criteria order.
            for section in reordered:
                if section.tag.rsplit('}', 1)[-1] in ('objects', 'states', 'variables', 'tests'):
                    section[:] = list(reversed(list(section)))
            objects = next(n for n in reordered if n.tag.rsplit('}',1)[-1] == 'objects')
            unused = copy.deepcopy(objects[0])
            unused.set('id', 'oval:org.scapng.board.unused:obj:901')
            # Same comment/capability deliberately challenges name collisions;
            # the extra Object is unreachable and must not affect this case.
            objects.append(unused)
            with self.subTest(case=case['name']):
                before = convert_case(case, original)
                after = convert_case(case, reordered)
                self.assertEqual(tuple(map(dump, before)), tuple(map(dump, after)))

    def test_source_object_selection_and_reference_contracts(self):
        # These assertions follow the selected source entities, not collected
        # output. The synthetic model intentionally does not execute selectors.
        def equality(value):
            return dict(value=value, operation='equal', datatype='string')
        for sample in self.manifest['samples']:
            source = ET.parse(PACKAGE/sample['source_extract']).getroot()
            nodes = {n.get('id'): n for n in source.iter() if n.get('id')}
            bindings = json.loads((PACKAGE/sample['provenance']).read_text(encoding='utf-8'))['native_bindings']
            native = self.sources[sample['assessment_id']]
            for identity, node in nodes.items():
                kind = node.tag.rsplit('}', 1)[-1]
                if kind.endswith('_test'):
                    test = native['tests'][bindings[identity].split('/')[1]]
                    for child in node:
                        original = child.get('object_ref')
                        if original:
                            if bindings[original].startswith('omitted:'):
                                self.assertNotIn('object', test)
                            else:
                                self.assertEqual(test['object'], bindings[original].split('/')[1])
                    original_states = [n.get('state_ref') for n in node if n.get('state_ref')]
                    self.assertEqual(test.get('states', []), [bindings[i].split('/')[1] for i in original_states])
                elif kind in ('file_object', 'symlink_object'):
                    obj = native['objects'][bindings[identity].split('/')[1]]
                    entities = {n.tag.rsplit('}',1)[-1]:n for n in node}
                    if 'filepath' in entities:
                        self.assertEqual(obj['select'], {'full_path':equality(entities['filepath'].text)})
                        if kind=='file_object':
                            self.assertEqual(obj['filesystem'], 'any')
                    elif 'path' in entities:
                        self.assertEqual(obj['select'], {'directory':equality(entities['path'].text), 'name':None})
                        self.assertEqual(entities['behaviors'].get('recurse_direction'), 'none')
                        self.assertEqual(obj['filesystem'], 'local')
                        self.assertNotIn('recurse', obj)
                elif kind == 'registry_object':
                    entities = {n.tag.rsplit('}',1)[-1]:n.text for n in node}
                    obj = native['objects'][bindings[identity].split('/')[1]]
                    self.assertEqual(entities['hive'], 'HKEY_LOCAL_MACHINE')
                    self.assertEqual(obj['select'], {'hive':'local_machine', 'key':equality(entities['key']), 'name':equality(entities['name'])})
                elif kind == 'wmi57_object':
                    entities = {n.tag.rsplit('}',1)[-1]:n.text for n in node}
                    obj = native['objects'][bindings[identity].split('/')[1]]
                    self.assertEqual(obj['collect'], {'namespace':entities['namespace'], 'query':entities['wql']})
        directory = self.sources['board.directory-filter']
        self.assertEqual(directory['objects']['filtered-support-directory-object']['set'],
                         {'operator':'union', 'operands':[{'object':'support-directory-object',
                          'filters':[{'action':'exclude','state':'excluded-directory-state'}]}]})

    def test_provenance_preserves_exact_source_ids_and_native_names(self):
        for sample in self.manifest['samples']:
            provenance = json.loads((PACKAGE/sample['provenance']).read_text(encoding='utf-8'))
            source = ET.parse(PACKAGE/sample['source_extract']).getroot()
            source_ids = {n.get('id') for n in source.iter() if n.get('id')}
            self.assertEqual(source_ids, set(provenance['native_bindings']))
            self.assertEqual(provenance['revision'], self.plan['source_revision'])
            self.assertEqual(provenance['converter_revision'], self.plan['converter_baseline'])
            self.assertEqual(provenance['conversion_adapter_sha256'], self.plan['conversion_adapter_sha256'])
            self.assertEqual(provenance['mapping_components'], self.plan['mapping_components'])
            self.assertTrue(provenance['mechanically_converted'])
            self.assertFalse(provenance['manually_corrected'])
            self.assertEqual(provenance['human_review'], 'pending-review')
            for identity, binding in provenance['native_bindings'].items():
                if binding.startswith(('assessment/', 'omitted:')):
                    continue
                section, name = binding.split('/')
                self.assertIn(name, self.sources[sample['assessment_id']][section], identity)
            for field in ('assessment', 'expected', 'mechanical'):
                self.assertEqual(hashlib.sha256((PACKAGE/sample[field]).read_bytes()).hexdigest(), sample[field+'_sha256'])

    def test_uncommented_source_state_naming_reproducer(self):
        from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
        from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
        from scap_upconvert_v003.native_capability_mapping import apply_ready_capability_mappings
        path = ROOT/'tests/focused-regressions/board-pilot/symlink-name-source.xml'
        source = ET.parse(path).getroot()
        lowered, error = lower_definition(source, 'oval:navy.navwar.niwcatlantic.scc.unix.test:def:1',
                                           'board.symlink-naming-reproducer', collection_graph=True)
        self.assertIsNone(error)
        generated = apply_ready_capability_mappings(align_assessment_vocabulary(lowered),
                                                    ROOT/'schema/v0.2.0/capability-mappings/supported')
        from lxml import etree
        schema = etree.XMLSchema(etree.parse(str(ROOT/'third_party/scap-1.4-schemas/omni-schema.xsd')))
        schema.assertValid(etree.parse(str(path)))
        provenance = json.loads(path.with_suffix('.provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), provenance['extract_sha256'])
        self.assertIn('state-no-comment', generated['assessment']['states'])
        self.assertEqual(generated['assessment']['states']['state-no-comment']['state']['field'], 'canonical_path')
        case = next(c for c in self.plan['cases'] if c['name']=='symlink-resolution')
        mechanical, _ = convert_case(case)
        self.assertIn('canonical-target-state', mechanical['assessment']['states'])
        self.assertNotIn('state-no-comment', mechanical['assessment']['states'])

    def test_names_are_meaningful_and_match_reviewed_source_keyed_plan(self):
        forbidden = re.compile(r'^(?:[a-z]|(?:test|object|obj|state|variable|var|case)[-_]?\d+|[0-9a-f]{32,})$', re.I)
        for case in self.plan['cases']:
            for relative, text in generated_files(case).items():
                document = yaml.safe_load(text)['assessment']
                self.assertEqual(document['id'], 'board.'+case['name'])
                planned = set(case['native_bindings'].values())
                actual = {section+'/'+name for section in ('objects','states','variables','tests') for name in document.get(section,{})}
                self.assertEqual(actual, planned)
                for section in ('objects','states','variables','tests'):
                    for name in document.get(section,{}):
                        self.assertIsNone(forbidden.fullmatch(name), name)
                        self.assertIn('-', name)
                for component in Path(relative).parts:
                    self.assertGreater(len(component), 1)
                    self.assertIsNone(forbidden.fullmatch(component), relative)


if __name__ == '__main__':
    unittest.main()
