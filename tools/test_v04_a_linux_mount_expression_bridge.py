#!/usr/bin/env python3
"""#238/#232: no-scanner Linux Test -> 0.4-A expression integration fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_prototype_a_linux_mount_scan import SOURCE, GOOD, BAD, OTHER
from research_provider_linux_mounts import (collect_current_linux_mounts,
                                            parse_mountinfo_text)
from v04_a_linux_mount_expression_bridge import bridge, STAGE


class LinuxExpressionBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(SOURCE.read_text(encoding="utf-8"))

    def run_fixture(self, *rows):
        observed = parse_mountinfo_text("\n".join(rows), "mnt:[fixture]")
        return bridge(self.doc, observed, fixture_mode=True)

    def test_good_complete_linux_mount_collection_reaches_true_expression(self):
        result = self.run_fixture(GOOD, OTHER)
        self.assertEqual(result["stage"], STAGE)
        self.assertEqual(result["result"], "true")
        self.assertEqual(result["test_result"]["result"], "true")
        self.assertEqual(result["assessment_expression"]["outcome"], "true")
        self.assertEqual(result["test_result"]["counts"]["selected"], 1)
        self.assertTrue(result["fixture_mode"])
        self.assertFalse(result["scanner_executed"])
        self.assertEqual(result["assessment_expression"]["tests_supplied"], 1)
        self.assertEqual(result["assessment_expression"]["trace"][0]["operation"], "read_test")
        self.assertEqual(len(result["source_assessment_sha256"]), 64)

    def test_noncompliant_mount_remains_false_in_expression(self):
        result = self.run_fixture(BAD, OTHER)
        self.assertEqual((result["result"], result["test_result"]["reason_code"]),
                         ("false", "mount_without_nosuid"))

    def test_no_home_is_false_not_a_vacuous_pass(self):
        result = self.run_fixture(OTHER)
        self.assertEqual(result["result"], "false")
        self.assertEqual(result["test_result"]["reason_code"], "required_mount_missing")

    def test_incomplete_collection_preserves_unknown(self):
        result = self.run_fixture(GOOD, "invalid line")
        self.assertEqual((result["result"], result["test_result"]["reason_code"]),
                         ("unknown", "collection_incomplete"))

    def test_incomplete_with_decisive_failure_stays_false(self):
        result = self.run_fixture(BAD, "invalid line")
        self.assertEqual(result["result"], "false")

    def test_explicit_collection_error_preserves_error(self):
        observed = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        observed["status"] = "error"
        result = bridge(self.doc, observed, fixture_mode=True)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["test_result"]["reason_code"], "collection_error")

    def test_source_mismatch_rejected_by_pinned_compiler(self):
        changed = deepcopy(self.doc)
        changed["assessment"]["evaluate"] = {
            "not": {"test": next(iter(changed["assessment"]["tests"]))}}
        with self.assertRaises(ValueError):
            bridge(changed, parse_mountinfo_text(GOOD, "mnt:[fixture]"))

    def test_missing_observation_field_fails_as_error(self):
        observation = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        del observation["items"][0]["fields"]["mount_options"]
        report = bridge(self.doc, observation, fixture_mode=True)
        self.assertEqual(report["result"], "error")

    def test_live_linux_namespace_only(self):
        if not Path("/proc/self/mountinfo").exists():
            self.skipTest("requires Linux /proc")
        observed = collect_current_linux_mounts()
        report = bridge(self.doc, observed, fixture_mode=False)
        self.assertIn(report["result"], {"true", "false", "unknown", "error"})
        self.assertFalse(report["fixture_mode"])
        self.assertEqual(report["assessment_expression"]["outcome"],
                         report["test_result"]["result"])
        self.assertEqual(report["test_result"]["collector"]["namespace"],
                         observed["namespace"])


if __name__ == "__main__":
    unittest.main()
