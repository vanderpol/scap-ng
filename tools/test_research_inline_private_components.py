#!/usr/bin/env python3
import copy
import unittest

from research_inline_private_components import inline_private, reexpand


class InlinePrivateComponentResearchTests(unittest.TestCase):
    def base(self):
        return {
            "assessment":{
                "id":"example",
                "mode":"automated",
                "objects":{
                    "private-object":{"capability":"unix.file","select":{"filepath":{"value":"/a"}}},
                    "shared-object":{"capability":"unix.file","select":{"filepath":{"value":"/b"}}},
                    "variable-source":{"capability":"unix.password","select":{"username":{"value":".*"}}},
                },
                "variables":{
                    "homes":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"values":{"object":"variable-source","field":"home_dir"}},
                    }
                },
                "states":{
                    "private-state":{"capability":"unix.file","state":{"field":"user_id","value":"0"}},
                    "shared-state":{"capability":"unix.file","state":{"field":"group_id","value":"0"}},
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"private-object","states":["private-state","shared-state"]},
                    "two":{"capability":"unix.file","object":"shared-object","states":["shared-state"]},
                    "three":{"capability":"unix.file","object":"shared-object"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"},{"test":"three"}]},
            }
        }

    def test_inlines_only_private_direct_test_components(self):
        source=self.base()
        rendered,identity=inline_private(source)
        a=rendered["assessment"]
        self.assertIsInstance(a["tests"]["one"]["object"],dict)
        self.assertIsInstance(a["tests"]["one"]["states"][0],dict)
        self.assertEqual(a["tests"]["one"]["states"][1],"shared-state")
        self.assertIn("shared-object",a["objects"])
        self.assertIn("variable-source",a["objects"])
        self.assertIn("shared-state",a["states"])
        self.assertNotIn("private-object",a["objects"])
        self.assertNotIn("private-state",a["states"])
        self.assertEqual(identity["inlined_objects"],{
            "private-object":"assessment.tests.one.object",
        })
        self.assertEqual(identity["inlined_states"],{
            "private-state":"assessment.tests.one.states[0]",
        })
        self.assertEqual(
            identity["retained_object_reasons"]["shared-object"],
            "multiple_tests",
        )
        self.assertEqual(
            identity["retained_object_reasons"]["variable-source"],
            "graph_only",
        )
        self.assertEqual(
            identity["retained_state_reasons"]["shared-state"],
            "multiple_tests",
        )

    def test_variable_reference_prevents_object_inlining(self):
        source=self.base()
        # Reuse private-object from a Variable to make it independently addressable.
        source["assessment"]["variables"]["other"]={
            "kind":"local","datatype":"string",
            "expression":{"values":{"object":"private-object","field":"filepath"}},
        }
        rendered,identity=inline_private(source)
        self.assertEqual(rendered["assessment"]["tests"]["one"]["object"],"private-object")
        self.assertNotIn("private-object",identity["inlined_objects"])
        self.assertEqual(
            identity["retained_object_reasons"]["private-object"],
            "test_and_graph",
        )

    def test_reexpand_is_structurally_identical(self):
        source=self.base()
        rendered,identity=inline_private(source)
        self.assertEqual(reexpand(rendered,identity),source)

    def test_private_unfiltered_leaf_set_operands_inline_and_roundtrip(self):
        source={
            "assessment":{
                "id":"set-example",
                "mode":"automated",
                "objects":{
                    "base":{"capability":"independent.textfilecontent54","select":{"full_path":{"value":"/etc/a"}}},
                    "dropin":{"capability":"independent.textfilecontent54","select":{"directory":{"value":"/etc/a.d"}}},
                    "combined":{
                        "capability":"independent.textfilecontent54",
                        "set":{
                            "operator":"union",
                            "operands":[
                                {"object":"base","filters":[]},
                                {"object":"dropin","filters":[]},
                            ],
                        },
                    },
                },
                "states":{},
                "tests":{
                    "one":{"capability":"independent.textfilecontent54","object":"combined"},
                },
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(source,inline_private_set_operands=True)
        test_object=rendered["assessment"]["tests"]["one"]["object"]
        self.assertIsInstance(test_object,dict)
        operands=test_object["set"]["operands"]
        self.assertIsInstance(operands[0]["object"],dict)
        self.assertIsInstance(operands[1]["object"],dict)
        self.assertEqual(
            {row["object"] for row in identity["inlined_set_operand_objects"]},
            {"base","dropin"},
        )
        self.assertEqual(reexpand(rendered,identity),source)

    def test_reused_set_operand_stays_named(self):
        source={
            "assessment":{
                "id":"reused-set-operand",
                "mode":"automated",
                "objects":{
                    "base":{"capability":"unix.file","select":{"path":{"value":"/tmp"}}},
                    "combined-a":{
                        "capability":"unix.file",
                        "set":{"operator":"union","operands":[{"object":"base","filters":[]}]},
                    },
                    "combined-b":{
                        "capability":"unix.file",
                        "set":{"operator":"union","operands":[{"object":"base","filters":[]}]},
                    },
                },
                "states":{},
                "tests":{
                    "one":{"capability":"unix.file","object":"combined-a"},
                    "two":{"capability":"unix.file","object":"combined-b"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            }
        }
        rendered,identity=inline_private(source,inline_private_set_operands=True)
        self.assertEqual(
            rendered["assessment"]["tests"]["one"]["object"]["set"]["operands"][0]["object"],
            "base",
        )
        self.assertEqual(
            rendered["assessment"]["tests"]["two"]["object"]["set"]["operands"][0]["object"],
            "base",
        )
        self.assertNotIn("base",identity["inlined_set_operand_objects"])
        self.assertEqual(reexpand(rendered,identity),source)

    def test_nested_set_operand_object_stays_named(self):
        source={
            "assessment":{
                "id":"nested-set-operand",
                "mode":"automated",
                "objects":{
                    "leaf":{"capability":"unix.file","select":{"path":{"value":"/tmp"}}},
                    "inner":{
                        "capability":"unix.file",
                        "set":{"operator":"union","operands":[{"object":"leaf","filters":[]}]},
                    },
                    "outer":{
                        "capability":"unix.file",
                        "set":{"operator":"union","operands":[{"object":"inner","filters":[]}]},
                    },
                },
                "states":{},
                "tests":{"one":{"capability":"unix.file","object":"outer"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(source,inline_private_set_operands=True)
        outer=rendered["assessment"]["tests"]["one"]["object"]
        # The leaf may localize inside the named inner Set, but the inner Set
        # itself is not collapsed as an operand because nested Set Objects are
        # outside this bounded proof class.
        self.assertEqual(outer["set"]["operands"][0]["object"],"inner")
        self.assertIn("inner",rendered["assessment"]["objects"])
        self.assertNotIn(
            "inner",
            {row["object"] for row in identity["inlined_set_operand_objects"]},
        )
        self.assertEqual(reexpand(rendered,identity),source)

    def test_filtered_set_operand_stays_named(self):
        source={
            "assessment":{
                "id":"filtered-set",
                "mode":"automated",
                "objects":{
                    "base":{"capability":"unix.file","select":{"path":{"value":"/tmp"}}},
                    "combined":{
                        "capability":"unix.file",
                        "set":{
                            "operator":"union",
                            "operands":[
                                {"object":"base","filters":[{"state":"some-state"}]},
                            ],
                        },
                    },
                },
                "states":{"some-state":{"capability":"unix.file","state":{"field":"type","value":"file"}}},
                "tests":{"one":{"capability":"unix.file","object":"combined"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(source,inline_private_set_operands=True)
        # Parent Set may inline into the Test, but the filtered operand remains a ref.
        self.assertEqual(
            rendered["assessment"]["tests"]["one"]["object"]["set"]["operands"][0]["object"],
            "base",
        )
        self.assertEqual(identity["inlined_set_operand_objects"],[])
        self.assertEqual(reexpand(rendered,identity),source)


if __name__=="__main__":
    unittest.main()
