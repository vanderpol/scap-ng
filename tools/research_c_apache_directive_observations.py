#!/usr/bin/env python3
"""Refs #245: Apache directive observations from precollected typed file lines.

This is a native C *research* fact reader, not a collector, Apache interpreter,
or faithful rewrite of DISA's distinct source shellcommand acquisitions.
No Includes, globs, module/vhost context, effective precedence, quoting or
configuration validation is performed. Two tests may consume one observation.
"""
from __future__ import annotations

import re
from copy import deepcopy

MAX_FILES=256
MAX_LINES=100000
MAX_LINE_BYTES=4096
KEYS=frozenset({"session","sessioncookiename"})
STATES=frozenset({"complete","incomplete","error","not_collected","not_applicable"})
PATTERN=re.compile(r"^\s*(Session|SessionCookieName)\s+(.+?)\s*$",re.IGNORECASE)

def observe_apache_directives(collected):
    if not isinstance(collected,dict) or set(collected)!={"population","status","files","provenance"}:
        raise ValueError("explicit file population/status/evidence contract required")
    population=collected["population"]
    status=collected["status"]
    files=collected["files"]
    if type(population) is not str or not population or status not in STATES or (
        not isinstance(files,list) or len(files)>MAX_FILES or
        not isinstance(collected["provenance"],dict)
    ):
        raise ValueError("invalid typed file observation")
    if status in {"error","not_collected","not_applicable"} and files:
        raise ValueError("untrusted terminal-status file population")
    by_key={"session":[],"sessioncookiename":[]}
    seen_files=set()
    count=0
    for file in files:
        if not isinstance(file,dict) or set(file)!={"id","path","lines"} or (
            any(type(file.get(k)) is not str or not file[k] for k in ("id","path")) or
            not isinstance(file["lines"],list) or file["id"] in seen_files
        ):
            raise ValueError("file has invalid or duplicated evidence identity")
        seen_files.add(file["id"])
        last=0
        for item in file["lines"]:
            count+=1
            if count>MAX_LINES:
                raise ValueError("excessive input line population")
            if not isinstance(item,dict) or set(item)!={"line","text"} or (
                type(item["line"]) is not int or item["line"]<=last or
                type(item["text"]) is not str or len(item["text"].encode("utf-8"))>MAX_LINE_BYTES
            ):
                raise ValueError("invalid or unordered source line identity")
            last=item["line"]
            match=PATTERN.fullmatch(item["text"])
            if not match:continue
            key=match.group(1).lower()
            by_key[key].append({"id":file["id"]+":"+str(item["line"]),
                                "file_id":file["id"],"path":file["path"],
                                "line":item["line"],
                                "directive":match.group(1),
                                "arguments":match.group(2),
                                "original_text":item["text"]})
    return {"kind":"C_RESEARCH_RAW_APACHE_DIRECTIVE_OBSERVATION",
            "population":population,
            "status":status,
            "directives":by_key,
            "provenance":deepcopy(collected["provenance"]),
            "parsed_from_file_items":len(files),
            "parsed_lines":count,
            "include_semantics_verified":False,
            "effective_apache_config_verified":False,
            "legacy_shellcommand_parity_verified":False,
            "scanner_executed":False}


def select_directives(observation, name):
    """Return evidence, NOT a truth value; consumers set their own policy."""
    if not isinstance(observation,dict) or (
        observation.get("kind")!="C_RESEARCH_RAW_APACHE_DIRECTIVE_OBSERVATION"
    ) or name not in KEYS:
        raise ValueError("unsupported raw Apache directive observation")
    return {"population":observation["population"],
            "status":observation["status"],
            "items":deepcopy(observation["directives"][name]),
            "provenance":deepcopy(observation["provenance"]),
            "evaluation_performed":False}
