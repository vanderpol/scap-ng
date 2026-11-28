"""Verify complete-empty count semantics separately from missing and invalid evidence."""
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load, validator

FIXTURE = CONFORMANCE / "empty-projection"


class EmptyProjectionCases(unittest.TestCase):
    def test_current_and_prior_ri_keep_empty_distinct_from_missing(self):
        expected = load(FIXTURE / "expected.json")
        receipt = load(FIXTURE / "ri-receipt.json")
        source = FIXTURE / expected["artifact"]
        doc = load(source)
        validator().validate(doc)
        self.assertEqual(receipt["schema_pin"], expected["schema_pin"])
        studio = load(FIXTURE / "studio-receipt.json")
        self.assertEqual(studio["sha256"], {
            source.relative_to(CONFORMANCE).as_posix(): sha256(source.read_bytes()).hexdigest()
        })
        self.assertEqual(studio["observed"]["undoRoundTrips"], 1)
        for path, digest in receipt["sha256"].items():
            self.assertEqual(sha256((CONFORMANCE / path).read_bytes()).hexdigest(), digest)

        assessment = doc["assessment"]
        selected = assessment["variables"]["observed-values-variable"]["expression"]["values"]
        source_object = assessment["shared_objects"][selected["object"]["object_ref"]]
        self.assertEqual((source_object["capability"], selected["field"]), ("unix.file", "full_path"))
        observed = receipt["observed"]
        self.assertNotEqual(observed["current"]["ri_revision"], observed["prior"]["ri_revision"])
        prior = observed["prior"]["cases"]
        current = observed["current"]["cases"]

        count_operand = assessment["tests"]["count-empty-test"]["require"]["fields"]["value"]["equals"]
        value_operand = assessment["tests"]["projection-has-values-test"]["require"]["fields"]["value"]["equals"]
        self.assertEqual(count_operand, 0)
        for name, oracle in expected["cases"].items():
            prefix = f"{name}/"
            count = current[prefix + "count-empty-test"]
            existence = current[prefix + "projection-has-values-test"]
            if "diagnostic" in oracle:
                self.assertEqual(count, {"diagnostic": oracle["diagnostic"]})
                self.assertEqual(existence, count)
            else:
                values = oracle["known_values"]
                matches = sum(value == value_operand for value in values)
                self.assertEqual(len(values), oracle["independent_count"])
                self.assertEqual(count, oracle["count_outcome"])
                self.assertEqual(count["outcome"], str(len(values) == count_operand).lower())
                self.assertEqual(existence, oracle["existence_outcome"])
                self.assertEqual(existence["outcome"], str(bool(values) and matches == len(values)).lower())
                self.assertEqual((existence["values_found"], existence["values_matching"]), (len(values), matches))
            if "prior_diagnostic" in oracle:
                for test_id in assessment["tests"]:
                    self.assertEqual(prior[prefix + test_id], {"diagnostic": oracle["prior_diagnostic"]})
            else:
                self.assertEqual(prior[prefix + "count-empty-test"], count)
                self.assertEqual(prior[prefix + "projection-has-values-test"], existence)


if __name__ == "__main__":
    unittest.main()
