"""Check separate source and native qualification for the experimental ESXi vectors."""
from collections import Counter
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load, validator

STIG = CONFORMANCE / "experimental/esxi/stig"


class EsxiStigCases(unittest.TestCase):
    def test_official_stig_rule_and_oval_family_dispositions_are_complete(self):
        source = load(STIG / "source.json")
        coverage = load(STIG / "coverage.json")
        census = load(CONFORMANCE / "oval-source-coverage.json")
        self.assertEqual(coverage["source"], source)
        self.assertEqual(coverage["oval_6_pin"], census["pins"]["oval_6_0"])
        rules = coverage["rules"]
        self.assertEqual(len(rules), source["rule_count"])
        self.assertEqual(coverage["dispositions"], Counter(row["disposition"] for row in rules.values()))
        self.assertEqual(set(coverage["dispositions"]), {"candidate-projection", "held"})
        self.assertEqual(len({row["group_id"] for row in rules.values()}), len(rules))
        self.assertTrue(all(row["check_kind"] == "manual" for row in rules.values()))
        self.assertEqual(rules["ESXI-80-000111"]["disposition"], "held")
        self.assertIn("disagree", rules["ESXI-80-000111"]["qualification_gap"])

        families = coverage["families"]
        self.assertEqual({row["oval_6_test"] for row in families.values()}, set(census["oval_6_0_esxi_tests"]))
        for capability, family in families.items():
            comparison = census["oval_6_0_esxi_tests"][family["oval_6_test"]]
            self.assertEqual((family["adoption"], capability), (comparison["status"], comparison["capability"]))
            projected = [key for key, row in rules.items()
                         if row["disposition"] == "candidate-projection" and capability in row["projections"]]
            self.assertEqual(family["projected_rule_ids"], projected)
        self.assertEqual(families["esx.host_acceptancelevel"]["projected_rule_ids"], ["ESXI-80-000133"])
        self.assertEqual(families["esx.host_vib"]["projected_rule_ids"], [])

    def test_pinned_native_cases_isolate_boundary_and_diagnostic_status(self):
        path = STIG / "release-checks.assessment.yaml"
        document = load(path)
        validator().validate(document)
        tests = document["assessment"]["tests"]
        expected = load(STIG / "expected.json")
        rules = load(STIG / "coverage.json")["rules"]
        receipt = load(STIG / "ri-hold.json")
        self.assertEqual(receipt["assessment_sha256"], sha256(path.read_bytes()).hexdigest())
        self.assertEqual(receipt["schema_pin"], load(CONFORMANCE / "manifest.json")["schema_commit"])
        self.assertEqual(tests.keys(), expected["tests"].keys())
        self.assertEqual(receipt["results"].keys(), tests.keys())
        types = {"integer": int, "boolean": bool}

        for name, oracle in expected["tests"].items():
            row = rules[oracle["stig_id"]]
            test = tests[name]
            projection = row["projections"][test["capability"]]
            self.assertEqual(row["experimental_test"], name)
            self.assertEqual(projection["adoption"], "experimental")
            self.assertIn(oracle["observed_field"], projection["fields"])
            require = test["require"]
            self.assertEqual(require["item_requirement"]["items_found"], "exactly_one")
            predicate = require["fields"][oracle["observed_field"]]
            self.assertEqual(predicate["datatype"], oracle["datatype"])
            for vector in oracle["vectors"].values():
                values = vector["values"]
                self.assertTrue(all(type(value) is types[oracle["datatype"]] for value in values))
                satisfied = False
                if len(values) == 1:
                    if "equals" in predicate:
                        satisfied = values[0] == predicate["equals"]
                    else:
                        satisfied = values[0] >= predicate["greater_than_or_equal"]
                self.assertEqual(str(satisfied).lower(), vector["outcome"])
            self.assertEqual(receipt["results"][name], {
                "exit_code": 2,
                "diagnostic": {"code": "object_capability_unsupported", "pointer": f"/assessment/tests/{name}/object"},
            })


if __name__ == "__main__":
    unittest.main()
