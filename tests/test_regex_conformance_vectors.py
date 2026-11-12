"""Phase 1 integrity checks for the proposed Issue #62 regex vector pack.

These tests validate provenance and vector shape only. They deliberately do not
invoke a regex engine or claim evaluator/scanner conformance.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "docs/regex/conformance-vectors.v1.json"


class RegexConformanceVectorIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(VECTORS.read_text(encoding="utf-8"))
        cls.vectors = cls.pack["vectors"]
        cls.by_id = {vector["id"]: vector for vector in cls.vectors}

    def test_pack_is_versioned_and_proposal_only(self):
        self.assertEqual(self.pack["format"], "scap-ng-regex-conformance-vectors/1")
        self.assertEqual(self.pack["profile_id"], "scap-ng-pcre2-oval-compatible/0.1")
        self.assertEqual(self.pack["status"], "owner-review-proposal")
        self.assertFalse(self.pack["normative"])
        self.assertEqual(len(self.by_id), len(self.vectors))
        self.assertIn("owner_decision", self.pack["result_statuses"])

    def test_evidence_register_covers_oval_and_pcre2_claims(self):
        evidence = {item["id"]: item for item in self.pack["evidence"]}
        self.assertEqual(len(evidence), len(self.pack["evidence"]))
        self.assertIn("oval-regex-policy", evidence)
        self.assertIn("oval-5.12.3-capture-xsd", evidence)
        self.assertIn("oval-5.12.3-text-behaviors", evidence)
        self.assertIn("pcre2-resource-and-unicode-policy", evidence)
        self.assertIn("pcre2-wasm-vector-smoke", evidence)
        self.assertIn("pcre2-10.49-release-and-ucd", evidence)
        self.assertIn("pcre2-wasm-wrapper-error-and-utf-policy", evidence)
        self.assertEqual(evidence["pcre2-10.49-release-and-ucd"]["unicode_version"], "17.0.0")
        self.assertEqual(evidence["oval-5.12.3-capture-xsd"]["sha256"],
                         "06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc")

    def test_vectors_have_engine_neutral_shape(self):
        allowed_operations = {"matches_regex", "regex_capture"}
        for vector in self.vectors:
            with self.subTest(vector=vector["id"]):
                self.assertIn(vector["operation"], allowed_operations)
                self.assertIsInstance(vector["pattern"], str)
                self.assertIn("flags", vector)
                self.assertIsInstance(vector["provenance"], dict)
                self.assertIn("cases", vector)
                self.assertGreater(len(vector["cases"]), 0)
                for case in vector["cases"]:
                    self.assertIn(case["status"], self.pack["result_statuses"])
                    if case["status"] in {"compile_error", "unsupported_feature", "invalid_utf8", "engine_unavailable", "input_limit", "resource_limit", "cancelled"}:
                        self.assertNotEqual(case.get("must_not_report"), None)

    def test_canonical_examples_are_used_without_rewriting_them(self):
        linux = (ROOT / "examples/linux-home-nosuid.assessment.yaml").read_text(encoding="utf-8")
        windows = (ROOT / "examples/windows-server-2025-sysvol-permissions.assessment.yaml").read_text(encoding="utf-8")
        self.assertIn(r"mount_point: {matches_regex: '.*\/home'}", linux)
        self.assertIn(r"pattern: '(^[a-zA-Z]:\\.+)\\sysvol'", windows)
        self.assertEqual(windows.count("- '(?i)"), 9)
        self.assertEqual(self.by_id["native-linux-home-unanchored-search"]["provenance"]["path"],
                         "examples/linux-home-nosuid.assessment.yaml")
        self.assertEqual(self.by_id["native-windows-regex-capture-path"]["provenance"]["path"],
                         "examples/windows-server-2025-sysvol-permissions.assessment.yaml")

    def test_required_phase_one_categories_are_present(self):
        ids = set(self.by_id)
        self.assertIn("oval-negative-lookahead-comment-exclusion", ids)
        self.assertIn("oval-positive-lookahead-presence", ids)
        self.assertIn("oval-single-digit-numbered-backreference", ids)
        self.assertIn("native-windows-inline-case-insensitive", ids)
        self.assertIn("oval-behavior-flags-to-effective-options", ids)
        self.assertIn("unicode-literal-no-normalization", ids)
        self.assertIn("unicode-ucp-word-class-policy", ids)
        self.assertIn("crlf-multiline-anchor-policy", ids)
        self.assertIn("named-and-numbered-captures", ids)
        self.assertIn("invalid-pattern", ids)
        self.assertIn("editor-pathological-match-limit", ids)
        self.assertIn("editor-worker-cancellation", ids)
        self.assertIn("empty-participating-versus-unmatched-capture", ids)
        self.assertIn("engine-unavailable-is-not-nonmatch", ids)


    def test_evidence_resolves_capture_value_rules_but_not_wire_status(self):
        repeated = self.by_id["oval-repeated-capture-last-participation"]
        self.assertEqual(repeated["compatibility_class"], "oval-evidence-backed")
        self.assertEqual(repeated["cases"][0]["captures"], ["ipp"])
        self.assertEqual(self.by_id["native-windows-inline-case-insensitive"]["compatibility_class"],
                         "source-preserved-pcre2-hold")
        self.assertEqual(self.by_id["absolute-and-line-anchors"]["compatibility_class"],
                         "pcre2-extension-hold")
        optional = self.by_id["optional-unmatched-versus-empty-capture"]
        self.assertEqual(optional["cases"][0]["captures"], [""])
        self.assertEqual(self.by_id["empty-participating-versus-unmatched-capture"]["cases"][0]["captures"], [""])

    def test_error_contract_never_coerces_diagnostics_to_nonmatch(self):
        contract = self.pack["error_contract"]
        self.assertIn("engine_unavailable", contract["diagnostic_statuses"])
        self.assertIn("nonmatch", contract["successful_statuses"])
        unavailable = self.by_id["engine-unavailable-is-not-nonmatch"]["cases"][0]
        self.assertEqual(unavailable["must_not_report"], "match_or_nonmatch")

    def test_resource_vectors_are_controls_not_matches(self):
        for vector_id in ("editor-input-limit", "editor-pathological-match-limit", "editor-worker-cancellation"):
            vector = self.by_id[vector_id]
            with self.subTest(vector=vector_id):
                self.assertIn("limits", vector)
                self.assertTrue(any(case.get("must_not_report") == "match" for case in vector["cases"]))
                self.assertNotIn("match", {case["status"] for case in vector["cases"]})

    def test_no_vector_claims_runtime_qualification(self):
        for vector in self.vectors:
            self.assertNotEqual(vector.get("qualification"), "qualified")
            self.assertNotEqual(vector.get("status"), "qualified")


if __name__ == "__main__":
    unittest.main()
