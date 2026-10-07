#!/usr/bin/env python3
import copy
import unittest

from prove_apache_observation_artifact import (
    OBSERVATION_ID,
    OBSERVATION_VERSION,
    CORE_OBJECTS,
    CORE_VARIABLES,
    EXPORTS,
    extract,
    flatten,
    observation_payload,
    validate_consumer_binding,
)


class ApacheObservationPrototypeTests(unittest.TestCase):
    def source(self):
        objects={name:{"capability":"x","value":name} for name in CORE_OBJECTS}
        variables={name:{"kind":"local","datatype":"string","expression":{"literal":name}} for name in CORE_VARIABLES}
        exported_source=next(iter(EXPORTS))
        private_source=next(name for name in CORE_VARIABLES if name not in EXPORTS)
        objects["local-object"]={"capability":"x","value":"local"}
        return {
            "assessment":{
                "id":"SV-test",
                "mode":"automated",
                "objects":objects,
                "variables":variables,
                "states":{},
                "tests":{
                    "one":{
                        "capability":"x",
                        "object":"local-object",
                        "some_exported_value":exported_source,
                    }
                },
                "evaluate":{"test":"one"},
            }
        }, private_source

    def test_extract_and_flatten_roundtrip(self):
        source,_=self.source()
        observation=observation_payload(source["assessment"])
        extracted,_=extract(source,observation)
        self.assertIn("observations",extracted["assessment"])
        self.assertEqual(flatten(extracted,observation),source)

    def test_version_mismatch_is_rejected(self):
        source,_=self.source()
        observation=observation_payload(source["assessment"])
        extracted,_=extract(source,observation)
        extracted["assessment"]["observations"]["apache"]["expected_version"]=999
        with self.assertRaisesRegex(ValueError,"version binding mismatch"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_unknown_export_is_rejected(self):
        source,_=self.source()
        observation=observation_payload(source["assessment"])
        extracted,_=extract(source,observation)
        extracted["assessment"]["tests"]["one"]["some_exported_value"]={
            "observation_export":{"observation":"apache","export":"does_not_exist"}
        }
        with self.assertRaisesRegex(ValueError,"unknown Observation export"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_private_node_reference_is_rejected(self):
        source,private_source=self.source()
        observation=observation_payload(source["assessment"])
        source2=copy.deepcopy(source)
        observation=observation_payload(source2["assessment"])
        extracted,_=extract(source2,observation)
        extracted["assessment"]["tests"]["one"]["bad_private_ref"]=private_source
        with self.assertRaisesRegex(ValueError,"private Observation node reference"):
            validate_consumer_binding(extracted["assessment"],observation)


if __name__=="__main__":
    unittest.main()
