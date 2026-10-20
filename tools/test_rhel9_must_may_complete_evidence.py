#!/usr/bin/env python3
"""Bounded *complete-evidence Boolean* model of RHEL9 must/may vocabulary.
This is NOT a six-state OVAL evaluator; partial/error/unknown/NA are rejected.
Research #227/#246; no 0.4-A schema change.
"""
from itertools import product

def interpret(items_required, predicate_name, outcomes, *, complete):
    if complete is not True:
        raise ValueError("incomplete/error/unknown/not-applicable needs native six-state semantics")
    if not isinstance(outcomes, list) or not all(type(x) is bool for x in outcomes):
        raise ValueError("only fully-known Item predicate results supported")
    n = len(outcomes)
    if items_required == "none":
        if predicate_name is not None:
            raise ValueError("absence test is State-free")
        return n == 0
    if items_required == "one_or_more":
        exists = n >= 1
    elif items_required == "may_be_absent":
        exists = True
    elif items_required == "exactly_one":
        exists = n == 1
    else:
        raise ValueError("unsupported required population")
    if predicate_name == "all_items_must":
        match = all(outcomes)
    elif predicate_name == "at_least_one_item_must":
        match = any(outcomes)
    elif predicate_name == "exactly_one_item_must":
        match = sum(outcomes) == 1
    elif predicate_name == "no_items_may":
        match = not any(outcomes)
    else:
        raise ValueError("unsupported matching operator")
    return exists and match

def test():
    cases = 0
    for length in range(5):
        for outcomes in product((False, True), repeat=length):
            outcomes = list(outcomes)
            # Two already-proven RHEL9 A requirement mappings:
            assert interpret("one_or_more", "all_items_must", outcomes, complete=True) == (
                len(outcomes) > 0 and all(outcomes))
            assert interpret("may_be_absent", "all_items_must", outcomes, complete=True) == all(outcomes)
            # Never conflate absence of forbidden package with "none match":
            assert interpret("none", None, outcomes, complete=True) == (not outcomes)
            assert interpret("may_be_absent", "no_items_may", outcomes, complete=True) == (
                not any(outcomes))
            # Exact number EXISTING differs from exactly one matching:
            assert interpret("exactly_one", "all_items_must", outcomes, complete=True) == (
                len(outcomes) == 1 and all(outcomes))
            assert interpret("may_be_absent", "exactly_one_item_must", outcomes, complete=True) == (
                sum(outcomes) == 1)
            cases += 1
    # Meaningful distinctions: empty Items, one nonmatching Item, multiple Items
    assert interpret("may_be_absent", "all_items_must", [], complete=True)
    assert not interpret("one_or_more", "all_items_must", [], complete=True)
    assert interpret("may_be_absent", "no_items_may", [False, False], complete=True)
    assert not interpret("none", None, [False, False], complete=True)
    assert interpret("may_be_absent", "exactly_one_item_must", [True, False], complete=True)
    assert not interpret("exactly_one", "all_items_must", [True, False], complete=True)
    for invalid in [
        ("one_or_more", "all_items_must", [True], False),
        ("one_or_more", "all_items_must", [True, None], True),
        ("one_or_more", "all_items_must", ["true"], True),
        ("none", "no_items_may", [], True),
    ]:
        try:
            interpret(*invalid[:3], complete=invalid[3])
        except ValueError:
            pass
        else:
            raise AssertionError("unsupported evidence accepted: " + repr(invalid))
    print(f"PASS: {cases} known-Boolean Item populations, six vocabulary relations each")
    print("Excluded: six-state/partial/collection errors and predicate-field semantics")

if __name__ == "__main__":
    test()
