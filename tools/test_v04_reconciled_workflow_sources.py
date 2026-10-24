"""Current-schema assertions retained from seven dated workflows (Refs #251).

Pinned original XML -> shared production converter -> current schema/compiler.
Legacy views exist only at independent reverse-exporter test boundaries; they
are never compiler input or published current authoring.
"""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import yaml

from build_v04_canonical_six_stigs import render_authoring
from scap_converter_core import convert
from test_scap_converter_core import legacy_oracle_view
from test_v04_field_requirement_conversion import documents, compile_documents
from v04_canonical_source_ir import decode_and_verify, validate_docs, _schema_validators
from v04_native_bundle_compiler import build_bundle, verify_bundle
from export_v04_oval_constant_family import export as export_family_constant
from export_v04_oval_family_constant_variable import emit as export_family_variable
from export_v04_oval_ios_global_multitest import emit as export_global
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from validate_v04_oval_5123 import check
from test_generate_capability_schema_v04 import materialize, validate

ROOT = Path(__file__).resolve().parents[1]
PIN = 'e3538595c5083b9c34d937a81d319234df9bbfaa'
CASES = (
    ('SCAP_NG_FAMILY_SOURCE_XML', 'independent', 'oval:org.mitre.oval.test:def:95',
     '6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7', 1),
    ('SCAP_NG_IOS_GLOBAL_SOURCE_XML', 'ios', 'oval:navy.navwar.niwcatlantic.scc.ios:def:1',
     '6015ddb9a1540fff61b7d8d6749a2bf6a1d309d823b40f53941e5ce6e488c7ec', 2),
    ('SCAP_NG_IOSXE_GLOBAL_SOURCE_XML', 'iosxe', 'oval:navy.navwar.niwcatlantic.scc.iosxe:def:1',
     'f88a4eea2858c07f76f6b03904cf6ce530a1e6b39bfc547589896dd586b0c87c', 2),
)


