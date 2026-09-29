#!/usr/bin/env python3
"""Regression tests for lossless XCCDF check-selector migration."""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("converter", HERE / "scap14_to_scapng.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def assessment(aid="assessment.example"):
    return {"id": aid, "version": 1}


single_default = {
    "id": "rule-default",
    "checks": [{"selector": None, "system": "oval"}],
}
plan, error = mod.check_selection_plan(single_default, assessment())
assert error is None, error
assert plan == {
    "checks": [{
        "selector": "default",
        "source_selector": None,
        "assessment": "assessment.example",
        "assessment_version": 1,
    }],
    "default_check": "default",
}, plan

single_named = {
    "id": "rule-automated",
    "checks": [{"selector": "automated", "system": "oval"}],
}
plan, error = mod.check_selection_plan(single_named, assessment("assessment.auto"))
assert error is None, error
assert plan["default_check"] == "automated", plan
assert plan["checks"][0]["source_selector"] == "automated", plan
assert plan["checks"][0]["assessment"] == "assessment.auto", plan

multiple = {
    "id": "rule-alternatives",
    "checks": [
        {"selector": "automated", "system": "oval"},
        {"selector": "manual", "system": "ocil"},
    ],
}
plan, error = mod.check_selection_plan(multiple, assessment())
assert plan is None, plan
assert error["status"] == "unsupported", error
assert error["reason"] == "selectable_check_alternatives_not_lowered", error
assert {x["selector"] for x in error["selectors"]} == {"automated", "manual"}, error

# Multiple checking-system candidates under the same selector remain one
# selector alternative; the source check logic retains system ordering.
same_selector = {
    "id": "rule-system-fallback",
    "checks": [
        {"selector": "automated", "system": "system-a"},
        {"selector": "automated", "system": "system-b"},
    ],
}
plan, error = mod.check_selection_plan(same_selector, assessment())
assert error is None, error
assert plan["default_check"] == "automated", plan

source = {
    "resolved_profiles": [{
        "id": "profile-a",
        "effective_actions": [
            {
                "kind": "refine-rule",
                "attributes": {"idref": "rule-1", "selector": "automated"},
                "targets": [{"kind": "rule", "id": "rule-1", "match": "id"}],
            },
            {
                "kind": "refine-rule",
                "attributes": {"idref": "rule-1", "selector": "manual"},
                "targets": [{"kind": "rule", "id": "rule-1", "match": "id"}],
            },
            {
                "kind": "select",
                "attributes": {"idref": "rule-2", "selected": "false"},
                "targets": [{"kind": "rule", "id": "rule-2", "match": "id"}],
            },
        ],
    }],
}
projected = mod.native_profile_check_selectors(source)
assert projected == [{
    "profile": "profile-a",
    "check_selectors": {"rule-1": "manual"},
}], projected

print("PASS: XCCDF check selectors are preserved or rejected loudly")
