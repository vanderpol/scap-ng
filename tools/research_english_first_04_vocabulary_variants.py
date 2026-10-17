#!/usr/bin/env python3
"""Issue #227/#235: vocabulary A/B/C experiment over pinned six-STIG source.

A: current English-first inspect/where/require (already source-exact).
B: technical original 0.4 Assessment (as-published, not a rewrite).
C: minimal hybrid check/capability/require, with selector attached to capability.

The hybrid uses a string capability for selector-free sources and a one-key
mapping {native.capability: native-selector-criteria} for selected sources.
This polymorphism is itself a usability drawback to assess. Selection is
NEVER omitted, only moved; this is source-structural parity research, not
OVAL scanner semantic equivalence.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

from research_english_first_04_complex import to_human, to_native
from research_english_first_04_compact_layout import compact, expand, PINNED

SAMPLES={
 "authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml":"linux-home",
 "authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml":"linux-files",
 "authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml":"win11-wmi-rights",
 "authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml":"dns-signing",
 "authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml":"apache-keepalive",
}
# Keep explicit names for semantic operations which DO remain distinct.
ALL_KNOWN_CAPABILITIES=("linux.", "unix.", "windows.", "independent.", "macos.",
                        "solaris.", "aix.", "freebsd.", "hpux.", "ios.", "android.")

def to_minimal(node):
    """Research C: replace 'inspect' and adjacent 'where' by one capability."""
    if isinstance(node,list):
        return [to_minimal(item) for item in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if "capability" in node and "inspect" in node:
        raise ValueError("two competing capability declarations")
    result={}
    for key,value in node.items():
        if key=="where" and "inspect" in node:
            # Move *only* an Object's own selector. A where appearing inside
            # a derived collection, Variable filter, or comparison is not
            # necessarily an Object selector and must retain its role.
            continue
        if key=="inspect":
            if not isinstance(value,str) or not value:
                raise ValueError("non-string inspector")
            selected=node.get("where")
            if "where" in node:
                if not isinstance(selected,dict) or not selected:
                    raise ValueError("empty or unsupported selector")
                result["capability"]={value:to_minimal(selected)}
            else:
                result["capability"]=value
        else:
            result[key]=to_minimal(value)
    return result

def from_minimal(node):
    """Restore original compact presentation unambiguously, rejecting collisions."""
    if isinstance(node,list):
        return [from_minimal(item) for item in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if "inspect" in node or "where" in node:
        raise ValueError("hybrid cannot contain inspect or where")
    out={}
    for key,value in node.items():
        if key!="capability":
            out[key]=from_minimal(value)
            continue
        if isinstance(value,str) and value:
            out["inspect"]=value
        elif isinstance(value,dict) and len(value)==1:
            cap,where=next(iter(value.items()))
            if not isinstance(cap,str) or not cap or not isinstance(where,dict) or not where:
                raise ValueError("unrecognized capability selector")
            out["inspect"]=cap
            out["where"]=from_minimal(where)
        else:
            raise ValueError("ambiguous capability value")
    return out

def document_to_minimal(doc):
    """Only transform the Assessment vocabulary, never source-native Variables."""
    if set(doc)!={"metadata","sources","checks","evaluate"}:
        raise ValueError("unexpected research Assessment")
    return {
        "metadata":deepcopy(doc["metadata"]),
        "sources":{k:to_minimal(v) for k,v in doc["sources"].items()},
        "checks":{k:to_minimal(v) for k,v in doc["checks"].items()},
        "evaluate":deepcopy(doc["evaluate"]),
    }


def document_from_minimal(doc):
    """Inverse of the vocabulary-only transformation."""
    if set(doc)!={"metadata","sources","checks","evaluate"}:
        raise ValueError("unexpected hybrid Assessment")
    return {
        "metadata":deepcopy(doc["metadata"]),
        "sources":{k:from_minimal(v) for k,v in doc["sources"].items()},
        "checks":{k:from_minimal(v) for k,v in doc["checks"].items()},
        "evaluate":deepcopy(doc["evaluate"]),
    }


def first_structural_difference(a,b, path=""):
    if type(a) is not type(b):
        return path + ": type " + type(a).__name__ + " vs " + type(b).__name__
    if isinstance(a,dict):
        if set(a)!=set(b):
            return path + ": keys " + repr(sorted(set(a)^set(b)))
        for key in a:
            if a[key]!=b[key]:
                return first_structural_difference(a[key],b[key],path+"/"+str(key))
    elif isinstance(a,list):
        if len(a)!=len(b): return path+": list sizes "+repr((len(a),len(b)))
        for i,(left,right) in enumerate(zip(a,b)):
            if left!=right: return first_structural_difference(left,right,path+"/"+str(i))
    elif a!=b:
        return path+": values "+repr((a,b))[:220]
    return path+": structural equality failed unexpectedly"


def examine(archive, examples_dir=None):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest != PINNED:raise ValueError("unexpected immutable archive")
    counts=Counter()
    rejections=[]
    chars=Counter()
    if examples_dir:Path(examples_dir).mkdir(parents=True,exist_ok=True)
    samples_found={}
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not (path.startswith("authoring/") and "/assessments/" in path
                    and path.endswith(".yaml")):
                continue
            source=(yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if source.get("mode")!="automated" or not source.get("tests"):
                continue
            counts["assessments_total"]+=1
            try:
                english=compact(to_human(source))
                hybrid=document_to_minimal(english)
                returned=document_from_minimal(hybrid)
                if returned!=english:
                    raise AssertionError("hybrid inverse: "+first_structural_difference(english,returned))
                reconstructed=to_native(expand(returned))
                if reconstructed!=source:
                    raise AssertionError("native inverse: "+first_structural_difference(source,reconstructed))
                # Retained nested "where" nodes are evidence against total
                # elimination of that keyword, not automatically a failure.
                # Count them explicitly; forbid an unconverted where only
                # when it would be a sibling of an encoded capability.
                if "where" in yaml.safe_dump(hybrid,sort_keys=False):
                    counts["retained_where_documents"]+=1
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError) as e:
                counts["rejected"]+=1
                if len(rejections)<20:rejections.append({"path":path,"error":str(e)[:200]})
                continue
            counts["exact"]+=1
            counts["tests_exact"]+=len(source["tests"])
            ey=yaml.safe_dump(english,sort_keys=False,allow_unicode=True)
            hy=yaml.safe_dump(hybrid,sort_keys=False,allow_unicode=True)
            chars["english"]+=len(ey)
            chars["hybrid"]+=len(hy)
            if path in SAMPLES:
                samples_found[SAMPLES[path]]={
                    "source":path,
                    "tests":len(source["tests"]),
                    "english_chars":len(ey),"minimal_chars":len(hy),
                    "hybrid_is_exact":True,
                }
                if examples_dir:
                    stem=SAMPLES[path]
                    (Path(examples_dir)/(stem+".minimal.research.yaml")).write_text(
                        "# EXPERIMENT ONLY: native Assessment source-structure round-trip, NOT SCAP 1.4 runtime parity\n"+
                        hy,encoding="utf-8")
    if counts["assessments_total"] != 872 or counts["exact"] < 871:
        raise AssertionError("source-exact grammar coverage regression "+repr(dict(counts))+" first rejections "+repr(rejections[:12]))
    if counts["exact"]+counts["rejected"]!=counts["assessments_total"]:
        raise AssertionError("unaccounted Assessment")
    # Adversarial invalid syntax: zero/2 capability names, empty selectors,
    # simultaneous where and capability, old inspect, inappropriate scalars.
    negatives=[
        {"capability":{}},
        {"capability":{"linux.partition":{}}},
        {"capability":{"linux.partition":{"mount_point":{"equals":"/home"}},"linux.file":{"path":{"equals":"/x"}}}},
        {"inspect":"linux.partition"},
        {"capability":"linux.partition","where":{"mount_point":{"equals":"/home"}}},
    ]
    for bad in negatives:
        try:from_minimal(bad)
        except ValueError:counts["negative_guards_passed"]+=1
        else:raise AssertionError("malformed hybrid syntax accepted: "+repr(bad))
    return {
        "status":"EXPERIMENTAL SOURCE-STRUCTURAL INVERSION; no scanner parity or human preference demonstrated",
        "archive_sha256":digest,
        "counts":dict(counts),
        "characters":dict(chars),
        "reduction_vs_current_english_percent":round(100*(chars["english"]-chars["hybrid"])/chars["english"],2),
        "cases":samples_found,
        "rejections":rejections,
        "caveats":["A scalar-vs-map capability is polymorphic and may harm learnability.",
                   "Embedding selection within capability could incorrectly suggest that selectors are intrinsic to the capability rather than Object instances.",
                   "All original zero/one/many cardinality axes and collection/Set operators still require explicit authoring.",
                   "The technical variant is the unchanged original source. Neither candidate is an approved 0.4 syntax."],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    p.add_argument("--examples-dir")
    args=p.parse_args()
    report=examine(args.archive,args.examples_dir)
    if args.output:Path(args.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
