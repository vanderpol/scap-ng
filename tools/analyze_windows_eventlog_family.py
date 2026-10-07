#!/usr/bin/env python3
"""Verify the Windows Server 2025 event-log permission family is one template.

Research-only. This performs no rewrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

RULE_IDS={"SV-278043","SV-278044","SV-278045"}
CONTROL_IDS={"WN25-AU-000030","WN25-AU-000040","WN25-AU-000050"}
FUNCTION_KEYS={"concat","regex_capture","values","object_values","object_component","variable_component"}

def walk(value:Any):
    yield value
    if isinstance(value,dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value,list):
        for child in value:
            yield from walk(child)

def normalize_string(value:str)->str:
    out=value
    out=re.sub(r"SV-27804[345]","SV-27804X",out)
    out=re.sub(r"WN25-AU-0000(?:30|40|50)","WN25-AU-0000XX",out)
    out=re.sub(r"(?i)application","<LOG>",out)
    out=re.sub(r"(?i)security","<LOG>",out)
    out=re.sub(r"(?i)system","<LOG>",out)
    return out

def normalize(value:Any)->Any:
    if isinstance(value,dict):
        return {normalize_string(str(k)):normalize(v) for k,v in value.items()}
    if isinstance(value,list):
        return [normalize(v) for v in value]
    if isinstance(value,str):
        return normalize_string(value)
    return value

def digest(value:Any)->str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    matches=[]
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        rid=next((x for x in RULE_IDS if x in aid),None)
        if rid and a.get("mode")=="automated":
            funcs=Counter()
            for node in walk(a.get("variables") or {}):
                if isinstance(node,dict):
                    for key in node:
                        if key in FUNCTION_KEYS:
                            funcs[key]+=1
            matches.append({
                "rule_id":rid,
                "assessment_id":aid,
                "path":str(path),
                "objects":len(a.get("objects") or {}),
                "variables":len(a.get("variables") or {}),
                "states":len(a.get("states") or {}),
                "tests":len(a.get("tests") or {}),
                "variable_functions":dict(funcs),
                "normalized_digest":digest(normalize(doc)),
            })

    if {x["rule_id"] for x in matches} != RULE_IDS:
        raise SystemExit(f"expected exactly {sorted(RULE_IDS)}, got {[x['rule_id'] for x in matches]}")
    hashes={x["normalized_digest"] for x in matches}
    if len(hashes)!=1:
        raise SystemExit(f"event-log family is not one normalized template: {sorted(hashes)}")

    report={
        "format":"scap-ng-windows-event-log-family-0.1",
        "status":"research_only_not_accepted_design",
        "template_equivalent_after_log_and_control_normalization":True,
        "normalized_digest":next(iter(hashes)),
        "members":matches,
        "common_shape":{
            "objects":matches[0]["objects"],
            "variables":matches[0]["variables"],
            "states":matches[0]["states"],
            "tests":matches[0]["tests"],
            "variable_functions":matches[0]["variable_functions"],
        },
        "modernization_boundary":{
            "safe_presentation":["consumer-local states","filtered Set operand locality"],
            "review_required":[
                "regex_capture identity-like path extraction",
                "two-dynamic-source concat used for %SystemRoot% path expansion",
                "Boolean branch to procedural conditional",
            ],
        },
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
