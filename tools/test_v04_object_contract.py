#!/usr/bin/env python3
"""Pinned SYSVOL schema/CLI regression and uniform Object-site contracts (#251)."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml
from v04_object_contract import object_errors, object_sites, format_path
from v04_flat_object_authoring import flatten_document, restore_document, load_catalog, dump_hybrid
from build_v04_canonical_six_stigs import promote, recover
from test_v04_package_consumer import fixture as wrapper
from test_v04_public_cli_smoke import authoring_archives
from validate_native_json_schemas import build_validators, document_errors
from v04_native_bundle_compiler import build_bundle

ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(ROOT / 'schema/v0.4.0/capability-mappings/supported')
TARGET = 'assessment.variables.icacls-path-sysvol-directory-variable.expression.concat[1].regex_capture.value.values.object'


def original():
    return {'assessment': json.loads((ROOT / 'tests/fixtures/v04-proof-expansion/windows-13.json').read_text())['assessment']}


def closed(doc):
    docs = wrapper()
    docs['authoring/demo/assessments/a1.json'] = doc
    docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = doc['assessment']['id']
    return docs


class CanonicalObjectContractTests(unittest.TestCase):
    def test_pinned_nested_registry_rejected_with_exact_public_schema_path(self):
        doc = original()
        before = deepcopy(doc)
        v = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        failures = list(document_errors(v, doc))
        self.assertTrue(failures)
        self.assertIn(TARGET + '.select', [format_path(e.path) for e in failures])
        self.assertEqual(doc, before, 'validation must not normalize invalid current authoring')
        with self.assertRaisesRegex(ValueError, 'icacls-path-sysvol-directory-variable'):
            build_bundle(closed(doc))

    def test_both_public_clis_block_original_and_accept_explicit_migration(self):
        fixed, proof = flatten_document(original(), CATALOG)
        self.assertEqual(restore_document(fixed, proof), original())
        for accepted, doc in ((False, original()), (True, fixed)):
            with self.subTest(accepted=accepted), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                directory = root / 'input'
                directory.mkdir()
                (directory / 'sysvol.assessment.yaml').write_text(yaml.safe_dump(doc))
                proc = subprocess.run([sys.executable, str(ROOT / 'tools/validate_native_json_schemas.py'),
                    str(directory), '--schema-dir', str(ROOT / 'schema/v0.4.0'), '--report', str(root / 'validation.json')],
                    capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0 if accepted else 1, proc.stderr[-1500:])
                report = json.loads((root / 'validation.json').read_text())
                self.assertEqual(report['documents_checked'], 1)
                if not accepted:
                    self.assertIn(TARGET + '.select', json.dumps(report))
                js, ya = authoring_archives(closed(doc), root)
                compiled = subprocess.run([sys.executable, str(ROOT / 'tools/v04_native_bundle_compiler.py'),
                    '--json-archive', str(js), '--yaml-archive', str(ya), '--output-dir', str(root / 'out'),
                    '--report', str(root / 'compiler.json')], capture_output=True, text=True)
                self.assertEqual(compiled.returncode == 0, accepted, compiled.stderr[-1500:])
                if not accepted:
                    self.assertIn(TARGET + '.select', compiled.stderr)
                    self.assertFalse((root / 'out').exists())

    def test_single_visitor_capability_scope_and_exact_inverse_hybrid_json_yaml(self):
        doc = original()
        source = deepcopy(doc)
        fixed, proof = flatten_document(doc, CATALOG)
        sites = [s for s in object_sites(fixed['assessment']) if s.context == 'variable']
        registry = next(s for s in sites if s.capability == 'windows.registry')
        self.assertEqual(format_path(registry.path), TARGET)
        self.assertIsNone(registry.inherited)
        self.assertEqual(registry.node['capability'], 'windows.registry')
        self.assertFalse(list(object_errors(fixed)))
        self.assertEqual(restore_document(fixed, proof), source)
        self.assertEqual(doc, source)
        self.assertEqual(flatten_document(fixed, CATALOG)[0], fixed)
        rendered = dump_hybrid({'object': registry.node})
        self.assertEqual(len(rendered.splitlines()), 1)
        self.assertIn('object: {capability: windows.registry', rendered)
        self.assertEqual(yaml.safe_load(dump_hybrid(fixed)), json.loads(json.dumps(fixed)))
        promoted, _ = promote(source, legacy_review=True)
        recover(promoted, source, legacy_review=True)
        self.assertFalse(list(object_errors(promoted)))
        self.assertEqual(promote(source)[0], source, 'current path is not an implicit Object repair')

    def test_direct_shared_variable_and_set_use_the_same_closed_contract(self):
        obj = {'hive': {'equals': 'local_machine'}, 'key': {'equals': 'SYSTEM'}, 'name': {'equals': 'SysVol'}}
        for context in ('test', 'shared', 'variable', 'set'):
            for mutation in ('valid', 'select', 'collect', 'unknown', 'predicate', 'capability'):
                with self.subTest(context=context, mutation=mutation):
                    node = deepcopy(obj)
                    if context in ('shared', 'variable'):
                        node.update(capability='windows.registry', object_title='Registry fixture')
                    if mutation in ('select', 'collect'):
                        node[mutation] = {'name': node.pop('name')}
                    elif mutation == 'unknown':
                        node['unreviewed'] = True
                    elif mutation == 'predicate':
                        node['key'] = {'equals': 'SYSTEM', 'matches_regex': '.*'}
                    elif mutation == 'capability':
                        node['capability'] = 'imaginary.registry'
                    a = {'specification': {'version': '0.4.0'}, 'tests': {}}
                    if context == 'shared':
                        a['shared_objects'] = {'fixture-object': node}
                    elif context == 'variable':
                        a['variables'] = {'fixture-variable': {'expression': {'values': {'object': node, 'field': 'value'}}}}
                    else:
                        a['tests']['fixture-test'] = {'capability': 'windows.registry', 'object': node if context == 'test' else
                            {'set': {'operator': 'union', 'operands': [{'object': node, 'filters': []}]}}}
                    self.assertEqual(bool(list(object_errors({'assessment': a}))), mutation != 'valid')

    def test_record_literals_and_cmdlet_select_do_not_become_acquisition_sites(self):
        cmdlet = {'capability': 'windows.cmdlet', 'module_name': None, 'module_id': None,
                  'module_version': None, 'verb': 'Get', 'noun': 'Item', 'parameters': None,
                  'select': {'fields': {'object': {'equals': 'a property named object', 'selection_match': 'one_or_more'}}}}
        a = {'specification': {'version': '0.4.0'}, 'shared_objects': {'cmdlet-object': cmdlet},
             'variables': {'literal-variable': {'expression': {'literal': {'datatype': 'record',
                 'value': {'object': {'select': {'never': 'visit'}}}}}}}}
        self.assertEqual(len(list(object_sites(a))), 1)
        self.assertFalse(list(object_errors({'assessment': a})))
        fixed, proof = flatten_document({'assessment': a}, CATALOG)
        self.assertEqual(fixed, {'assessment': a})
        self.assertEqual(proof['edits'], [])

    def test_deep_composition_and_nested_sets_keep_paths_and_scope(self):
        reg = {'capability': 'windows.registry', 'hive': {'equals': 'local_machine'},
               'key': {'equals': 'SYSTEM'}, 'name': {'equals': 'SysVol'}}
        expression = {'values': {'object': reg, 'field': 'value'}}
        for _ in range(30):
            expression = {'concat': [{'literal': 'prefix'}, {'regex_capture': {'pattern': '(.*)', 'value': expression}}]}
        a = {'specification': {'version': '0.4.0'}, 'variables': {'deep-variable': {'expression': expression}}}
        self.assertEqual(len(list(object_sites(a))), 1)
        self.assertFalse(list(object_errors({'assessment': a})))
        reg['select'] = {'name': reg.pop('name')}
        self.assertTrue(list(object_errors({'assessment': a})))

    def test_missing_variable_capability_and_wrong_inherited_capability_rejected(self):
        doc, _ = flatten_document(original(), CATALOG)
        node = next(s.node for s in object_sites(doc['assessment']) if s.capability == 'windows.registry')
        node.pop('capability')
        self.assertTrue(any('explicit capability' in e.message for e in object_errors(doc)))
        doc, _ = flatten_document(original(), CATALOG)
        test = next(iter(doc['assessment']['tests'].values()))
        test['object']['capability'] = 'windows.registry'
        self.assertTrue(any('conflicts' in e.message for e in object_errors(doc)))

    def test_all_existing_function_operand_positions_reach_acquisition_objects(self):
        reg = {'capability': 'windows.registry', 'hive': {'equals': 'local_machine'},
               'key': {'equals': 'SYSTEM'}, 'name': {'equals': 'SysVol'}}
        for op in ('concat', 'unique', 'count', 'escape_regex', 'merge', 'split',
                   'substring', 'regex_capture', 'glob_to_regex', 'arithmetic',
                   'begin', 'end', 'time_difference'):
            with self.subTest(function=op):
                binding = {'values': {'object': deepcopy(reg), 'field': 'value'}}
                if op == 'concat':
                    operand = [binding]
                elif op in ('unique', 'count', 'escape_regex'):
                    operand = binding
                elif op in ('arithmetic', 'time_difference'):
                    operand = {'operands' if op == 'arithmetic' else 'values': [binding]}
                else:
                    operand = {'values' if op == 'merge' else 'value': binding}
                doc = {'assessment': {'specification': {'version': '0.4.0'},
                    'variables': {'fixture-variable': {'expression': {op: operand}}}}}
                sites = list(object_sites(doc['assessment']))
                self.assertEqual(len(sites), 1)
                self.assertFalse(list(object_errors(doc)))
                sites[0].node['collect'] = {'unrecognized': True}
                self.assertTrue(list(object_errors(doc)))


if __name__ == '__main__':
    unittest.main()
