#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "compile_foreach_v1", HERE / "compile_foreach_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class ForeachV1Compiler(unittest.TestCase):
    def test_home_dir_to_unix_file_directory_infers_string(self):
        assessment = {
            "objects": {
                "non-system-users": {
                    "capability": "unix.password",
                    "select": {
                        "username": {
                            "value": ".+",
                            "operation": "match",
                            "datatype": "string",
                        }
                    },
                },
                "initialization-files": {
                    "capability": "unix.file",
                    "for_each": {
                        "item": "user",
                        "in": "non-system-users",
                    },
                    "select": {
                        "directory": {
                            "from": "user.home_dir",
                        },
                        "name": {
                            "value": r"^\.[^\s\.]+",
                            "operation": "match",
                            "datatype": "string",
                        },
                    },
                },
            }
        }
        compiled = MOD.compile_assessment_foreach(assessment)
        row = compiled["initialization-files"]
        self.assertEqual(row["source_capability"], "unix.password")
        self.assertEqual(row["source_field"], "home_dir")
        self.assertEqual(row["target_capability"], "unix.file")
        self.assertEqual(row["target_field"], "directory")
        self.assertEqual(row["datatype"], "string")
        selector = row["lowered"]["target_object"]["select"]["directory"]
        self.assertEqual(selector["datatype"], "string")
        self.assertEqual(selector["var_check"], "at least one")

    def test_incompatible_source_target_fields_fail_closed(self):
        assessment = {
            "objects": {
                "users": {
                    "capability": "unix.password",
                },
                "files": {
                    "capability": "unix.file",
                    "for_each": {
                        "item": "user",
                        "in": "users",
                    },
                    "select": {
                        "directory": {
                            "from": "user.last_login",
                        }
                    },
                },
            }
        }
        with self.assertRaises(MOD.ForeachV1Error):
            MOD.compile_assessment_foreach(assessment)

    def test_missing_source_object_fails_closed(self):
        assessment = {
            "objects": {
                "files": {
                    "capability": "unix.file",
                    "for_each": {
                        "item": "user",
                        "in": "missing-users",
                    },
                    "select": {
                        "directory": {
                            "from": "user.home_dir",
                        }
                    },
                }
            }
        }
        with self.assertRaises(MOD.ForeachV1Error):
            MOD.compile_assessment_foreach(assessment)


if __name__ == "__main__":
    unittest.main()
