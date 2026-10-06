from pathlib import Path

import yaml

from tools.normalize_p1_projection import (
    apply_p1_projection_normalization,
    plan_p1_projection_normalization,
)


def base_document():
    return {
        "assessment": {
            "id": "example",
            "version": 1,
            "objects": {
                "users": {
                    "capability": "unix.password",
                },
                "files": {
                    "capability": "unix.file",
                    "select": {
                        "path": {
                            "operation": "equals",
                            "datatype": "string",
                            "variable_check": "at least one",
                            "value": {"variable": "home-dirs"},
                        }
                    },
                },
            },
            "variables": {
                "home-dirs": {
                    "title": "home directories",
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
            "tests": {},
            "evaluate": {},
        }
    }


def test_single_use_projection_is_p1_candidate():
    doc = base_document()
    plan = plan_p1_projection_normalization(doc)
    assert len(plan) == 1
    row = plan[0]
    assert row["classification"] == "P1_flattened_projection"
    assert row["variable"] == "home-dirs"
    assert row["projection"] == {"object": "users", "field": "home_dir"}
    assert row["variable_check"] == "at least one"


def test_p1_application_inlines_projection_without_binding_scope():
    doc = base_document()
    normalized, report = apply_p1_projection_normalization(doc)

    value = normalized["assessment"]["objects"]["files"]["select"]["path"]["value"]
    assert value == {
        "projection": {
            "object": "users",
            "field": "home_dir",
        }
    }
    assert "variables" not in normalized["assessment"]
    assert normalized["assessment"]["objects"]["files"]["select"]["path"]["variable_check"] == "at least one"

    assert report["semantic_effect"] == "none"
    assert report["creates_binding_scope"] is False
    assert report["applied"][0]["source_variable"]["title"] == "home directories"


def test_multi_use_projection_is_preserved():
    doc = base_document()
    doc["assessment"]["objects"]["other"] = {
        "capability": "unix.file",
        "select": {
            "path": {
                "operation": "equals",
                "datatype": "string",
                "variable_check": "all",
                "value": {"variable": "home-dirs"},
            }
        },
    }
    assert plan_p1_projection_normalization(doc) == []


def test_direct_variable_test_identity_blocks_normalization():
    doc = base_document()
    doc["assessment"]["tests"]["variable-value-test"] = {
        "capability": "variable.value",
        "variable": {"variable": "home-dirs"},
    }
    # Two semantic consumers now exist; the named Variable must survive.
    assert plan_p1_projection_normalization(doc) == []


def test_datatype_mismatch_blocks_normalization():
    doc = base_document()
    doc["assessment"]["objects"]["files"]["select"]["path"]["datatype"] = "integer"
    assert plan_p1_projection_normalization(doc) == []


def test_missing_variable_check_blocks_normalization():
    doc = base_document()
    del doc["assessment"]["objects"]["files"]["select"]["path"]["variable_check"]
    assert plan_p1_projection_normalization(doc) == []


def test_projection_into_another_variable_is_not_first_p1_class():
    doc = base_document()
    # Remove the Object consumer and make the projection feed one transform.
    doc["assessment"]["objects"]["files"]["select"]["path"]["value"] = "/fixed"
    doc["assessment"]["variables"]["derived"] = {
        "kind": "local",
        "datatype": "string",
        "expression": {
            "concat": [
                {"variable": "home-dirs"},
                {"literal": "/.ssh"},
            ]
        },
    }
    assert plan_p1_projection_normalization(doc) == []


def test_record_field_projection_preserved():
    doc = base_document()
    doc["assessment"]["variables"]["home-dirs"]["expression"]["values"] = {
        "object": "users",
        "field": "record",
        "record_field": "home_dir",
    }
    normalized, report = apply_p1_projection_normalization(doc)
    value = normalized["assessment"]["objects"]["files"]["select"]["path"]["value"]
    assert value["projection"]["record_field"] == "home_dir"
    assert report["applied"][0]["projection"]["record_field"] == "home_dir"


def test_state_expected_value_is_supported():
    doc = base_document()
    doc["assessment"]["objects"]["files"]["select"]["path"]["value"] = "/tmp"
    doc["assessment"]["states"] = {
        "expected-owner": {
            "state": {
                "field": "owner",
                "operation": "equals",
                "datatype": "string",
                "variable_check": "all",
                "value": {"variable": "home-dirs"},
            }
        }
    }
    normalized, report = apply_p1_projection_normalization(doc)
    value = normalized["assessment"]["states"]["expected-owner"]["state"]["value"]
    assert value == {"projection": {"object": "users", "field": "home_dir"}}
    assert len(report["applied"]) == 1


def test_rhel9_sv257889_real_projection_pattern_normalizes_losslessly_in_shape():
    root = Path(__file__).resolve().parents[1]
    source = yaml.safe_load(
        (
            root
            / "research/assessment-simplification/samples/rhel_9/assessments/automated"
            / "niwc.rhel_9.SV-257889.automated.assessment.yaml"
        ).read_text()
    )

    plan = plan_p1_projection_normalization(source)
    assert {row["variable"] for row in plan} == {
        "home-directories-non-system-users-variable",
        "home-directory-root-user-variable",
    }

    normalized, report = apply_p1_projection_normalization(source)
    assessment = normalized["assessment"]

    assert "variables" not in assessment

    non_system_path = assessment["objects"][
        "local-initialization-files-non-system-users-object"
    ]["select"]["path"]
    assert non_system_path["variable_check"] == "at least one"
    assert non_system_path["value"] == {
        "projection": {
            "object": "only-non-system-users-uid-999-home-dirs-excluding-root-object",
            "field": "home_dir",
        }
    }

    root_path = assessment["objects"][
        "local-initialization-files-root-user-object"
    ]["select"]["path"]
    assert root_path["variable_check"] == "at least one"
    assert root_path["value"] == {
        "projection": {
            "object": "only-root-users-uid-0-home-dirs-excluding-root-directory-object",
            "field": "home_dir",
        }
    }

    assert len(report["applied"]) == 2
    assert all(row["classification"] == "P1_flattened_projection" for row in report["applied"])


def test_integer_native_projection_is_inside_initial_p1_envelope():
    doc=base_document()
    var=doc["assessment"]["variables"]["home-dirs"]
    var["datatype"]="integer"
    entity=doc["assessment"]["objects"]["files"]["select"]["path"]
    entity["datatype"]="integer"
    plan=plan_p1_projection_normalization(doc)
    assert len(plan)==1
    assert plan[0]["datatype"]=="integer"


def test_unproven_native_datatype_fails_closed():
    doc=base_document()
    var=doc["assessment"]["variables"]["home-dirs"]
    var["datatype"]="boolean"
    entity=doc["assessment"]["objects"]["files"]["select"]["path"]
    entity["datatype"]="boolean"
    assert plan_p1_projection_normalization(doc)==[]
