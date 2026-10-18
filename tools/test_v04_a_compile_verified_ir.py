#!/usr/bin/env python3
"""#240: one-command dual-format 0.4-A research compiler acceptance tests."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_end_to_end_base_authoring import input_documents
from v04_a_compile_verified_ir import compile_pair


def archive(path, docs, fmt):
    with zipfile.ZipFile(path, "w") as out:
        for name, doc in docs.items():
            member = name[:-5] + "." + fmt
            raw = (json.dumps(doc, sort_keys=True) if fmt == "json"
                   else yaml.safe_dump(doc, sort_keys=True))
            out.writestr(member, raw)


class SingleCommandCompilerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.json = Path(self.temp.name) / "j.zip"
        self.yaml = Path(self.temp.name) / "y.zip"
        self.docs = input_documents()

    def pair(self):
        archive(self.json, self.docs, "json")
        archive(self.yaml, self.docs, "yaml")
        return compile_pair(self.json, self.yaml, validate_base=False)

    def test_independent_inputs_compile_same_research_ir(self):
        ir_bytes, unsigned_zip, result = self.pair()
        self.assertEqual(result["status"], "DUAL_FORMAT_VERIFIED_IR_RESEARCH_NOT_EXECUTABLE")
        self.assertEqual(result["source_documents"], 4)
        self.assertEqual(result["automated_assessments"], 1)
        self.assertEqual(result["automated_tests"], 1)
        self.assertEqual(result["rule_choice_links"], 2)
        self.assertEqual(result["yaml_json_base_byte_parity"], "PASS")
        self.assertEqual(result["yaml_json_ir_byte_parity"], "PASS")
        self.assertEqual(result["research_ir_schema"], "PASS")
        self.assertEqual(result["base_schema"], "NOT_CHECKED_RESEARCH_FIXTURE")
        self.assertFalse(result["native_executable_compiler_completed"])
        self.assertFalse(result["version_policy_approved"])
        self.assertFalse(result["scanner_executed"])
        self.assertFalse(result["signed_bundle"])
        self.assertEqual(result["ir_sha256"], sha256(ir_bytes).hexdigest())
        self.assertEqual(result["unsigned_base_archive_sha256"], sha256(unsigned_zip).hexdigest())

    def test_document_order_does_not_change_ir_bytes(self):
        before, _, report1 = self.pair()
        self.docs = dict(reversed(list(self.docs.items())))
        after, _, report2 = self.pair()
        self.assertEqual(before, after)
        self.assertEqual(report1, report2)

    def test_independent_yaml_divergence_fails_closed(self):
        archive(self.json, self.docs, "json")
        modified = deepcopy(self.docs)
        auto = next(doc["assessment"] for doc in modified.values()
                    if doc.get("assessment", {}).get("mode") == "automated")
        tests = next(iter(auto["tests"].values()))
        tests["states"][0]["and"][0]["a"]["equals"] = 999
        archive(self.yaml, modified, "yaml")
        with self.assertRaisesRegex(ValueError, "base research packages differ"):
            compile_pair(self.json, self.yaml, validate_base=False)

    def test_dangling_rule_choice_in_one_format_rejected(self):
        archive(self.json, self.docs, "json")
        altered = deepcopy(self.docs)
        rule = next(doc["rule"] for doc in altered.values() if "rule" in doc)
        rule["assessment_choices"]["automated"]["assessment"] = "missing"
        archive(self.yaml, altered, "yaml")
        with self.assertRaisesRegex(ValueError, "unresolved"):
            compile_pair(self.json, self.yaml, validate_base=False)

    def test_missing_explicit_test_requirement_fails_closed(self):
        altered = deepcopy(self.docs)
        auto = next(doc["assessment"] for doc in altered.values()
                    if doc.get("assessment", {}).get("mode") == "automated")
        next(iter(auto["tests"].values())).pop("collected_items_require")
        archive(self.json, altered, "json")
        archive(self.yaml, altered, "yaml")
        with self.assertRaisesRegex(ValueError, "mixed or missing"):
            compile_pair(self.json, self.yaml, validate_base=False)

    def test_json_and_yaml_paths_parsed_independently(self):
        archive(self.json, self.docs, "json")
        archive(self.yaml, self.docs, "yaml")
        with zipfile.ZipFile(self.yaml, "a") as out:
            out.writestr("authoring/invalid.yaml", "assessment: {id: a, id: b}")
        with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
            compile_pair(self.json, self.yaml, validate_base=False)


if __name__ == "__main__":
    unittest.main()
