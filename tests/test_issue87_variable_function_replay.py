"""Verify the ordered population oracle and the pinned RI comparison receipt."""
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load, validator

ASSESSMENT = "cases/core/variable-functions.assessment.yaml"
EVIDENCE = "fixtures/core-variable-functions.json"
EXPECTED = "expected/core-variable-functions.json"
REPLAY = CONFORMANCE / "variable-function-replay"


class VariableFunctionReplayCases(unittest.TestCase):
    def test_per_value_and_ordered_population_checks_follow_the_oracle(self):
        document = load(CONFORMANCE / ASSESSMENT)
        validator().validate(document)
        assessment = document["assessment"]
        expected = load(CONFORMANCE / EXPECTED)
        fixture = load(CONFORMANCE / EVIDENCE)
        receipt = load(REPLAY / "ri-receipt.json")
        control = load(REPLAY / "controls.json")
        self.assertEqual(receipt["schema_pin"], control["schema_pin"])
        self.assertEqual(receipt["assessment_closure_sha256"], control["assessment_closure_sha256"])
        for path in (ASSESSMENT, EVIDENCE, EXPECTED):
            self.assertEqual(sha256((CONFORMANCE / path).read_bytes()).hexdigest(), receipt["sha256"][path])

        previous = receipt["prior_observations"]
        self.assertEqual(sorted(name for name, row in previous.items() if row["outcome"] == "false"),
                         control["prior_false"])
        observations = receipt["positive_observations"]
        self.assertEqual(set(observations), set(fixture["test_outcomes"]))
        self.assertEqual(set(observations), set(assessment["tests"]))
        self.assertEqual({child["test"] for child in assessment["evaluate"]["and"]}, set(observations))

        for function, row in expected["functions"].items():
            name = f'function-{function.replace("_", "-")}-test'
            test = assessment["tests"][name]
            field = test["require"]["fields"]["value"]
            wanted_var = field["equals"]["variable"]
            wanted = assessment["variables"][wanted_var]["expression"]["literal"]["value"]
            self.assertEqual(wanted if isinstance(wanted, list) else [wanted], row["values"])
            self.assertEqual(fixture["variables"][test["variable"]], row["values"])
            self.assertEqual(field["value_match"], "exactly_one" if isinstance(wanted, list) else "every")
            self.assertEqual(observations[name], {
                "outcome": row["outcome"], "values_found": row["values_found"],
                "values_matching": row["values_found"],
            })

        ordered = expected["ordered_population_checks"]
        multi = {function for function, row in expected["functions"].items() if row["values_found"] > 1}
        self.assertEqual({row["function"] for row in ordered.values()}, multi)
        self.assertEqual(len(ordered), len(multi))
        for test_id, row in ordered.items():
            test = assessment["tests"][test_id]
            merge = assessment["variables"][test["variable"]]["expression"]["merge"]
            self.assertEqual((merge["sort"], merge["order"]), ("document", "ascending"))
            values = expected["functions"][row["function"]]["values"]
            self.assertTrue(all(merge["delimiter"] not in str(value) for value in values))
            self.assertEqual(merge["delimiter"].join(map(str, values)), row["sequence"])
            self.assertEqual(test["require"]["fields"]["value"]["equals"], row["sequence"])
            self.assertEqual(observations[test_id], {"outcome": "true", "values_found": 1, "values_matching": 1})

    def test_alias_leaves_isolate_the_intended_cardinality_difference(self):
        paths = ("cases/core/variable-interactions.assessment.yaml", "expected/core-variable-interactions.json")
        doc = load(CONFORMANCE / paths[0])
        expected = load(CONFORMANCE / paths[1])
        receipt = load(REPLAY / "ri-receipt.json")
        for path in paths:
            self.assertEqual(sha256((CONFORMANCE / path).read_bytes()).hexdigest(), receipt["sha256"][path])
        observed = receipt["alias_interaction"]
        self.assertEqual(observed["baseline"], load(REPLAY / "controls.json")["prior_alias"])
        assessment = doc["assessment"]
        leaf_outcomes = {}
        for name, row in expected["assertions"].items():
            predicate = assessment["tests"][name]["require"]["fields"]["value"]
            self.assertEqual(predicate["value_match"], "exactly_one")
            self.assertEqual(observed["current"][name], {
                key: row[key] for key in ("outcome", "values_found", "values_matching")
            })
            leaf_outcomes[name] = row["outcome"]
        positive, negative = assessment["evaluate"]["and"]
        self.assertEqual(leaf_outcomes[positive["test"]], "true")
        self.assertEqual(leaf_outcomes[negative["not"]["test"]], "false")
        self.assertEqual(expected["enclosing_outcome"], "true")

    def test_studio_receipt_covers_the_same_revised_assessments(self):
        studio = load(REPLAY / "studio-receipt.json")
        evaluator = load(REPLAY / "ri-receipt.json")
        self.assertEqual(studio["schema_pin"], evaluator["schema_pin"])
        self.assertEqual(set(studio["sha256"]), {ASSESSMENT, "cases/core/variable-interactions.assessment.yaml"})
        self.assertEqual(studio["sha256"], {name: evaluator["sha256"][name] for name in studio["sha256"]})
        for key in ("files", "ok", "noOpRoundTrips", "editRoundTrips", "undoRoundTrips"):
            self.assertEqual(studio["observed"][key], len(studio["sha256"]))
        self.assertEqual(studio["observed"]["failed"], 0)
        self.assertEqual(studio["observed"]["excludedExperimentalFiles"], 0)

    def test_projection_mutations_keep_sequence_and_evidence_status_separate(self):
        expected = load(REPLAY / "controls.json")["projection_variants"]
        observations = load(REPLAY / "ri-receipt.json")["projection_controls"]
        baseline = load(CONFORMANCE / EXPECTED)["functions"]["values"]["values"]
        first, second = baseline
        populations = {
            "nonmatching": ["/scap-ng-function-fixture/gamma", second],
            "reordered": [second, first],
            "duplicate": [first, second, first],
            "one-item": [first],
        }
        self.assertEqual(len(observations), 2 * len(expected))
        for name, row in expected.items():
            members = observations[f"{name}/function-values-test"]
            ordered = observations[f"{name}/function-values-ordered-test"]
            if "diagnostic" in row:
                self.assertEqual(members, row)
                self.assertEqual(ordered, row)
                continue
            values = populations[name]
            matches = sum(sum(value == want for want in baseline) == 1 for value in values)
            self.assertEqual(members, {"outcome": str(matches == len(values)).lower(),
                                       "values_found": len(values), "values_matching": matches})
            self.assertEqual(ordered, {"outcome": str(values == baseline).lower(),
                                       "values_found": 1, "values_matching": int(values == baseline)})


if __name__ == "__main__":
    unittest.main()
