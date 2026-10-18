#!/usr/bin/env python3
"""#232/#239: deterministic 0.4-A unsigned content graph container regressions."""
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_benchmark_choice_version_closure import pack
from v04_a_deterministic_research_container import (
    create_research_container, verify_research_container, canonical_json,
)


def rewrite(raw, change):
    with ZipFile(io.BytesIO(raw)) as source:
        bodies = {name: source.read(name) for name in source.namelist()}
    change(bodies)
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for name, body in bodies.items():
            archive.writestr(name, body)
    return buffer.getvalue()


class DeterministicResearchContainerTests(unittest.TestCase):
    def setUp(self):
        self.documents = pack()

    def test_verified_output_is_research_not_a_compiled_bundle(self):
        data, manifest = create_research_container(self.documents)
        result = verify_research_container(data)
        self.assertEqual(result["status"], "UNSIGNED_RESEARCH_CONTAINER_VERIFIED_NOT_EXECUTABLE")
        self.assertEqual(result["member_count"], 4)
        self.assertEqual(result["choice_links"], 2)
        self.assertFalse(result["signatures_verified"])
        self.assertFalse(result["native_compiler_completed"])
        self.assertFalse(manifest["authoring_spec_approval"])
        self.assertFalse(manifest["migration_policy_approval"])

    def test_reordered_source_documents_yield_same_zip_bytes(self):
        a, _ = create_research_container(self.documents)
        reordered = dict(reversed(list(self.documents.items())))
        b, _ = create_research_container(reordered)
        self.assertEqual(a, b)

    def test_json_and_yaml_source_extension_yield_same_zip_bytes(self):
        a, _ = create_research_container(self.documents)
        renamed = {path.replace(".json", ".yaml"): data
                   for path, data in self.documents.items()}
        b, _ = create_research_container(renamed)
        self.assertEqual(a, b)

    def test_only_benchmark_version_differs(self):
        d = deepcopy(self.documents)
        raw, manifest = create_research_container(d)
        self.assertEqual(d, self.documents)
        with ZipFile(io.BytesIO(raw)) as z:
            payloads = {
                (record["kind"], record["id"]): json.loads(z.read(record["member"]))
                for record in manifest["documents"]
            }
        benchmark = payloads[("benchmark", "ng.rhel_9")]["benchmark"]
        self.assertEqual(benchmark["assessment_specifications"], [
            {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}])
        self.assertEqual(benchmark["id"], "ng.rhel_9")
        assessment = payloads[("assessment", "ng.shared.manual")]["assessment"]
        self.assertEqual(assessment["mode"], "manual")
        self.assertNotIn("specification", assessment)

    def test_changed_assessment_state_changes_archive_hash(self):
        docs = deepcopy(self.documents)
        first, _ = create_research_container(docs)
        docs["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]["tests"] = {
            "a": {"require": "only_one_exists"}}
        second, _ = create_research_container(docs)
        self.assertNotEqual(sha256(first).hexdigest(), sha256(second).hexdigest())

    def test_rejects_tampered_member_content(self):
        source, manifest = create_research_container(self.documents)
        def tamper(items):
            member = next(r["member"] for r in manifest["documents"] if r["kind"] == "assessment")
            items[member] = b'{"assessment":{"id":"attacker"}}'
        corrupted = rewrite(source, tamper)
        with self.assertRaisesRegex(ValueError, "digest or size mismatch"):
            verify_research_container(corrupted)

    def test_rejects_missing_member(self):
        source, manifest = create_research_container(self.documents)
        target = manifest["documents"][0]["member"]
        def tamper(items):
            del items[target]
        with self.assertRaisesRegex(ValueError, "missing manifest-named"):
            verify_research_container(rewrite(source, tamper))

    def test_rejects_forged_approval_flag(self):
        source, _ = create_research_container(self.documents)
        def tamper(items):
            manifest = json.loads(items["manifest.json"])
            manifest["authoring_spec_approval"] = True
            items["manifest.json"] = canonical_json(manifest)
        with self.assertRaisesRegex(ValueError, "not an unapproved"):
            verify_research_container(rewrite(source, tamper))

    def test_rejects_additional_untracked_member(self):
        source, _ = create_research_container(self.documents)
        def tamper(items):
            items["extra/hidden.json"] = b"{}"
        with self.assertRaisesRegex(ValueError, "unexpected extra"):
            verify_research_container(rewrite(source, tamper))

    def test_rejects_forged_graph_fingerprint(self):
        source, _ = create_research_container(self.documents)
        def tamper(items):
            manifest = json.loads(items["manifest.json"])
            manifest["staged_graph_sha256"] = "f" * 64
            items["manifest.json"] = canonical_json(manifest)
        with self.assertRaisesRegex(ValueError, "staged graph mismatch"):
            verify_research_container(rewrite(source, tamper))

    def test_rejects_source_with_unresolved_assessment_reference(self):
        d = deepcopy(self.documents)
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = "does-not-exist"
        with self.assertRaisesRegex(ValueError, "unresolved Assessment"):
            create_research_container(d)

    def test_no_source_level_spec_upgrades_without_explicit_stage(self):
        _, manifest = create_research_container(self.documents)
        self.assertNotEqual(manifest["source_graph_sha256"], manifest["staged_graph_sha256"])
        self.assertIn("Benchmark specification declaration policy", manifest["required_owner_decisions"])


if __name__ == "__main__":
    unittest.main()
