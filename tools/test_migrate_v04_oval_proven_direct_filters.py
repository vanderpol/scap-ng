#!/usr/bin/env python3
"""Targeted 0.4.0 source-backed Filter migration rejection/proof fixtures."""
from copy import deepcopy
import unittest

from migrate_v04_oval_proven_direct_filters import (
    STATUS, PENDING, index_provenance, migrate, recover_migration,
)

PATH = "authoring/ms_windows_11/assessments/applicability/bluetooth.json"
TEST = "bluetooth-test"
CAP = "independent.shellcommand"


def original():
    return {"assessment": {"id": "bluetooth-assessment", "mode": "automated",
        "tests": {TEST: {"capability": CAP, "object": {
            "object_title": "Bluetooth source", "set": {
                "operator": "union", "operands": [{
                    "object": {"object_title": "Bluetooth source", "capability": CAP,
                               "collect": {"shell": "powershell", "command": "Get-PnpDevice"}},
                    "filters": [{"include": {"stdout_line": {
                        "case_insensitive_equals": "Bluetooth"}}}],
                }],
            }},
            "require": {"items": "one_or_more"},
        }}}}


def evidence(status=STATUS):
    row = {
        "assessment": "bluetooth-assessment",
        "test_id": TEST, "capability": CAP, "path": PATH,
        "source_title": "Bluetooth source",
        "status": status,
        "source_direct_filter_without_set_confirmed": status == STATUS,
        "source_candidates": [{"id": "oval:obj:101",
                               "source_has_set": status != STATUS,
                               "direct_filter_actions": ["include"]}],
    }
    return {"status": "STRUCTURAL_SOURCE_FILTER_AUDIT_NOT_RUNTIME_PARITY",
            "scanner_semantics_verified": False,
            "source_archive_checksums": {str(i): {"zip_sha256": str(i)} for i in range(6)},
            "entries": [row]}


class ProvenFilterTests(unittest.TestCase):
    def test_source_exact_conversion_and_inverse(self):
        proof = index_provenance(evidence())
        old = original()
        new, counts = migrate(old, PATH, proof)
        self.assertEqual(counts["source_proven_direct_filters"], 1)
        obj = new["assessment"]["tests"][TEST]["object"]
        self.assertNotIn("set", obj)
        self.assertNotIn("capability", obj)
        self.assertEqual(len(obj["filters"]), 1)
        self.assertEqual(old, original(), "Original source input changed")
        self.assertTrue(recover_migration(new, old, PATH, proof))

    def test_unresolved_source_set_is_never_flattened(self):
        proof = index_provenance(evidence(PENDING))
        old = original()
        new, counts = migrate(old, PATH, proof)
        self.assertEqual(new, old)
        self.assertEqual(counts["source_review_required_unchanged"], 1)

    def test_filter_changes_and_wrong_capability_rejected(self):
        proof = index_provenance(evidence())
        old = original()
        new, _ = migrate(old, PATH, proof)
        new["assessment"]["tests"][TEST]["object"]["filters"][0]["include"]["stdout_line"]["case_insensitive_equals"] = "WiFi"
        with self.assertRaisesRegex(ValueError, "not reversible"):
            recover_migration(new, old, PATH, proof)
        wrong = deepcopy(old)
        wrong["assessment"]["tests"][TEST]["object"]["set"]["operands"][0]["object"]["capability"] = "windows.registry"
        with self.assertRaisesRegex(ValueError, "different original Object capability"):
            migrate(wrong, PATH, proof)

    def test_untrusted_or_ambiguous_provenance_fails_closed(self):
        for edit in (
            lambda r: r.update(scanner_semantics_verified=True),
            lambda r: r["source_archive_checksums"].pop("1"),
            lambda r: r["entries"][0]["source_candidates"].append(
                deepcopy(r["entries"][0]["source_candidates"][0])),
            lambda r: r["entries"][0]["source_candidates"][0].update(source_has_set=True),
        ):
            report=evidence()
            edit(report)
            with self.assertRaises(ValueError):
                index_provenance(report)

    def test_pinned_six_source_counts_are_required_when_requested(self):
        with self.assertRaisesRegex(ValueError, "baseline changed"):
            index_provenance(evidence(), assert_six=True)


if __name__ == "__main__":
    unittest.main()
