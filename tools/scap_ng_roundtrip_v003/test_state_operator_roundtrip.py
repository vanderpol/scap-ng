#!/usr/bin/env python3
import unittest

from scap_ng_roundtrip_v003.native_assessment_to_oval import Builder, OD, q


class StateOperatorRoundTripTests(unittest.TestCase):
    def builder(self):
        return Builder({"assessment":{"collections":{},"tests":{}}})

    def predicate(self, field, value):
        return {
            "field":field,
            "value":value,
            "operation":"equals",
            "datatype":"string",
            "mask":False,
            "entity_check":"all",
            "entity_existence":"at_least_one_exists",
        }

    def emitted_operator(self, expr):
        b=self.builder()
        sid=b.emit_state(
            "unix.file",
            expr,
            "operator fixture",
        )
        state=next(
            node for node in b.states
            if node.get("id")==sid
        )
        return state.get("operator")

    def test_one_state_operator_round_trips(self):
        self.assertEqual(
            self.emitted_operator({
                "one":[
                    self.predicate("path","/a"),
                    self.predicate("path","/b"),
                ]
            }),
            "ONE",
        )

    def test_xor_state_operator_round_trips_from_native_odd(self):
        self.assertEqual(
            self.emitted_operator({
                "odd":[
                    self.predicate("path","/a"),
                    self.predicate("path","/b"),
                ]
            }),
            "XOR",
        )

    def test_native_evaluate_odd_emits_xor_criteria(self):
        b=self.builder()
        parent=b.defs
        b.emit_logic_node(
            parent,
            {"odd":[]},
            force_criteria=True,
        )
        criteria=parent.find(q(OD,"criteria"))
        self.assertIsNotNone(criteria)
        self.assertEqual(criteria.get("operator"),"XOR")


if __name__=="__main__":
    unittest.main()
