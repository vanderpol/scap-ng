#!/usr/bin/env python3
"""#245 0.4-C research: meaningful POSIX permissions authoring compression.

Unlike numeric "mode <= 0740", the C phrase "no_more_permissive_than: '0740'"
means *set bits must be a subset* of allowed POSIX mode bits. This is lowered
to existing 0.4-A native unix.file State booleans using the version-local
OVAL-to-native mapping. It does NOT create a new OS collector.

This only covers conventional 12-bit POSIX mode flags. ACLs, mode rounding,
reparse paths, symlinks, recursive traversal, missing evidence, record status,
or whole Rule truth are NOT inferred from this macro.
"""
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.4.0/capability-mappings/supported/unix.file.json"

OVAL_BITS=(
    ("suid",0o4000),("sgid",0o2000),("sticky",0o1000),
    ("uread",0o400),("uwrite",0o200),("uexec",0o100),
    ("gread",0o040),("gwrite",0o020),("gexec",0o010),
    ("oread",0o004),("owrite",0o002),("oexec",0o001),
)
ALL=0o7777

def parse_allowed_mode(spec):
    if type(spec) is not str or not re.fullmatch(r"[0-7]{3,4}",spec):
        raise ValueError("POSIX allowed mode must be quoted octal with three or four digits")
    value=int(spec,8)
    if not 0<=value<=ALL:
        raise ValueError("mode out of POSIX 12-bit range")
    return value

def lower_no_more_permissive_than(candidate):
    if not isinstance(candidate,dict) or set(candidate)!={"no_more_permissive_than"}:
        raise ValueError("C permission macro must explicitly state maximum allowed mode bits")
    allowed=parse_allowed_mode(candidate["no_more_permissive_than"])
    mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
    if mapping.get("specification_version")!="0.4.0" or (
        mapping.get("capability")!="unix.file" or
        mapping.get("native",{}).get("post_alignment_ready") is not True
    ):
        raise ValueError("A mapping version cannot be trusted")
    native=mapping["native"]
    forbidden=[]
    native_states=[]
    for source_field,bit in OVAL_BITS:
        if allowed&bit:continue
        mapped=native["state_field_map"].get(source_field)
        if type(mapped) is not str or (
            native["field_datatypes"].get(mapped)!=["boolean"]
        ):
            raise ValueError("unsupported POSIX permission mapping / type")
        forbidden.append({"source_field":source_field,"native_field":mapped,
                          "octal_bit":format(bit,"04o")})
        native_states.append({mapped:{
            "require":"at_least_one_exists_and_all_match",
            "equals":False
        }})
    if not native_states:
        raise ValueError("permission macro allows every bit; use an explicit existence-only requirement")
    return {"stage":"C_RESEARCH_PERMISSION_BIT_SUBSET_TO_A_STATES",
            "capability":"unix.file","allowed_octal":format(allowed,"04o"),
            "forbidden":forbidden,"states":native_states,
            "states_match":"all" if len(native_states)>1 else None,
            "scanner_executed":False,
            "source_parity_verified":False}

def prove_legacy_source_permission_state_context(assessment, *, state_id,
                                                 permitted="0740"):
    """Guard a converted source rewrite as an authoring-only State alias.

    This is stricter than generic C-native authoring. All bit States must be
    referenced ONLY as an AND State in Tests, and NOT as a collection filter.
    The source Object/filter, Variable and Test references remain untouched.
    Passing proves rewrite ELIGIBILITY, not data acquisition/runtime parity.
    """
    from copy import deepcopy
    from hashlib import sha256

    if type(state_id) is not str or not isinstance(assessment,dict):
        raise ValueError("explicit legacy Assessment and State identity required")
    states=assessment.get("states")
    objects=assessment.get("objects")
    tests=assessment.get("tests")
    variables=assessment.get("variables")
    if not all(isinstance(x,dict) for x in (states,objects,tests,variables)) or (
        state_id not in states
    ):
        raise ValueError("full source State/Object/Variable/Test context required")
    source=states[state_id]
    if not isinstance(source,dict) or source.get("capability")!="unix.file" or (
        not isinstance(source.get("state"),dict) or
        set(source["state"])!={"all"} or
        not isinstance(source["state"]["all"],list)
    ):
        raise ValueError("permission State must be an explicit AND over native Unix file bits")
    macro=lower_no_more_permissive_than({"no_more_permissive_than":permitted})
    expected={b["source_field"] for b in macro["forbidden"]}
    original=source["state"]["all"]
    names=[]
    for term in original:
        if not isinstance(term,dict) or set(term)!={
            "field","value","operation","datatype",
            "entity_check","entity_existence"
        } or (
            term["field"] not in expected or
            term["value"]!="false" or
            term["operation"]!="equals" or
            term["datatype"]!="boolean" or
            term["entity_check"]!="all" or
            term["entity_existence"]!="at_least_one_exists"
        ):
            raise ValueError("permission State differs in field, operator or entity presence")
        names.append(term["field"])
    if len(names)!=len(expected) or set(names)!=expected:
        raise ValueError("permission bit State incomplete, duplicated or extra")

    def state_filter_refs(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key=="state" and child==state_id:
                    return True
                if state_filter_refs(child):
                    return True
        elif isinstance(value,list):
            return any(state_filter_refs(v) for v in value)
        return False

    for object_name,obj in objects.items():
        if state_filter_refs(obj):
            raise ValueError("permission State used by a collection Set/Filter: macro rewrite prohibited")

    consumers={}
    for name,test in tests.items():
        refs=test.get("states") if isinstance(test,dict) else None
        if not isinstance(refs,list):
            raise ValueError("unsupported original Test State references")
        if state_id in refs:
            if refs!=[state_id] or test.get("check")!="all" or (
                type(test.get("object")) is not str or
                test["object"] not in objects
            ):
                raise ValueError("shared State has nontrivial Test use")
            consumers[name]={
                "object":test["object"],
                "check_existence":test.get("check_existence"),
                "check":test["check"],
            }
    if not consumers:
        raise ValueError("permission State is not referenced by an Assessment Test")
    # The alias changes no legacy source graph; save a stable context witness
    # so a later compiler can assert that the source did not change.
    evidence={
        "source_state":state_id,
        "source_state_terms":deepcopy(original),
        "source_test_consumers":consumers,
        "source_objects":deepcopy(objects),
        "source_variables":deepcopy(variables),
    }
    digest=sha256(json.dumps(assessment,sort_keys=True,separators=(",",":"),
                              ensure_ascii=False).encode("utf-8")).hexdigest()
    return {"status":"SOURCE_STATE_ONLY_REWRITE_ELIGIBLE_NOT_EXECUTABLE",
            "source_assessment_sha256":digest,
            "source_context":evidence,
            "expanded_native_states":deepcopy(macro["states"]),
            "authoring_only":True,
            "filters_rewritten":False,
            "runtime_parity_verified":False}


def evaluate_mode_against_C_macro(mode,compiled):
    """Independent source mode oracle: no disallowed POSIX permission bit."""
    if type(mode) is not int or not 0<=mode<=ALL:
        raise ValueError("POSIX mode integer 0000..7777 required")
    allowed=int(compiled["allowed_octal"],8)
    return mode&~allowed==0
