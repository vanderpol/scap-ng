"""Regression gates for the isolated OVAL 6.0 ESX Issue #86 design."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "proposed/issue86-esx-oval6"


class Issue86EsxProposed(unittest.TestCase):
    def test_proposal_does_not_change_active_041_contract(self):
        manifest = json.loads((ROOT / "conformance/manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], "0.4.1")
        self.assertNotIn("proposed/issue86-esx-oval6", manifest.get("schema_inventory", ""))
        pins = json.loads((DESIGN / "source-pins.json").read_text())
        self.assertEqual(pins["oval_6_0"]["status"], "pinned")
        self.assertIsNone(pins["oval_6_0_1"]["commit"])

    def test_source_derived_inventory_and_crosswalk_are_exhaustive(self):
        inventory = json.loads((DESIGN / "schema-inventory.json").read_text())
        crosswalk = json.loads((DESIGN / "capability-crosswalk.json").read_text())
        self.assertEqual(inventory["status"], "proposed-0.5.0")
        self.assertEqual(inventory["source"]["release_tag"], "v6.0")
        self.assertEqual(inventory["counts"]["test_families"], 20)
        self.assertEqual(inventory["counts"]["object_elements"], 20)
        self.assertEqual(inventory["counts"]["state_elements"], 20)
        self.assertEqual(inventory["counts"]["item_elements"], 20)
        self.assertEqual(inventory["counts"]["enumerations"], 19)
        self.assertEqual(len(crosswalk["families"]), 20)
        self.assertEqual({row["capability"] for row in crosswalk["families"]}, {f"esx.{row['family']}" for row in inventory["families"]})
        for filename, digest in inventory["source"]["schema_files_sha256"].items():
            self.assertEqual(hashlib.sha256((DESIGN / "source" / filename).read_bytes()).hexdigest(), digest)

    def test_proposed_assessments_preserve_object_before_require(self):
        for path in (DESIGN / "assessments").glob("*.yaml"):
            doc = yaml.safe_load(path.read_text())
            self.assertEqual(doc["assessment"]["specification"]["version"], "0.5.0")
            for test in doc["assessment"]["tests"].values():
                keys = list(test)
                self.assertLess(keys.index("object"), keys.index("require"), path)
                self.assertTrue(test["capability"].startswith("esx."))

    def test_deterministic_fixture_negative_variants_preserve_selectors(self):
        for fixture_path in (DESIGN / "fixtures").glob("*.json"):
            fixture = json.loads(fixture_path.read_text())
            expected = json.loads((DESIGN / "expected" / fixture_path.name).read_text())
            positive = fixture["variants"]["positive"]["items"]
            negative = fixture["variants"]["negative"]["items"]
            self.assertNotEqual(positive, negative)
            self.assertNotEqual(expected["variants"]["positive"]["assessment_outcome"], expected["variants"]["negative"]["assessment_outcome"])
            contract = fixture["semantic_contract"]
            for selector in contract["selector_fields"]:
                self.assertEqual(positive[0]["fields"][selector], negative[0]["fields"][selector])
            self.assertNotEqual(positive[0]["fields"][contract["negative_field"]], negative[0]["fields"][contract["negative_field"]])
            self.assertEqual(fixture["clock"]["locale"], "C")

    def test_isolated_validator_passes(self):
        result = subprocess.run([sys.executable, str(DESIGN / "tools/validate.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
