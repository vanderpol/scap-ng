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
plan, error = mod.check_selection_plan(single_default, {"automated": assessment(), "manual": None})
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
plan, error = mod.check_selection_plan(single_named, {"automated": assessment("assessment.auto"), "manual": None})
assert error is None, error
assert "default_check" not in plan, plan
assert plan["checks"][0]["source_selector"] == "automated", plan
assert plan["checks"][0]["assessment"] == "assessment.auto", plan

multiple = {
    "id": "rule-alternatives",
    "checks": [
        {"selector": "", "system": "oval"},
        {"selector": "automated", "system": "oval"},
        {"selector": "manual", "system": "ocil", "inline_content": "Review manually."},
    ],
}
plan, error = mod.check_selection_plan(
    multiple,
    {
        "automated": assessment("assessment.auto"),
        "manual": assessment("assessment.manual"),
    },
)
assert error is None, error
assert plan["default_check"] == "default", plan
assert {x["selector"] for x in plan["checks"]} == {"default", "automated", "manual"}, plan
by_selector = {x["selector"]: x["assessment"] for x in plan["checks"]}
assert by_selector["default"] == "assessment.auto", by_selector
assert by_selector["automated"] == "assessment.auto", by_selector
assert by_selector["manual"] == "assessment.manual", by_selector


unsupported = {
    "id": "rule-external",
    "checks": [{"selector": "vendor", "system": "urn:example:unsupported"}],
}
plan, error = mod.check_selection_plan(
    unsupported,
    {"automated": assessment(), "manual": assessment("manual")},
)
assert plan is None, plan
assert error["status"] == "unsupported", error
assert error["reason"] == "check_selector_without_assessment", error

# Multiple non-equivalent candidates under the same selector are a loud
# blocker until checking-system fallback is modeled explicitly.
same_selector = {
    "id": "rule-system-fallback",
    "checks": [
        {"selector": "automated", "system": "oval", "content_refs": [{"name": "def:a"}]},
        {"selector": "automated", "system": "oval", "content_refs": [{"name": "def:b"}]},
    ],
}
plan, error = mod.check_selection_plan(
    same_selector,
    {"automated": assessment(), "manual": None},
)
assert plan is None, plan
assert error["status"] == "unsupported", error
assert error["reason"] == "same_selector_alternatives_not_lowered", error

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
