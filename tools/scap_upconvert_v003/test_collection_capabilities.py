#!/usr/bin/env python3
"""Regression tests for first-class Collection capability/type identity."""
import copy
import unittest

from collection_graph import collection_types, nodes, validate_capabilities


class CollectionCapabilityTests(unittest.TestCase):
    def source(self):
        return {
            "assessment": {
                "id": "example",
                "collections": {
                    "accounts": {
                        "collection_title": "Local accounts",
                        "capability": "unix.password",
                        "select": {},
                    }
                },
                "variables": {
                    "account-names": {
                        "datatype": "string",
                        "expression": {
                            "values": {
                                "collection": "accounts",
                                "field": "username",
                            }
                        },
                    }
                },
                "tests": {
                    "test-account": {
                        "test_title": "Account check",
                        "capability": "unix.password",
                        "collection": "accounts",
                        "assertion": {
                            "existence": "at_least_one_exists",
                            "item_quantifier": "all",
                            "state_capability": "unix.password",
                            "state": {
                                "field": "username",
                                "operation": "equals",
                                "datatype": "string",
                                "value": "root",
                            },
                        },
                    }
                },
                "evaluate": {"test": "test-account"},
            }
        }

    def test_deep_generic_graph_walk_is_stack_safe(self):
        value={"leaf":True}
        for _ in range(1500):
            value={"nested":value}
        seen=sum(1 for _ in nodes(value))
        self.assertEqual(seen,1501)

    def test_collection_keeps_own_capability(self):
        document = self.source()
        before = copy.deepcopy(document)
        types = collection_types(document["assessment"])
        self.assertEqual(types, {"accounts": "unix.password"})
        validate_capabilities(document["assessment"])
        self.assertEqual(document, before)
        self.assertEqual(
            document["assessment"]["collections"]["accounts"]["capability"],
            "unix.password",
        )

    def test_variable_reference_does_not_redeclare_collection_capability(self):
        document = self.source()
        variable = document["assessment"]["variables"]["account-names"]
        self.assertNotIn("collection_capabilities", variable)
        validate_capabilities(document["assessment"])

    def test_deep_collection_dependency_chain_is_stack_safe(self):
        assessment={"collections":{},"tests":{},"variables":{}}
        count=1500
        for index in range(count):
            payload={"capability":"unix.file"}
            if index+1 < count:
                payload["set"]={
                    "operator":"union",
                    "members":[{"collection":f"c{index+1}"}],
                }
            assessment["collections"][f"c{index}"]=payload
        types=collection_types(assessment)
        self.assertEqual(len(types),count)
        self.assertEqual(types["c0"],"unix.file")
        self.assertEqual(types[f"c{count-1}"],"unix.file")

    def test_deep_collection_cycle_is_reported_without_recursion_error(self):
        assessment={"collections":{},"tests":{},"variables":{}}
        count=1500
        for index in range(count):
            target=f"c{index+1}" if index+1 < count else "c0"
            assessment["collections"][f"c{index}"]={
                "capability":"unix.file",
                "set":{"operator":"union","members":[{"collection":target}]},
            }
        with self.assertRaisesRegex(ValueError,"Collection dependency cycle"):
            collection_types(assessment)

    def test_missing_collection_capability_rejected(self):
        document = self.source()
        del document["assessment"]["collections"]["accounts"]["capability"]
        with self.assertRaisesRegex(ValueError, "Missing Collection accounts capability"):
            validate_capabilities(document["assessment"])

    def test_test_collection_mismatch_rejected_without_retagging(self):
        document = self.source()
        document["assessment"]["tests"]["test-account"]["capability"] = "unix.file"
        with self.assertRaisesRegex(ValueError, "Test/Collection capability mismatch"):
            validate_capabilities(document["assessment"])
        self.assertEqual(
            document["assessment"]["collections"]["accounts"]["capability"],
            "unix.password",
        )

    def test_state_capability_mismatch_rejected(self):
        document = self.source()
        document["assessment"]["tests"]["test-account"]["assertion"][
            "state_capability"
        ] = "unix.file"
        with self.assertRaisesRegex(ValueError, "Test/State capability mismatch"):
            validate_capabilities(document["assessment"])

    def test_variable_side_collection_capability_is_obsolete(self):
        document = self.source()
        document["assessment"]["variables"]["account-names"][
            "collection_capabilities"
        ] = {"accounts": "unix.password"}
        with self.assertRaisesRegex(
            ValueError, "Variable-side Collection capability declarations are obsolete"
        ):
            validate_capabilities(document["assessment"])


if __name__ == "__main__":
    unittest.main()
