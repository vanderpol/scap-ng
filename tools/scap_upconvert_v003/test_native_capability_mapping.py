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

    def test_collector_redaction_fails_closed_until_output_binding_is_explicit(self):
        doc=self.aligned_wmi_document()
        selector=doc["assessment"]["objects"]["query-object"]["select"]["namespace"]
        selector.pop("mask",None)
        selector["redact_result"]=True
        with self.assertRaisesRegex(ValueError,"collector input redaction cannot be preserved"):
            apply_capability_mapping(doc,self.mapping)

    def test_wmi_test_controls_use_native_shared_vocabulary(self):
        out=apply_capability_mapping(self.aligned_wmi_document(),self.mapping)
        test=out["assessment"]["tests"]["test-query"]
        self.assertEqual(test["capability"],"windows.wmi.query")
        self.assertEqual(test["check_existence"],"some")
        self.assertEqual(test["check"],"all")

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

    def test_omitted_oval_state_operator_is_materialized_for_multiple_states(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["states"]["state-result-2"]=copy.deepcopy(
            doc["assessment"]["states"]["state-result"]
        )
        doc["assessment"]["tests"]["test-query"]["states"].append("state-result-2")
        out=apply_capability_mapping(doc,self.mapping)
        test=out["assessment"]["tests"]["test-query"]
        self.assertEqual(test["states_match"],"all")

    def test_collector_comparison_semantics_fail_closed(self):
        doc=self.aligned_wmi_document()
        doc["assessment"]["objects"]["query-object"]["select"]["wql"]["operation"]="pattern match"
        with self.assertRaisesRegex(ValueError,"collector input cannot use comparison semantics"):
            apply_capability_mapping(doc,self.mapping)



class ReviewedNativeCapabilityMappingRegressionTests(unittest.TestCase):
    def mapping(self,name):
        return json.loads(
            (ROOT/"schema/v0.1.0/capability-mappings"/name).read_text(encoding="utf-8")
        )

    def test_textfilecontent54_object_predicates_and_defaults_become_native(self):
        mapping=self.mapping("independent.textfilecontent54.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"sudoers",
                "capability":"independent.textfilecontent54",
                "select":{
                    "filepath":{
                        "value":"/etc/sudoers",
                        "operation":"equals",
                        "datatype":"string",
                        "mask":False,
                    },
                    "pattern":{
                        "value":"^Defaults",
                        "operation":"pattern match",
                        "datatype":"string",
                        "mask":False,
                    },
                    "instance":{
                        "value":"1",
                        "operation":"greater than or equal",
                        "datatype":"int",
                        "mask":False,
                    },
                },
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        obj=out["assessment"]["objects"]["o"]
        self.assertEqual(obj["capability"],"independent.textfilecontent54")
        self.assertEqual(obj["select"]["full_path"]["operation"],"equal")
        self.assertEqual(obj["select"]["pattern"]["operation"],"match")
        self.assertEqual(obj["select"]["instance"]["operation"],"greater_or_equal")
        self.assertEqual(obj["select"]["instance"]["datatype"],"integer")
        self.assertEqual(obj["collect"],{
            "ignore_case":False,
            "multiline":True,
            "singleline":False,
            "item_creation":"all_object_elements_fullfilled",
        })

    def test_file_nil_name_becomes_native_directory_selection(self):
        mapping=self.mapping("independent.textfilecontent54.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"directory",
                "capability":"independent.textfilecontent54",
                "select":{
                    "path":{"value":"/etc","operation":"equals","datatype":"string"},
                    "filename":{"value":"","operation":"equals","datatype":"string","nil":True},
                    "pattern":{"value":"x","operation":"pattern match","datatype":"string"},
                    "instance":{"value":"1","operation":"equals","datatype":"int"},
                },
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        self.assertIsNone(out["assessment"]["objects"]["o"]["select"]["name"])

    def test_singleton_source_removes_meaningless_object_and_test_reference(self):
        mapping=self.mapping("windows.auditeventpolicysubcategories.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"singleton",
                "capability":"windows.auditeventpolicysubcategories",
            }},
            "states":{"s":{
                "state_title":"audit",
                "capability":"windows.auditeventpolicysubcategories",
                "state":{
                    "field":"logon",
                    "value":"AUDIT_SUCCESS",
                    "operation":"equals",
                    "datatype":"string",
                    "entity_check":"all",
                    "entity_existence":"at_least_one_exists",
                },
            }},
            "tests":{"t":{
                "test_title":"audit",
                "capability":"windows.auditeventpolicysubcategories",
                "object":"o",
                "check_existence":"at_least_one_exists",
                "check":"all",
                "states":["s"],
            }},
        }}
        out=apply_capability_mapping(doc,mapping)
        self.assertNotIn("o",out["assessment"]["objects"])
        self.assertNotIn("object",out["assessment"]["tests"]["t"])
        self.assertEqual(out["assessment"]["tests"]["t"]["check_existence"],"some")
        self.assertEqual(out["assessment"]["tests"]["t"]["check"],"all")

    def test_singleton_source_fails_closed_on_meaningful_object(self):
        mapping=self.mapping("windows.auditeventpolicysubcategories.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"not actually singleton",
                "capability":"windows.auditeventpolicysubcategories",
                "select":{"unexpected":{"value":"x","operation":"equals","datatype":"string"}},
            }},
            "states":{},
            "tests":{"t":{
                "test_title":"audit",
                "capability":"windows.auditeventpolicysubcategories",
                "object":"o",
            }},
        }}
        with self.assertRaisesRegex(ValueError,"unexpected semantics"):
            apply_capability_mapping(doc,mapping)


    def test_nullable_pid_preserves_source_nil_semantics(self):
        mapping=self.mapping("independent.environmentvariable58.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"current process",
                "capability":"independent.environmentvariable58",
                "select":{
                    "pid":{"value":"","operation":"equals","datatype":"int","nil":True},
                    "name":{"value":"PATH","operation":"equals","datatype":"string"},
                },
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        obj=out["assessment"]["objects"]["o"]
        self.assertIsNone(obj["select"]["pid"])
        self.assertEqual(obj["select"]["name"]["operation"],"equal")

    def test_file_traversal_behaviors_become_shared_native_traversal(self):
        mapping=self.mapping("independent.textfilecontent54.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"recursive configs",
                "capability":"independent.textfilecontent54",
                "select":{
                    "path":{"value":"/etc","operation":"equals","datatype":"string"},
                    "filename":{"value":".*\\.conf$","operation":"pattern match","datatype":"string"},
                    "pattern":{"value":"enabled","operation":"pattern match","datatype":"string"},
                    "instance":{"value":"1","operation":"equals","datatype":"int"},
                },
                "behaviors":{
                    "max_depth":"-1",
                    "recurse":"symlinks and directories",
                    "recurse_direction":"down",
                    "recurse_file_system":"local",
                },
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        obj=out["assessment"]["objects"]["o"]
        self.assertEqual(obj["filesystem"],"local")
        self.assertEqual(obj["traversal"],{
            "max_depth":None,
            "recurse":"symlinks_and_directories",
        })
        self.assertNotIn("behaviors",obj)

    def test_full_path_preserves_nondefault_filesystem_scope_without_recursion(self):
        mapping=self.mapping("independent.textfilecontent54.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"scoped exact file",
                "capability":"independent.textfilecontent54",
                "select":{
                    "filepath":{"value":"/etc/example","operation":"equals","datatype":"string"},
                    "pattern":{"value":"x","operation":"pattern match","datatype":"string"},
                    "instance":{"value":"1","operation":"equals","datatype":"int"},
                },
                "behaviors":{"recurse_file_system":"local"},
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        obj=out["assessment"]["objects"]["o"]
        self.assertEqual(obj["filesystem"],"local")
        self.assertNotIn("traversal",obj)

    def test_rpmverifyfile_behaviors_become_explicit_collect_flags(self):
        mapping=self.mapping("linux.rpmverifyfile.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"rpm file",
                "capability":"linux.rpmverifyfile",
                "select":{
                    "name":{"value":"bash","operation":"equals","datatype":"string"},
                    "epoch":{"value":"0","operation":"equals","datatype":"string"},
                    "version":{"value":"5","operation":"equals","datatype":"string"},
                    "release":{"value":"1","operation":"equals","datatype":"string"},
                    "arch":{"value":"x86_64","operation":"equals","datatype":"string"},
                    "filepath":{"value":"/bin/bash","operation":"equals","datatype":"string"},
                },
                "behaviors":{"noconfigfiles":"true","noghostfiles":"false"},
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        collect=out["assessment"]["objects"]["o"]["collect"]
        self.assertTrue(collect["skip_config_files"])
        self.assertFalse(collect["skip_ghost_files"])
        self.assertFalse(collect["skip_link_target"])
        self.assertFalse(collect["skip_file_digest"])
        self.assertNotIn("behaviors",out["assessment"]["objects"]["o"])

    def test_deprecated_rpm_nomd5_remains_a_conversion_error(self):
        mapping=self.mapping("linux.rpmverifyfile.json")
        doc={"assessment":{
            "objects":{"o":{
                "object_title":"legacy rpm file",
                "capability":"linux.rpmverifyfile",
                "select":{
                    "name":{"value":"bash","operation":"equals","datatype":"string"},
                    "epoch":{"value":"0","operation":"equals","datatype":"string"},
                    "version":{"value":"5","operation":"equals","datatype":"string"},
                    "release":{"value":"1","operation":"equals","datatype":"string"},
                    "arch":{"value":"x86_64","operation":"equals","datatype":"string"},
                    "filepath":{"value":"/bin/bash","operation":"equals","datatype":"string"},
                },
                "behaviors":{"nomd5":"true"},
            }},
            "states":{},
            "tests":{},
        }}
        with self.assertRaisesRegex(ValueError,"nomd5"):
            apply_capability_mapping(doc,mapping)


if __name__=="__main__":
    unittest.main()
