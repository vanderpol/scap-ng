"""Bridge current iteration-003 converter output to OVAL-aligned native vocabulary.

This is intentionally a post-round-trip transformation.  The existing semantic
round-trip machinery still consumes the older intermediate Collection/assertion
shape; emitted native authoring uses Test/Object/State/Variable terminology.

The transformation must not change evaluation semantics.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re


def _slug(value: str | None, fallback: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:56] or fallback


def _fingerprint(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _replace_object_refs(value):
    """Rename intermediate Collection references to native Object references."""
    if isinstance(value, list):
        return [_replace_object_refs(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        new_key = "object" if key == "collection" else key
        result[new_key] = _replace_object_refs(item)
    return result


def align_assessment_vocabulary(document: dict) -> dict:
    """Return an OVAL-vocabulary-aligned native Assessment document.

    Input is the current collection_graph=True converter shape:
    collections / tests / assertion / item_quantifier.

    Output uses:
    objects / states / tests / check_existence / check / state_operator.
    """
    result = copy.deepcopy(document)
    assessment = result.get("assessment")
    if not isinstance(assessment, dict):
        return result
    if assessment.get("mode") != "automated":
        return result

    collections = assessment.pop("collections", {})
    objects = {}
    for name, payload in collections.items():
        payload = _replace_object_refs(payload)
        if "collection_title" in payload:
            payload["object_title"] = payload.pop("collection_title")
        objects[name.replace("-collection", "-object")] = payload

    # Old Object names may appear in Tests, sets and Variable object components.
    object_names = {
        old: old.replace("-collection", "-object")
        for old in collections
    }

    def remap_object_names(value):
        if isinstance(value, list):
            return [remap_object_names(x) for x in value]
        if not isinstance(value, dict):
            if isinstance(value, str) and value in object_names:
                return object_names[value]
            return value
        out = {}
        for key, item in value.items():
            new_key = "object" if key == "collection" else key
            if new_key == "object" and isinstance(item, str) and item in object_names:
                out[new_key] = object_names[item]
            else:
                out[new_key] = remap_object_names(item)
        return out

    objects = remap_object_names(objects)
    if "variables" in assessment:
        assessment["variables"] = remap_object_names(assessment["variables"])

    states = {}
    state_by_fingerprint = {}
    used_state_ids = set()

    def register_state(title, capability, state_payload):
        candidate = {
            "state_title": title,
            "capability": capability,
            # Transitional generic payload.  Capability-specific generated
            # schemas will replace/refine this body without changing State
            # identity or Test->State references.
            "state": copy.deepcopy(state_payload),
        }
        fp = _fingerprint(candidate)
        if fp in state_by_fingerprint:
            return state_by_fingerprint[fp]
        base = "state-" + _slug(title, capability.replace(".", "-") if capability else "predicate")
        name = base
        suffix = 2
        while name in used_state_ids:
            name = f"{base}-{suffix}"
            suffix += 1
        used_state_ids.add(name)
        states[name] = candidate
        state_by_fingerprint[fp] = name
        return name

    tests = assessment.get("tests", {})
    for test in tests.values():
        collection = test.pop("collection", None)
        if collection is not None:
            test["object"] = object_names.get(collection, collection)

        assertion = test.pop("assertion", None)
        if assertion is None:
            continue

        if "existence" in assertion:
            test["check_existence"] = assertion["existence"]
        if "item_quantifier" in assertion:
            test["check"] = assertion["item_quantifier"]

        refs = []
        embedded = assertion.get("states")
        if isinstance(embedded, list):
            for state in embedded:
                refs.append(register_state(
                    state.get("state_title"),
                    state.get("capability"),
                    state.get("state"),
                ))
            if refs:
                test["state_operator"] = assertion.get("state_operator", "AND")
        elif "state" in assertion and assertion.get("state") is not None:
            refs.append(register_state(
                assertion.get("state_title"),
                assertion.get("state_capability"),
                assertion.get("state"),
            ))
            # Keep the explicit Test-level operator when source/converter
            # supplied one. A single State does not need a synthetic operator.
            if "state_operator" in assertion:
                test["state_operator"] = assertion["state_operator"]

        if refs:
            test["states"] = refs

    # Filters are State predicates too.  Promote the intermediate inline match
    # into the same local State registry and reference it from the Object.
    def promote_filters(value):
        if isinstance(value, list):
            return [promote_filters(x) for x in value]
        if not isinstance(value, dict):
            return value
        if "match" in value and "action" in value:
            state_ref = register_state(
                value.get("state_title"),
                value.get("capability"),
                value.get("match"),
            )
            out = {k: promote_filters(v) for k, v in value.items()
                   if k not in ("match", "state_title", "capability")}
            out["state"] = state_ref
            return out
        return {k: promote_filters(v) for k, v in value.items()}

    objects = promote_filters(objects)

    assessment["objects"] = objects
    assessment["states"] = states

    # Canonical presentation order is metadata, Objects, Variables, States,
    # Tests, evaluate. Mapping order is presentation-only.
    ordered = {}
    section_order = ("objects", "variables", "states", "tests", "evaluate")
    for key, value in assessment.items():
        if key not in section_order:
            ordered[key] = value
    for key in section_order:
        if key in assessment:
            ordered[key] = assessment[key]
    result["assessment"] = ordered
    return result


def verify_alignment(intermediate: dict, aligned: dict) -> None:
    if aligned != align_assessment_vocabulary(intermediate):
        raise ValueError("Assessment changed beyond declared OVAL vocabulary alignment")
