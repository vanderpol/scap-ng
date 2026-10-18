#!/usr/bin/env python3
"""#232/#239: adversarial per-Benchmark Rule/Assessment version closure."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_benchmark_choice_version_closure import inspect_edges, main

SPEC = "scap-ng.pre-alpha.assessment"


def pack(two_benchmarks=False, old_benchmark=True):
    def benchmark(ident, version):
        return {"benchmark": {"id": ident, "assessment_specifications": [
            {"id": SPEC, "version": version}]}}
    def rule(ident, automated, manual="ng.shared.manual"):
        return {"rule": {"id": ident,
                         "default_assessment_choice": "automated",
                         "assessment_choices": {
                             "automated": {"assessment": automated},
                             "manual": {"assessment": manual}}}}
    a = {
        "authoring/rhel_9/benchmark.rhel_9.json":
            benchmark("ng.rhel_9", "0.3.0" if old_benchmark else "0.4.0"),
        "authoring/rhel_9/rules/SV-TEST.rule.json":
            rule("SV-TEST", "ng.shared.auto"),
        "authoring/shared/assessments/ng.shared.auto.json": {"assessment": {
            "id": "ng.shared.auto", "mode": "automated",
            "specification": {"id": SPEC, "version": "0.4.0"}}},
        "authoring/shared/assessments/ng.shared.manual.json": {"assessment": {
            "id": "ng.shared.manual", "mode": "manual"}},
    }
    if two_benchmarks:
        a["authoring/win11/benchmark.win11.json"] = benchmark("ng.win11", "0.4.0")
        a["authoring/win11/rules/SV-OTHER.rule.json"] = rule("SV-OTHER", "ng.shared.auto")
    return a


class BenchmarkEdgeGateTests(unittest.TestCase):
    def test_old_benchmark_detected_at_actual_rule_choice(self):
        r = inspect_edges(pack())
        self.assertEqual(r["status"], "BLOCKED_PER_BENCHMARK_SPECIFICATION")
        self.assertEqual(r["incompatible_edge_count"], 1)
        self.assertEqual(r["counts"]["choice_links"], 2)
        self.assertEqual(r["counts"]["manual_choice_links"], 1)
        self.assertEqual(r["incompatible_edge_samples"][0]["rule"], "SV-TEST")
        self.assertEqual(r["incompatible_edge_samples"][0]["choice"], "automated")
        self.assertFalse(r["allowed_to_compile"])

    def test_same_spec_is_necessary_not_compiled(self):
        r = inspect_edges(pack(old_benchmark=False))
        self.assertEqual(r["status"], "EDGE_DECLARATIONS_CONSISTENT_NOT_COMPILED")
        self.assertFalse(r["allowed_to_compile"])

    def test_second_benchmark_version_does_not_waive_first(self):
        r = inspect_edges(pack(two_benchmarks=True))
        self.assertEqual(r["incompatible_edge_count"], 1)
        self.assertEqual(len(r["benchmarks"]), 2)
        self.assertEqual(r["counts"]["choice_links"], 4)
        self.assertEqual(r["counts"]["automated_choice_links"], 2)
        self.assertEqual(r["counts"]["manual_choice_links"], 2)
        self.assertEqual(r["incompatible_edge_samples"][0]["benchmark"], "ng.rhel_9")

    def test_authoring_docs_are_not_mutated(self):
        d = pack()
        before = json.dumps(d, sort_keys=True)
        inspect_edges(d)
        self.assertEqual(json.dumps(d, sort_keys=True), before)

    def test_missing_assessment_fails(self):
        d = pack()
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = "not-present"
        with self.assertRaisesRegex(ValueError, "unresolved Assessment"):
            inspect_edges(d)

    def test_missing_default_fails(self):
        d = pack()
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"][
            "default_assessment_choice"] = "unknown"
        with self.assertRaisesRegex(ValueError, "undeclared default"):
            inspect_edges(d)

    def test_cross_benchmark_private_assessment_rejected(self):
        d = pack(two_benchmarks=True)
        ident = "ng.win11.private"
        d["authoring/win11/assessments/private.json"] = {"assessment": {
            "id": ident, "mode": "automated",
            "specification": {"id": SPEC, "version": "0.4.0"}}}
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = ident
        with self.assertRaisesRegex(ValueError, "cross-Benchmark private"):
            inspect_edges(d)

    def test_shared_benchmark_not_allowed(self):
        d = pack()
        d["authoring/shared/shared-benchmark.json"] = {"benchmark": {
            "id": "ng.shared", "assessment_specifications": [{"id": SPEC, "version": "0.4.0"}]}}
        with self.assertRaisesRegex(ValueError, "shared Benchmark"):
            inspect_edges(d)

    def test_orphan_rule_namespace_rejected(self):
        d = pack()
        d["authoring/unknown/rules/SV-ORPHAN.json"] = {
            "rule": deepcopy(d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"])}
        with self.assertRaisesRegex(ValueError, "no Benchmark in its own"):
            inspect_edges(d)

    def test_duplicate_assessment_id_rejected_even_if_otherwise_valid(self):
        d = pack()
        d["authoring/rhel_9/assessments/duplicate.json"] = deepcopy(
            d["authoring/shared/assessments/ng.shared.auto.json"])
        with self.assertRaisesRegex(ValueError, "duplicate Assessment id"):
            inspect_edges(d)

    def test_manual_alternative_without_automated_spec_stays_explicit(self):
        r = inspect_edges(pack())
        self.assertEqual(r["counts"]["manual_choice_links"], 1)
        self.assertEqual(r["counts"]["automated_default_choices"], 1)
        self.assertNotIn("manual", r["incompatible_edge_samples"][0]["choice"])

    def test_absent_benchmark_declared_spec_fails(self):
        d = pack()
        d["authoring/rhel_9/benchmark.rhel_9.json"]["benchmark"].pop("assessment_specifications")
        with self.assertRaisesRegex(ValueError, "missing declared"):
            inspect_edges(d)

    def test_cli_blocks_and_can_assert_expected_blocker(self):
        with TemporaryDirectory() as folder:
            z = Path(folder)/"source.zip"
            with ZipFile(z, "w") as out:
                for k, v in pack().items():
                    out.writestr(k, json.dumps(v))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--json-archive", str(z)]), 2)
                self.assertEqual(main(["--json-archive", str(z), "--expect-blocked"]), 0)


if __name__ == "__main__":
    unittest.main()
