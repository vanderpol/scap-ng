#!/usr/bin/env python3
import unittest

from prove_windows_domainrole_observation import (
    EXPECTED_CAPABILITY,
    EXPECTED_COLLECT,
    candidate_object,
    extract,
    flatten,
    observation_document,
)


class WindowsDomainRoleObservationTests(unittest.TestCase):
    def source(self):
        return {
            "assessment":{
                "id":"SV-test",
                "mode":"automated",
                "objects":{
                    "role-object":{
                        "capability":EXPECTED_CAPABILITY,
                        "object_title":None,
                        "collect":dict(EXPECTED_COLLECT),
                    },
                    "local-object":{
                        "capability":"windows.userright",
                        "select":{"userright":"EXAMPLE"},
                    },
                },
                "states":{
                    "role-state":{
                        "capability":EXPECTED_CAPABILITY,
                        "state":{"field":"result"},
                    }
                },
                "tests":{
                    "role-test":{
                        "capability":EXPECTED_CAPABILITY,
                        "object":"role-object",
                        "states":["role-state"],
                    },
                    "local-test":{
                        "capability":"windows.userright",
                        "object":"local-object",
                    },
                },
                "evaluate":{"all":[{"test":"role-test"},{"test":"local-test"}]},
            }
        }

    def test_extract_item_export_and_roundtrip(self):
        source=self.source()
        name,payload=candidate_object(source["assessment"])
        observation=observation_document(payload)
        extracted,original,refs=extract(source,observation)
        self.assertEqual(original,name)
        self.assertEqual(refs,1)
        obj=extracted["assessment"]["tests"]["role-test"]["object"]
        self.assertEqual(obj,{"observation":"system_role","export":"computer_system"})
        self.assertEqual(flatten(extracted,observation,original),source)

    def test_non_test_consumer_is_rejected(self):
        source=self.source()
        source["assessment"]["variables"]={
            "bad":{"kind":"local","datatype":"string","expression":{"object":"role-object"}}
        }
        _,payload=candidate_object(source["assessment"])
        observation=observation_document(payload)
        with self.assertRaisesRegex(ValueError,"non-Test consumers"):
            extract(source,observation)


if __name__=="__main__":
    unittest.main()
