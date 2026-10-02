#!/usr/bin/env python3
import unittest

from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
    validate_declared_semantic_rules,
    validate_unix_file_object,
)


def entity(value, operation="equal", datatype="string", **extra):
    return {
        "value":value,
        "operation":operation,
        "datatype":datatype,
        **extra,
    }


class SemanticRuleCoverageTests(unittest.TestCase):
    def test_declared_rules_require_executable_coverage_accounting(self):
        mapping={"semantic_validator_rules":[{"id":"a"},{"id":"b"}]}
        self.assertEqual(validate_declared_semantic_rules(mapping,{"a"}),["b"])
        self.assertEqual(validate_declared_semantic_rules(mapping,{"a","b"}),[])


class UnixFileSemanticValidationTests(unittest.TestCase):
    def test_full_path_rejects_traversal(self):
        obj={
            "capability":"unix.file",
            "select":{"full_path":entity("/etc/passwd")},
            "traversal":{
                "max_depth":1,
                "follow_links":False,
                "filesystem":"local",
            },
        }
        rows=validate_unix_file_object(obj)
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.full_path_no_traversal"],
        )
        self.assertEqual(
            set(rows[0]["fields"]),
            {"traversal"},
        )

    def test_full_path_rejects_any_traversal(self):
        rows=validate_unix_file_object({
            "capability":"unix.file",
            "select":{"full_path":entity("/etc/.*",operation="match")},
            "traversal":{"max_depth":1,"follow_links":False,"filesystem":"same"},
        })
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.full_path_no_traversal"],
        )

    def test_directory_pattern_rejects_traversal(self):
        rows=validate_unix_file_object({
            "capability":"unix.file",
            "select":{
                "directory":entity("/etc/.*",operation="match"),
                "name":entity("passwd"),
            },
            "traversal":{
                "max_depth":2,
                "follow_links":False,
                "filesystem":"same",
            },
        })
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.pattern_directory_no_traversal"],
        )
        self.assertEqual(
            set(rows[0]["fields"]),
            {"traversal"},
        )

    def test_empty_name_and_directory_itself_semantics(self):
        literal=validate_unix_file_object({
            "capability":"unix.file",
            "select":{"directory":entity("/etc"),"name":entity("")},
        })
        self.assertEqual([r["code"] for r in literal],["unix.file.name_empty"])

        for name in (
            None,
            entity("",operation="match"),
            entity({"variable":"filename-var"}),
        ):
            with self.subTest(name=name):
                rows=validate_unix_file_object({
                    "capability":"unix.file",
                    "select":{"directory":entity("/etc"),"name":name},
                })
                self.assertEqual(rows,[])

    def test_file_hash_reuses_file_selection_semantics(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "h":{
                        "capability":"file.hash",
                        "select":{"full_path":entity("/etc/passwd")},
                        "traversal":{
                            "max_depth":1,
                            "follow_links":False,
                            "filesystem":"local",
                        },
                        "collect":{"algorithm":"sha256"},
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        self.assertIn(
            "file.hash.full_path_no_traversal",
            {row["code"] for row in rows},
        )

    def test_filter_state_capability_must_match_object(self):
        doc={
            "assessment":{
                "objects":{
                    "source":{"capability":"unix.file"},
                    "filtered":{"capability":"unix.file","set":{
                        "operator":"union",
                        "operands":[{"object":"source","filters":[{"state":"filter-state","action":"include"}]}]
                    }},
                    "o":{"capability":"unix.file","set":{
                        "operator":"union",
                        "operands":[{"object":"source","filters":[
                            {"state":"s","action":"include"}
                        ]}]
                    }}
                },
                "states":{
                    "s":{"capability":"linux.rpminfo"}
                },
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("object.filter_state_capability",{r["code"] for r in rows})

    def test_deep_nested_set_filter_capability_is_validated(self):
        expression={"operator":"union","operands":[{"object":"source","filters":[{"state":"wrong","action":"include"}]}]}
        for _ in range(31):
            expression={"operator":"union","operands":[{"set":expression}]}
        doc={
            "assessment":{
                "objects":{
                    "source":{"capability":"unix.file"},
                    "o":{"capability":"unix.file","set":expression},
                },
                "states":{"wrong":{"capability":"windows.file"}},
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("object.filter_state_capability",{r["code"] for r in rows})

    def test_nested_set_filter_capability_is_validated(self):
        doc={
            "assessment":{
                "objects":{
                    "source":{"capability":"unix.file"},
                    "o":{"capability":"unix.file","set":{
                        "operator":"union","operands":[{"set":{
                            "operator":"union","operands":[{
                                "object":"source","filters":[{"state":"wrong","action":"include"}]
                            }]
                        }}]
                    }},
                },
                "states":{"wrong":{"capability":"windows.file"}},
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("object.filter_state_capability",{r["code"] for r in rows})

    def test_set_object_reference_and_capability_are_validated(self):
        missing={
            "assessment":{
                "objects":{
                    "o":{"capability":"unix.file","set":{
                        "operator":"union",
                        "operands":[{"object":"missing","filters":[]}]
                    }}
                },
                "states":{},
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(missing)
        self.assertIn("object.set_object_missing",{r["code"] for r in rows})

        mismatch={
            "assessment":{
                "objects":{
                    "other":{"capability":"linux.rpminfo"},
                    "o":{"capability":"unix.file","set":{
                        "operator":"union",
                        "operands":[{"object":"other","filters":[]}]
                    }}
                },
                "states":{},
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(mismatch)
        self.assertIn("object.set_object_capability",{r["code"] for r in rows})

    def test_test_object_state_capabilities_are_validated(self):
        doc={
            "assessment":{
                "objects":{"o":{"capability":"unix.file"}},
                "states":{"s":{"capability":"linux.rpminfo"}},
                "tests":{
                    "t":{
                        "capability":"unix.file",
                        "object":"o",
                        "states":["s"],
                    }
                },
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertEqual([r["code"] for r in rows],["test.state_capability"])


    def test_windows_hierarchy_pattern_key_rejects_traversal(self):
        for capability in ("windows.registry","windows.ntuser","windows.regkeyeffectiverights53"):
            with self.subTest(capability=capability):
                rows=validate_assessment_capability_semantics({
                    "assessment":{
                        "objects":{
                            "o":{
                                "capability":capability,
                                "select":{"key":entity("Software/.*",operation="match")},
                                "traversal":{"max_depth":2},
                            }
                        },
                        "states":{},
                        "tests":{},
                    }
                })
                self.assertIn(
                    f"{capability}.pattern_key_no_traversal",
                    {row["code"] for row in rows},
                )


    def test_ntuser_registry_type_value_datatype(self):
        doc={
            "assessment":{
                "objects":{},
                "states":{
                    "type":{"capability":"windows.ntuser","state":{
                        "field":"type","value":"dword","operation":"equal","datatype":"string"
                    }},
                    "value":{"capability":"windows.ntuser","state":{
                        "field":"value","value":"1","operation":"equal","datatype":"string"
                    }},
                },
                "tests":{
                    "t":{"capability":"windows.ntuser","states":["type","value"]}
                },
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("windows.ntuser.value_type_datatype",{r["code"] for r in rows})

    def test_pwpolicy_auth_pair_and_equal_only_fields(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"macos.pwpolicy512",
                        "select":{
                            "authenticator":entity("admin"),
                            "authenticator_password":None,
                            "directory_node":entity("/LDAPv3/example",operation="match"),
                            "xpath":entity("/dict/key/text()",operation="match"),
                        },
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        codes={r["code"] for r in rows}
        self.assertIn("macos.pwpolicy512.auth_pair",codes)
        self.assertIn("macos.pwpolicy512.directory_node_equal",codes)
        self.assertIn("macos.pwpolicy512.xpath_equal",codes)

    def test_lockout_policy_negative_literal_time_is_rejected(self):
        doc={"assessment":{"objects":{},"states":{
            "duration":{"capability":"windows.lockoutpolicy","state":{
                "field":"lockout_duration","value":-1,"datatype":"integer","operation":"equal"}}
        },"tests":{"t":{"capability":"windows.lockoutpolicy","states":["duration"]}}}}
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("windows.lockoutpolicy.nonnegative_time_values",{row["code"] for row in rows})

    def test_lockout_policy_variable_time_is_not_guessed_statically(self):
        doc={"assessment":{"objects":{},"states":{
            "duration":{"capability":"windows.lockoutpolicy","state":{
                "field":"lockout_duration","value":{"variable":"duration"},"datatype":"integer","operation":"equal"}}
        },"tests":{"t":{"capability":"windows.lockoutpolicy","states":["duration"]}}}}
        rows=validate_assessment_capability_semantics(doc)
        self.assertNotIn("windows.lockoutpolicy.nonnegative_time_values",{row["code"] for row in rows})

    def test_wuaupdatesearcher_xml_date_lexical_form(self):
        bad={
            "assessment":{
                "objects":{},
                "states":{
                    "s":{"capability":"windows.wuaupdatesearcher","state":{
                        "field":"last_deployment_change_time",
                        "value":"2026-10-02T00:00:00",
                        "operation":"equal","datatype":"string"
                    }}
                },
                "tests":{
                    "t":{"capability":"windows.wuaupdatesearcher","states":["s"]}
                },
            }
        }
        rows=validate_assessment_capability_semantics(bad)
        self.assertIn("windows.wuaupdatesearcher.date_lexical_form",{r["code"] for r in rows})

        good={
            "assessment":{
                "objects":{},
                "states":{
                    "s":{"capability":"windows.wuaupdatesearcher","state":{
                        "field":"last_deployment_change_time",
                        "value":"2026-10-02",
                        "operation":"equal","datatype":"string"
                    }}
                },
                "tests":{
                    "t":{"capability":"windows.wuaupdatesearcher","states":["s"]}
                },
            }
        }
        self.assertEqual(validate_assessment_capability_semantics(good),[])

    def test_wuaupdatesearcher_source_path_repair_is_filterable_state(self):
        document = {
            "assessment": {
                "objects": {},
                "variables": {},
                "states": {
                    "source-path": {
                        "capability": "windows.wuaupdatesearcher",
                        "state_title": "offline catalog path",
                        "state": {
                            "field": "source_path",
                            "value": "C:\\\\wsusscn2.cab",
                            "datatype": "string",
                            "operation": "equal",
                        },
                    }
                },
                "tests": {
                    "update-source": {
                        "capability": "windows.wuaupdatesearcher",
                        "test_title": "offline source path",
                        "states": ["source-path"],
                    }
                },
            }
        }
        self.assertEqual(validate_assessment_capability_semantics(document), [])

    def test_valid_graph_is_clean(self):
        doc={
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"unix.file",
                        "select":{
                            "directory":entity("/etc"),
                            "name":entity("passwd"),
                        },
                    }
                },
                "states":{
                    "filter-state":{"capability":"unix.file"},
                    "required-state":{"capability":"unix.file"},
                },
                "tests":{
                    "t":{
                        "capability":"unix.file",
                        "object":"o",
                        "states":["required-state"],
                    }
                },
            }
        }
        self.assertEqual(validate_assessment_capability_semantics(doc),[])


if __name__=="__main__":
    unittest.main()
