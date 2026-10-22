#!/usr/bin/env python3
"""Construct the strict accepted 0.4 field/condition grammar in memory.

This is a promotion candidate, not a replacement for the complete versioned
Assessment schema until native capability and converter gates pass.
Refs #248 #239.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "schema/v0.4.0/assessment-language.schema.json"


def build():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    defs = source["$defs"]
    paired = {"$ref": "#/$defs/paired_requirement"}

    # Preserve the source's full native operator/value coverage. Only the
    # authored field-presence key is renamed; no operator is reinterpreted.
    field = deepcopy(defs["inherited_field_predicate"])
    field["properties"]["field_requirement"] = field["properties"].pop("require")
    defs["canonical_field_predicate"] = field

    defs["canonical_condition"] = {"oneOf": [
        {
            "type": "object",
            "required": ["fields"],
            "properties": {
                "field_requirement": paired,
                "fields": {
                    "type": "object",
                    "minProperties": 1,
                    "additionalProperties": {
                        "$ref": "#/$defs/canonical_field_predicate"
                    },
                },
            },
            "additionalProperties": False,
            "description": "One complete OVAL State-sized condition. Distinct field predicates are ANDed.",
        },
        *[
            {
                "type": "object",
                "required": [operator],
                "properties": {
                    "field_requirement": paired,
                    operator: {
                        "type": "array",
                        "minItems": 1,
                        "items": {"$ref": "#/$defs/canonical_condition"},
                    },
                },
                "additionalProperties": False,
                "description": f"Logical {operator.upper()} of complete conditions.",
            }
            for operator in ("and", "or", "one", "xor")
        ],
    ]}
    defs["canonical_all_items_requirement"] = {
        "type": "object",
        "required": ["items", "all_items_must"],
        "properties": {
            "items": {"enum": ["one_or_more", "may_be_absent"]},
            "field_requirement": paired,
            "all_items_must": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/$defs/canonical_condition"},
            },
        },
        "additionalProperties": False,
        "description": "Item population is distinct from field requirement and condition logic.",
    }
    # A standalone candidate definition permits direct validation of the
    # new Test.require structure without weakening the existing published
    # Test/legacy exceptions or pretending native capability parity.
    defs["canonical_test_requirement"] = {
        "$ref": "#/$defs/canonical_all_items_requirement"
    }
    return source
