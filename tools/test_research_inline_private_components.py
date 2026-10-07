#!/usr/bin/env python3
import copy
import unittest

from research_inline_private_components import context_signature, inline_private, reexpand


class InlinePrivateComponentResearchTests(unittest.TestCase):
    def test_context_signature_is_stable(self):
        self.assertEqual(context_signature({"variable":1}),"variable:1")
        self.assertEqual(
            context_signature({"test_object":1,"variable":2}),
            "test_object:1+variable:2",
        )
        self.assertEqual(context_signature({}),"unreferenced")

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
        self.assertEqual(
            identity["retained_object_contexts"]["shared-object"],
            {"test_object":2},
        )
        self.assertEqual(
            identity["retained_object_contexts"]["variable-source"],
            {"variable":1},
        )
        self.assertEqual(
            identity["retained_state_contexts"]["shared-state"],
            {"test_state":2},
        )


    def test_consumer_local_states_duplicate_reused_test_state_and_roundtrip(self):
        source=self.base()
        rendered,identity=inline_private(source,inline_state_consumers=True)
        a=rendered["assessment"]
        self.assertIsInstance(a["tests"]["one"]["states"][1],dict)
        self.assertIsInstance(a["tests"]["two"]["states"][0],dict)
        self.assertNotIn("shared-state",a.get("states",{}))
        rows=[
            row for row in identity["inlined_state_consumer_occurrences"]
            if row["state"]=="shared-state"
        ]
        self.assertEqual(len(rows),2)
        self.assertEqual({row["consumer"] for row in rows},{"test"})
        self.assertEqual(reexpand(rendered,identity),source)

    def test_consumer_local_filter_state_roundtrip(self):
        source={
            "assessment":{
                "id":"filter-state-locality",
                "mode":"automated",
                "objects":{
                    "a":{"capability":"unix.file","select":{"path":{"value":"/a"}}},
                    "b":{"capability":"unix.file","select":{"path":{"value":"/b"}}},
                    "combined":{
                        "capability":"unix.file",
                        "set":{
                            "operator":"union",
                            "operands":[
                                {"object":"a","filters":[{"state":"only-root","action":"include"}]},
                                {"object":"b","filters":[{"state":"only-root","action":"include"}]},
                            ],
                        },
                    },
                },
                "states":{
                    "only-root":{
                        "capability":"unix.file",
                        "state":{"field":"user_id","value":"0"},
                    },
                },
                "tests":{"one":{"capability":"unix.file","object":"combined"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_set_operands=True,
            inline_state_consumers=True,
        )
        a=rendered["assessment"]
        combined=a["tests"]["one"]["object"]
        for operand in combined["set"]["operands"]:
            self.assertIsInstance(operand["filters"][0]["state"],dict)
        self.assertNotIn("states",a)
        rows=identity["inlined_state_consumer_occurrences"]
        self.assertEqual(len(rows),2)
        self.assertEqual({row["consumer"] for row in rows},{"filter"})
        self.assertEqual(reexpand(rendered,identity),source)


    def test_consumer_local_filter_state_in_named_variable_source_roundtrip(self):
        # Mirrors the SV-257889 boundary: an Object remains named because a
        # Variable consumes it, while the Object's Set Filter State is localized.
        source={
            "assessment":{
                "id":"variable-source-filter-locality",
                "mode":"automated",
                "objects":{
                    "users":{"capability":"unix.password","select":{"username":{"value":".*"}}},
                    "filtered-users":{
                        "capability":"unix.password",
                        "set":{
                            "operator":"difference",
                            "operands":[{
                                "object":"users",
                                "filters":[{"state":"system-user","action":"exclude"}],
                            }],
                        },
                    },
                },
                "variables":{
                    "homes":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"values":{"object":"filtered-users","field":"home_dir"}},
                    },
                },
                "states":{
                    "system-user":{
                        "capability":"unix.password",
                        "state":{"field":"user_id","value":"1000","operation":"less_than"},
                    },
                },
                "tests":{"one":{"capability":"unix.password","object":"users"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_set_operands=True,
            inline_state_consumers=True,
        )
        operand=rendered["assessment"]["objects"]["filtered-users"]["set"]["operands"][0]
        self.assertIsInstance(operand["filters"][0]["state"],dict)
        self.assertEqual(reexpand(rendered,identity),source)

    def test_variable_only_object_localizes_and_roundtrips(self):
        source=self.base()
        rendered,identity=inline_private(
            source,
            inline_variable_object_consumers=True,
        )
        a=rendered["assessment"]
        embedded=a["variables"]["homes"]["expression"]["values"]["object"]
        self.assertIsInstance(embedded,dict)
        self.assertNotIn("variable-source",a.get("objects",{}))
        self.assertEqual(
            identity["inlined_variable_objects"],
            [{
                "object":"variable-source",
                "path":["variables","homes","expression","values","object"],
            }],
        )
        self.assertEqual(reexpand(rendered,identity),source)

    def test_test_and_variable_shared_object_does_not_localize_to_variable(self):
        source=self.base()
        source["assessment"]["variables"]["other"]={
            "kind":"local",
            "datatype":"string",
            "expression":{"values":{"object":"private-object","field":"filepath"}},
        }
        rendered,identity=inline_private(
            source,
            inline_variable_object_consumers=True,
        )
        self.assertEqual(rendered["assessment"]["tests"]["one"]["object"],"private-object")
        self.assertEqual(
            rendered["assessment"]["variables"]["other"]["expression"]["values"]["object"],
            "private-object",
        )
        self.assertNotIn(
            "private-object",
            {row["object"] for row in identity["inlined_variable_objects"]},
        )
        self.assertEqual(reexpand(rendered,identity),source)

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

    def test_private_leaf_local_variable_localizes_and_roundtrips(self):
        source={
            "assessment":{
                "id":"private-local-variable",
                "mode":"automated",
                "objects":{
                    "source":{"capability":"unix.file","select":{"path":{"value":"/src"}}},
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                                "value":{"variable":"derived-path"},
                            }
                        },
                    },
                },
                "variables":{
                    "derived-path":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"values":{"object":"source","field":"path"}},
                                {"literal":{"value":"/x","datatype":"string"}},
                            ]
                        },
                    }
                },
                "tests":{"one":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_variable_object_consumers=True,
            inline_private_local_variables=True,
        )
        self.assertEqual(
            len([
                row for row in identity["inlined_variables"]
                if row["variable"]=="derived-path"
            ]),
            1,
        )
        self.assertNotIn("derived-path",rendered["assessment"].get("variables",{}))
        self.assertEqual(reexpand(rendered,identity),source)

    def test_local_variable_chain_stays_named(self):
        source={
            "assessment":{
                "id":"local-variable-chain",
                "mode":"automated",
                "objects":{
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                                "value":{"variable":"outer"},
                            }
                        },
                    },
                },
                "variables":{
                    "inner":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"concat":[{"literal":{"value":"/a","datatype":"string"}}]},
                    },
                    "outer":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"variable":{"variable":"inner"}},
                                {"literal":{"value":"/b","datatype":"string"}},
                            ]
                        },
                    },
                },
                "tests":{"one":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_local_variables=True,
        )
        self.assertIn("inner",rendered["assessment"]["variables"])
        self.assertIn("outer",rendered["assessment"]["variables"])
        self.assertEqual(identity["inlined_variables"],[])
        self.assertEqual(reexpand(rendered,identity),source)

    def test_private_constant_in_retained_top_level_state_roundtrips(self):
        # Regression for RHEL SV-258042-style shape: the State remains top-level
        # while its sole constant Variable reference is localized.
        source={
            "assessment":{
                "id":"constant-in-retained-state",
                "mode":"automated",
                "objects":{
                    "obj":{"capability":"unix.file","select":{"path":{"value":"/tmp"}}},
                },
                "states":{
                    "unused-state":{
                        "capability":"unix.file",
                        "state":{
                            "field":"user_id",
                            "value":{"variable":"anonymous-uids"},
                        },
                    },
                },
                "variables":{
                    "anonymous-uids":{
                        "kind":"constant",
                        "datatype":"int",
                        "expression":{"literal":["65534","65535"]},
                    },
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"obj"},
                },
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_state_consumers=True,
            inline_private_variables=True,
        )
        embedded=rendered["assessment"]["states"]["unused-state"]["state"]["value"]["variable"]
        self.assertIsInstance(embedded,dict)
        self.assertEqual(identity["inlined_variables"][0]["variable"],"anonymous-uids")
        self.assertEqual(reexpand(rendered,identity),source)

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


    def test_private_filtered_leaf_set_operand_localizes_and_roundtrips(self):
        source={
            "assessment":{
                "id":"filtered-set-locality",
                "mode":"automated",
                "objects":{
                    "base":{"capability":"unix.file","select":{"path":{"value":"/tmp"}}},
                    "combined":{
                        "capability":"unix.file",
                        "set":{
                            "operator":"union",
                            "operands":[{
                                "object":"base",
                                "filters":[{"state":"only-root","action":"include"}],
                            }],
                        },
                    },
                },
                "states":{
                    "only-root":{
                        "capability":"unix.file",
                        "state":{"field":"user_id","value":"0"},
                    },
                },
                "tests":{"one":{"capability":"unix.file","object":"combined"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
        )
        operand=rendered["assessment"]["tests"]["one"]["object"]["set"]["operands"][0]
        self.assertIsInstance(operand["object"],dict)
        self.assertEqual(operand["filters"][0]["state"],"only-root")
        rows=identity["inlined_set_operand_objects"]
        self.assertEqual(rows[0]["filter_count"],1)
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


    def test_single_use_external_variable_localizes_and_roundtrips(self):
        source={
            "assessment":{
                "id":"external-variable-locality",
                "mode":"automated",
                "objects":{
                    "target":{
                        "capability":"windows.registry",
                        "select":{
                            "value":{
                                "operation":"equal",
                                "datatype":"string",
                                "value":{"variable":"expected-value"},
                            }
                        },
                    },
                },
                "variables":{
                    "expected-value":{
                        "title":"organizationally supplied expected value",
                        "kind":"external",
                        "datatype":"string",
                        "input":{
                            "required":True,
                            "cardinality":"one_or_more",
                            "parameter":"policy.expected",
                        },
                    },
                },
                "tests":{
                    "one":{"capability":"windows.registry","object":"target"},
                },
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_variables=True,
        )
        a=rendered["assessment"]
        inline=a["tests"]["one"]["object"]["select"]["value"]["value"]["variable"]
        self.assertIsInstance(inline,dict)
        self.assertEqual(inline["kind"],"external")
        self.assertNotIn("variables",a)
        self.assertEqual(
            identity["inlined_variables"],
            [{
                "variable":"expected-value",
                "kind":"external",
                "path":[
                    "tests","one","object","select","value","value"
                ],
            }],
        )
        self.assertEqual(reexpand(rendered,identity),source)

    def test_single_use_constant_variable_localizes_and_roundtrips(self):
        source={
            "assessment":{
                "id":"constant-variable-locality",
                "mode":"automated",
                "objects":{
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "operation":"equal",
                                "datatype":"string",
                                "value":{"variable":"constant-path"},
                            }
                        },
                    },
                },
                "variables":{
                    "constant-path":{
                        "title":"fixed path",
                        "kind":"constant",
                        "datatype":"string",
                        "expression":{"literal":"/etc/example"},
                    },
                },
                "tests":{"one":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_variables=True,
        )
        inline=rendered["assessment"]["tests"]["one"]["object"]["select"]["path"]["value"]["variable"]
        self.assertEqual(inline["kind"],"constant")
        self.assertEqual(inline["expression"],{"literal":"/etc/example"})
        self.assertEqual(reexpand(rendered,identity),source)

    def test_reused_external_variable_stays_named(self):
        source={
            "assessment":{
                "id":"reused-external-variable",
                "mode":"automated",
                "objects":{
                    "one":{
                        "capability":"unix.file",
                        "select":{"path":{"value":{"variable":"input"}}},
                    },
                    "two":{
                        "capability":"unix.file",
                        "select":{"path":{"value":{"variable":"input"}}},
                    },
                },
                "variables":{
                    "input":{
                        "kind":"external",
                        "datatype":"string",
                        "input":{"required":True,"cardinality":"one_or_more"},
                    },
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"one"},
                    "two":{"capability":"unix.file","object":"two"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_variables=True,
        )
        self.assertIn("input",rendered["assessment"]["variables"])
        self.assertEqual(identity["inlined_variables"],[])
        self.assertEqual(reexpand(rendered,identity),source)

    def test_local_derived_variable_stays_named(self):
        source={
            "assessment":{
                "id":"local-variable-stays-named",
                "mode":"automated",
                "objects":{
                    "source":{"capability":"unix.password","select":{"username":{"value":".*"}}},
                    "target":{
                        "capability":"unix.file",
                        "select":{"path":{"value":{"variable":"derived"}}},
                    },
                },
                "variables":{
                    "derived":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"values":{"object":"source","field":"home_dir"}},
                    },
                },
                "tests":{"one":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"one"},
            }
        }
        rendered,identity=inline_private(
            source,
            inline_private_variables=True,
        )
        self.assertIn("derived",rendered["assessment"]["variables"])
        self.assertEqual(identity["inlined_variables"],[])
        self.assertEqual(reexpand(rendered,identity),source)


if __name__=="__main__":
    unittest.main()
