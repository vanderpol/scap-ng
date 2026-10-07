#!/usr/bin/env python3
"""Research-only semantic probe for typed /etc/fstab modernization.

This module intentionally models only the bounded proof class documented in
research/assessment-simplification/fstab-13/README.md:

* source text collection is complete;
* the source textfilecontent Object selects instance 1;
* the projected fstab option field is nonempty and comma-delimited;
* the proposed typed collector preserves source row order and selects the first
  matching record before Test evaluation.

Non-complete collection flags and parser/regex lexical differences are outside
this first proof class and must remain review-required.
"""
from __future__ import annotations

from oval_result_truth_tables import (
    TRUE,
    FALSE,
    ERROR,
    UNKNOWN,
    aggregate_operator,
    evaluate_collected_object_test,
)

REWRITE_ID = "linux.fstab.first-occurrence-option.v1"


def _first_source_row(rows):
    rows = list(rows)
    return rows[0] if rows else None


def faithful_split_variable_complete(rows, required_option):
    """Model the complete-collection result of the five split-Variable Rules.

    The source graph is:

      textfilecontent54(instance=1)
        -> object_component(subexpression)
        -> split(',')
        -> variable_test(option)
      AND
      textfilecontent54(instance=1) existence Test

    OVAL ObjectComponentType says zero source Items is an error.  The separate
    row-presence Test is false for a complete zero-item collection, so the outer
    OVAL AND resolves to false.
    """
    first = _first_source_row(rows)
    if first is None:
        projected_option_test = ERROR
        row_presence_test = FALSE
    else:
        raw = first.get("options")
        if not isinstance(raw, str) or not raw:
            raise ValueError(
                "first proof class requires a nonempty source option capture"
            )
        projected_option_test = (
            TRUE if required_option in raw.split(",") else FALSE
        )
        row_presence_test = TRUE

    return aggregate_operator(
        "AND", [projected_option_test, row_presence_test]
    )


def typed_fstab_complete(rows, required_option):
    """Model a compact typed linux.fstab Test for the same bounded class."""
    first = _first_source_row(rows)
    if first is None:
        return evaluate_collected_object_test(
            "complete",
            existence="at_least_one_exists",
            check="all",
            has_state=True,
            exists=0,
        )

    options = first.get("options")
    if not isinstance(options, list) or not options:
        raise ValueError(
            "first proof class requires one or more typed option values"
        )
    item_result = TRUE if required_option in options else FALSE
    return evaluate_collected_object_test(
        "complete",
        existence="at_least_one_exists",
        check="all",
        item_results=[item_result],
        has_state=True,
        exists=1,
    )


def faithful_split_variable_incomplete(rows, required_option):
    """Model the source persistent subgraph for an incomplete text collection.

    Historical OVAL processing-model text, consistent with the retained 5.12.3
    ObjectComponent contract, gives an ObjectComponent sourced from an
    incomplete Object an incomplete flag when values exist. OVAL Functions
    proceed only from complete sub-components; otherwise the Function result is
    error. With zero source Items, ObjectComponent itself is error.

    Therefore the split/local-Variable path is error for both zero and nonzero
    incomplete source populations. The separate source-row existence Test is
    unknown for this check_existence shape. OVAL AND(error, unknown) is error.
    """
    del required_option  # the Function cannot safely reach option evaluation
    first = _first_source_row(rows)
    exists = 1 if first is not None else 0
    row_presence_test = evaluate_collected_object_test(
        "incomplete",
        existence="at_least_one_exists",
        check="all",
        has_state=False,
        exists=exists,
    )
    projected_option_test = ERROR
    return aggregate_operator(
        "AND", [projected_option_test, row_presence_test]
    )


def typed_fstab_incomplete(rows, required_option):
    """Model ordinary generic Test semantics for an incomplete typed collector."""
    first = _first_source_row(rows)
    if first is None:
        # OVAL incomplete collection is unknown here: no decisive false State
        # exists and at_least_one_exists cannot be proven false until collection
        # is complete.
        return UNKNOWN

    options = first.get("options")
    if not isinstance(options, list) or not options:
        raise ValueError(
            "first proof class requires one or more typed option values"
        )
    item_result = TRUE if required_option in options else FALSE
    return evaluate_collected_object_test(
        "incomplete",
        existence="at_least_one_exists",
        check="all",
        item_results=[item_result],
        has_state=True,
        exists=1,
    )


def compare_incomplete_case(rows, required_option):
    typed = source_rows_to_typed(rows)
    faithful = faithful_split_variable_incomplete(rows, required_option)
    candidate = typed_fstab_incomplete(typed, required_option)
    return {
        "rewrite_id": REWRITE_ID,
        "faithful": faithful,
        "candidate": candidate,
        "equivalent": faithful == candidate,
        "source_rows": rows,
        "typed_rows": typed,
    }


def source_rows_to_typed(rows):
    """Translate only the lexical subset proven by the first fixture class."""
    out = []
    for row in rows:
        raw = row.get("options")
        if not isinstance(raw, str) or not raw:
            raise ValueError("source option capture is outside first proof class")
        out.append({**row, "options": raw.split(",")})
    return out


def compare_complete_case(rows, required_option):
    typed = source_rows_to_typed(rows)
    faithful = faithful_split_variable_complete(rows, required_option)
    candidate = typed_fstab_complete(typed, required_option)
    return {
        "rewrite_id": REWRITE_ID,
        "faithful": faithful,
        "candidate": candidate,
        "equivalent": faithful == candidate,
        "source_rows": rows,
        "typed_rows": typed,
    }


def modernization_preconditions(candidate):
    """Fail-closed report for the narrow complete-source proof class.

    A converter cannot use runtime collection status as a static proof
    precondition.  Even a report whose bounded complete-case conditions pass is
    therefore not eligible for automatic migration.
    """
    reasons = []
    if candidate.get("source_capability") != "independent.textfilecontent54":
        reasons.append("source_is_not_textfilecontent54")
    if candidate.get("filepath") != "/etc/fstab":
        reasons.append("source_is_not_etc_fstab")
    if candidate.get("instance") != 1:
        reasons.append("first_proof_class_requires_instance_1")
    if candidate.get("source_collection_status") != "complete":
        reasons.append("non_complete_collection_not_proven")
    if candidate.get("projection_field") != "subexpression":
        reasons.append("projection_is_not_subexpression")
    if candidate.get("split_delimiter") != ",":
        reasons.append("option_projection_is_not_comma_split")
    if not candidate.get("regex_field_mapping_proven", False):
        reasons.append("regex_to_fstab_field_mapping_not_proven")
    if not candidate.get("lexical_equivalence_proven", False):
        reasons.append("parser_lexical_equivalence_not_proven")
    bounded_complete_case_proven = not reasons
    automatic_reasons = list(reasons)
    automatic_reasons.append("runtime_collection_status_not_statically_provable")
    return {
        "rewrite_id": REWRITE_ID,
        "bounded_complete_case_proven": bounded_complete_case_proven,
        "eligible": False,
        "reasons": sorted(set(automatic_reasons)),
    }
