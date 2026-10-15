#!/usr/bin/env python3
"""Measure exact lossless aliases for common existence/match *pairs* in released 0.3.

NO new runtime semantics, defaults, or unsupported cardinalities. Research only.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import argparse
import json
import zipfile

import yaml

ITEM_ALIAS = "at_least_one_all_match"
FIELD_ALIAS = "at_least_one_matches"
ITEM_PAIR = {"existence":"one_or_more", "match":"all"}
FIELD_PAIR = {"existence":"one_or_more", "match":"one_or_more"}


def shorten_pair(node, *, pair, label):
    """Replace an exactly matching pair; fail closed for partial pairs."""
    if not isinstance(node, dict):
        raise ValueError("Expected mapping")
    if any(k not in node for k in pair):
        raise ValueError("Cannot shorten a partial or implicit pair")
    if any(node[k] != value for k,value in pair.items()):
        raise ValueError("Pair does not match the named preset")
    if "require" in node:
        raise ValueError("Refusing collision with existing require")
    out=deepcopy(node)
    for key in pair:
        del out[key]
    out["require"]=label
    return out


def expand_pair(node, *, pair, label):
    if not isinstance(node,dict) or node.get("require") != label:
        raise ValueError("Unrecognized shorthand")
    if any(k in node for k in pair):
        raise ValueError("Explicit quantifiers conflict with shorthand")
    out=deepcopy(node)
    del out["require"]
    out.update(pair)
    return out


def measure(archive_path):
    counts=Counter()
    by_benchmark=defaultdict(Counter)
    item_pairs=Counter()
    field_pairs=Counter()
    examples=[]
    with zipfile.ZipFile(archive_path) as z:
        if z.testzip() is not None:
            raise ValueError("Bad source archive")
        for path in sorted(z.namelist()):
            if not path.startswith("authoring/") or not path.endswith(".automated.yaml"):
                continue
            document=yaml.safe_load(z.read(path))
            assessment=(document or {}).get("assessment") or {}
            if assessment.get("mode") != "automated":
                continue
            benchmark=path.split("/")[1]
            counts["automated_assessment_files"]+=1
            by_benchmark[benchmark]["automated_assessment_files"]+=1
            for test_name,test in (assessment.get("tests") or {}).items():
                if not isinstance(test,dict):
                    continue
                counts["named_tests"]+=1
                by_benchmark[benchmark]["named_tests"]+=1
                pair=(str(test.get("existence","<missing>")),str(test.get("match","<missing>")))
                item_pairs[pair]+=1
                try:
                    concise=shorten_pair(test,pair=ITEM_PAIR,label=ITEM_ALIAS)
                    assert expand_pair(concise,pair=ITEM_PAIR,label=ITEM_ALIAS)==test
                except ValueError:
                    pass
                else:
                    counts["item_pair_eligible"]+=1
                    by_benchmark[benchmark]["item_pair_eligible"]+=1
                    if len(examples)<8:
                        examples.append({"assessment":path,"test":test_name,"kind":"items","preset":ITEM_ALIAS})
                for state in (test.get("states") or []):
                    if not isinstance(state,dict) or not ("field" in state and "value" in state):
                        continue
                    counts["state_field_predicates"]+=1
                    by_benchmark[benchmark]["state_field_predicates"]+=1
                    pair=(str(state.get("existence","<missing>")),str(state.get("match","<missing>")))
                    field_pairs[pair]+=1
                    try:
                        concise=shorten_pair(state,pair=FIELD_PAIR,label=FIELD_ALIAS)
                        assert expand_pair(concise,pair=FIELD_PAIR,label=FIELD_ALIAS)==state
                    except ValueError:
                        pass
                    else:
                        counts["field_pair_eligible"]+=1
                        by_benchmark[benchmark]["field_pair_eligible"]+=1
                        if len(examples)<16:
                            examples.append({"assessment":path,"test":test_name,"field":state["field"],
                                             "kind":"field","preset":FIELD_ALIAS})
    return {
        "research_only":True,
        "source_archive":archive_path.name,
        "structural_identity_only":True,
        "presets":{"item":{"name":ITEM_ALIAS, "expansion":ITEM_PAIR},
                   "field":{"name":FIELD_ALIAS, "expansion":FIELD_PAIR}},
        "totals":dict(counts),
        "by_benchmark":{k:dict(v) for k,v in sorted(by_benchmark.items())},
        "item_existence_match_pairs":{f"{k[0]} / {k[1]}":v for k,v in sorted(item_pairs.items())},
        "field_existence_match_pairs":{f"{k[0]} / {k[1]}":v for k,v in sorted(field_pairs.items())},
        "sample_candidates":examples,
        "proof_claim":"Only exact dictionary round-trip of independent quantifier aliases; not OVAL/runtime engine parity.",
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--authoring-zip",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    data=measure(a.authoring_zip)
    result=json.dumps(data,indent=2,sort_keys=True)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(result+"\n")
    print(result)
