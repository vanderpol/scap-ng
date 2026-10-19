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
    if type(spec) is not str or not re.fullmatch(r"0?[0-7]{3,4}",spec):
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
    return {"stage":"C_RESEARCH_PERMISSION_BIT_SUBSET_TO_A_STATES",
            "capability":"unix.file","allowed_octal":format(allowed,"04o"),
            "forbidden":forbidden,"states":native_states,
            "states_match":"all" if len(native_states)>1 else None,
            "scanner_executed":False,
            "source_parity_verified":False}

def evaluate_mode_against_C_macro(mode,compiled):
    """Independent source mode oracle: no disallowed POSIX permission bit."""
    if type(mode) is not int or not 0<=mode<=ALL:
        raise ValueError("POSIX mode integer 0000..7777 required")
    allowed=int(compiled["allowed_octal"],8)
    return mode&~allowed==0
