#!/usr/bin/env python3
import unittest

from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
    validate_unix_file_object,
)


def entity(value, operation="equal", datatype="string", **extra):
    return {
        "value":value,
        "operation":operation,
        "datatype":datatype,
        **extra,
    }


class UnixFileSemanticValidationTests(unittest.TestCase):
    def test_full_path_rejects_traversal(self):
        obj={
            "capability":"unix.file",
            "select":{"full_path":entity("/etc/passwd")},
            "traversal":{
                "max_depth":1,
                "follow_symlinks":False,
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
            "traversal":{"max_depth":1,"follow_symlinks":False,"filesystem":"same"},
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
                "follow_symlinks":False,
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
                            "follow_symlinks":False,
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
