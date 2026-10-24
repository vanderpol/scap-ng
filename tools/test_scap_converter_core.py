#!/usr/bin/env python3
"""0.3 shared lowering -> native 0.4 converter integration, positive/negative."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator
from build_v04_canonical_six_stigs import promote
from v04_canonical_source_ir import validate_docs, _schema_validators

from scap_converter_core import convert, project_v003_to_v04
from test_audit_v04_original_oval_forward import (
    OD, registry_source, shell_source,
)
from test_export_v04_shellcommand_pilot import native as shell_expected
from test_export_v04_registry_pilot import fixture as registry_expected
from compare_v04_fresh_oval_import import compare
from export_v04_oval_registry_pilot import emit as emit_registry
from export_v04_oval_shellcommand_pilot import emit as emit_shell
from v04_native_bundle_compiler import compile_test_instruction


SCHEMA = json.loads((Path(__file__).resolve().parents[1] /
                     "schema/v0.4.0/assessment-language.schema.json").read_text())


def legacy_oracle_view(native):
    """Test-only inverse for retained independent OVAL exporters.

    This is never compiler input or published authoring. Every pair is explicit;
    missing counts fail. Source all_exist cannot be reconstructed from this view.
    """
    from research_04_one_grammar_proof import CODES
    from v04_field_requirement import validate_test
    out = deepcopy(native)
    found = {'none': 'none', 'exactly_one': 'one', 'one_or_more': 'one_or_more',
             'every': 'all', 'may_be_absent': 'optional'}
    matching = {'none': 'none', 'exactly_one': 'one', 'one_or_more': 'one_or_more', 'every': 'all'}
    def predicate(p):
        p = deepcopy(p)
        pair = (found[p.pop('values_found')], matching[p.pop('values_matching')])
        p['require'] = CODES[pair]
        if 'value_match' in p: p['value_match'] = matching[p['value_match']]
        return p
    def condition(c):
        if 'fields' in c:
            parts = [{name: predicate(p)} for name, p in c['fields'].items()]
            return parts[0] if len(parts) == 1 else {'and': parts}
        op = next(k for k in ('and', 'or', 'one', 'xor') if k in c)
        return {op: [condition(child) for child in c[op]]}
    for test in out['assessment']['tests'].values():
        validate_test(test)
        req = test['require']
        if set(req) == {'items_found'}:
            test['require'] = {'items': req['items_found']}
        else:
            test['states'] = [condition(req)]
            test['require'] = CODES[(found[req['items_found']], matching[req['items_satisfying']])]
    return out


def fixture_path(directory, name, data):
    path = directory / name
    path.write_bytes(data)
    return path


class SharedConverterIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def checked(self, xml, definition, expected, opcode):
        path = fixture_path(self.directory, "input.xml", xml)
        native, evidence = convert(path, definition)
        self.assertEqual(compare(native, promote(expected, legacy_review=True)[0])["status"],
                         "TRUE_FRESH_OVAL_IMPORT_MATCHES_CANONICAL_040_TEST")
        validate_docs({'authoring/core/a.json': native}, _schema_validators(
            Path(__file__).resolve().parents[1] / 'schema/v0.4.0'))
        ident, test = next(iter(native["assessment"]["tests"].items()))
        self.assertEqual(compile_test_instruction(ident, test)["opcode"], opcode)
        self.assertEqual(evidence["shared_semantic_ir"], "0.1-prototype")
        self.assertTrue(evidence["v003_source_lowering_reused"])
        self.assertTrue(evidence["independent_leaf_import_agreement"])
        self.assertFalse(evidence["full_oval_coverage"])
        self.assertFalse(evidence["scanner_parity"])
        self.assertNotIn("collect", test["object"])
        self.assertNotIn("select", test["object"])
        return native

    def test_shell_real_oval_filter_through_mature_lowering_and_current_compiler(self):
        native = self.checked(shell_source(), "oval:a:def:1", shell_expected(),
                              "CHECK_COLLECTION_PRESENCE")
        self.assertEqual(len(emit_shell(shell_expected())[0].getroot().findall(
            ".//{" + OD + "}filter")), 1)

    def test_registry_source_exact_uncommon_quantifier_kept(self):
        native = self.checked(registry_source(), "oval:b:def:1", registry_expected(),
                              "CHECK_ITEM_CONDITION")
        self.assertEqual(native["assessment"]["class"], "compliance")
        self.assertTrue(any(node.tag.endswith("}registry_state")
                            for node in emit_registry(registry_expected())[0].getroot().iter()))

    def test_errors_for_unimplemented_semantics_do_not_emit_partial_native(self):
        mutants = (
            (shell_source(), "oval:a:def:1", "exclude Filter",
             lambda root: next(n for n in root.iter()
                               if n.tag == "{" + OD + "}filter").set("action", "exclude")),
            (shell_source(), "oval:a:def:1", "negated criterion",
             lambda root: next(n for n in root.iter()
                               if n.tag == "{" + OD + "}criterion").set("negate", "true")),
            (shell_source(), "oval:a:def:1", "non-AND check",
             lambda root: next(n for n in root.iter()
                               if n.tag.endswith("}shellcommand_test")).set("check", "only one")),
            (shell_source(), "oval:a:def:1", "missing Test reference",
             lambda root: next(n for n in root.iter()
                               if n.tag == "{" + OD + "}criterion").set("test_ref", "oval:missing:tst:0")),
            (registry_source(), "oval:b:def:1", "unsupported registry quantifier",
             lambda root: next(n for n in root.iter()
                               if n.tag.endswith("}registry_test")).set("check", "none satisfy")),
            (registry_source(), "oval:b:def:1", "deprecated definition",
             lambda root: next(n for n in root.iter()
                               if n.tag == "{" + OD + "}definition").set("deprecated", "true")),
        )
        for source, definition, label, mutate in mutants:
            with self.subTest(label=label):
                root = ET.fromstring(source)
                mutate(root)
                path = fixture_path(self.directory, "mutant.xml", ET.tostring(root))
                with self.assertRaises(ValueError):
                    convert(path, definition)

    def test_semantic_differential_rejects_mature_lowering_regression(self):
        from scap_converter_core import postprocess_automated_assessment

        def corrupted_lowering(*args, **kwargs):
            aligned, report = postprocess_automated_assessment(*args, **kwargs)
            aligned = deepcopy(aligned)
            obj = next(iter(aligned["assessment"]["objects"].values()))
            obj["set"]["operands"][0]["object"]["collect"]["command"] = "Get-PnpDevice -class camera"
            return aligned, report

        path = fixture_path(self.directory, "input.xml", shell_source())
        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted_lowering):
            with self.assertRaisesRegex(ValueError, "differs"):
                convert(path, "oval:a:def:1")

    def test_cli_writes_native_and_separate_nonconformance_evidence(self):
        src = fixture_path(self.directory, "source.xml", registry_source())
        output = self.directory / "output.json"
        report = self.directory / "proof.json"
        completed = subprocess.run([
            sys.executable, str(Path(__file__).with_name("scap_converter_core.py")),
            "--source-xml", str(src), "--definition-id", "oval:b:def:1",
            "--output", str(output), "--evidence", str(report),
        ], capture_output=True, text=True, check=True)
        self.assertIn("TWO_LEAF_LOCKSTEP", completed.stdout)
        self.assertEqual(json.loads(report.read_text())["definition_id"], "oval:b:def:1")
        self.assertEqual(compare(json.loads(output.read_text()), promote(registry_expected(), legacy_review=True)[0])
                         ["capability"], "windows.registry")


class EnterpriseRegistryStateTests(unittest.TestCase):
    """Pinned NIWC Test 25325400; source AST comparison is not scanner parity."""
    definition = 'oval:mil.disa.stig.defs:def:253254'
    source_test = 'oval:mil.disa.stig.win:tst:25325400'
    windows = OD + '#windows'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = Path(__file__).resolve().parents[1] / (
            'research/assessment-simplification/evidence/ms_windows_11/SV-253254/source-oval.xml')
        self.root = ET.parse(self.source).getroot()

    def converted(self, root=None):
        path = self.directory / 'source.xml'
        ET.ElementTree(self.root if root is None else root).write(path, encoding='utf-8')
        native, evidence = convert(path, self.definition)
        validate_docs({'authoring/enterprise/a.json': native}, _schema_validators(
            Path(__file__).resolve().parents[1] / 'schema/v0.4.0'))
        return path, native

    def source_semantics(self, path, native):
        """Independent narrow reverse oracle, built solely from generated 0.4.

        Compare effective OVAL Test/Object/State semantics, including defaults,
        rather than source IDs or metadata. No original XML subtrees are copied.
        """
        from scap_ng_roundtrip_v003.compare_oval_semantics import Model
        _, test = next(iter(native['assessment']['tests'].items()))
        req = test['require']
        outer = next(k for k in ('and', 'or') if k in req)
        out = ET.Element('{' + OD + '}oval_definitions')
        tests = ET.SubElement(out, '{' + OD + '}tests')
        ot = ET.SubElement(tests, '{' + self.windows + '}registry_test',
                           id='rebuilt-test', check={'every': 'all', 'one_or_more': 'at least one'}[
                               req['items_satisfying']],
                           check_existence='at_least_one_exists', state_operator=outer.upper())
        ET.SubElement(ot, '{' + self.windows + '}object', object_ref='rebuilt-object')
        objects = ET.SubElement(out, '{' + OD + '}objects')
        obj = ET.SubElement(objects, '{' + self.windows + '}registry_object', id='rebuilt-object')
        for field in ('hive', 'key', 'name'):
            value = test['object'][field]
            if field == 'hive':
                value = 'HKEY_LOCAL_MACHINE' if value == 'local_machine' else value
            else:
                value = value['equals']
            ET.SubElement(obj, '{' + self.windows + '}' + field, datatype='string').text = value
        states = ET.SubElement(out, '{' + OD + '}states')
        for index, branch in enumerate(req[outer]):
            sid = 'rebuilt-state-' + str(index)
            ET.SubElement(ot, '{' + self.windows + '}state', state_ref=sid)
            inner = next((k for k in ('and', 'or') if k in branch), None)
            state = ET.SubElement(states, '{' + self.windows + '}registry_state',
                                  id=sid, operator=inner.upper() if inner else 'AND')
            for term in branch[inner] if inner else [branch]:
                for field, predicate in term['fields'].items():
                    value = predicate['equals']
                    if field == 'type':
                        self.assertEqual(value, 'string')
                        value = 'reg_sz'
                    ET.SubElement(state, '{' + self.windows + '}' + field,
                                  datatype=predicate['datatype']).text = value
        rebuilt = self.directory / 'rebuilt.xml'
        ET.ElementTree(out).write(rebuilt, encoding='utf-8')
        self.assertEqual(Model(path).test(self.source_test), Model(rebuilt).test('rebuilt-test'))

    def test_original_and_default_and_explicit_state_operators_preserve_source_semantics(self):
        for operator in ('OR', 'AND', None):
            for field_operator in ('AND', 'OR'):
                with self.subTest(state_operator=operator, field_operator=field_operator):
                    root = deepcopy(self.root)
                    test = root.find('.//{' + self.windows + '}registry_test')
                    if operator is None:
                        test.attrib.pop('state_operator')
                    else:
                        test.set('state_operator', operator)
                    for state in root.findall('.//{' + self.windows + '}registry_state'):
                        state.set('operator', field_operator)
                    path, native = self.converted(root)
                    self.source_semantics(path, native)
                    _, generated = next(iter(native['assessment']['tests'].items()))
                    self.assertIsInstance(generated['object'], dict)
                    self.assertFalse({'states', 'states_match', 'state_fields_require'} & set(generated))

    def test_unsupported_source_semantics_fail_closed(self):
        mutations = {
            'state XOR': lambda r: r.find('.//{' + self.windows + '}registry_test').set('state_operator', 'XOR'),
            'field ONE': lambda r: r.find('.//{' + self.windows + '}registry_state').set('operator', 'ONE'),
            'all_exist': lambda r: r.find('.//{' + self.windows + '}registry_test').set('check_existence', 'all_exist'),
            'entity quantifier': lambda r: r.find('.//{' + self.windows + '}value').set('entity_check', 'at least one'),
            'dynamic value': lambda r: r.find('.//{' + self.windows + '}value').set('var_ref', 'oval:missing:var:1'),
            'unsupported scalar datatype': lambda r: r.find('.//{' + self.windows + '}value').set('datatype', 'int'),
            'negated criterion': lambda r: r.find('.//{' + OD + '}criterion').set('negate', 'true'),
        }
        for label, mutate in mutations.items():
            with self.subTest(mutation=label), self.assertRaises(ValueError):
                root = deepcopy(self.root)
                mutate(root)
                self.converted(root)

    def test_mature_lowering_corruption_is_rejected_against_original_states(self):
        from scap_converter_core import postprocess_automated_assessment
        mutations = {
            'operand': lambda a: next(iter(a['states'].values()))['state']['all'][1].update(value='Education'),
            'Test operator': lambda a: next(iter(a['tests'].values())).update(states_match='all'),
            'field operator': lambda a: next(iter(a['states'].values()))['state'].update(
                any=next(iter(a['states'].values()))['state'].pop('all')),
            'hive': lambda a: next(iter(a['objects'].values()))['select'].update(hive='users'),
        }
        for label, mutate in mutations.items():
            def corrupt(*args, **kwargs):
                native, report = postprocess_automated_assessment(*args, **kwargs)
                native = deepcopy(native)
                mutate(native['assessment'])
                return native, report
            with self.subTest(mutation=label), patch(
                    'scap_converter_core.postprocess_automated_assessment', side_effect=corrupt):
                with self.assertRaisesRegex(ValueError, 'differs|drift'):
                    self.converted()

    def test_semantic_oracle_rejects_changed_grouping_and_operands(self):
        path, native = self.converted()
        for change in ('outer AND', 'inner OR', 'different value'):
            bad = deepcopy(native)
            req = next(iter(bad['assessment']['tests'].values()))['require']
            if change == 'outer AND':
                req['and'] = req.pop('or')
            elif change == 'inner OR':
                req['or'][0]['or'] = req['or'][0].pop('and')
            else:
                req['or'][0]['and'][1]['fields']['value']['equals'] = 'Education'
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.source_semantics(path, bad)

    def test_production_cli_and_yaml_projection_preserve_source(self):
        import yaml
        from build_v04_canonical_six_stigs import render_authoring
        output, report = self.directory / 'enterprise.json', self.directory / 'proof.json'
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('scap_converter_core.py')),
            '--source-xml', str(self.source), '--definition-id', self.definition,
            '--output', str(output), '--evidence', str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        emitted = json.loads(output.read_text())
        native = yaml.safe_load(render_authoring(emitted, is_yaml=True))
        self.assertEqual(native, emitted)
        _, test = next(iter(native['assessment']['tests'].items()))
        self.assertIsInstance(test['object'], dict)
        self.assertIn('or', test['require'])
        self.source_semantics(self.source, native)


if __name__ == "__main__":
    unittest.main()
