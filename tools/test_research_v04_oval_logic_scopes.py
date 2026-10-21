#!/usr/bin/env python3
"""Exhaustive six-state operator/quantifier and OVAL scope-boundary fixtures."""
from itertools import product
import unittest
import xml.etree.ElementTree as ET
from collections import Counter

from oval_result_truth_tables import aggregate_operator,aggregate_check
from audit_v04_oval_boolean_scopes import examine_oval,OD
from research_v04_oval_logic_scopes import (
    RESULTS,OPERATORS,ITEM_QUANTIFIERS,candidate_logic,
    candidate_item_quantifier,scoped_state_item,checked_items
)


class SixStateScopeTests(unittest.TestCase):
    def test_all_six_state_tables_match_oval_per_operator(self):
        compared=0
        for n in range(1,5):
            for states in product(RESULTS,repeat=n):
                for ng,oval in OPERATORS.items():
                    self.assertEqual(candidate_logic(ng,states),
                                     aggregate_operator(oval,states),
                                     (ng,states))
                    compared+=1
        self.assertEqual(compared,6216)

    def test_all_four_item_matching_quantifiers_match_oval(self):
        compared=0
        for n in range(1,5):
            for states in product(RESULTS,repeat=n):
                for ng,oval in ITEM_QUANTIFIERS.items():
                    self.assertEqual(candidate_item_quantifier(ng,states),
                                     aggregate_check(oval,states),
                                     (ng,states))
                    compared+=1
        self.assertEqual(compared,6216)

    def test_and_or_one_xor_have_distinct_meanings(self):
        both=("true","true")
        self.assertEqual(candidate_logic("or",both),"true")
        self.assertEqual(candidate_logic("one",both),"false")
        triples=("true","true","true")
        self.assertEqual(candidate_logic("one",triples),"false")
        self.assertEqual(candidate_logic("xor",triples),"true")
        self.assertEqual(candidate_logic("xor",("true","error")),"error")
        self.assertEqual(candidate_logic("or",("true","error")),"true")
        self.assertEqual(candidate_logic("and",("false","unknown")),"false")

    def test_two_states_or_cannot_be_flattened_to_field_or(self):
        # Original OVAL State A = (type dword AND value 0)
        # and State B = (type string AND value Disabled).
        # A collected Item with type=dword, value=Disabled matches neither.
        states=[["true","false"],["false","true"]]
        faithful=scoped_state_item(states,
                                  fields_operators=["and","and"],
                                  state_operator="or")
        incorrectly_flattened=candidate_logic("or",sum(states,[]))
        self.assertEqual(faithful,"false")
        self.assertEqual(incorrectly_flattened,"true")

    def test_state_field_or_is_different_from_inter_state_or(self):
        state_fields=["true","false"]
        self.assertEqual(scoped_state_item([state_fields],
                         fields_operators=["or"],state_operator="and"),"true")
        self.assertEqual(scoped_state_item([state_fields],
                         fields_operators=["and"],state_operator="or"),"false")

    def test_item_matching_cardinality_not_mistaken_for_condition_or(self):
        # On Item 1, State A false, State B false; on Item 2, A true, B false.
        # OR between states and ALL Items => false;
        # the exact SAME per-item predicates with ONE_OR_MORE Items => true.
        items=[[["false"],["false"]],[["true"],["false"]]]
        ops=[["and","and"],["and","and"]]
        self.assertEqual(checked_items(items,fields_operators_by_item=ops,
                       state_operator="or",matching_items="all"),"false")
        self.assertEqual(checked_items(items,fields_operators_by_item=ops,
                       state_operator="or",matching_items="one_or_more"),"true")

    def test_ill_defined_synonyms_or_empty_input_fail_closed(self):
        for n in ("any","all","exactly_one","one_or_more"):
            with self.assertRaises(ValueError):
                candidate_logic(n,["true","false"])
        with self.assertRaises(ValueError):
            candidate_logic("or",[])
        with self.assertRaises(ValueError):
            candidate_item_quantifier("one_or_more",[])

    def test_repeated_same_entity_names_in_real_oval_state_are_counted(self):
        source=f'''<oval_definitions xmlns="{OD}" xmlns:ind="{OD}#independent">
        <tests>
          <ind:variable_test id="oval:org.example:tst:1" version="1"
                             comment="two same entities" check="all">
            <ind:object object_ref="oval:org.example:obj:1"/>
            <ind:state state_ref="oval:org.example:ste:1"/>
          </ind:variable_test>
        </tests>
        <states><ind:variable_state id="oval:org.example:ste:1" version="1"
            operator="OR">
           <ind:value>alpha</ind:value><ind:value>beta</ind:value>
        </ind:variable_state></states>
        </oval_definitions>'''
        counts=Counter()
        examples={}
        examine_oval(ET.fromstring(source),"fixture/source.xml",counts,examples)
        self.assertEqual(counts["states_repeated_field_names"],1)
        self.assertEqual(counts["referenced_repeated_field_names"],1)
        self.assertEqual(counts["referenced_nondefault_field_operator:OR"],1)
        self.assertEqual(examples["same_field_name_repeated_in_state"][0]["fields"],
                         ["value","value"])


if __name__=="__main__":
    unittest.main()
