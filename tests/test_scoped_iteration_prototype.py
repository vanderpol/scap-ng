from pathlib import Path
import json

import pytest
from jsonschema import Draft202012Validator

from tools.scoped_iteration_semantics import validate_for_each_scopes


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "research/for-each-0.3.0/scoped-value-flow.prototype.schema.json").read_text()
)
VALIDATOR = Draft202012Validator(SCHEMA)


def assert_schema_valid(instance):
    errors = sorted(VALIDATOR.iter_errors(instance), key=lambda e: list(e.path))
    assert not errors, "\n".join(e.message for e in errors)


def test_projection_reference_shape():
    assert_schema_valid({
        "projection": {
            "object": "discovered-config-paths",
            "field": "subexpression",
        }
    })


def test_binding_reference_shape():
    assert_schema_valid({
        "binding": "user",
        "field": "home_dir",
    })


def test_nested_for_each_shape_and_lexical_scope():
    scopes = [
        {
            "binding": "user",
            "object": "interactive-users",
            "check_existence": "at_least_one_exists",
            "check": "all",
        },
        {
            "binding": "file",
            "object": {
                "object_title": "files in bound user's home",
                "capability": "unix.file",
                "select": {
                    "path": {
                        "value": {
                            "binding": "user",
                            "field": "home_dir",
                        }
                    }
                },
            },
            "check_existence": "at_least_one_exists",
            "check": "all",
        },
    ]
    assert_schema_valid(scopes)

    final_test = {
        "object": {
            "capability": "unix.file",
            "select": {
                "filepath": {
                    "value": {
                        "binding": "file",
                        "field": "filepath",
                    }
                }
            },
        },
        "state": {
            "owner": {
                "value": {
                    "binding": "user",
                    "field": "username",
                }
            }
        },
    }
    assert validate_for_each_scopes(scopes, final_test=final_test) == []


def test_binding_shadowing_is_rejected_semantically():
    scopes = [
        {
            "binding": "user",
            "object": "interactive-users",
            "check_existence": "at_least_one_exists",
            "check": "all",
        },
        {
            "binding": "user",
            "object": "other-users",
            "check_existence": "at_least_one_exists",
            "check": "all",
        },
    ]
    assert any(
        "shadowing" in msg
        for msg in validate_for_each_scopes(scopes)
    )


def test_scope_cannot_reference_its_own_binding_source():
    scopes = [
        {
            "binding": "user",
            "object": {
                "capability": "unix.password",
                "select": {
                    "username": {
                        "value": {
                            "binding": "user",
                            "field": "username",
                        }
                    }
                },
            },
            "check_existence": "at_least_one_exists",
            "check": "all",
        }
    ]
    assert any(
        "not yet in scope" in msg
        for msg in validate_for_each_scopes(scopes)
    )


def test_final_test_cannot_reference_undeclared_binding():
    scopes = [
        {
            "binding": "user",
            "object": "interactive-users",
            "check_existence": "at_least_one_exists",
            "check": "all",
        }
    ]
    final_test = {
        "state": {
            "owner": {
                "value": {
                    "binding": "missing",
                    "field": "username",
                }
            }
        }
    }
    assert any(
        "undeclared binding" in msg
        for msg in validate_for_each_scopes(scopes, final_test=final_test)
    )


def test_scope_shape_requires_explicit_existence_and_check():
    invalid = [
        {
            "binding": "user",
            "object": "interactive-users",
        }
    ]
    assert list(VALIDATOR.iter_errors(invalid))
