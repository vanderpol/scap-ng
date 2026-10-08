"""Experimental registry authoring expansion for SV-278217.

NOT wired into the SCAP-NG compiler. Never silently defaults operation,
registry type, entity quantifier or item existence.
"""
from __future__ import annotations

import copy

OPERATIONS = {"equals", "not_equal", "pattern_match", "case_insensitive_equals"}
HIVES = {"classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"}
TYPES = {"string": "string", "expand_string": "string", "multi_string": "string", "dword": "integer", "dword_big_endian": "integer", "qword": "integer", "binary": "binary"}

class AuthoringError(ValueError):
    pass


def predicate(value, *, datatype, context):
    if not isinstance(value, dict) or len(value) != 1:
        raise AuthoringError(f"{context}: exactly one explicit comparison operator required")
    operation, literal = next(iter(value.items()))
    if operation not in OPERATIONS:
        raise AuthoringError(f"{context}: unsupported operator {operation!r}")
    if datatype == "integer" and (type(literal) is not int):
        raise AuthoringError(f"{context}: expected integer, not {type(literal).__name__}")
    if datatype == "string" and not isinstance(literal, str):
        raise AuthoringError(f"{context}: expected string")
    if datatype == "binary":
        raise AuthoringError(f"{context}: binary authoring not specified by this experiment")
    return {"value": literal, "operation": operation, "datatype": datatype}


def expand_registry_test(test):
    """Expand one proposal Test; fail closed on unsupported keys/shapes.

    This produces a canonical field predicate contract, not a claimed
    schema-validated SCAP-NG 0.3 Assessment.
    """
    if test.get("capability") != "windows.registry":
        raise AuthoringError("only windows.registry supported")
    if set(test) != {"capability", "object", "states", "reported_elements", "existence", "match"}:
        raise AuthoringError("unsupported/missing Test fields")
    if test["reported_elements"] != "all":
        raise AuthoringError("unsupported reported_elements")
    select = test["object"].get("select")
    if set(test["object"]) != {"select"} or not isinstance(select, dict) or set(select) != {"hive", "key", "name"}:
        raise AuthoringError("select must specify exact hive/key/name")
    obj = {}
    for name in ("hive", "key", "name"):
        obj[name] = predicate(select[name], datatype="string", context=name)
    if obj["hive"]["value"] not in HIVES or obj["hive"]["operation"] != "equals":
        raise AuthoringError("invalid native registry hive selector")
    # Native windows.registry mapping defines hive as an enumeration scalar.
    # Do not emit an object-entity triple for this field.
    obj["hive"] = obj["hive"]["value"]
    states = test["states"]
    if not isinstance(states, list) or len(states) != 1:
        raise AuthoringError("exactly one State expected")
    st = states[0]
    if set(st) != {"expect"}:
        raise AuthoringError("expected a single expect field")
    expect = st["expect"]
    if set(expect) != {"type", "value", "match", "existence"}:
        raise AuthoringError("explicit type, value, match, existence required")
    kind = predicate(expect["type"], datatype="string", context="registry type")
    if kind["operation"] != "equals" or kind["value"] not in TYPES:
        raise AuthoringError("explicit supported registry type equality required")
    datatype = TYPES[kind["value"]]
    if kind["value"] == "multi_string":
        raise AuthoringError("REG_MULTI_SZ native element mapping is not yet specified")
    val = predicate(expect["value"], datatype=datatype, context="registry value")
    if expect["match"] not in {"all", "one_or_more", "one", "none"}:
        raise AuthoringError("unsupported explicit match")
    if expect["existence"] not in {"one_or_more", "none", "all", "one", "optional"}:
        raise AuthoringError("unsupported explicit existence")
    result = {
        "test_title": None,
        "capability": "windows.registry",
        "object": {"capability": "windows.registry", "select": obj},
        "states": [{"capability": "windows.registry", "state": {"all": [
            dict(field="type", **kind, match=expect["match"], existence=expect["existence"]),
            dict(field="value", **val, match=expect["match"], existence=expect["existence"]),
        ]}}],
        "reported_elements": test["reported_elements"],
        "existence": test["existence"], "match": test["match"]
    }
    return copy.deepcopy(result)
