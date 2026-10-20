#!/usr/bin/env python3
"""Bounded reversible research mapping: proposed RHEL9 must/may item wording to
existing version-pinned 0.4-A item-requirement tokens. Not a scanner evaluator,
not a schema change and not a generic OVAL existence/match compiler.
Run: python3 tools/research_rhel9_must_may_item_language.py
Refs #227 #246.
"""
from itertools import product

# Mapping only for item-collection quantifier phrases actually observed in the
# original pinned RHEL9 /home and initialization-file source fixtures.
PAIR_TO_A = {
    ("one_or_more", "all_items_must"): "at_least_one_exists_and_all_match",
    ("may_be_absent", "all_items_must"): "may_be_absent_and_all_match",
}
A_TO_PAIR = {token: pair for pair, token in PAIR_TO_A.items()}

def lower(require):
    if not isinstance(require, dict) or set(require) != {"items", "all_items_must"}:
        raise ValueError("unsupported or ambiguous item requirement shape")
    if require["all_items_must"] is not True:
        raise ValueError("the predicate must be specified separately")
    pair = (require["items"], "all_items_must")
    if pair not in PAIR_TO_A:
        raise ValueError("unproven quantifier combination")
    return PAIR_TO_A[pair]

def expand(token):
    if token not in A_TO_PAIR:
        raise ValueError("unproven A requirement token")
    return {"items": A_TO_PAIR[token][0], "all_items_must": True}

def test_exact_reversal():
    expected = {
        "home-mounted-nosuid-option-test": "at_least_one_exists_and_all_match",
        "local-initialization-files-non-system-users-have-mode-0740-or-test": "may_be_absent_and_all_match",
        "local-initialization-files-root-have-mode-0740-or-less-permissive-test": "at_least_one_exists_and_all_match",
    }
    # Tokens transcribed from pinned actual RHEL9 shared assessment source.
    for test_id, original in expected.items():
        assert lower(expand(original)) == original, test_id
    assert len(PAIR_TO_A) == len(A_TO_PAIR)
    return len(expected)

def test_fail_closed():
    rejected = [
        {},
        {"items": "one_or_more"},
        {"items": "one_or_more", "no_items_may": True},
        {"items": "one_or_more", "all_items_must": False},
        {"items": "none", "all_items_must": True},
        {"items": "exactly_one", "all_items_must": True},
        {"items": "one_or_more", "all_items_must": True, "no_items_may": True},
        {"items": "one_or_more", "all_items_must": {}},
        {"items": "may_be_absent", "all_items_must": None},
    ]
    for candidate in rejected:
        try:
            lower(candidate)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("incorrectly accepted unsupported syntax: " + repr(candidate))
    for unknown in ("none_exist", "at_least_one_exists_and_some_match", "only_one_exists"):
        try:
            expand(unknown)
        except ValueError:
            pass
        else:
            raise AssertionError("incorrectly recognized unproven mapping: " + unknown)
    return len(rejected) + 3

if __name__ == "__main__":
    positive = test_exact_reversal()
    negative = test_fail_closed()
    print(f"RHEL9 must/may *syntax* mappings: {positive} fixture-token reversals, {negative} negative cases PASS")
    print("LIMITATION: no predicate translation, fixture loading, or six-state runtime parity tested")
