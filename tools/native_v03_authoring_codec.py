#!/usr/bin/env python3
"""Accepted v0.3 compact Assessment authoring -> explicit canonical Assessment.

This is a source-language expansion step, not runtime inference. Every accepted
compact predicate is turned into the existing typed canonical predicate BEFORE
schema/capability validation or compilation. SCAP 0.2 and canonical 0.3 are
preserved. This module deliberately rejects the unaccepted compare_as syntax.
"""
from __future__ import annotations

from copy import deepcopy

from research_type_syntax_codec import TypeSyntaxError, to_canonical


def _reject_compare_as(value, path="$"):
    if isinstance(value, dict):
        if "compare_as" in value:
            raise TypeSyntaxError(
                f"{path}: compare_as is not a supported SCAP-NG 0.3 authoring field; "
                "use a typed operator such as rpm_evr_greater_than"
            )
        for key, item in value.items():
            _reject_compare_as(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_compare_as(item, f"{path}[{index}]")


def canonicalize_assessment_document(document):
    """Return an independent, validated-to-be-expandable canonical document.

    Native 0.3 Assessments ONLY; the caller must run existing JSON Schema,
    capability and semantic validators against the returned canonical document.
    Variable/Input contracts and uncertain array/dynamic operands are retained.
    """
    if not isinstance(document, dict):
        return document
    assessment = document.get("assessment")
    if not isinstance(assessment, dict):
        return deepcopy(document)
    version = (assessment.get("specification") or {}).get("version")
    if version != "0.3.0":
        return deepcopy(document)
    _reject_compare_as(document)
    return to_canonical(document)
