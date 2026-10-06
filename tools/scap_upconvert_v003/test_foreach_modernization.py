#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scap_upconvert_v003.foreach_modernization import (
    REWRITE_ID,
    modernize_foreach_v1,
)
from scap_upconvert_v003.convert_collection_review import (
    postprocess_automated_assessment,
)
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
)


def fixture():
    return {
        "assessment": {
            "id": "foreach-converter-fixture",
            "version": 1,
            "assessment_title": "Foreach converter fixture",
            "mode": "automated",
            "class": "compliance",
            "purpose": "assessment",
            "specification": {
                "id": "scap-ng.pre-alpha.assessment",
                "version": "0.3.0",
            },
            "objects": {
                "users": {
                    "object_title": "Non-system users",
                    "capability": "unix.password",
                    "select": {
                        "username": {
                            "value": ".+",
                            "operation": "match",
                            "datatype": "string",
                        }
                    },
                },
                "files": {
                    "object_title": "Initialization files",
                    "capability": "unix.file",
                    "select": {
                        "directory": {
                            "value": {"variable": "home-dirs"},
                            "operation": "equal",
                            "datatype": "string",
                            "variable_match": "any",
                        },
                        "name": {
                            "value": r"^\.[^\s\.]+",
                            "operation": "match",
                            "datatype": "string",
                        },
                    },
                    "filesystem": "any",
                },
            },
            "variables": {
                "home-dirs": {
                    "title": "Home directories",
                    "kind": "local",
                    "datatype": "string",
                    "expression": {
                        "values": {
                            "object": "users",
                            "field": "home_dir",
                        }
                    },
                }
            },
            "states": {},
            "tests": {
                "test-files": {
                    "test_title": "Initialization files",
                    "reported_elements": "all",
                    "capability": "unix.file",
                    "object": "files",
                    "check_existence": "optional",
                    "check": "all",
                }
            },
            "evaluate": {"test": "test-files"},
        }
    }


