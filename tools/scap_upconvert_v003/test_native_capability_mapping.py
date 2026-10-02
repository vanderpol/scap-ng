#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

from native_capability_mapping import apply_capability_mapping, source_capability


ROOT=Path(__file__).resolve().parents[2]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.wmi.query.json"


class NativeCapabilityMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))

    def aligned_wmi_document(self):
        return {
            "assessment":{
                "objects":{
                    "query-object":{
                        "object_title":"OS query",
                        "capability":"windows.wmi57",
                        "select":{
                            "namespace":{
                                "value":"root\\cimv2",
                                "operation":"equals",
                                "datatype":"string",
                                "mask":False,
                            },
                            "wql":{
                                "value":"SELECT Caption, Version FROM Win32_OperatingSystem",
                                "operation":"equals",
                                "datatype":"string",
                                "mask":False,
                            },
                        },
                    }
                },
                "states":{
                    "state-result":{
                        "state_title":"expected OS",
                        "capability":"windows.wmi57",
                        "state":{
                            "field":"result",
                            "value":{
                                "record":[
                                    {
                                        "name":"caption",
                                        "value":"Microsoft Windows 11 Enterprise",
                                        "operation":"equals",
                                        "datatype":"string",
                                        "mask":False,
                                        "entity_check":"all",
                                    },
                                    {
                                        "name":"version",
                                        "value":"10.0",
                                        "operation":"greater than or equal",
                                        "datatype":"version",
                                        "mask":False,
                                        "entity_check":"all",
                                    },
                                ]
                            },
                            "operation":"equals",
                            "datatype":"record",
                            "mask":False,
                            "entity_check":"all",
                            "entity_existence":"at_least_one_exists",
                        },
                    }
                },
                "tests":{
                    "test-query":{
                        "test_title":"OS query",
                        "capability":"windows.wmi57",
                        "object":"query-object",
                        "check_existence":"at_least_one_exists",
                        "check":"all",
                        "states":["state-result"],
                    }
                },
            }
        }

    def test_source_capability_is_derived_from_pinned_family(self):
        self.assertEqual(source_capability(self.mapping),"windows.wmi57")

    def test_wmi_object_becomes_collector_driven(self):
        out=apply_capability_mapping(self.aligned_wmi_document(),self.mapping)
        obj=out["assessment"]["objects"]["query-object"]
        self.assertEqual(obj["capability"],"windows.wmi.query")
        self.assertNotIn("select",obj)
        self.assertEqual(obj["collect"],{
            "namespace":"root\\cimv2",
            "query":"SELECT Caption, Version FROM Win32_OperatingSystem",
        })

    def test_wmi_record_state_becomes_native_record_predicate(self):
        out=apply_capability_mapping(self.aligned_wmi_document(),self.mapping)
        state=out["assessment"]["states"]["state-result"]
        self.assertEqual(state["capability"],"windows.wmi.query")
        payload=state["state"]
        self.assertEqual(payload["field"],"result")
        self.assertNotIn("datatype",payload)
        self.assertNotIn("operation",payload)
        record=payload["record"]
        self.assertEqual(record["match"],"all")
        self.assertEqual(record["existence"],"some")
        self.assertNotIn("mask",record)
        self.assertNotIn("redact_result",record)
        self.assertEqual(record["fields"]["caption"]["operation"],"equal")
        self.assertEqual(record["fields"]["caption"]["datatype"],"string")
        self.assertEqual(record["fields"]["caption"]["existence"],"some")
        self.assertEqual(record["fields"]["version"]["operation"],"greater_or_equal")
        self.assertEqual(record["fields"]["version"]["datatype"],"version")

    def test_legacy_mask_true_becomes_native_result_redaction(self):
        doc=self.aligned_wmi_document()
        state=doc["assessment"]["states"]["state-result"]["state"]
        state["mask"]=True
        state["value"]["record"][0]["mask"]=True
        out=apply_capability_mapping(doc,self.mapping)
        record=out["assessment"]["states"]["state-result"]["state"]["record"]
        self.assertTrue(record["redact_result"])
        self.assertTrue(record["fields"]["caption"]["redact_result"])
        self.assertNotIn("mask",record)
        self.assertNotIn("mask",record["fields"]["caption"])

    def test_collector_mask_true_fails_closed_until_output_binding_is_explicit(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["objects"]["query-object"]["select"]["namespace"]["mask"]=True
        with self.assertRaisesRegex(ValueError,"collector input cannot be masked"):
            apply_capability_mapping(doc,self.mapping)

    def test_wmi_test_controls_use_native_shared_vocabulary(self):
        out=apply_capability_mapping(self.aligned_wmi_document(),self.mapping)
        test=out["assessment"]["tests"]["test-query"]
        self.assertEqual(test["capability"],"windows.wmi.query")
        self.assertEqual(test["existence"],"some")
        self.assertEqual(test["match"],"all")

    def test_legacy_set_shape_becomes_native_operands(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["objects"]["query-object"]={
            "object_title":"combined",
            "capability":"windows.wmi57",
            "set":{
                "operator":"complement",
                "members":[
                    {"object":"query-a"},
                    {"object":"query-b"},
                ],
                "filters":[
                    {"action":"exclude","state":"state-result"},
                ],
            },
        }
        out=apply_capability_mapping(doc,self.mapping)
        expr=out["assessment"]["objects"]["query-object"]["set"]
        self.assertEqual(expr["operator"],"difference")
        self.assertEqual(len(expr["operands"]),2)
        self.assertEqual(expr["operands"][0],{
            "object":"query-a",
            "filters":[{"action":"exclude","state":"state-result"}],
        })

    def test_test_state_operator_uses_clean_native_logical_name(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["tests"]["test-query"]["state_operator"]="XOR"
        out=apply_capability_mapping(doc,self.mapping)
        test=out["assessment"]["tests"]["test-query"]
        self.assertNotIn("state_operator",test)
        self.assertEqual(test["states_match"],"odd")

    def test_collector_comparison_semantics_fail_closed(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["objects"]["query-object"]["select"]["wql"]["operation"]="pattern match"
        with self.assertRaisesRegex(ValueError,"collector input cannot use comparison semantics"):
            apply_capability_mapping(doc,self.mapping)


if __name__=="__main__":
    unittest.main()
