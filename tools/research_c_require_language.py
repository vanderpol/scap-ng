#!/usr/bin/env python3
"""#245 A real 0.4-C requirements-first *research* compiler.

C syntax is NOT normative. It compiles a small native, typed subset to the
existing v0.4-A collection and State contract. No collector code or result
tables are reimplemented. Unusual existence/matching combinations remain
representable via an explicit source-preserving advanced pair.

Never treat schema validity, structural lowering or synthetic Item results as
proven OVAL source/scanner parity.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import yaml

def parse_c_yaml(source):
    """Strict, one-document YAML input; silent duplicate predicates are unsafe."""
    if type(source) is not str or not source or len(source)>200000:
        raise ValueError("bounded C YAML source text required")

    class StrictLoader(yaml.SafeLoader):
        pass

    def mapping(loader,node):
        out={}
        for kn,vn in node.value:
            key=loader.construct_object(kn)
            if type(key) is not str:
                raise ValueError("C YAML mapping key must be a string; quote YAML 1.1 boolean-like words")
            try:known=key in out
            except TypeError as exc:raise ValueError("non-scalar mapping key") from exc
            if known:raise ValueError("duplicate YAML mapping key "+str(key))
            out[key]=loader.construct_object(vn)
        return out

    StrictLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
    docs=list(yaml.load_all(source,Loader=StrictLoader))
    if len(docs)!=1 or not isinstance(docs[0],dict):
        raise ValueError("exactly one C YAML mapping required")
    return docs[0]

ROOT=Path(__file__).resolve().parents[1]
MAPPINGS=ROOT/"schema/v0.4.0/capability-mappings/supported"
SCHEMA=ROOT/"schema/v0.4.0/assessment-language.schema.json"
# Both values are maintained by the existing A schema, not redefined here.
PRESENCE="presence_requirement"
PAIRED="paired_requirement"
# Literal shorthand is a source-level contract, not a guess made by runtime.
SHORTHANDS={
    "any_item": "at_least_one_exists_and_some_match",
    "every_item": "at_least_one_exists_and_all_match",
    "one_matching_item": "at_least_one_exists_and_only_one_matches",
    "no_matching_item": "at_least_one_exists_and_none_match",
    "exactly_one_item": "only_one_exists_and_matches",
}
PRESENCE_WORDS={
    "present":"at_least_one_exists",
    "absent":"none_exist",
    "one_item_exists":"only_one_exists",
    "all_items_exist":"all_exist",
    "optional":"may_be_absent",
}
EXISTENCE={
    "none":"none_exist",
    "exactly_one":"only_one_exists",
    "one_or_more":"at_least_one_exists",
    "all":"all_exist",
    "optional":"may_be_absent",
}
MATCH={
    "every":"all_match",
    "one":"only_one_matches",
    "some":"some_match",
    "none":"none_match",
}
SCALAR=(str,int,float,bool)
OPS={"equals","not_equal","matches_regex"}
MAX_FIELDS=100

def _catalog():
    data=json.loads(SCHEMA.read_text(encoding="utf-8"))
    defs=data["$defs"]
    return set(defs[PAIRED]["enum"]),set(defs[PRESENCE]["enum"])

def _mapping(capability):
    if type(capability) is not str or not capability or "/" in capability or (
        capability.startswith(".")
    ):
        raise ValueError("invalid capability identity")
    p=MAPPINGS/(capability+".json")
    if not p.is_file():
        raise ValueError("capability has no supported A mapping")
    m=json.loads(p.read_text(encoding="utf-8"))
    if m.get("specification_version")!="0.4.0" or m.get("capability")!=capability or (
        m.get("native",{}).get("post_alignment_ready") is not True
    ):
        raise ValueError("native capability mapping unsupported")
    return m["native"]

def _typed_fields(fields, native, capability):
    if isinstance(fields,dict) and "permission_bits" in fields:
        if capability!="unix.file" or set(fields)!={"permission_bits"}:
            raise ValueError("permission macro only valid as explicit unix.file Item predicate")
        from research_c_permissions_macro import lower_no_more_permissive_than
        return lower_no_more_permissive_than(fields["permission_bits"])["states"]
    if not isinstance(fields,dict) or not fields or len(fields)>MAX_FIELDS:
        raise ValueError("must name 1..100 fields tested on the SAME Item")
    allowed=native["state_field_map"]
    out=[]
    registry_type=fields.get("type") if "type" in fields else None
    registry_expected=(registry_type if isinstance(registry_type,str)
                       else registry_type.get("equals") if isinstance(registry_type,dict)
                       else None)
    for field,raw in fields.items():
        if field not in allowed or not isinstance(field,str):
            raise ValueError(f"unknown or unsupported State field {field!r}")
        if type(raw) in SCALAR:
            op,value="equals",raw
        elif isinstance(raw,dict) and set(raw) in ({ "equals" },{"not_equal"},{"matches_regex"}):
            op,value=next(iter(raw.items()))
        elif isinstance(raw,dict) and set(raw)=={"equals","datatype"}:
            op,value="equals",raw["equals"]
            if raw["datatype"] not in native["field_datatypes"].get(field,[]):
                raise ValueError(f"invalid typed {field} datatype")
        elif isinstance(raw,dict) and set(raw)=={"contains"}:
            # Exists+some-match over observed MULTI-VALUED field, not an
            # ordinary substring operation. The field must be explicitly
            # approved for this currently one real Linux source fixture.
            if field!="mount_options":
                raise ValueError("contains is not a universal field operation")
            op,value="equals",raw["contains"]
        else:
            raise ValueError(f"unsupported / ambiguous predicate at {field}")
        if type(value) not in SCALAR or isinstance(value,float) or (
            type(value) is str and not value
        ):
            raise ValueError("typed literal required; no implicit values or coercion")
        if op=="matches_regex" and type(value) is not str:
            raise ValueError("regular expression requires a string pattern")
        expected_types=native["field_datatypes"].get(field,[])
        if type(value) is str and not any(t in expected_types for t in ("string","version")):
            raise ValueError("string value incompatible with native field datatype")
        if type(value) is int and "integer" not in expected_types:
            raise ValueError("integer value incompatible with native field datatype")
        if type(value) is bool and "boolean" not in expected_types:
            raise ValueError("boolean value incompatible with native field datatype")
        if field=="type" and "type" in native.get("state_value_enums",{}) and (
            value not in native["state_value_enums"]["type"]
        ):
            raise ValueError("registry storage type is not a pinned native enum")
        # A single Item's field can itself be many-valued; the shorthand
        # 'contains' is explicitly some of the available values. Plain
        # equals is all matches for an ordinary scalar field in this pilot.
        field_req=("at_least_one_exists_and_some_match" if
                   isinstance(raw,dict) and "contains" in raw else
                   "at_least_one_exists_and_all_match")
        out.append({field:{"require":field_req,op:deepcopy(value)}})
    if registry_expected in ("dword","qword") and "value" in fields:
        v=fields["value"]
        v=v.get("equals") if isinstance(v,dict) else v
        if type(v) is not int:
            raise ValueError("DWORD/QWORD requires explicitly numeric value")
    return out

def _selectors(selector, native):
    # Author can type simple literal selector fields; all matching
    # operations are preserved when a mapping explicitly supports them.
    if not isinstance(selector,dict):
        raise ValueError("a named source selector mapping is required")
    sets=native.get("object_selector_alternatives",[])
    if not any(set(selector)==set(keys) for keys in sets):
        raise ValueError("selector fields don't match an A mapping alternative")
    converted={}
    for field,value in selector.items():
        # The 0.4-A selector alternatives use canonical *native* names,
        # whereas selector_map keys are legacy OVAL source names. Never
        # force C authors back to the OVAL "filepath/path/filename" tokens.
        if field not in native["selector_map"].values():
            raise ValueError("unsupported Object selector")
        if type(value) in (str,int):
            converted[field]={"equals":value}
        elif isinstance(value,dict) and set(value) in ({"equals"},{"matches_regex"}):
            converted[field]=deepcopy(value)
        else:
            raise ValueError("unsupported/implicit Object predicate")
        if "matches_regex" in converted[field] and (
            type(converted[field]["matches_regex"]) is not str
        ):
            raise ValueError("selector regex requires a string pattern")
        enumerated=native.get("selector_value_enums",{}).get(field)
        if enumerated and converted[field].get("equals") not in enumerated:
            raise ValueError(f"{field} selector must use native enum")
    return converted

def _source_object(capability, authored, native):
    """One A contract: a selector OR a typed collection-parameter shape."""
    if "object_selector_alternatives" in native:
        return {"capability":capability,"select":_selectors(authored,native)}
    parameters=native.get("collection_parameters")
    if not isinstance(parameters,dict) or not isinstance(authored,dict):
        raise ValueError("capability lacks supported native acquisition contract")
    required={name for name,definition in parameters.items()
              if definition.get("required") is True}
    if not required <= set(authored) or set(authored)-set(parameters):
        raise ValueError("missing or unexpected source collection parameter")
    result={}
    for name,value in authored.items():
        definition=parameters[name]
        if definition.get("type")=="string":
            if type(value) is not str or not value or len(value)>4096:
                raise ValueError("bounded literal collection argument required")
        elif definition.get("type")=="boolean":
            if type(value) is not bool:
                raise ValueError("explicit Boolean collector flag required")
        else:
            raise ValueError("unsupported native collector parameter type")
        if definition.get("enum") and value not in definition["enum"]:
            raise ValueError("collection parameter not in versioned capability enum")
        result[name]=deepcopy(value)
    return {"capability":capability,"collect":result}


def _requirement(must,has_fields):
    paired,presence=_catalog()
    if must in PRESENCE_WORDS if isinstance(must,str) else False:
        if has_fields:raise ValueError("presence-only Test cannot have States")
        token=PRESENCE_WORDS[must]
        if token not in presence:raise ValueError("unsupported presence token")
        return token,{}
    if not isinstance(must,dict) or not must:
        raise ValueError("must is explicit; no hidden defaults")
    # Bare must means a successful, NONEMPTY Item population with SOME match.
    # No invented exact-one-exists or all-match default.
    if not any(k in must for k in (
        "any_item","every_item","one_matching_item","no_matching_item",
        "exactly_one_item","items_exist","items_match","special_source_requirement",
        "fields")):
        fields=must
        token=SHORTHANDS["any_item"]
    elif len(must)==1 and next(iter(must)) in SHORTHANDS:
        mode=next(iter(must))
        fields=must[mode]
        token=SHORTHANDS[mode]
    elif set(must)=={"items_exist","items_match","fields"}:
        exp=must["items_exist"]; match=must["items_match"]
        if exp not in EXISTENCE or match not in MATCH:
            raise ValueError("advanced existence/match enum unsupported")
        token=EXISTENCE[exp]+"_and_"+MATCH[match]
        fields=must["fields"]
    elif set(must)=={"special_source_requirement","fields"}:
        token=must["special_source_requirement"]
        fields=must["fields"]
        # Special source combinations such as only_one_exists_and_matches,
        # none_exist_and_only_one_matches must be transparent, not erased.
    else:
        raise ValueError("choose bare fields, named shorthand or explicit advanced pair")
    if token not in paired:
        raise ValueError("source requirement has no 0.4-A equivalent")
    if not has_fields:
        raise ValueError("State-bearing requirement needs field predicates")
    return token,fields

def compile_c_requirement(document):
    """Pure adapter: C YAML dict -> canonical A Test pieces, no execution."""
    if not isinstance(document,dict) or set(document)!={"from","must"}:
        raise ValueError("C requires from and must (no invented defaults)")
    source=document["from"]
    if not isinstance(source,dict) or len(source)!=1:
        raise ValueError("from must identify one capability")
    cap, selectors=next(iter(source.items()))
    native=_mapping(cap)
    obj=_source_object(cap,selectors,native)
    must=document["must"]
    has_fields=isinstance(must,dict)
    token,raw_fields=_requirement(must,has_fields)
    states=_typed_fields(raw_fields,native,cap) if has_fields else []
    result={"capability":cap,"object":obj,"require":token}
    if states:
        result["states"]=states
        if len(states)>1:result["states_match"]="all"
    return {"stage":"C_RESEARCH_LOWERED_TO_A_TEST_PIECES_NOT_EXECUTABLE",
            "test":result,"scanner_executed":False,"source_parity_verified":False}

# Only source-backed and audited common pair meanings enter the executable
# supplied-results seam. Every other A token remains preserved as authored
# compatibility data but is NOT guessed into one of these common operators.
TEST_OUTCOMES={
    "at_least_one_exists_and_some_match":("at_least_one_exists","one_of",True),
    "at_least_one_exists_and_all_match":("at_least_one_exists","every",True),
    "at_least_one_exists_and_only_one_matches":("at_least_one_exists","exactly_one",True),
    "at_least_one_exists_and_none_match":("at_least_one_exists","none",True),
}
PRESENCE_OUTCOMES={
    "at_least_one_exists":"at_least_one_exists",
    "none_exist":"none_exist",
    "only_one_exists":"only_one_exists",
    "all_exist":"all_exist",
    "may_be_absent":"any_exist",
}

def evaluate_compiled_c_supplied_items(compiled,evidence):
    """Reuse A's generic Test logic with externally supplied *Item* outcomes.

    All state-field evaluation is external. No OS collection, datatype
    comparison, Variable resolution, or source scanner parity is claimed.
    Unsupported advanced combinations are REPRESENTABLE but NOT executed.
    """
    from research_c_common_evaluation import population_outcome
    if not isinstance(compiled,dict) or compiled.get("stage")!=(
        "C_RESEARCH_LOWERED_TO_A_TEST_PIECES_NOT_EXECUTABLE"
    ) or compiled.get("source_parity_verified") is not False:
        raise ValueError("untrusted or executable C contract")
    t=compiled["test"]
    token=t["require"]
    if token in TEST_OUTCOMES and t.get("states"):
        exists,match,has_state=TEST_OUTCOMES[token]
    elif token in PRESENCE_OUTCOMES and not t.get("states"):
        exists,match,has_state=PRESENCE_OUTCOMES[token],"every",False
    else:
        raise ValueError("advanced C requirement preserved but not runtime-proven")
    if evidence.get("capability")!=t["capability"]:
        raise ValueError("collected Item capability differs from authored C selector")
    outcome=population_outcome(
        {"exists":exists,"items_match":match,"has_state":has_state},evidence)
    return {"outcome":outcome,
            "stage":"RESEARCH_SUPPLIED_ITEM_RESULTS_ONLY_NOT_SCANNER",
            "source_parity_verified":False,"collector_executed":False}

