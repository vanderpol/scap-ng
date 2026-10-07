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


V03_COMMON_CROSSWALK = {
    "operation": {
        "equals": "equals",
        "not equal": "not_equal",
        "case insensitive equals": "case_insensitive_equals",
        "case insensitive not equal": "case_insensitive_not_equal",
        "greater than": "greater_than",
        "greater than or equal": "greater_than_or_equal",
        "less than": "less_than",
        "less than or equal": "less_than_or_equal",
        "bitwise and": "bitwise_and",
        "bitwise or": "bitwise_or",
        "pattern match": "pattern_match",
        "subset of": "subset_of",
        "superset of": "superset_of",
    },
    "check": {
        "all": "all",
        "at least one": "one_or_more",
        "only one": "one",
        "none satisfy": "none",
    },
    "existence": {
        "all_exist": "all",
        "at_least_one_exists": "one_or_more",
        "none_exist": "none",
        "only_one_exists": "one",
        "any_exist": "optional",
    },
}

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
    if mapping.get("specification_version") == "0.3.0":
        # 0.3 canonical vocabulary deliberately supersedes 0.2 presentation
        # aliases even when an older copied mapping still documents them.
        table.update(V03_COMMON_CROSSWALK.get(group) or {})
    if value in table:
        translated=table[value]
        if isinstance(translated,str) and translated.startswith("migration_error"):
            raise ValueError(f"unsupported legacy {group} value: {value}")
        return translated
    return value


