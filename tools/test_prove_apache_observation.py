#!/usr/bin/env python3
import unittest

from prove_apache_observation import (
    CORE_OBJECTS,
    CORE_VARIABLES,
    EXPORTS,
    extract,
    flatten,
    observation_document,
    validate_consumer_binding,
)


class ApacheObservationProofTests(unittest.TestCase):
    def source(self):
        objects={
            name:{
                "capability":"independent.shellcommand",
                "select":{"name":{"value":name}},
            }
            for name in CORE_OBJECTS
        }
        variables={
            name:{
                "kind":"local",
                "datatype":"string",
                "expression":{"literal":name},
            }
            for name in CORE_VARIABLES
        }
        exported_var=next(iter(EXPORTS))
        return {
            "assessment":{
                "id":"SV-test",
                "mode":"automated",
                "objects":objects,
                "variables":variables,
                "tests":{
                    "one":{
                        "capability":"independent.variable",
                        "variable":exported_var,
                    }
                },
                "evaluate":{"test":"one"},
            }
        }

    def test_extract_and_flatten_are_structurally_exact(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        self.assertIsNotNone(observation)
        extracted,counts=extract(source,observation)
        a=extracted["assessment"]
        self.assertNotIn(next(iter(EXPORTS)),a.get("variables",{}))
        self.assertIn("observations",a)
        self.assertTrue(counts)
        self.assertEqual(flatten(extracted,observation),source)

    def test_only_declared_exports_may_cross_boundary(self):
        source=self.source()
        private_var=next(name for name in CORE_VARIABLES if name not in EXPORTS)
        source["assessment"]["tests"]["one"]["variable"]=private_var
        observation=observation_document(source["assessment"])
        with self.assertRaisesRegex(ValueError,"private Observation node"):
            extract(source,observation)

    def test_consumer_version_mismatch_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_=extract(source,observation)
        extracted["assessment"]["observations"]["apache"]["expected_version"]=999
        with self.assertRaisesRegex(ValueError,"expected_version mismatch"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_consumer_id_mismatch_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_=extract(source,observation)
        extracted["assessment"]["observations"]["apache"]["expected_id"]="wrong.id"
        with self.assertRaisesRegex(ValueError,"expected_id mismatch"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_unknown_export_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_=extract(source,observation)
        extracted["assessment"]["tests"]["one"]["variable"]={
            "observation":"apache",
            "export":"does_not_exist",
        }
        with self.assertRaisesRegex(ValueError,"unknown Observation export"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_observation_exports_are_typed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        exports=observation["observation"]["exports"]
        self.assertEqual(set(exports),set(EXPORTS.values()))
        for contract in exports.values():
            self.assertEqual(contract["kind"],"values")
            self.assertEqual(contract["datatype"],"string")
            self.assertEqual(contract["cardinality"],"zero_or_more")
            self.assertIn("variable",contract)


if __name__=="__main__":
    unittest.main()