class ForeachConverterModernization(unittest.TestCase):

    def faithful_pre_mapping_fixture(self):
        return {
            "assessment": {
                "id": "faithful-pre-mapping",
                "version": 1,
                "assessment_title": "Faithful pre-mapping graph",
                "mode": "automated",
                "class": "compliance",
                "purpose": "assessment",
                "collections": {
                    "users-collection": {
                        "collection_title": "Users",
                        "capability": "unix.password",
                        "select": {
                            "username": {
                                "value": ".+",
                                "operation": "pattern match",
                                "datatype": "string",
                            }
                        },
                    },
                    "files-collection": {
                        "collection_title": "Files",
                        "capability": "unix.file",
                        "select": {
                            "path": {
                                "value": {"variable": "home-dirs"},
                                "operation": "equals",
                                "datatype": "string",
                                "variable_check": "at least one",
                            },
                            "filename": {
                                "value": r"^\\.[^\\s\\.]+",
                                "operation": "pattern match",
                                "datatype": "string",
                            },
                        },
                    },
                },
                "variables": {
                    "home-dirs": {
                        "title": "Home directories",
                        "kind": "local",
                        "datatype": "string",
                        "expression": {
                            "values": {
                                "collection": "users-collection",
                                "field": "home_dir",
                            }
                        },
                    }
                },
                "tests": {
                    "test-files": {
                        "test_title": "Files",
                        "capability": "unix.file",
                        "collection": "files-collection",
                        "assertion": {
                            "existence": "any_exist",
                            "item_quantifier": "all",
                        },
                    }
                },
                "evaluate": {"test": "test-files"},
            }
        }

    def test_postprocess_default_stays_02_and_faithful(self):
        source = self.faithful_pre_mapping_fixture()
        result, report = postprocess_automated_assessment(source)
        self.assertIsNone(report)
        assessment = result["assessment"]
        self.assertEqual(assessment["specification"]["version"], "0.2.0")
        self.assertIn("home-dirs", assessment["variables"])
        self.assertNotIn("for_each", assessment["objects"]["files-object"])
        self.assertEqual(
            assessment["objects"]["files-object"]["select"]["path"]["value"],
            {"variable": "home-dirs"},
        )

    def test_postprocess_03_opt_in_maps_then_rewrites(self):
        source = self.faithful_pre_mapping_fixture()
        result, report = postprocess_automated_assessment(
            source,
            target_ng_version="0.3.0",
            modernize_foreach=True,
        )
        assessment = result["assessment"]
        self.assertEqual(assessment["specification"]["version"], "0.3.0")
        self.assertTrue(report["rewrite_performed"], report)
        self.assertNotIn("variables", assessment)
        self.assertEqual(
            assessment["objects"]["files-object"]["for_each"],
            {"item": "user", "in": "users-object"},
        )
        self.assertEqual(
            assessment["objects"]["files-object"]["select"]["directory"],
            {"from": "user.home_dir"},
        )
        self.assertEqual(
            validate_assessment_capability_semantics(result),
            [],
        )

    def test_postprocess_rejects_modernization_on_02(self):
        with self.assertRaisesRegex(
            ValueError,
            "requires target SCAP-NG 0.3.0",
        ):
            postprocess_automated_assessment(
                self.faithful_pre_mapping_fixture(),
                modernize_foreach=True,
            )

    def test_default_disabled_is_identity(self):
        source = fixture()
        result, report = modernize_foreach_v1(source)
        self.assertEqual(result, source)
        self.assertFalse(report["enabled"])
        self.assertFalse(report["rewrite_performed"])
        self.assertEqual(report["rewrite_id"], REWRITE_ID)

    def test_exact_v1_rewrite(self):
        source = fixture()
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertTrue(report["rewrite_performed"], report)
        self.assertEqual(len(report["applied"]), 1)
        assessment = result["assessment"]
        self.assertNotIn("variables", assessment)
        files = assessment["objects"]["files"]
        self.assertEqual(
            files["for_each"],
            {"item": "user", "in": "users"},
        )
        self.assertEqual(
            files["select"]["directory"],
            {"from": "user.home_dir"},
        )
        self.assertEqual(
            validate_assessment_capability_semantics(result),
            [],
        )

    def test_wrong_quantifier_fails_closed(self):
        source = fixture()
        source["assessment"]["objects"]["files"]["select"]["directory"][
            "variable_match"
        ] = "all"
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        self.assertFalse(report["rewrite_performed"])
        self.assertIn(
            "target_variable_match_not_any",
            report["review_required"][0]["reasons"],
        )

    def test_second_consumer_fails_closed(self):
        source = fixture()
        source["assessment"]["states"]["uses-home"] = {
            "state_title": "Uses same Variable elsewhere",
            "capability": "unix.file",
            "state": {
                "field": "directory",
                "value": {"variable": "home-dirs"},
                "operation": "equal",
                "datatype": "string",
                "match": "all",
                "variable_match": "any",
                "existence": "some",
            },
        }
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        self.assertIn(
            "single_target_consumer_required",
            report["review_required"][0]["reasons"],
        )

    def test_helper_target_fails_closed(self):
        source = fixture()
        source["assessment"]["tests"]["test-files"]["object"] = "users"
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        self.assertIn(
            "target_not_directly_tested",
            report["review_required"][0]["reasons"],
        )

    def test_datatype_mismatch_fails_closed(self):
        source = fixture()
        source["assessment"]["variables"]["home-dirs"]["datatype"] = "integer"
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        self.assertIn(
            "variable_datatype_mismatch",
            report["review_required"][0]["reasons"],
        )

    def test_second_target_variable_fails_closed(self):
        source = fixture()
        source["assessment"]["variables"]["other"] = {
            "title": "Other value",
            "kind": "constant",
            "datatype": "string",
            "expression": {"literal": "root"},
        }
        source["assessment"]["objects"]["files"]["select"]["name"] = {
            "value": {"variable": "other"},
            "operation": "equal",
            "datatype": "string",
            "variable_match": "any",
        }
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        rows = [
            row for row in report["review_required"]
            if row.get("variable") == "home-dirs"
        ]
        self.assertIn(
            "independent_additional_variable_selector",
            rows[0]["reasons"],
        )


    def test_pinned_rhel_sv257889_source_rewrites_through_converter_path(self):
        root = Path(__file__).resolve().parents[2]
        source = ET.parse(
            root
            / "research/assessment-simplification/evidence/rhel_9/SV-257889/source-oval.xml"
        ).getroot()
        faithful, error = lower_definition(
            source,
            "oval:mil.disa.stig.defs:def:230325",
            "foreach-production-rhel",
            collection_graph=True,
        )
        self.assertIsNone(error)
        self.assertIsNotNone(faithful)

        modern, report = postprocess_automated_assessment(
            faithful,
            target_ng_version="0.3.0",
            modernize_foreach=True,
        )
        self.assertTrue(report["rewrite_performed"], report)
        self.assertEqual(report["rewrite_id"], REWRITE_ID)
        self.assertEqual(len(report["applied"]), 2, report)

        assessment = modern["assessment"]
        self.assertEqual(assessment["specification"]["version"], "0.3.0")
        self.assertNotIn("variables", assessment)
        foreach_objects = {
            object_id: obj
            for object_id, obj in assessment["objects"].items()
            if isinstance(obj, dict) and "for_each" in obj
        }
        self.assertEqual(len(foreach_objects), 2, foreach_objects)
        for obj in foreach_objects.values():
            self.assertEqual(obj["for_each"]["item"], "user")
            bound = [
                spec["from"]
                for spec in obj.get("select", {}).values()
                if isinstance(spec, dict) and "from" in spec
            ]
            self.assertEqual(len(bound), 1)
            self.assertTrue(bound[0].endswith(".home_dir"))

        diagnostics = validate_assessment_capability_semantics(modern)
        self.assertFalse(
            [
                row
                for row in diagnostics
                if str(row.get("code", "")).startswith("foreach.")
            ],
            diagnostics,
        )

    def test_02_never_rewrites(self):
        source = fixture()
        source["assessment"]["specification"]["version"] = "0.2.0"
        result, report = modernize_foreach_v1(source, enabled=True)
        self.assertEqual(result, source)
        self.assertFalse(report["rewrite_performed"])
        self.assertEqual(
            report["review_required"][0]["reasons"],
            ["foreach_v1_requires_0.3.0"],
        )


if __name__ == "__main__":
    unittest.main()