def _normalize_legacy_literal(value, datatype):
    """Convert XML lexical scalar values to native JSON/YAML scalar types."""
    if isinstance(value, dict):
        return copy.deepcopy(value)
    if datatype == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1"}:
                return True
            if normalized in {"false", "0"}:
                return False
        raise ValueError(f"invalid legacy boolean literal: {value!r}")
    if datatype == "integer":
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str):
            return int(value, 10)
        raise ValueError(f"invalid legacy integer literal: {value!r}")
    if datatype == "float":
        if isinstance(value, bool):
            raise ValueError(f"invalid legacy float literal: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        raise ValueError(f"invalid legacy float literal: {value!r}")
    return copy.deepcopy(value)


def _native_scalar_predicate(payload: dict, mapping: dict, *, record_field=False):
    datatype = _translate(mapping,"datatype",payload.get("datatype","string"))
    out={
        "value": _normalize_legacy_literal(payload.get("value"), datatype),
        "operation": _translate(mapping,"operation",payload.get("operation","equals")),
        "datatype": datatype,
        "match": _translate(mapping,"check",payload.get("entity_check","all")),
    }
    if bool(payload.get("mask",False)):
        out["redact_result"]=True
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



def _native_object_predicate(payload: dict, mapping: dict):
    """Translate one aligned OVAL Object entity into the shared native predicate."""
    if not isinstance(payload,dict) or "value" not in payload:
        raise ValueError("native Object selector requires an entity payload with value")
    datatype = _translate(mapping,"datatype",payload.get("datatype","string"))
    out={
        "value":_normalize_legacy_literal(payload.get("value"), datatype),
        "operation":_translate(mapping,"operation",payload.get("operation","equals")),
        "datatype":datatype,
    }
    if bool(payload.get("mask",False)) or bool(payload.get("redact_result",False)):
        out["redact_result"]=True
    if "variable_check" in payload:
        out["variable_match"]=_translate(
            mapping,"check",payload.get("variable_check","all")
        )
    return out


def _coerce_collection_parameter(value, spec: dict):
    kind=spec.get("type")
    if kind=="boolean":
        if isinstance(value,bool):
            return value
        if isinstance(value,str):
            normalized=value.strip().lower()
            if normalized in ("true","1"):
                return True
            if normalized in ("false","0"):
                return False
        raise ValueError(f"invalid boolean collection parameter value: {value!r}")
    if kind=="integer":
        if isinstance(value,int) and not isinstance(value,bool):
            return value
        if isinstance(value,str):
            return int(value,10)
        raise ValueError(f"invalid integer collection parameter value: {value!r}")
    return copy.deepcopy(value)


def _materialize_file_traversal(obj: dict, mapping: dict):
    """Translate OVAL file scope and downward recursion into separate native fields.

    Filesystem scope remains explicit even when no recursion occurs because
    OVAL recurse_file_system also constrains exact-path and search collection.
    """
    native_cfg=mapping.get("native") or {}
    traversal_definition=native_cfg.get("traversal_definition")
    if traversal_definition is None and native_cfg.get("uses_file_traversal",False):
        traversal_definition="file_traversal"
    if traversal_definition not in {"file_traversal","windows_file_traversal"}:
        return

    # Set-only Objects inherit the scope of their operand Objects. Direct file
    # selectors materialize the OVAL recurse_file_system default explicitly.
    if not isinstance(obj.get("select"),dict):
        return

    behaviors=obj.get("behaviors") or {}
    traversal_keys={"max_depth","recurse","recurse_direction","recurse_file_system"}

    direction=str(behaviors.get("recurse_direction","none"))
    if direction=="up":
        raise ValueError("unsupported deprecated OVAL recurse_direction value: up")
    if direction not in {"none","down"}:
        raise ValueError(f"unsupported OVAL recurse_direction value: {direction!r}")

    filesystem_source=str(behaviors.get("recurse_file_system","all"))
    traversal_crosswalk=(mapping.get("migration_crosswalk") or {}).get("traversal") or {}
    mapped=traversal_crosswalk.get(f"recurse_file_system.{filesystem_source}")
    if isinstance(mapped,str) and mapped.startswith("migration_error"):
        raise ValueError(
            f"unsupported OVAL recurse_file_system value: {filesystem_source!r}"
        )
    if mapped is None:
        mapped={
            "all":"all" if mapping.get("specification_version")=="0.3.0" else "any",
            "local":"local",
            "defined":"same",
        }.get(filesystem_source)
    if mapped is None:
        raise ValueError(
            f"unsupported OVAL recurse_file_system value: {filesystem_source!r}"
        )
    # 0.3 canonical scope restores OVAL 'all'; 0.2 remains frozen as 'any'.
    if mapping.get("specification_version")=="0.3.0" and mapped=="any":
        mapped="all"
    obj["filesystem"]=mapped

    recurse_source=str(
        behaviors.get(
            "recurse",
            "junctions and directories"
            if traversal_definition=="windows_file_traversal"
            else "symlinks and directories",
        )
    )
    recurse_map={
        "directories":"directories",
        "symlinks":"symlinks",
        "symlinks and directories":"symlinks_and_directories",
        "junctions":"junctions",
        "junctions and directories":"junctions_and_directories",
    }
    recurse=recurse_map.get(recurse_source)
    if recurse is None:
        raise ValueError(f"unsupported or deprecated OVAL recurse value: {recurse_source!r}")

    try:
        raw_depth=int(behaviors.get("max_depth",-1))
    except (TypeError,ValueError) as exc:
        raise ValueError(
            f"invalid OVAL max_depth value: {behaviors.get('max_depth')!r}"
        ) from exc
    if raw_depth < -1:
        raise ValueError(f"invalid OVAL max_depth value: {raw_depth}")

    select=obj.get("select") or {}
    has_full_path="full_path" in select or "filepath" in select
    if has_full_path and direction=="down":
        raise ValueError("OVAL file recursion is not valid with full_path selection")
    if not has_full_path and direction=="down":
        obj["traversal"]={
            "max_depth":None if raw_depth==-1 else raw_depth,
            "recurse":recurse,
        }

    for key in traversal_keys:
        behaviors.pop(key,None)
    if behaviors:
        obj["behaviors"]=behaviors
    else:
        obj.pop("behaviors",None)


def _materialize_hierarchy_traversal(obj: dict, mapping: dict):
    """Translate non-deprecated OVAL hierarchy recursion to native traversal."""
    native_cfg=mapping.get("native") or {}
    if native_cfg.get("traversal_definition")!="hierarchy_traversal":
        return
    if not isinstance(obj.get("select"),dict):
        return

    behaviors=obj.get("behaviors") or {}
    direction=str(behaviors.get("recurse_direction","none"))
    if direction=="up":
        raise ValueError("unsupported deprecated OVAL recurse_direction value: up")
    if direction not in {"none","down"}:
        raise ValueError(f"unsupported OVAL recurse_direction value: {direction!r}")
    try:
        raw_depth=int(behaviors.get("max_depth",-1))
    except (TypeError,ValueError) as exc:
        raise ValueError(
            f"invalid OVAL max_depth value: {behaviors.get('max_depth')!r}"
        ) from exc
    if raw_depth < -1:
        raise ValueError(f"invalid OVAL max_depth value: {raw_depth}")

    if direction=="down":
        obj["traversal"]={"max_depth":None if raw_depth==-1 else raw_depth}

    for key in ("max_depth","recurse_direction"):
        behaviors.pop(key,None)
    if behaviors:
        obj["behaviors"]=behaviors
    else:
        obj.pop("behaviors",None)


def _materialize_behavior_collection_parameters(obj: dict, mapping: dict):
    """Move reviewed OVAL behavior inputs into explicit native collection parameters."""
    native_cfg=mapping.get("native") or {}
    specs=native_cfg.get("collection_parameters") or {}
    if not specs:
        return
    crosswalk=mapping.get("migration_crosswalk") or {}
    defaults=crosswalk.get("materialized_defaults") or {}
    behavior_map=crosswalk.get("behaviors") or {}
    source_for_collect={}
    for source_name,target in behavior_map.items():
        if isinstance(target,str) and target.startswith("collect."):
            source_for_collect[target.split(".",1)[1]]=source_name

    behaviors=obj.get("behaviors") or {}
    collect=copy.deepcopy(obj.get("collect") or {})
    consumed=set()
    for name,spec in specs.items():
        default_key=f"behaviors.{name}"
        source_name=source_for_collect.get(name,name)
        source_default_key=f"behaviors.{source_name}"
        if source_name in behaviors:
            collect[name]=_coerce_collection_parameter(behaviors[source_name],spec)
            consumed.add(source_name)
        elif default_key in defaults:
            collect[name]=_coerce_collection_parameter(defaults[default_key],spec)
        elif source_default_key in defaults:
            collect[name]=_coerce_collection_parameter(defaults[source_default_key],spec)
        elif name in source_for_collect and spec.get("required") and spec.get("type")=="boolean":
            # Reviewed OVAL behavior mappings are XSD-defaulted false unless the
            # mapping explicitly supplies a different materialized default.
            collect[name]=False
    if collect:
        obj["collect"]=collect
    remaining={k:v for k,v in behaviors.items() if k not in consumed}
    deprecated=set(crosswalk.get("deprecated") or {}) & set(remaining)
    if deprecated:
        raise ValueError(
            "unsupported deprecated OVAL behavior semantics: "
            + ", ".join(sorted(deprecated))
        )
    if remaining:
        raise ValueError(
            "unmapped OVAL behavior semantics remain for reviewed native capability: "
            + ", ".join(sorted(remaining))
        )
    obj.pop("behaviors",None)

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
    out={
        "match":_translate(mapping,"check",parent_payload.get("entity_check","all")),
        "existence":_translate(
            mapping,"existence",
            parent_payload.get("entity_existence","at_least_one_exists")
        ),
        "fields":fields,
    }
    if bool(parent_payload.get("mask",False)):
        out["redact_result"]=True
    return out


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
    state_value_crosswalk=(mapping.get("native") or {}).get("state_value_crosswalk") or {}
    group=state_value_crosswalk.get(native_field)
    if group and not isinstance(predicate.get("value"),dict):
        predicate["value"]=_translate(mapping,group,predicate.get("value"))
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


def _native_object_record(record_value, mapping: dict):
    fields={}
    for field in record_value.get("record") or []:
        name=field.get("name")
        if not isinstance(name,str) or not name:
            raise ValueError("record field missing name")
        if name in fields:
            raise ValueError(f"legacy Object record contains duplicate field {name!r}")
        predicate=_native_object_predicate(field,mapping)
        predicate["match"]=_translate(
            mapping,"check",field.get("entity_check","all")
        )
        fields[name]=predicate
    return {"fields":fields}


def _extract_collector_value(source_value, mapping: dict, *, allowed_source_operations=None):
    if isinstance(source_value,dict) and bool(source_value.get("nil",False)):
        return None
    if isinstance(source_value,dict) and "value" in source_value:
        op=source_value.get("operation","equals")
        allowed=set(allowed_source_operations or ("equals",))
        if op not in allowed:
            raise ValueError(
                "collector input cannot use comparison semantics: "
                f"operation={op!r}, allowed={sorted(allowed)!r}"
            )
        if bool(source_value.get("mask",False)) or bool(source_value.get("redact_result",False)):
            raise ValueError(
                "collector input redaction cannot be preserved by scalar collection-parameter lowering"
            )
        datatype=_translate(mapping,"datatype",source_value.get("datatype","string"))
        raw=source_value["value"]
        if datatype=="record" and isinstance(raw,dict) and "record" in raw:
            return _native_object_record(raw,mapping)
        return _normalize_legacy_literal(raw,datatype)
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
            source_operations=native_cfg.get("collection_parameter_source_operations") or {}
            for key,value in select.items():
                if key in collector_map:
                    collect[collector_map[key]]=_extract_collector_value(
                        value,
                        mapping,
                        allowed_source_operations=source_operations.get(key),
                    )
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
            enum_selectors=set((native_cfg.get("selector_value_enums") or {}).keys())
            selector_value_crosswalk=native_cfg.get("selector_value_crosswalk") or {}
            selector_source_operations=native_cfg.get("selector_source_operations") or {}
            for key,value in obj["select"].items():
                native_key=selector_map.get(key,key)
                if isinstance(value,dict) and bool(value.get("nil",False)):
                    nullable=set(native_cfg.get("nullable_selectors",["name"]))
                    if native_key not in nullable:
                        raise ValueError(
                            f"legacy nil Object entity has no reviewed native mapping: {key}"
                        )
                    renamed[native_key]=None
                    continue
                if native_key in enum_selectors:
                    if isinstance(value,dict) and "variable" in value:
                        renamed[native_key]=copy.deepcopy(value)
                    elif isinstance(value,dict) and "value" in value:
                        raw=_extract_collector_value(
                            value,
                            mapping,
                            allowed_source_operations=selector_source_operations.get(key),
                        )
                        group=selector_value_crosswalk.get(native_key)
                        renamed[native_key]=_translate(mapping,group,raw) if group else raw
                    else:
                        group=selector_value_crosswalk.get(native_key)
                        renamed[native_key]=_translate(mapping,group,value) if group else copy.deepcopy(value)
                    continue
                renamed[native_key]=_native_object_predicate(value,mapping)
            obj["select"]=renamed

        _materialize_file_traversal(obj,mapping)
        _materialize_hierarchy_traversal(obj,mapping)
        if isinstance(obj.get("set"),dict):
            if obj.get("behaviors"):
                raise ValueError(
                    "Set Object carries unexpected capability behaviors that require explicit migration"
                )
            obj.pop("behaviors",None)
        else:
            _materialize_behavior_collection_parameters(obj,mapping)

        if isinstance(obj.get("set"),dict):
            obj["set"]=_transform_set(obj["set"])

        direct_filters=copy.deepcopy(obj.pop("filters",None) or [])
        if direct_filters and not isinstance(obj.get("set"),dict):
            # OVAL permits filters directly on an Object. Native 0.3 keeps
            # filters on Set operands, so represent the same population as a
            # one-operand union whose inline Object is the unfiltered source.
            title=obj.get("object_title")
            base=copy.deepcopy(obj)
            obj.clear()
            obj["capability"]=native
            if title is not None:
                obj["object_title"]=title
            obj["set"]={
                "operator":"union",
                "operands":[{"object":base,"filters":direct_filters}],
            }

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
            translated=_translate(mapping,"existence",test.pop("check_existence"))
            if mapping.get("specification_version")=="0.3.0":
                test["existence"]=translated
            else:
                test["check_existence"]=translated
        if "check" in test:
            translated=_translate(mapping,"check",test.pop("check"))
            if mapping.get("specification_version")=="0.3.0":
                test["match"]=translated
            else:
                test["check"]=translated
        if "state_operator" in test:
            legacy_operator=test.pop("state_operator")
            test["states_match"]=LOGICAL_OPERATOR.get(
                legacy_operator,legacy_operator
            )
        elif len(test.get("states") or []) > 1:
            # OVAL's omitted state_operator is AND. SCAP-NG native 0.2.0
            # forbids hidden semantic defaults, so conversion materializes it.
            test["states_match"]="all"

    test_source=native_cfg.get("test_source") or {}
    if test_source.get("kind")=="variable":
        variable_field=test_source.get("field","variable")
        variables=assessment.get("variables") or {}
        consumed_objects=set()

        def explicit_object_refs(value, target):
            count=0
            if isinstance(value,dict):
                for key,child in value.items():
                    if key=="object" and child==target:
                        count+=1
                    else:
                        count+=explicit_object_refs(child,target)
            elif isinstance(value,list):
                for child in value:
                    count+=explicit_object_refs(child,target)
            return count

        for test_id,test in tests.items():
            if test.get("capability") != native:
                continue
            object_id=test.pop("object",None)
            if not isinstance(object_id,str) or object_id not in objects:
                raise ValueError(
                    f"Variable-source Test {test_id!r} does not reference one legacy Variable Object"
                )
            obj=objects[object_id]
            if obj.get("capability") != native:
                raise ValueError(
                    f"Variable-source Test {test_id!r} references incompatible Object {object_id!r}"
                )
            meaningful=set(obj)-{"object_title","capability","select"}
            if meaningful:
                raise ValueError(
                    f"legacy Variable Object {object_id!r} carries unexpected semantics: "
                    + ", ".join(sorted(meaningful))
                )
            select=obj.get("select")
            if not isinstance(select,dict) or set(select)!={"var_ref"}:
                raise ValueError(
                    f"legacy Variable Object {object_id!r} must contain only select.var_ref"
                )
            selector=select["var_ref"]
            if not isinstance(selector,dict):
                raise ValueError(f"invalid var_ref selector on {object_id!r}")
            if selector.get("operation","equals")!="equals":
                raise ValueError(
                    f"legacy Variable Object {object_id!r} var_ref must use equality"
                )
            if selector.get("datatype","string")!="string":
                raise ValueError(
                    f"legacy Variable Object {object_id!r} var_ref must be a string identity"
                )
            if bool(selector.get("mask",False)) or bool(selector.get("redact_result",False)):
                raise ValueError(
                    f"legacy Variable Object {object_id!r} var_ref cannot carry redaction semantics"
                )
            unsupported=set(selector)-{"operation","datatype","value","mask","redact_result"}
            if unsupported:
                raise ValueError(
                    f"legacy Variable Object {object_id!r} var_ref carries unsupported semantics: "
                    + ", ".join(sorted(unsupported))
                )
            source=selector.get("value")
            if not (
                isinstance(source,dict)
                and set(source)=={"variable"}
                and isinstance(source.get("variable"),str)
            ):
                raise ValueError(
                    f"legacy Variable Object {object_id!r} var_ref is not one exact Variable reference"
                )
            variable_id=source["variable"]
            if variable_id not in variables:
                raise ValueError(
                    f"Variable-source Test {test_id!r} references missing Variable {variable_id!r}"
                )
            test[variable_field]=variable_id
            consumed_objects.add(object_id)

        if consumed_objects:
            other_objects={
                identity:payload
                for identity,payload in objects.items()
                if identity not in consumed_objects
            }
            remaining_graph={
                "objects":other_objects,
                "variables":assessment.get("variables") or {},
                "states":states,
                "tests":tests,
                "evaluate":assessment.get("evaluate"),
            }
            for object_id in sorted(consumed_objects):
                if explicit_object_refs(remaining_graph,object_id):
                    raise ValueError(
                        f"legacy Variable Object {object_id!r} has non-Test graph consumers"
                    )
                del objects[object_id]

    elif test_source.get("kind")=="none":
        singleton_ids={
            object_id
            for object_id,obj in objects.items()
            if obj.get("capability")==native
        }
        for test in tests.values():
            if test.get("capability") != native:
                continue
            object_id=test.pop("object",None)
            if object_id is not None and object_id not in singleton_ids:
                raise ValueError(
                    f"singleton-source Test referenced non-singleton Object: {object_id}"
                )
        for object_id in sorted(singleton_ids):
            obj=objects[object_id]
            meaningful=set(obj)-{"object_title","capability"}
            if meaningful:
                raise ValueError(
                    f"singleton-source Object carries unexpected semantics: {object_id}: "
                    + ", ".join(sorted(meaningful))
                )
            del objects[object_id]

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
    assessment=result.get("assessment",result)
    # OVAL permits an omitted Test state_operator and defines that omission as
    # AND. Native SCAP-NG 0.2.0 does not permit hidden semantic defaults, so
    # materialize the equivalent aggregation after all capability mappings.
    for test in (assessment.get("tests") or {}).values():
        if isinstance(test,dict) and len(test.get("states") or []) > 1 and "states_match" not in test:
            test["states_match"]="all"
    for section in ("objects","states","tests"):
        for identity,node in (assessment.get(section) or {}).items():
            if not isinstance(node,dict):
                continue
            capability=node.get("capability")
            if capability == "windows.wmi":
                raise ValueError(f"deprecated source capability windows.wmi at {section}.{identity}; use reviewed windows.wmi.query only for wmi57 source")
            if capability == "independent.sqlext":
                raise ValueError(
                    f"nonstandard source capability independent.sqlext at {section}.{identity}; "
                    "publisher extensions outside official SCAP 1.4/OVAL are not convertible to SCAP-NG"
                )
    return result
