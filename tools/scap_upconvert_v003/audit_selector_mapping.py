#!/usr/bin/env python3
"""Independent audit of source-XCCDF choice preservation in normalized NG Rules.

Current authoring stores a named publisher default, not a redundant 'default'
choice. This module checks the SOURCE->TARGET binding map and does not accept
a generated default merely because its label exists. Cross-check actual
Assessment documents and source OVAL/OCIL content in audit_full_review.py.
"""
from pathlib import PurePosixPath


def normalize_source_path(path):
    if not isinstance(path, str) or not path:
        raise ValueError("empty source Assessment binding")
    path = path.replace("\\", "/")
    if path.startswith("/") or ".." in PurePosixPath(path).parts:
        raise ValueError("invalid source Assessment binding path")
    return path


def normalize_native_ref(ref):
    if not isinstance(ref, str) or not ref:
        raise ValueError("empty native Assessment binding")
    path = ref.replace("\\", "/")
    if not path.startswith("../") or ".." in PurePosixPath(path[3:]).parts:
        raise ValueError("native Assessment binding must be a safe ../ relative reference")
    return normalize_source_path(path[3:])


def audit_normalized_selection(
    *, source_order, source_bindings, native_choices,
    native_default, omitted_source_selectors=(), quarantined=False
):
    """Return issues and source selector -> selected NG selector for independent review.

    'omitted_source_selectors' are documented fallbacks/quarantines only.
    This helper compares target *identity*, not the old selector spelling.
    """
    problems = []
    source_order = list(source_order)
    source_set = set(source_order)
    omitted = set(omitted_source_selectors)
    if len(source_set) != len(source_order):
        problems.append("source has duplicate selectors")
    if not isinstance(source_bindings, dict):
        return ["source selector binding map is absent"], {}
    if set(source_bindings) != source_set:
        problems.append("source selector/evidence key set differs")
    if omitted - source_set:
        problems.append("fallback identifies nonexistent source selector")
    if not isinstance(native_choices, dict) or not native_choices:
        return problems + ["native Rule has no choices"], {}
    if "default" in native_choices:
        problems.append("redundant literal default Assessment choice remains")
    if native_default not in native_choices:
        problems.append("default_assessment_choice does not name an existing method")
    try:
        expected = {s: normalize_source_path(ref) for s, ref in source_bindings.items()}
        native = {
            name: normalize_native_ref(choice.get("assessment"))
            for name, choice in native_choices.items()
        }
    except (TypeError, AttributeError, ValueError) as exc:
        return problems + [str(exc)], {}

    if quarantined:
        if set(native) != {"manual"} or native_default != "manual":
            problems.append("fully quarantined Rule did not select manual")
        if not (omitted or set(source_order) == {"manual"}):
            problems.append("manual quarantine lacks documented source fallback")
        return problems, {k: "manual" for k in source_order if k not in omitted
                          and expected.get(k) == native.get("manual")}

    lookup = {}
    valid = {s: p for s, p in expected.items() if s not in omitted}
    for selector in source_order:
        if selector in omitted or selector not in valid:
            continue
        ref = valid[selector]
        if selector != "default":
            if selector not in native:
                problems.append("missing named native method: " + selector)
            elif native[selector] != ref:
                problems.append("changed Assessment binding for " + selector)
            else:
                lookup[selector] = selector
        else:
            if native_default in native and native[native_default] == ref:
                lookup[selector] = native_default
            else:
                problems.append("source default Assessment binding changed")

    # The source's first selected method remains default when no unselected
    # check exists. Do not force a new literal 'default' choice.
    if "default" not in valid and not omitted and source_order:
        first = source_order[0]
        if first in valid and native.get(native_default) != valid[first]:
            problems.append("source first named Assessment default binding changed")

    extra = set(native.values()) - set(valid.values())
    if extra:
        problems.append("native Rule introduces unsupported Assessment reference")
    for selector in native:
        if selector not in source_set and selector not in {"automated", "manual",
                                                          "publisher-automated",
                                                          "publisher-manual"}:
            problems.append("unexpected generated method name: " + selector)
    return problems, lookup
