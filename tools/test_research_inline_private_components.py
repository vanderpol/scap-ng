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

    def test_reexpand_is_structurally_identical(self):
        source=self.base()
        rendered,identity=inline_private(source)
        self.assertEqual(reexpand(rendered,identity),source)


if __name__=="__main__":
    unittest.main()
