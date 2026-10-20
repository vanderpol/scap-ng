#!/usr/bin/env python3
"""RHEL9 inline must/may authoring experiment: whole source exact mapping.
Uses pinned fixture literals from test_rhel9_must_may_full_source.py.
No 0.4-A schema change or OVAL runtime equivalence claim. Refs #227 #246.
"""
from copy import deepcopy
import yaml
from test_rhel9_must_may_full_source import SOURCES

TO_WORDS = {
    "at_least_one_exists_and_all_match": "one_or_more",
    "may_be_absent_and_all_match": "may_be_absent",
}
FROM_WORDS = {v: k for k, v in TO_WORDS.items()}

def present(document):
    out = deepcopy(document)
    for test in out["assessment"]["tests"].values():
        count = test.pop("collected_items_require")
        states = test.pop("states")
        if count not in TO_WORDS or not isinstance(states, list) or not states:
            raise ValueError("unproven item requirement or State shape")
        test["require"] = {
            "items": TO_WORDS[count],
            "all_items_must": states,
        }
    return out

def restore(document):
    out = deepcopy(document)
    for test in out["assessment"]["tests"].values():
        if "states" in test or "collected_items_require" in test:
            raise ValueError("ambiguous authoring format")
        req = test.pop("require", None)
        if not isinstance(req, dict) or set(req) != {"items", "all_items_must"}:
            raise ValueError("unsupported shape")
        items, states = req["items"], req["all_items_must"]
        if not isinstance(items, str) or items not in FROM_WORDS:
            raise ValueError("unsupported Item existence")
        if not isinstance(states, list) or not states or not all(isinstance(s, dict) for s in states):
            raise ValueError("all_items_must requires nonempty local State predicates")
        test["states"] = states
        test["collected_items_require"] = FROM_WORDS[items]
    return out

def main():
    documents = [yaml.safe_load(v) for v in SOURCES.values()]
    source_tests = 0
    for original in documents:
        candidate = present(original)
        assert restore(candidate) == original
        source_tests += len(original["assessment"]["tests"])
    home = present(documents[0])
    test = next(iter(home["assessment"]["tests"].values()))
    assert test["require"]["all_items_must"][0]["mount_options"]["equals"] == "nosuid"
    assert test["require"]["all_items_must"][0]["mount_options"]["require"] == "at_least_one_exists_and_some_match"
    for bad in [None, [], {}, True, "nosuid", [True], [{"mount_options": "nosuid"}, None]]:
        broken = deepcopy(home)
        next(iter(broken["assessment"]["tests"].values()))["require"]["all_items_must"] = bad
        try:
            restore(broken)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted non-State syntax: " + repr(bad))
    print(f"PASS: {len(documents)} full fixture documents / {source_tests} Tests, 7 invalid-structure rejections")
    print("The Item-level matching requirement now encloses its Test-local State predicates.")
    print("NOT tested: parsed native schema for the candidate; item runtime/six-state parity")

if __name__ == "__main__":
    main()
