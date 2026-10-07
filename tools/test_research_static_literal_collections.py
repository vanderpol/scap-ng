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
                                    "datatype": "string",
                                    "operation": "equals",
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
        entity=rendered["assessment"]["tests"]["t"]["object"]["select"]["path"]
        self.assertEqual(entity["datatype"],"string")
        self.assertEqual(entity["operation"],"equals")
        self.assertEqual(entity["variable_match"],"only_one")
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
                                    "datatype": "string",
                                    "operation": "equals",
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
        state_entity=rendered["assessment"]["tests"]["t"]["states"][0]["state"]
        self.assertEqual(state_entity["datatype"],"string")
        self.assertEqual(state_entity["operation"],"equals")
        self.assertEqual(state_entity["variable_match"],"all")
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

    def test_no_static_constant_is_exact_noop(self):
        source={
            "assessment":{
                "variables":{
                    "runtime":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"values":{"object":"users","field":"home_dir"}},
                    }
                }
            }
        }
        rendered,identity=proof.inline_constants(copy.deepcopy(source))
        self.assertEqual(identity,[])
        self.assertEqual(rendered,source)
        self.assertEqual(proof.reexpand_constants(rendered,identity),source)

    def test_list_constant_outside_direct_value_stays_named(self):
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
        rendered, identity = proof.inline_constants(copy.deepcopy(source))
        self.assertEqual(identity, [])
        self.assertEqual(rendered, source)
        self.assertEqual(proof.reexpand_constants(rendered, identity), source)

    def test_mixed_safe_and_unsupported_refs_are_atomic_noop(self):
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
                },
                "tests": {
                    "t": {
                        "object": {
                            "select": {
                                "path": {
                                    "value": {"variable": "values"},
                                    "datatype": "string",
                                    "operation": "equals",
                                    "variable_match": "one_or_more",
                                }
                            }
                        }
                    }
                },
            }
        }
        rendered, identity = proof.inline_constants(copy.deepcopy(source))
        self.assertEqual(identity, [])
        self.assertEqual(rendered, source)


if __name__ == "__main__":
    unittest.main()
