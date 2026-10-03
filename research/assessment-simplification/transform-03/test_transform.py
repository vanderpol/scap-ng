"""Synthetic lowering tests: no filesystem collection or target scanner execution."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import random
import unittest
import xml.etree.ElementTree as ET

import yaml
import jsonschema

from compile_requirements import (AuthoringError, UniqueLoader, compile_author,
                                  load_author, permission_fields, validate_native)
from oval_result_truth_tables import (aggregate_operator, evaluate_collected_object_test,
                                      evaluate_state_entity_existence)
from demo import explain_false_comparison

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "evidence/rhel_9/SV-257889/source-oval.xml"
# Independent POSIX mode oracle, not imported from compiler RIGHT declarations.
BITS = {"setuid": 0o4000, "setgid": 0o2000, "sticky": 0o1000,
        "owner_read": 0o400, "owner_write": 0o200, "owner_execute": 0o100,
        "group_read": 0o40, "group_write": 0o20, "group_execute": 0o10,
        "other_read": 0o4, "other_write": 0o2, "other_execute": 0o1}
SOURCE_BITS = {"suid": 0o4000, "sgid": 0o2000, "sticky": 0o1000, "gwrite": 0o20,
               "gexec": 0o10, "oread": 0o4, "owrite": 0o2, "oexec": 0o1}


def conjunction_oracle(results):
    # Independently stated ALL truth table for the bounded comparison result domain.
    for outcome in ("false", "error", "unknown", "not evaluated"):
        if outcome in results:
            return outcome
    return "true" if "true" in results else "not applicable"


def compiled_item(assessment, test_id, comparisons):
    test = assessment["tests"][test_id]
    results = [comparisons[assessment["states"][s]["state"]["field"]] for s in test["states"]]
    return aggregate_operator("AND", results)


def compiled_test(assessment, test_id, flag, item_results, **counts):
    test = assessment["tests"][test_id]
    # Reuse the repository's pinned six-state Test control-flow helper explicitly.
    # This is not an independent scanner oracle.
    existence = {"optional": "any_exist", "some": "at_least_one_exists"}[test["existence"]]
    return evaluate_collected_object_test(flag, existence=existence, check=test["match"],
                                         item_results=item_results, **counts)


class PermissionTransformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author = load_author(HERE / "examples/initialization-files.author.yaml")
        cls.document, cls.mapping = compile_author(cls.author)
        cls.assessment = cls.document["assessment"]
        cls.user = "test-protect-user-files"
        cls.root = "test-protect-root-files"
        source = ET.parse(SOURCE)
        cls.source_state = next(node for node in source.iter()
                                if node.tag.endswith("}file_state")
                                and node.attrib["id"].endswith(":ste:20000020"))

    def test_exhaustive_modes_match_original_source_state(self):
        self.assertEqual({node.tag.split("}")[-1] for node in self.source_state}, set(SOURCE_BITS))
        for mode in range(0o10000):
            expected = all(bool(mode & SOURCE_BITS[node.tag.split("}")[-1]]) ==
                           (node.text.strip() == "true") for node in self.source_state)
            observations = {field: "false" if mode & bit else "true" for field, bit in BITS.items()}
            actual = compiled_item(self.assessment, self.user, observations)
            self.assertEqual(actual, "true" if expected else "false", oct(mode))

    def test_allowance_is_subset_not_numeric_limit(self):
        mode = 0o604
        self.assertLess(mode, 0o740)
        actual = compiled_item(self.assessment, self.user,
                               {f: "false" if mode & b else "true" for f, b in BITS.items()})
        self.assertEqual(actual, "false")

    def test_all_nontrivial_allowances_against_posix_masks(self):
        rights = [("owner", "read", 0o400), ("owner", "write", 0o200), ("owner", "execute", 0o100),
                  ("group", "read", 0o40), ("group", "write", 0o20), ("group", "execute", 0o10),
                  ("other", "read", 0o4), ("other", "write", 0o2), ("other", "execute", 0o1),
                  ("special", "setuid", 0o4000), ("special", "setgid", 0o2000), ("special", "sticky", 0o1000)]
        rng = random.Random(3)
        for allowance_mask in range(0o7777):
            allowance = {category: [right for cat, right, bit in rights
                                    if cat == category and bit & allowance_mask]
                         for category in ("owner", "group", "other", "special")}
            fields = permission_fields(allowance)
            for mode in (0, 0o7777, allowance_mask, rng.randrange(0o10000)):
                self.assertEqual(all(not mode & BITS[f] for f in fields),
                                 mode & ~allowance_mask == 0, (oct(allowance_mask), oct(mode)))

    def test_partial_comparison_results_preserve_conjunction(self):
        required_fields = list(SOURCE_BITS)  # eight independent comparisons
        native_fields = [self.assessment["states"][s]["state"]["field"]
                         for s in self.assessment["tests"][self.user]["states"]]
        self.assertEqual(len(native_fields), len(required_fields))
        for outcomes in product(("true", "false", "error", "unknown"), repeat=8):
            actual = compiled_item(self.assessment, self.user, dict(zip(native_fields, outcomes)))
            self.assertEqual(actual, conjunction_oracle(outcomes))
        for outcomes in product(("true", "false", "error", "unknown", "not evaluated", "not applicable"), repeat=2):
            comparisons = dict.fromkeys(native_fields, "not applicable")
            comparisons.update(dict(zip(native_fields[:2], outcomes)))
            self.assertEqual(compiled_item(self.assessment, self.user, comparisons), conjunction_oracle(outcomes))

    def test_unconstrained_unknown_or_error_bits_do_not_change_result(self):
        for status in ("error", "unknown"):
            comparisons = dict.fromkeys(BITS, "true")
            for field in ("owner_read", "owner_write", "owner_execute", "group_read"):
                comparisons[field] = status
            self.assertEqual(compiled_item(self.assessment, self.user, comparisons), "true")

    def test_missing_required_entity_is_not_an_allowed_permission(self):
        self.assertEqual(evaluate_state_entity_existence("at_least_one_exists", does_not_exist=1), "false")
        self.assertEqual(evaluate_state_entity_existence("at_least_one_exists", error=1), "error")
        self.assertEqual(evaluate_state_entity_existence("at_least_one_exists", not_collected=1), "unknown")

    def test_original_test_existence_defaults_are_preserved(self):
        tests = [n for n in ET.parse(SOURCE).iter() if n.tag.endswith("}file_test")]
        self.assertEqual(tests[0].get("check_existence"), "any_exist")
        self.assertIsNone(tests[1].get("check_existence"))
        # Pinned XSD default at_least_one_exists was proved in refinement-01.
        self.assertEqual(self.assessment["tests"][self.user]["existence"], "optional")
        self.assertEqual(self.assessment["tests"][self.root]["existence"], "some")

    def test_absence_unknown_and_collection_errors(self):
        cases = [("does not exist", [], {}, "true", "false"),
                 ("not collected", [], {}, "unknown", "unknown"),
                 ("error", ["false"], {"exists": 1}, "error", "error"),
                 ("not applicable", [], {}, "not applicable", "not applicable"),
                 ("complete", ["unknown"], {"exists": 1}, "unknown", "unknown")]
        for flag, values, counts, user, root in cases:
            self.assertEqual(compiled_test(self.assessment, self.user, flag, values, **counts), user)
            self.assertEqual(compiled_test(self.assessment, self.root, flag, values, **counts), root)

    def test_multiple_matches_and_incomplete_population(self):
        cases = [("complete", ["true", "true"], "true"),
                 ("complete", ["true", "false"], "false"),
                 ("complete", ["unknown", "false"], "false"),
                 ("incomplete", ["true"], "unknown"),
                 ("incomplete", ["false"], "false")]
        for flag, values, expected in cases:
            self.assertEqual(compiled_test(self.assessment, self.user, flag, values, exists=len(values)), expected)

    def test_fixed_object_scope_survives_unchanged(self):
        obj = self.assessment["objects"]["object-alice-initialization-files"]
        self.assertEqual(obj["select"]["directory"]["value"], "/home/alice")
        self.assertEqual(obj["select"]["name"]["value"], r"^\.[^\s\.]+")
        self.assertEqual(obj["traversal"], {"max_depth": 1, "recurse": "symlinks"})
        self.assertEqual(obj["filesystem"], "any")

    def test_literal_path_object_compiles_without_traversal(self):
        author = deepcopy(self.author)
        author["objects"]["alice-initialization-files"]["files"] = {"path": "/home/alice/.bashrc", "filesystem": "any"}
        output, _ = compile_author(author)
        obj = output["assessment"]["objects"]["object-alice-initialization-files"]
        self.assertNotIn("traversal", obj)
        self.assertEqual(obj["select"]["full_path"]["value"], "/home/alice/.bashrc")

    def test_generated_content_passes_reviewed_deep_schema_and_closure(self):
        validate_native(self.document)
        bad = deepcopy(self.document)
        bad["assessment"]["states"][next(iter(bad["assessment"]["states"]))]["state"]["field"] = "mode"
        with self.assertRaises(jsonschema.ValidationError):
            validate_native(bad)
        bad = deepcopy(self.document)
        bad["assessment"]["tests"][self.user]["object"] = "object-missing"
        with self.assertRaises(AuthoringError):
            validate_native(bad)

    def test_unknown_rights_duplicates_and_runtime_inputs_rejected(self):
        modifications = [("other", ["read", "read"]), ("special", ["execute"]), ("owner", [True]),
                         ("group", {"variable": "org-input"})]
        for category, value in modifications:
            author = deepcopy(self.author)
            author["tests"]["protect-user-files"]["permissions_at_most"][category] = value
            with self.assertRaises(AuthoringError):
                compile_author(author)
        for key, value in (("inputs", {}), ("commands", ["anything"]), ("evaluate", {})):
            author = deepcopy(self.author)
            author[key] = value
            with self.assertRaises(AuthoringError):
                compile_author(author)

    def test_unsupported_methods_and_account_source_plans_rejected(self):
        author = deepcopy(self.author)
        author["objects"]["alice-initialization-files"] = {"capability": "unix.file", "scope": {"beneath_account_homes": {}}}
        with self.assertRaises(AuthoringError):
            compile_author(author)
        author = deepcopy(self.author)
        author["tests"]["protect-user-files"] = {"audit_coverage": {"architectures": ["b64"]}}
        with self.assertRaises(AuthoringError):
            compile_author(author)
        author = deepcopy(self.author)
        author["tests"]["protect-user-files"]["every"] = "unbound"
        with self.assertRaises(AuthoringError):
            compile_author(author)

    def test_invalid_traversal_and_fully_unrestricted_allowance_rejected(self):
        for key, value in (("depth", True), ("depth", -1), ("recurse", "junctions"), ("filesystem", "invented")):
            author = deepcopy(self.author)
            author["objects"]["alice-initialization-files"]["files"][key] = value
            with self.assertRaises(AuthoringError):
                compile_author(author)
        with self.assertRaises(AuthoringError):
            permission_fields({"owner": ["read", "write", "execute"], "group": ["read", "write", "execute"],
                               "other": ["read", "write", "execute"], "special": ["setuid", "setgid", "sticky"]})

    def test_yaml_duplicate_keys_and_tags_rejected(self):
        with self.assertRaises(AuthoringError):
            yaml.load("tests: {}\ntests: {}\n", Loader=UniqueLoader)
        with self.assertRaises(yaml.constructor.ConstructorError):
            yaml.load("x: !!python/object/apply:os.system ['echo bad']", Loader=UniqueLoader)

    def test_repeatable_output_and_separate_provenance(self):
        output, mapping = compile_author(self.author)
        self.assertEqual(output, self.document)
        self.assertEqual(mapping, self.mapping)
        self.assertEqual(len(output["assessment"]["tests"]), len(self.author["tests"]))
        self.assertNotIn("source_map", output["assessment"])
        self.assertNotIn("SV-257889", yaml.safe_dump(output))

    def test_diagnostic_points_to_the_author_requirement(self):
        finding = explain_false_comparison(self.mapping, "state-protect-user-files-other-read")
        self.assertEqual(finding["test"], "protect-user-files")
        self.assertEqual(finding["author_path"], "tests.protect-user-files.permissions_at_most.other")
        self.assertEqual(finding["message"], "other read is outside the allowed permissions")


if __name__ == "__main__":
    unittest.main()
