#!/usr/bin/env python3
import unittest

from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
    validate_unix_file_object,
)


def entity(value, operation="equals", datatype="string", **extra):
    return {
        "value":value,
        "operation":operation,
        "datatype":datatype,
        **extra,
    }


class UnixFileSemanticValidationTests(unittest.TestCase):
    def test_filepath_rejects_recursion_behaviors(self):
        obj={
            "capability":"unix.file",
            "select":{"filepath":entity("/etc/passwd")},
            "behaviors":{
                "max_depth":1,
                "recurse":"directories",
                "recurse_direction":"down",
            },
        }
        rows=validate_unix_file_object(obj)
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.filepath_no_recursion_behaviors"],
        )
        self.assertEqual(
            set(rows[0]["fields"]),
            {"max_depth","recurse","recurse_direction"},
        )

    def test_filepath_pattern_rejects_defined_filesystem(self):
        rows=validate_unix_file_object({
            "capability":"unix.file",
            "select":{"filepath":entity("/etc/.*",operation="pattern match")},
            "behaviors":{"recurse_file_system":"defined"},
        })
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.filepath_pattern_defined_filesystem"],
        )

    def test_path_pattern_rejects_recursion_controls(self):
        rows=validate_unix_file_object({
            "capability":"unix.file",
            "select":{
                "path":entity("/etc/.*",operation="pattern match"),
                "filename":entity("passwd"),
            },
            "behaviors":{
                "max_depth":2,
                "recurse":"directories",
                "recurse_direction":"down",
                "recurse_file_system":"defined",
            },
        })
        self.assertEqual(
            [r["code"] for r in rows],
            ["unix.file.path_pattern_no_recursion_behaviors"],
        )
        self.assertEqual(
            set(rows[0]["fields"]),
            {"max_depth","recurse","recurse_direction","recurse_file_system"},
        )

    def test_empty_filename_requires_defined_special_semantics(self):
        literal=validate_unix_file_object({
            "capability":"unix.file",
            "select":{"path":entity("/etc"),"filename":entity("")},
        })
        self.assertEqual([r["code"] for r in literal],["unix.file.filename_empty"])

        for filename in (
            entity("",nil=True),
            entity("",operation="pattern match"),
            entity({"variable":"filename-var"}),
        ):
            with self.subTest(filename=filename):
                rows=validate_unix_file_object({
                    "capability":"unix.file",
                    "select":{"path":entity("/etc"),"filename":filename},
                })
                self.assertEqual(rows,[])

    def test_filter_state_capability_must_match_object(self):
        doc={
            "assessment":{
                "objects":{
                    "o":{"capability":"unix.file","filters":[
                        {"state":"s","action":"include"}
                    ]}
                },
                "states":{
                    "s":{"capability":"linux.rpminfo"}
                },
                "tests":{},
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("object.filter_state_capability",{r["code"] for r in rows})

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
                            "path":entity("/etc"),
                            "filename":entity("passwd"),
                        },
                        "filters":[{"state":"filter-state","action":"include"}],
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
