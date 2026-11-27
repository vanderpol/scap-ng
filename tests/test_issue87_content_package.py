"""Verify stable byte identities for the canonical package and its RI receipt."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from conformance.tools.build_content_fixture import build
from conformance.tools.runner import CONFORMANCE, load

FIXTURE = CONFORMANCE / "content-package"


class ContentPackageCases(unittest.TestCase):
    def test_package_build_preserves_source_members_and_bindings(self):
        expected = load(FIXTURE / "expected.json")
        receipt = load(FIXTURE / "ri-receipt.json")
        sources = load(FIXTURE / "sources.json")
        self.assertEqual(receipt["schema_pin"], expected["schema_pin"])
        self.assertEqual(set(receipt["variants"]), expected["variants"].keys())
        for name, variant in expected["variants"].items():
            observed = receipt["variants"][name]
            self.assertEqual(observed["exit_code"], variant["exit_code"])
            if "reason" in variant:
                self.assertIn(variant["reason"], observed["diagnostic"])

        with TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            manifest = build(first)
            self.assertEqual(build(second), manifest)
            raw = (first / "manifest.json").read_bytes()
            self.assertEqual(raw, (second / "manifest.json").read_bytes())
            self.assertEqual(sha256(raw).hexdigest(), receipt["manifest_sha256"])
            self.assertEqual(manifest["benchmark_id"], expected["benchmark_id"])
            self.assertEqual(manifest["benchmark_version"], expected["benchmark_version"])
            self.assertEqual(receipt["variants"]["accepted"]["benchmark_id"], expected["benchmark_id"])
            records = {row["path"]: row for row in manifest["objects"].values()}
            ids = {"assessment": [], "rule": []}
            self.assertEqual(len(records), len(sources["members"]))
            for member in sources["members"]:
                kind, path = member["kind"], member["path"]
                original = load(CONFORMANCE / member["source"])
                member_bytes = (first / path).read_bytes()
                self.assertEqual(member_bytes, (second / path).read_bytes())
                self.assertEqual(sha256(member_bytes).hexdigest(), records[path]["sha256"])
                self.assertEqual(len(member_bytes), records[path]["size"])
                packaged = load(first / path)
                if kind == "assessment":
                    self.assertEqual(packaged["schema_family_sha256"], sources["assessment_closure_sha256"])
                    packaged = packaged["assessment_document"]
                if kind in ids:
                    ids[kind].append(packaged[kind]["id"])
                if kind == "rule":
                    requirements = packaged[kind].pop("organizational_input_requirements")
                    if packaged[kind]["id"] == "primary-rule":
                        routes = load(first / "assessments/routes.json")["assessment_document"]["assessment"]
                        guard = routes["evaluate"]["if"]["input_provided"]
                        self.assertEqual(requirements, {"standard": [
                            {"input": guard, "required": routes["inputs"][guard]["required"],
                             "uses": [{"kind": "presence", "source_path": "/evaluate/if/input_provided"}]},
                        ]})
                    else:
                        self.assertEqual(requirements, {})
                self.assertEqual(packaged, original)
            self.assertEqual(sorted(ids["assessment"]), expected["assessment_ids"])
            self.assertEqual(sorted(ids["rule"]), expected["rule_ids"])
