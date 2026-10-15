#!/usr/bin/env python3
"""Tiny Slang-inspired authoring research lowerer.

Only one explicit, schema-constrained linux.partition check is supported.
This is NOT a replacement SCAP-NG grammar and NOT a general OVAL converter.
No implicit quantifiers, guessed capability fields, or Boolean aliases.
"""
from __future__ import annotations
from copy import deepcopy
import yaml


class UnsupportedFacade(ValueError):
    pass


def exact_keys(value, keys, location):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise UnsupportedFacade(
            f"{location}: required keys {sorted(keys)}; got "
            f"{sorted(value) if isinstance(value,dict) else type(value).__name__}")


def lower(source: dict) -> dict:
    exact_keys(source, {"checks", "evaluate"}, "assessment")
    if not isinstance(source["checks"], dict) or len(source["checks"]) != 1:
        raise UnsupportedFacade("This prototype supports one named check; no implicit AND")
    name, check = next(iter(source["checks"].items()))
    if not isinstance(name, str) or not name or not name.replace("-", "").isalnum():
        raise UnsupportedFacade("Check identifier must be a stable, nonempty slug")
    if source["evaluate"] != {"check": name}:
        raise UnsupportedFacade("Explicit evaluate.check required; no implicit order")
    exact_keys(check, {"on","select","expect","require","evidence"}, "check")
    if check["on"] != "linux.partition":
        raise UnsupportedFacade("Only the proven linux.partition capability is supported")
    exact_keys(check["select"], {"mount_point"}, "select")
    selector=check["select"]["mount_point"]
    exact_keys(selector, {"matches_regex"}, "select.mount_point")
    regex=selector["matches_regex"]
    if not isinstance(regex,str) or not regex:
        raise UnsupportedFacade("Regex must be a source-preserved nonempty string")
    exact_keys(check["expect"], {"mount_options"}, "expect")
    expectation=check["expect"]["mount_options"]
    exact_keys(expectation, {"equals","values"}, "expect.mount_options")
    wanted=expectation["equals"]
    if not isinstance(wanted,str):
        raise UnsupportedFacade("This prototype only compares scalar string values")
    exact_keys(expectation["values"],{"exists","match"},"expect.mount_options.values")
    if expectation["values"] != {"exists":"one_or_more","match":"one_or_more"}:
        raise UnsupportedFacade("Unsupported field cardinality: fail instead of weakening")
    exact_keys(check["require"], {"items"}, "require")
    exact_keys(check["require"]["items"], {"exists","match"},"require.items")
    if check["require"]["items"] != {"exists":"one_or_more","match":"all"}:
        raise UnsupportedFacade("Unsupported Item cardinality: fail instead of weakening")
    exact_keys(check["evidence"], {"fields"}, "evidence")
    if check["evidence"]["fields"] != "all":
        raise UnsupportedFacade("Unsupported evidence: fail instead of truncating")
    return {
        "tests":{
            name+"-test":{
                "capability":"linux.partition",
                "object":{"capability":"linux.partition",
                          "select":{"mount_point":{"value":regex,"operation":"pattern_match"}}},
                "states":[{"field":"mount_options","value":wanted,"operation":"equals",
                           "match":"one_or_more","existence":"one_or_more"}],
                "reported_elements":"all",
                "existence":"one_or_more","match":"all",
            }
        },
        "evaluate":{"test":name+"-test"},
    }


RESEARCH_SAMPLE = r"""
checks:
  home-mounted-nosuid-option:
    on: linux.partition
    select:
      mount_point:
        matches_regex: '.*\\/home'
    expect:
      mount_options:
        equals: nosuid
        values:
          exists: one_or_more
          match: one_or_more
    require:
      items:
        exists: one_or_more
        match: all
    evidence:
      fields: all
evaluate:
  check: home-mounted-nosuid-option
"""


if __name__ == "__main__":
    print(yaml.safe_dump(lower(yaml.safe_load(RESEARCH_SAMPLE)),sort_keys=False))
