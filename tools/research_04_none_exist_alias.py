#!/usr/bin/env python3
"""Research-only absence preset for SCAP-NG 0.3: no hidden scanner defaults.

For an existence-only Test without States, OVAL 5.12.3 check is not consulted.
Therefore source Test match values may be normalized to 'all' on expansion if
and only if no State is present. Field-state aliases are structurally exact
only where the original existence/match pair is none/all.
"""
from copy import deepcopy
from pathlib import Path
import argparse
from collections import Counter
import json
import zipfile

import yaml

ABSENT = "none_exist"
MATCHES = frozenset(("all", "one", "one_or_more", "none"))


def compress_test(test):
    if not isinstance(test, dict) or test.get("existence") != "none":
        raise ValueError("Only explicit Test existence:none can use this preset")
    if test.get("match") not in MATCHES:
        raise ValueError("Unrecognized or missing match")
    if "states" in test and test["states"] is not None:
        raise ValueError("No-state check required: even empty states must be reviewed")
    if "require" in test:
        raise ValueError("Existing require would be overwritten")
    original=test["match"]
    new=deepcopy(test)
    del new["existence"]
    del new["match"]
    new["require"]=ABSENT
    return new, original


def expand_test(test):
    if not isinstance(test,dict) or test.get("require")!=ABSENT:
        raise ValueError("Missing or unrecognized absence preset")
    if "existence" in test or "match" in test:
        raise ValueError("Absence preset conflicts with explicit existence/match")
    if "states" in test and test["states"] is not None:
        raise ValueError("No-state check required")
    new=deepcopy(test)
    del new["require"]
    new["existence"]="none"
    new["match"]="all"
    return new


def compress_state_field(state):
    if not isinstance(state,dict) or (
        state.get("existence")!="none" or state.get("match")!="all"
        or "field" not in state or "value" not in state
    ):
        raise ValueError("Only proven exact field none/all pair can use preset")
    if "require" in state:
        raise ValueError("Existing require would be overwritten")
    new=deepcopy(state)
    del new["existence"]
    del new["match"]
    new["require"]=ABSENT
    return new


def expand_state_field(state):
    if not isinstance(state,dict) or state.get("require")!=ABSENT:
        raise ValueError("Missing/unrecognized field preset")
    if "existence" in state or "match" in state:
        raise ValueError("Field preset conflicts with explicit existence/match")
    new=deepcopy(state)
    del new["require"]
    new["existence"]="none"
    new["match"]="all"
    return new


def audit(archive_path):
    counts=Counter()
    normalized=[]
    for scope,name in (("Test","items"),("field","field")):
        pass
    with zipfile.ZipFile(archive_path) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP failed CRC")
        for fn in sorted(z.namelist()):
            if not fn.startswith("authoring/") or not fn.endswith(".automated.yaml"):
                continue
            a=(yaml.safe_load(z.read(fn)) or {}).get("assessment") or {}
            if a.get("mode")!="automated":
                continue
            for tid,test in (a.get("tests") or {}).items():
                if not isinstance(test,dict):
                    continue
                if test.get("existence")=="none":
                    counts["test_none_total"]+=1
                    short,original=compress_test(test)
                    actual=expand_test(short)
                    if actual!=test and original=="all":
                        raise AssertionError("Exact original Test none/all failed structural proof")
                    # Other original match values can differ only at the
                    # unused Test.match attribute; test all 6 flags separately.
                    old=deepcopy(test)
                    old["match"]="all"
                    if actual!=old:
                        raise AssertionError("Other fields changed while normalizing")
                    counts["test_none_no_state_eligible"]+=1
                    if original!="all":
                        counts["test_unused_match_normalized"]+=1
                        normalized.append({"assessment":fn,"test":tid,"original_match":original,
                            "normalized_match":"all","has_states":False})
                for state in (test.get("states") or []):
                    if not isinstance(state,dict) or state.get("existence")!="none":
                        continue
                    counts["field_none_total"]+=1
                    short=compress_state_field(state)
                    if expand_state_field(short)!=state:
                        raise AssertionError("Field none/all not structurally identical")
                    counts["field_none_exact_eligible"]+=1
    return {"counts":dict(counts),"normalized_original_match":normalized,
            "source":archive_path.name,
            "claim":"Test absence-only normalizes inert match under scoped evaluation model; field none/all is exact structural expansion; six-outcome proof tested independently; no vendor scanner differential."}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--authoring-zip",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=audit(args.authoring_zip)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
