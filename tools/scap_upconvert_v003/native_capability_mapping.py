"""Apply reviewed legacy-to-native capability mappings after OVAL vocabulary alignment.

This layer intentionally sits *after* the lossless OVAL semantic lowering and
generic Object/State/Test alignment. It converts explicit legacy semantics into
clean SCAP-NG capability shapes without changing the round-trip IR underneath.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


LOGICAL_OPERATOR = {"AND": "all", "OR": "any", "ONE": "one", "XOR": "odd"}

COMMON_CROSSWALK = {
    "operation": {
        "equals": "equal",
        "not equal": "not_equal",
        "case insensitive equals": "equal_ci",
        "case insensitive not equal": "not_equal_ci",
        "greater than": "greater_than",
        "greater than or equal": "greater_or_equal",
        "less than": "less_than",
        "less than or equal": "less_or_equal",
        "bitwise and": "bit_and",
        "bitwise or": "bit_or",
        "pattern match": "match",
        "subset of": "subset",
        "superset of": "superset",
    },
    "check": {
        "all": "all",
        "at least one": "any",
        "only one": "one",
        "none satisfy": "none",
    },
    "existence": {
        "all_exist": "all",
        "at_least_one_exists": "some",
        "none_exist": "none",
        "only_one_exists": "one",
        "any_exist": "optional",
    },
    "datatype": {
        "string": "string",
        "boolean": "boolean",
        "int": "integer",
        "float": "float",
        "binary": "binary",
        "version": "version",
        "ipv4_address": "ipv4",
        "ipv6_address": "ipv6",
        "evr_string": "rpm_evr",
        "debian_evr_string": "debian_evr",
        "fileset_revision": "fileset_revision",
        "ios_version": "ios_version",
        "record": "record",
    },
}


def source_capability(mapping: dict) -> str:
    source=mapping["source"]
    family=source["namespace"].split("#")[-1].split("/")[-1]
    test=source["test"]
    if test.endswith("_test"):
        test=test[:-5]
    return f"{family}.{test}"


def _translate(mapping: dict, group: str, value):
    table=dict(COMMON_CROSSWALK.get(group) or {})
    table.update((mapping.get("migration_crosswalk") or {}).get(group) or {})
    if value in table:
        translated=table[value]
        if isinstance(translated,str) and translated.startswith("migration_error"):
            raise ValueError(f"unsupported legacy {group} value: {value}")
        return translated
    return value


def _native_scalar_predicate(payload: dict, mapping: dict, *, record_field=False):
    out={
        "value": copy.deepcopy(payload.get("value")),
        "operation": _translate(mapping,"operation",payload.get("operation","equals")),
        "datatype": _translate(mapping,"datatype",payload.get("datatype","string")),
        "mask": bool(payload.get("mask",False)),
        "match": _translate(mapping,"check",payload.get("entity_check","all")),
    }
    if "variable_check" in payload:
        out["variable_match"]=_translate(
            mapping,"check",payload.get("variable_check","all")
        )
    # OVAL record fields have no independent check_existence attribute. A State
    # field named in a record is required to have at least one corresponding
    # collected occurrence; duplicate occurrences are handled by match.
    existence="at_least_one_exists" if record_field else payload.get(
        "entity_existence","at_least_one_exists"
    )
    out["existence"]=_translate(mapping,"existence",existence)
    return out


def _native_record(record_value, parent_payload: dict, mapping: dict):
    fields={}
    for field in record_value.get("record") or []:
        name=field.get("name")
        if not isinstance(name,str) or not name:
            raise ValueError("record field missing name")
        if name in fields:
            raise ValueError(
                f"legacy record contains duplicate named field {name!r}; "
                "native field maps require a deliberate multiplicity translation"
            )
        fields[name]=_native_scalar_predicate(field,mapping,record_field=True)
    return {
        "mask":bool(parent_payload.get("mask",False)),
        "match":_translate(mapping,"check",parent_payload.get("entity_check","all")),
        "existence":_translate(
            mapping,"existence",
            parent_payload.get("entity_existence","at_least_one_exists")
        ),
        "fields":fields,
    }


def _transform_state_payload(value, mapping: dict):
    if isinstance(value,list):
        return [_transform_state_payload(x,mapping) for x in value]
    if not isinstance(value,dict):
        return copy.deepcopy(value)

    if any(key in value for key in ("all","any","one","odd")):
        out={}
        for key,item in value.items():
            native_key={
                "all":"all",
                "any":"any",
                "one":"one",
                "odd":"odd",
            }.get(key,key)
            out[native_key]=_transform_state_payload(item,mapping)
        return out

    if "field" not in value:
        return {k:_transform_state_payload(v,mapping) for k,v in value.items()}

    field_map=(mapping.get("native") or {}).get("state_field_map") or {}
    native_field=field_map.get(value["field"],value["field"])
    record_fields=set((mapping.get("native") or {}).get("record_state_fields") or [])
    raw_value=value.get("value")
    if native_field in record_fields and isinstance(raw_value,dict) and "record" in raw_value:
        return {
            "field":native_field,
            "record":_native_record(raw_value,value,mapping),
        }

    predicate=_native_scalar_predicate(value,mapping)
    return {"field":native_field,**predicate}


def _transform_set(expression):
    if not isinstance(expression,dict):
        return copy.deepcopy(expression)
    if "operands" in expression:
        return copy.deepcopy(expression)

    operator={
        "union":"union",
        "intersection":"intersection",
        "complement":"difference",
    }.get(str(expression.get("operator","union")).lower())
    if operator is None:
        raise ValueError(f"unsupported legacy Set operator: {expression.get('operator')!r}")

    members=expression.get("members") or []
    filters=copy.deepcopy(expression.get("filters") or [])
    operands=[]
    for member in members:
        if not isinstance(member,dict):
            raise ValueError("invalid legacy Set member")
        if isinstance(member.get("object"),str):
            operands.append({
                "object":member["object"],
                "filters":copy.deepcopy(filters),
            })
        elif isinstance(member.get("set"),dict):
            if filters:
                raise ValueError(
                    "legacy nested Set unexpectedly carries object filters"
                )
            operands.append({"set":_transform_set(member["set"])})
        else:
            raise ValueError("unsupported legacy Set member")
    if not operands:
        raise ValueError("legacy Set has no operands")
    return {"operator":operator,"operands":operands}


def _extract_collector_value(source_value, mapping: dict):
    if isinstance(source_value,dict) and "value" in source_value:
        op=source_value.get("operation","equals")
        if _translate(mapping,"operation",op) != "equal":
            raise ValueError("collector input cannot use comparison semantics")
        if bool(source_value.get("mask",False)):
            raise ValueError("collector input cannot be masked")
        source_value=source_value["value"]
    return copy.deepcopy(source_value)


def apply_capability_mapping(document: dict, mapping: dict) -> dict:
    """Translate one aligned Assessment capability into its clean native shape."""
    result=copy.deepcopy(document)
    assessment=result.get("assessment",result)
    legacy=source_capability(mapping)
    native=mapping["capability"]
    native_cfg=mapping.get("native") or {}

    objects=assessment.get("objects") or {}
    for obj in objects.values():
        if obj.get("capability") != legacy:
            continue
        obj["capability"]=native
        select=obj.get("select")
        collector_map=native_cfg.get("collection_parameter_source_map") or {}
        if isinstance(select,dict) and collector_map:
            collect={}
            remaining={}
            for key,value in select.items():
                if key in collector_map:
                    collect[collector_map[key]]=_extract_collector_value(value,mapping)
                else:
                    remaining[key]=value
            if collect:
                obj["collect"]=collect
            if remaining:
                obj["select"]=remaining
            else:
                obj.pop("select",None)

        selector_map=native_cfg.get("selector_map") or {}
        if isinstance(obj.get("select"),dict) and selector_map:
            renamed={}
            for key,value in obj["select"].items():
                renamed[selector_map.get(key,key)]=value
            obj["select"]=renamed

        if isinstance(obj.get("set"),dict):
            obj["set"]=_transform_set(obj["set"])
        obj.pop("filters",None)
        obj.pop("behaviors",None)

    states=assessment.get("states") or {}
    for state in states.values():
        if state.get("capability") != legacy:
            continue
        state["capability"]=native
        state["state"]=_transform_state_payload(state.get("state"),mapping)

    tests=assessment.get("tests") or {}
    for test in tests.values():
        if test.get("capability") != legacy:
            continue
        test["capability"]=native
        if "check_existence" in test:
            test["existence"]=_translate(
                mapping,"existence",test.pop("check_existence")
            )
        if "check" in test:
            test["match"]=_translate(mapping,"check",test.pop("check"))
        if "state_operator" in test:
            legacy_operator=test.pop("state_operator")
            test["states_match"]=LOGICAL_OPERATOR.get(
                legacy_operator,legacy_operator
            )

    return result



def ready_capability_mappings(mapping_dir: Path):
    """Yield reviewed mappings explicitly approved for post-alignment conversion."""
    for path in sorted(mapping_dir.glob("*.json")):
        mapping=json.loads(path.read_text(encoding="utf-8"))
        if (mapping.get("native") or {}).get("post_alignment_ready",False):
            yield mapping


def apply_ready_capability_mappings(document: dict, mapping_dir: Path) -> dict:
    """Apply only explicitly reviewed clean-native mappings to one Assessment."""
    result=copy.deepcopy(document)
    for mapping in ready_capability_mappings(mapping_dir):
        result=apply_capability_mapping(result,mapping)
    return result
