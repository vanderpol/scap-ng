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


if __name__ == "__main__":
    unittest.main()
