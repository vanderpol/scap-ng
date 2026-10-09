#!/usr/bin/env python3
"""0.3 expected-value quantifier conformance against OVAL 5.12.3 semantics.

value_match aggregates comparisons to expected values. It must never be
confused with observed entity match or existence. This is a contract and
truth-table test, not a claim that a scanner has passed end-to-end evaluation.
"""
from __future__ import annotations

import copy
import itertools
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from generate_capability_schema import generate
from oval_result_truth_tables import (
    RESULTS,
    aggregate_check,
    aggregate_many_to_many,
    evaluate_variable_entity_reference,
)
from scap_upconvert_v003.native_capability_mapping import apply_capability_mapping
from validate_native_json_schemas import schema_store

ROOT = Path(__file__).resolve().parents[1]
V03 = ROOT / "schema" / "v0.3.0"
VALUES = {
    "all": "all",
    "one_or_more": "at least one",
    "one": "only one",
    "none": "none satisfy",
}


class ValueMatchContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().with_resources(
            (uri, Resource.from_contents(schema))
            for uri, schema in schema_store(V03).items()
        )
        cls.common = json.loads((V03 / "capability-common.schema.json").read_text())
        cls.prefix = cls.common["$id"] + "#/$defs/"
        cls.validators = {
            kind: Draft202012Validator({"$ref": cls.prefix + kind},
                                        registry=cls.registry)
            for kind in ("object_entity_base", "state_entity_base",
                         "scalar_value_predicate")
        }

    def base(self, kind, operand, *, quantifier="all"):
        row = {"value": operand, "operation": "equals", "datatype": "string"}
        if kind != "object_entity_base":
            row.update({"match": "all", "existence": "one_or_more"})
        if quantifier is not None:
            row["value_match"] = quantifier
        return row

    def test_all_operand_forms_require_explicit_quantifier(self):
        for kind, validator in self.validators.items():
            for operand in (
                {"variable": "approved-types-variable"},
                {"input": "approved-types"},
                ["ext4", "xfs"],
            ):
                if kind == "object_entity_base" and "input" in operand:
                    continue  # Collection selectors cannot consume Organizational Input.
                with self.subTest(kind=kind, operand=operand):
                    good = self.base(kind, operand)
                    self.assertEqual(list(validator.iter_errors(good)), [])
                    missing = self.base(kind, operand, quantifier=None)
                    self.assertTrue(list(validator.iter_errors(missing)),
                                    "multivalued expected operands may not get a hidden default")
                    legacy = copy.deepcopy(good)
                    legacy["variable_match"] = legacy.pop("value_match")
                    self.assertTrue(list(validator.iter_errors(legacy)),
                                    "0.3 must not accept the obsolete key")

    def test_organizational_input_is_for_expected_state_not_collection_selectors(self):
        for operand in ({"input":"approved-types"},
                        {"variable":"approved-types-variable"},
                        ["ext4","xfs"]):
            object_pred=self.base("object_entity_base",operand)
            state_pred=self.base("state_entity_base",operand)
            object_errors=list(self.validators["object_entity_base"].iter_errors(object_pred))
            state_errors=list(self.validators["state_entity_base"].iter_errors(state_pred))
            self.assertEqual(state_errors,[])
            if "input" in operand:
                self.assertTrue(object_errors,
                    "Organizational Input must never redirect collection targets")
            else:
                self.assertEqual(object_errors,[])

    def test_scalar_quantifier_preserves_explicit_oval_state_expectations(self):
        for kind, validator in self.validators.items():
            with self.subTest(kind=kind):
                scalar = self.base(kind, "ext4", quantifier=None)
                self.assertEqual(list(validator.iter_errors(scalar)), [])
                legacy = copy.deepcopy(scalar)
                legacy["variable_match"] = "none"
                self.assertTrue(list(validator.iter_errors(legacy)))
                explicit = copy.deepcopy(scalar)
                explicit["value_match"] = "none"
                if kind == "state_entity_base":
                    # OVAL-authored States sometimes explicitly carry
                    # value_match/var_check even with one expected value.
                    # Preserve the author's aggregator over a singleton.
                    self.assertEqual(list(validator.iter_errors(explicit)), [])
                else:
                    # No change to the collection selector or generic scalar
                    # predicate contracts.
                    self.assertTrue(list(validator.iter_errors(explicit)))

    def test_observed_match_and_existence_are_independent_scopes(self):
        v = self.validators["state_entity_base"]
        expected = ["ext4", "xfs"]
        good = self.base("state_entity_base", expected, quantifier="one")
        self.assertEqual(list(v.iter_errors(good)), [])
        for missing in ("value_match", "match", "existence"):
            changed = copy.deepcopy(good)
            changed.pop(missing)
            self.assertTrue(list(v.iter_errors(changed)), missing)
        for bad in ("any", "some", "at least one", "only one", "none satisfy"):
            changed = copy.deepcopy(good)
            changed["value_match"] = bad
            self.assertTrue(list(v.iter_errors(changed)))

    def test_generated_capability_uses_current_common_contract(self):
        mapping=json.loads(
            (V03 / "capability-mappings/supported/windows.ntuser.json").read_text()
        )
        generated=generate(mapping, ROOT, schema_version="0.3.0")
        validator=Draft202012Validator(generated["$defs"]["state"],
                                        registry=self.registry)
        state={
            "state_title":"Expected registry type",
            "capability":"windows.ntuser",
            "state":{"field":"type", "value":["dword","string"],
                     "operation":"equals", "datatype":"string",
                     "value_match":"one_or_more", "match":"all",
                     "existence":"one_or_more"},
        }
        self.assertEqual(list(validator.iter_errors(state)), [])
        del state["state"]["value_match"]
        self.assertTrue(list(validator.iter_errors(state)))

    def test_current_03_converter_emits_value_match(self):
        source={"assessment":{"objects":{"file-selector":{
            "capability":"unix.file",
            "select":{"full_path":{
                "value":{"variable":"required-path-variable"},
                "operation":"equal", "datatype":"string",
                "variable_check":"at least one"
            }}
        }},"states":{},"tests":{}}}
        mapping=json.loads(
            (V03 / "capability-mappings/supported/unix.file.json").read_text())
        converted=apply_capability_mapping(source,mapping)
        selector=converted["assessment"]["objects"]["file-selector"]["select"]["full_path"]
        self.assertEqual(selector["value_match"], "one_or_more")
        self.assertNotIn("variable_match", selector)

    def test_oval_var_check_six_state_truth_table_parity(self):
        statuses=sorted(RESULTS)
        # A 2-expected-value by 2-observed-item comparison surface exercises
        # every OVAL CheckEnumeration combination, unknown/error and both
        # aggregation boundaries. The new name never changes the combiner.
        for row in itertools.product(statuses, repeat=4):
            comparisons=[row[:2],row[2:]]
            for value_match, old_var_check in VALUES.items():
                for observed_match, old_entity_check in VALUES.items():
                    old=aggregate_many_to_many(
                        var_check=old_var_check, entity_check=old_entity_check,
                        comparison_rows=comparisons)
                    new=aggregate_check(
                        old_entity_check,
                        [aggregate_check(old_var_check, values)
                         for values in comparisons])
                    self.assertEqual(new, old,
                        (row,value_match,observed_match))
        # A missing/invalid/unresolved input propagates rather than being
        # spuriously converted to a passing state by value_match.
        for state in sorted(RESULTS-{"true"}):
            self.assertEqual(
                evaluate_variable_entity_reference(
                    variable_status=state, var_check="at least one",
                    entity_check="all"),
                state)


if __name__ == "__main__":
    unittest.main()
