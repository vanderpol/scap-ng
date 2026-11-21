"""Regression gates for the independent SCAP-NG 0.4.1 conformance corpus."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "conformance"
SCHEMA = ROOT / "schema"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Issue87Conformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read(CONF / "manifest.json")
        cls.inventory = read(CONF / "schema-coverage.json")

    def test_manifest_is_exactly_pinned_to_checked_out_schema(self):
        commit = self.manifest["schema_commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT).returncode, 0)
        paths = sorted((ROOT / "schema").glob("*.json")) + sorted((ROOT / "schema/capability-mappings").rglob("*.json"))
        digest = hashlib.sha256()
        for path in sorted(paths):
            digest.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
            digest.update(path.read_bytes())
        self.assertEqual(self.inventory["schema_family_sha256"], digest.hexdigest())
        self.assertEqual(self.manifest["schema_family_sha256"], self.inventory["schema_family_sha256"])

    def test_inventory_and_vectors_are_exhaustive_for_mappings(self):
        capabilities = {row["capability"] for row in self.inventory["capabilities"]}
        cases = {row["capability"] for row in self.manifest["capabilities"]}
        self.assertEqual(cases, capabilities)
        self.assertEqual(self.inventory["counts"]["capability_mappings"], len(cases))
        required = {"positive", "negative", "boundary", "empty", "permission-denied", "error", "not-applicable"}
        for row in self.manifest["capabilities"]:
            self.assertEqual(set(row["vectors"]), required, row["capability"])
            for kind in ("assessment", "fixture", "expected"):
                path = CONF / row[kind]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"][kind], path)

    def test_core_semantics_keep_false_leaf_visible_and_only_not_negates(self):
        assessment = (CONF / "cases/core/evaluate-not.assessment.yaml").read_text(encoding="utf-8")
        self.assertIn("not:", assessment)
        self.assertNotIn("negate:", assessment)
        expected = read(CONF / "expected/core-evaluate-not.json")
        self.assertEqual(expected["underlying"]["false-test"], "false")
        self.assertEqual(expected["assertions"]["not(false)"], "true")
        self.assertEqual(expected["assertions"]["unknown"], "unknown")
        self.assertEqual(expected["assertions"]["error"], "error")
        self.assertEqual(expected["assertions"]["not_applicable"], "not_applicable")

    def test_offline_schema_runner_and_invalid_negate_gate(self):
        command = [sys.executable, str(CONF / "tools/runner.py"), "validate"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(CONF / "tools/runner.py"), "coverage"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
