#!/usr/bin/env python3
"""Field-as-key compact State lowering: exact, scoped, and fail-closed tests."""
import unittest
from collections import Counter
from copy import deepcopy
from research_04_field_key_authoring import (
    fold_node, unfold_node, fold_document, unfold_document,
)

class FieldKeyTests(unittest.TestCase):
    def test_home_mount_example(self):
        original={"field":"mount_options","value":"nosuid","operation":"equals",
                  "existence":"one_or_more","match":"one_or_more"}
        compact=fold_node(original,Counter())
        self.assertEqual(compact,{"mount_options":{"value":"nosuid",
            "operation":"equals","existence":"one_or_more",
            "match":"one_or_more"}})
        self.assertEqual(unfold_node(compact),original)

    def test_repeated_same_field_remains_ordered_list(self):
        original={"assessment":{"mode":"automated","tests":{"a":{
            "states":[
                {"field":"name","value":"pattern-one","operation":"pattern_match",
                 "existence":"one_or_more","match":"all"},
                {"field":"name","value":"pattern-two","operation":"pattern_match",
                 "existence":"optional","match":"all"}],
            "states_match":"any"}}}}
        compact,counts=fold_document(original)
        self.assertEqual(counts["field_key_compacted"],2)
        self.assertEqual(len(compact["assessment"]["tests"]["a"]["states"]),2)
        self.assertEqual(unfold_document(compact),original)

    def test_nested_logic_unchanged(self):
        x={"any":[
            {"field":"owner_uid","value":0,"operation":"equals","match":"all"},
            {"all":[{"field":"mode","value":"0600","operation":"equals"}]}]}
        c=Counter()
        shortened=fold_node(x,c)
        self.assertEqual(unfold_node(shortened),x)
        self.assertEqual(c["field_key_compacted"],2)
        self.assertEqual(c["logic_branch:any"],1)
        self.assertEqual(c["logic_branch:all"],1)

    def test_record_array_variable_or_typed_predicates(self):
        entries=[
            {"field":"field_data","value":{"variable":"lookup"},
             "operation":"greater_than","datatype":"version",
             "value_match":"all"},
            {"field":"groups","value":[1,3,4],
             "operation":"subset_of","datatype":"integer"},
            {"field":"record","value":{"fields":[{"key":"x","value":"y"}]},
             "operation":"equals"}]
        for entry in entries:
            with self.subTest(entry=entry):
                original=deepcopy(entry)
                self.assertEqual(unfold_node(fold_node(entry,Counter())),original)

    def test_field_name_collisions_are_unambiguous_by_payload_shape(self):
        for field in ("all","value","field","operation","reported_elements"):
            source={"field":field,"value":"y","operation":"equals"}
            shortened=fold_node(source,Counter())
            self.assertEqual(shortened,{field:{"value":"y","operation":"equals"}})
            self.assertEqual(unfold_node(shortened),source)
        self.assertEqual(
            unfold_node({"all":[{"value":{"value":"forbidden","operation":"equals"}}]}),
            {"all":[{"field":"value","value":"forbidden","operation":"equals"}]}
        )

    def test_bad_compact_forms_are_rejected(self):
        for candidate in (
            {"mount_options":"nosuid"},      # no semantic contract for bare scalar
            {"mount_options":{}},
            {"mount_options":{"field":"owner_uid","value":0}},
            {"mount_options":{"value":0},"owner_uid":{"value":100}},
            {"all":"x"},  # logical all requires list; field all requires mapping
            {"field_name":None},
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    unfold_node(candidate)

    def test_no_inferred_operators_or_quantifiers(self):
        x={"field":"owner_uid","value":0}
        c=Counter()
        self.assertEqual(unfold_node(fold_node(x,c)),x)
        self.assertNotIn("operation",unfold_node(fold_node(x,Counter())))
        self.assertNotIn("existence",unfold_node(fold_node(x,Counter())))

if __name__=="__main__":
    unittest.main()
