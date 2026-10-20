#!/usr/bin/env python3
"""RHEL9 source-snippet based 0.4-A must/may vocabulary probe.
No runtime/scanner equivalence claim. Run directly with Python 3.
Refs #227 #246.
"""
from copy import deepcopy

# Source-backed 0.4-A Test fragments transcribed from:
# scap-ng-editor-sample-data/focused-fixtures/source-backed/authoring/shared/
# assessments/linux/other/{home-mounted-nosuid-option,
# initialization-files-0740-less-permissive}.assessment.yaml.
# Intentionally preserve fields and selectors, not only the cardinality token.
TESTS = {
    "rhel9-home-nosuid": {
        "capability": "linux.partition",
        "object": {"capability": "linux.partition", "select": {
            "mount_point": {"matches_regex": r".*\/home"}}},
        "states": [{"mount_options": {
            "require": "at_least_one_exists_and_some_match",
            "equals": "nosuid"}}],
        "collected_items_require": "at_least_one_exists_and_all_match",
    },
    "rhel9-user-init-files": {
        "capability": "unix.file",
        "states": [{"and": [
            {field: {"equals": False}} for field in (
                "setuid", "setgid", "sticky", "group_write", "group_execute",
                "other_read", "other_write", "other_execute")],
            "state_fields_require": "at_least_one_exists_and_all_match"}],
        "collected_items_require": "may_be_absent_and_all_match",
    },
    "rhel9-root-init-files": {
        "capability": "unix.file",
        "states": [{"and": [
            {field: {"equals": False}} for field in (
                "setuid", "setgid", "sticky", "group_write", "group_execute",
                "other_read", "other_write", "other_execute")],
            "state_fields_require": "at_least_one_exists_and_all_match"}],
        "collected_items_require": "at_least_one_exists_and_all_match",
    },
}

TO_ENGLISH = {
    "at_least_one_exists_and_all_match": "one_or_more",
    "may_be_absent_and_all_match": "may_be_absent",
}
TO_NATIVE = {v: k for k, v in TO_ENGLISH.items()}

def present(test):
    original = deepcopy(test)
    token = original.pop("collected_items_require")
    if token not in TO_ENGLISH or not original.get("states"):
        raise ValueError("unsupported source Test")
    original["require"] = {
        "items": TO_ENGLISH[token],
        # Shorthand of the Item-level quantifier only.
        # State fields remain local and unchanged.
        "all_items_must": True,
    }
    return original

def restore(test):
    translated = deepcopy(test)
    if "collected_items_require" in translated:
        raise ValueError("conflicting native and research vocabulary")
    req = translated.pop("require", None)
    if not isinstance(req, dict) or set(req) != {"items", "all_items_must"}:
        raise ValueError("not a recognized requirement")
    if req["all_items_must"] is not True or not translated.get("states"):
        raise ValueError("a State-bearing all-Items requirement is needed")
    if not isinstance(req["items"], str) or req["items"] not in TO_NATIVE:
        raise ValueError("unsupported existence semantics")
    translated["collected_items_require"] = TO_NATIVE[req["items"]]
    return translated

def test():
    for test_id, original in TESTS.items():
        translated = present(original)
        assert restore(translated) == original, test_id
        assert translated["states"] == original["states"], test_id
    adversarial = [
        {"items": "one_or_more", "all_items_must": False},
        {"items": "one_or_more", "no_items_may": True},
        {"items": "none", "all_items_must": True},
        {"items": "exactly_one", "all_items_must": True},
        {"items": "may_be_absent"},
        {"items": "one_or_more", "all_items_must": True, "extra": True},
    ]
    for altered in adversarial:
        example = present(TESTS["rhel9-home-nosuid"])
        example["require"] = altered
        try:
            restore(example)
        except ValueError:
            pass
        else:
            raise AssertionError("unsupported form accepted: " + repr(altered))
    print("PASS: 3 RHEL9 Test-fragment reversals; 6 negative guards")
    print("Scope: source-fragment syntactic equivalence, NOT six-state or scanner parity")

if __name__ == "__main__":
    test()
