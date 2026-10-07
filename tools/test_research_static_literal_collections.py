#!/usr/bin/env python3
import copy
import unittest

import research_static_literal_collections as proof


class StaticLiteralCollectionTests(unittest.TestCase):
    def test_object_collection_round_trip(self):
        source = {
            "assessment": {
                "variables": {
                    "paths": {
                        "kind": "constant",
                        "datatype": "string",
                        "expression": {"literal": ["/lib", "/usr/lib"]},
                    }
                },
                "tests": {
                    "t": {
                        "object": {
                            "select": {
                                "path": {
                                    "value": {"variable": "paths"},
                                    "variable_match": "only_one",
                                }
                            }
                        }
                    }
                },
            }
        }
        rendered, identity = proof.inline_constants(source)
        self.assertEqual(
            rendered["assessment"]["tests"]["t"]["object"]["select"]["path"]["value"],
            ["/lib", "/usr/lib"],
        )
        self.assertNotIn("variables", rendered["assessment"])
        self.assertEqual(proof.reexpand_constants(rendered, identity), source)

    def test_state_collection_round_trip(self):
        source = {
            "assessment": {
                "variables": {
                    "permissions": {
                        "kind": "constant",
                        "datatype": "string",
                        "expression": {"literal": ["read", "execute"]},
                    }
                },
                "tests": {
                    "t": {
                        "states": [
                            {
                                "state": {
                                    "value": {"variable": "permissions"},
                                    "variable_match": "all",
                                }
                            }
                        ]
                    }
                },
            }
        }
        rendered, identity = proof.inline_constants(source)
        self.assertEqual(
            rendered["assessment"]["tests"]["t"]["states"][0]["state"]["value"],
            ["read", "execute"],
        )
        self.assertEqual(identity[0]["mode"], "state_collection_ref")
        self.assertEqual(proof.reexpand_constants(rendered, identity), source)

    def test_static_operand_inside_dynamic_variable_round_trip(self):
        source = {
            "assessment": {
                "variables": {
                    "prefix": {
                        "kind": "constant",
                        "datatype": "string",
                        "expression": {"literal": "/etc/dconf/db/"},
                    },
                    "database": {
                        "kind": "external",
                        "datatype": "string",
                    },
                    "derived": {
                        "kind": "local",
                        "datatype": "string",
                        "expression": {
                            "concat": [
                                {"variable": "prefix"},
                                {"variable": "database"},
                                {"literal": ".d/locks"},
                            ]
                        },
                    },
                }
            }
        }
        rendered, identity = proof.inline_constants(source)
        self.assertEqual(
            rendered["assessment"]["variables"]["derived"]["expression"]["concat"][0],
            {"literal": "/etc/dconf/db/"},
        )
        self.assertIn("derived", rendered["assessment"]["variables"])
        self.assertIn("database", rendered["assessment"]["variables"])
        self.assertNotIn("prefix", rendered["assessment"]["variables"])
        self.assertEqual(proof.reexpand_constants(rendered, identity), source)

    def test_list_constant_outside_direct_value_fails_closed(self):
        source = {
            "assessment": {
                "variables": {
                    "values": {
                        "kind": "constant",
                        "datatype": "string",
                        "expression": {"literal": ["a", "b"]},
                    },
                    "derived": {
                        "kind": "local",
                        "datatype": "string",
                        "expression": {"concat": [{"variable": "values"}]},
                    },
                }
            }
        }
        with self.assertRaises(ValueError):
            proof.inline_constants(copy.deepcopy(source))


if __name__ == "__main__":
    unittest.main()