class ReconciledSourceAssertions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = []
        for variable, platform, did, checksum, count in CASES:
            # Mandatory CI binds these exact sources; absence must fail, not skip.
            path = Path(os.environ[variable])
            if sha256(path.read_bytes()).hexdigest() != checksum:
                raise ValueError('pinned original source changed: ' + variable)
            native, evidence = convert(path, did, assessment_id=(
                'system-family-assessment' if platform == 'independent' else
                platform + '-global-configuration-assessment'))
            cls.cases.append((path, platform, did, count, native, evidence))
        cls.validators = _schema_validators(ROOT / 'schema/v0.4.0')

    def assert_roundtrip(self, case, native, exporter):
        source, platform, did, _, _, _ = case
        tree, output_id = exporter(legacy_oracle_view(native))
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / 'regenerated.xml'
            tree.write(output, encoding='utf-8', xml_declaration=True)
            xsd = check(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3', output, platform)
            self.assertEqual(xsd['status'], 'PASS', xsd['diagnostics'])
            self.assertTrue(compare(source, output, source_root=did,
                                   regenerated_root=output_id, root_only=True)['equal'])

    def assert_changed(self, case, changed, exporter):
        tree, output_id = exporter(legacy_oracle_view(changed))
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / 'changed.xml'
            tree.write(output, encoding='utf-8', xml_declaration=True)
            self.assertFalse(compare(case[0], output, source_root=case[2],
                                    regenerated_root=output_id, root_only=True)['equal'])

    def test_family_current_schema_variable_cardinalities_and_both_independent_exporters(self):
        case = self.cases[0]
        native, evidence = case[4:]
        validate_docs({'authoring/source/family.json': native}, self.validators)
        a = native['assessment']
        test, = a['tests'].values()
        self.assertEqual(test['capability'], 'independent.family')
        self.assertNotIn('object', test)
        self.assertFalse(validate(materialize('independent.family'), 'test', test))
        self.assertEqual(test['require']['items_found'], 'one_or_more')
        self.assertEqual(test['require']['items_satisfying'], 'one_or_more')
        field = test['require']['fields']['family']
        self.assertEqual(field['value_match'], 'every')
        self.assertEqual(field['values_found'], 'one_or_more')
        self.assertEqual(field['values_matching'], 'every')
        name, variable = next(iter(a['variables'].items()))
        self.assertEqual(len(a['variables']), 1)
        self.assertEqual(variable['kind'], 'constant')
        self.assertEqual(field['matches_regex'], {'variable': name})
        source_var = next(n for n in ET.parse(case[0]).getroot().iter()
                          if n.tag.endswith('}constant_variable'))
        self.assertEqual(source_var.get('id'), 'oval:org.mitre.oval.test:var:403')
        self.assertEqual(variable['expression']['literal'], source_var[0].text)
        self.assertTrue(evidence['independent_family_import_agreement'])
        for exporter in (export_family_constant, export_family_variable):
            self.assert_roundtrip(case, native, exporter)

    def test_family_mutated_literal_var_check_and_test_quantifier_are_detected(self):
        case = self.cases[0]
        for exporter in (export_family_constant, export_family_variable):
            changed = deepcopy(case[4])
            next(iter(changed['assessment']['variables'].values()))['expression']['literal'] = 'changed-family'
            self.assert_changed(case, changed, exporter)
            for target in ('value_match', 'items_satisfying'):
                changed = deepcopy(case[4])
                test = next(iter(changed['assessment']['tests'].values()))
                if target == 'value_match':
                    test['require']['fields']['family'][target] = 'one_or_more'
                else:
                    test['require'][target] = 'every'
                with self.assertRaises(ValueError):
                    exporter(legacy_oracle_view(changed))

    def test_both_global_sources_flat_objects_schema_xsd_and_original_graph(self):
        for case in self.cases[1:]:
            native = case[4]
            validate_docs({'authoring/source/global.json': native}, self.validators)
            self.assertEqual(len(native['assessment']['tests']), 2)
            self.assertIn('and', native['assessment']['evaluate'])
            for test in native['assessment']['tests'].values():
                self.assertEqual(test['require'], {'items_found': 'one_or_more'})
                self.assertNotIn('states', test)
                self.assertNotIn('select', test['object'])
                self.assertNotIn('collect', test['object'])
                self.assertFalse(validate(materialize(test['capability']), 'test', test))
            self.assert_roundtrip(case, native, export_global)

    def test_global_selector_mutations_and_source_quantifier_operation_rejection(self):
        for case in self.cases[1:]:
            changed = deepcopy(case[4])
            test = next(iter(changed['assessment']['tests'].values()))
            op, = test['object']['global_command']
            test['object']['global_command'][op] = 'changed-original-selector'
            self.assert_changed(case, changed, export_global)
            for element, attribute, value in (('_test', 'check', 'only one'),
                                               ('}global_command', 'operation', 'not equal')):
                root = ET.parse(case[0]).getroot()
                node = next(n for n in root.iter() if n.tag.endswith(element))
                node.set(attribute, value)
                with tempfile.TemporaryDirectory() as td:
                    path = Path(td) / 'mutated.xml'
                    path.write_bytes(ET.tostring(root))
                    with self.assertRaises(ValueError):
                        convert(path, case[2])

    def test_all_sources_current_yaml_json_typed_ir_programs_and_bundle(self):
        for case in self.cases:
            native, evidence = case[4:]
            parsed = yaml.safe_load(render_authoring(native, is_yaml=True))
            self.assertEqual(parsed, json.loads(render_authoring(native, is_yaml=False)))
            data, report = compile_documents(documents(parsed))
            self.assertEqual(report['native_source_schema'], 'PASS')
            self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
            decoded = decode_and_verify(json.loads(data))
            self.assertEqual(decoded, documents(parsed))
            raw, _ = build_bundle(decoded)
            result = verify_bundle(raw)
            self.assertEqual((result['documents'], result['programs'], result['tests']), (3, 1, case[3]))
            self.assertFalse(result['scanner_evaluated'])
            self.assertFalse(result['signature_verified'])
            self.assertEqual(evidence['source_sha256'], sha256(case[0].read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
