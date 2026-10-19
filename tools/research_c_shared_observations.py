#!/usr/bin/env python3
"""Refs #245: read-only C shared-observation census over pinned source.

Indexes exactly reusable acquisition contracts and their source consumers.
It does NOT merge distinct shell commands, evaluate OVAL, collect Items, or
authorize replacing source import with a new native Apache provider.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
import json


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _sha(value):
    return sha256(_canon(value).encode("utf-8")).hexdigest()


def index_shared_observations(assessment):
    if not isinstance(assessment, dict) or not isinstance(assessment.get("id"), str):
        raise ValueError("source Assessment with stable identity required")
    sections = {}
    for name in ("shared_objects", "variables", "tests"):
        section = assessment.get(name, {})
        if not isinstance(section, dict):
            raise ValueError("unsupported source declarations: " + name)
        sections[name] = section

    discovered = {}
    references = []
    var_uses = defaultdict(list)

    def walk(node, path, owner):
        if isinstance(node, dict):
            if "capability" in node or "collect" in node:
                if "collect" in node:
                    if type(node.get("capability")) is not str or not isinstance(node["collect"], dict):
                        raise ValueError("invalid typed acquisition at " + "/".join(path))
                    # Preserve *every* collection-affecting key: selector, Set,
                    # Filter, for_each, flags, shell and dynamic Variables.
                    # object_title is historical presentation metadata only.
                    desc = {k: deepcopy(v) for k, v in node.items()
                            if k not in ("object_title",)}
                    key = _sha(desc)
                    entry = discovered.setdefault(key, {"key": key, "request": desc,
                                                       "source_sites": []})
                    if entry["request"] != desc:
                        raise ValueError("observation identity collision")
                    entry["source_sites"].append("/".join(path))
            for field, value in node.items():
                if field == "variable" and type(value) is str:
                    var_uses[value].append({"owner": owner, "path": "/".join(path + (field,))})
                if field == "object" and type(value) is str:
                    references.append({"object": value, "owner": owner,
                                       "path": "/".join(path + (field,))})
                walk(value, path + (field,), owner)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, path + (str(i),), owner)

    for section, declarations in sections.items():
        for owner, body in sorted(declarations.items()):
            if not isinstance(body, dict):
                raise ValueError("malformed source declaration")
            walk(body, (section, owner), section + "/" + owner)

    for name in var_uses:
        if name not in sections["variables"]:
            raise ValueError("unresolved source Variable " + name)
    shared_refs = []
    for ref in references:
        if ref["object"] not in sections["shared_objects"]:
            raise ValueError("unresolved shared Object " + ref["object"])
        shared_refs.append(ref)

    return {
        "status": "READ_ONLY_SOURCE_OBSERVATION_CENSUS",
        "source_assessment_id": assessment["id"],
        "source_sha256": _sha(assessment),
        "variable_count": len(sections["variables"]),
        "test_count": len(sections["tests"]),
        "acquisition_site_count": sum(len(x["source_sites"]) for x in discovered.values()),
        "distinct_acquisition_contracts": len(discovered),
        "acquisitions": sorted(discovered.values(), key=lambda x:x["key"]),
        "shared_object_references": shared_refs,
        "multi_consumer_variables": {name: uses for name, uses in sorted(var_uses.items())
                                     if len(uses)>1},
        "can_assume_one_runtime_collection_per_contract": False,
        "can_replace_distinct_commands_with_one_observation": False,
        "source_runtime_parity_verified": False,
        "scanner_executed": False,
    }
