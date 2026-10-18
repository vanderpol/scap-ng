"""#238: adversarial tests for the bounded live A Linux mount pilot."""
import copy
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prototype_a_linux_mount_scan import (
    compile_assessment, evaluate, UnsupportedAssessment, main,
)
from research_provider_linux_mounts import collect_current_linux_mounts, parse_mountinfo_text

SOURCE = (Path(__file__).resolve().parents[1]
          / "research/assessment-simplification/compact-authoring-04"
          / "runtime-slice/home-nosuid.assessment.json")
GOOD = "201 101 8:17 / /home rw,nosuid,relatime shared:8 - ext4 /dev/sdb1 rw,data=ordered"
BAD = "202 101 8:18 / /home rw,relatime shared:8 - ext4 /dev/sdb2 rw"
OTHER = "203 101 8:19 / /var rw,nosuid,relatime - ext4 /dev/sdc rw"


class PrototypeALinuxMountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.compiled = compile_assessment(cls.document)

    def outcome(self, *lines):
        return evaluate(self.compiled, parse_mountinfo_text("\n".join(lines), "mnt:[fixture]"))

    def test_one_compliant_mount(self):
        result = self.outcome(GOOD, OTHER)
        self.assertEqual(result["result"], "true")
        self.assertEqual(result["counts"], {"observed": 2, "selected": 1, "violating": 0})
        self.assertEqual(result["evidence"][0]["mount_options"], ["rw", "nosuid", "relatime"])

    def test_one_violating_mount(self):
        result = self.outcome(BAD, OTHER)
        self.assertEqual((result["result"], result["reason_code"]),
                         ("false", "mount_without_nosuid"))

    def test_duplicate_path_kept_separate_and_fails(self):
        result = self.outcome(GOOD, BAD)
        self.assertEqual(result["result"], "false")
        self.assertEqual(result["counts"]["selected"], 2)
        self.assertEqual(result["counts"]["violating"], 1)

    def test_complete_collection_missing_home_fails(self):
        result = self.outcome(OTHER)
        self.assertEqual((result["result"], result["reason_code"]),
                         ("false", "required_mount_missing"))

    def test_incomplete_collection_never_passes(self):
        result = self.outcome(GOOD, "bad record")
        self.assertEqual((result["result"], result["reason_code"]),
                         ("unknown", "collection_incomplete"))

    def test_incomplete_collection_with_decisive_failure(self):
        result = self.outcome(BAD, "bad record")
        self.assertEqual(result["result"], "false")

    def test_explicit_collector_error(self):
        obs = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        obs["status"] = "error"
        result = evaluate(self.compiled, obs)
        self.assertEqual((result["result"], result["reason_code"]),
                         ("error", "collection_error"))

    def test_duplicate_item_identity_is_error(self):
        obs = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        obs["items"].append(copy.deepcopy(obs["items"][0]))
        self.assertEqual(evaluate(self.compiled, obs)["result"], "error")

    def test_missing_required_field_is_error(self):
        obs = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        del obs["items"][0]["fields"]["mount_options"]
        self.assertEqual(evaluate(self.compiled, obs)["result"], "error")

    def test_unknown_quantifier_rejected_not_defaulted(self):
        altered = copy.deepcopy(self.document)
        test = next(iter(altered["assessment"]["tests"].values()))
        test["require"] = "may_be_absent"
        with self.assertRaises(UnsupportedAssessment):
            compile_assessment(altered)

    def test_unknown_state_semantics_rejected(self):
        altered = copy.deepcopy(self.document)
        test = next(iter(altered["assessment"]["tests"].values()))
        test["states"][0]["mount_options"]["require"] = "only_one_exists_and_matches"
        with self.assertRaises(UnsupportedAssessment):
            compile_assessment(altered)

    def test_unexpected_assessment_behavior_rejected(self):
        altered = copy.deepcopy(self.document)
        altered["assessment"]["evaluate"] = {"and": [{"test": self.compiled["test_id"]}]}
        with self.assertRaises(UnsupportedAssessment):
            compile_assessment(altered)

    def test_bad_provider_identity_is_error(self):
        obs = parse_mountinfo_text(GOOD, "mnt:[fixture]")
        obs["provider"] = "fake.mount.provider"
        self.assertEqual(evaluate(self.compiled, obs)["result"], "error")

    def test_cli_reads_assessment_and_offline_fixture(self):
        with TemporaryDirectory() as temp:
            fixture = Path(temp) / "mountinfo"
            fixture.write_text(GOOD + "\n" + OTHER + "\n", encoding="utf-8")
            captured = io.StringIO()
            with redirect_stdout(captured):
                code = main(["--assessment", str(SOURCE),
                             "--fixture-mountinfo", str(fixture)])
            report = json.loads(captured.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(report["result"], "true")
            self.assertTrue(report["fixture_mode"])
            self.assertEqual(report["assessment_id"], self.compiled["assessment_id"])

    def test_current_linux_namespace_live_smoke(self):
        if not Path("/proc/self/mountinfo").exists():
            self.skipTest("Linux /proc not present on this runner")
        observed = collect_current_linux_mounts()
        self.assertEqual(observed["provider"], "linux.mounts")
        self.assertEqual(observed["status"], "complete", observed["diagnostics"])
        result = evaluate(self.compiled, observed)
        self.assertFalse(result["fixture_mode"])
        self.assertIn(result["result"], {"true", "false"})
        self.assertGreater(result["counts"]["observed"], 0)


if __name__ == "__main__":
    unittest.main()
