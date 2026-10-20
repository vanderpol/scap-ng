#!/usr/bin/env python3
"""Generate six complete SCAP-NG 0.4.0 source-backed authoring sets.

Source: October 15 r3 pre-alpha archive, pinned by SHA-256 in workflow.
Only promote the two proven all-match requirement pairs to inline
`require.items` / `require.all_items_must`; leave exceptional pairs explicit.
Inherit inline Object capability only for identical Test/Object capability.
Preserve all other graph content and prove parsed-source exact recovery.

Refs #227 #232 #239 #246.
"""
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

from migrate_v04_oval_proven_direct_filters import (
    index_provenance, migrate as migrate_proven_filter, recover_migration,
)

PAIRS={"at_least_one_exists_and_all_match":"one_or_more",
       "may_be_absent_and_all_match":"may_be_absent"}
INVERSE={v:k for k,v in PAIRS.items()}
PRESENCE={
    "at_least_one_exists":"one_or_more",
    "none_exist":"none",
    "only_one_exists":"exactly_one",
    "all_exist":"all",
    "may_be_absent":"may_be_absent",
}
PRESENCE_INVERSE={v:k for k,v in PRESENCE.items()}


def promote(doc):
    new=deepcopy(doc)
    audit=Counter()
    a=new.get("assessment")
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return new,audit
    for test in (a.get("tests") or {}).values():
        cap=test.get("capability")
        obj=test.get("object")
        if isinstance(obj,dict) and "capability" in obj:
            if obj["capability"]!=cap:
                raise ValueError("Inline Object capability conflicts with Test")
            del obj["capability"]
            audit["inline_capabilities_removed"]+=1
        old=test.get("collected_items_require",test.get("require"))
        if "collected_items_require" in test and "require" in test:
            raise ValueError("Mixed Test requirement dialect")
        states=test.get("states")
        if old in PAIRS and isinstance(states,list) and states:
            source_key="collected_items_require" if "collected_items_require" in test else "require"
            test.pop(source_key)
            test.pop("states")
            test["require"]={"items":PAIRS[old],"all_items_must":states}
            audit["all_items_must"]+=1
        elif old in PRESENCE and not states and "states_match" not in test:
            source_key="collected_items_require" if "collected_items_require" in test else "require"
            test.pop(source_key)
            test["require"]={"items":PRESENCE[old]}
            audit["presence_only_structured"]+=1
        elif "collected_items_require" in test:
            test["require"]=test.pop("collected_items_require")
            audit["explicit_fallback"]+=1
    return new,audit

def recover(candidate,original):
    restored=deepcopy(candidate)
    oa=original.get("assessment")
    if not isinstance(oa,dict) or oa.get("mode")!="automated":
        if restored!=original:
            raise ValueError("Non-automated source changed")
        return
    for id,test in restored["assessment"].get("tests",{}).items():
        orig=oa["tests"][id]
        if isinstance(test.get("object"),dict) and "capability" in orig.get("object",{}):
            if "capability" in test["object"]:
                raise ValueError("Redundant inline capability survived promotion")
            test["object"]["capability"]=orig["object"]["capability"]
        source_key="collected_items_require" if "collected_items_require" in orig else "require"
        req=test.get("require")
        if isinstance(req,dict) and set(req)=={"items"}:
            if req["items"] not in PRESENCE_INVERSE or "states" in test:
                raise ValueError("Invalid presence-only structured requirement")
            test.pop("require")
            test[source_key]=PRESENCE_INVERSE[req["items"]]
        elif isinstance(req,dict):
            if set(req)!={"items","all_items_must"} or req["items"] not in INVERSE:
                raise ValueError("Unsupported new requirement structure")
            states=req["all_items_must"]
            if not isinstance(states,list) or not states:
                raise ValueError("Missing inline States")
            test.pop("require")
            test["states"]=states
            test[source_key]=INVERSE[req["items"]]
        elif source_key=="collected_items_require":
            test["collected_items_require"]=test.pop("require")
    if restored!=original:
        raise ValueError("Original authoring source differs after exact reverse translation")

def reconcile_benchmark_specifications(documents, *, expected_benchmarks=6,
                                      expected_conflicts=1391):
    """Owner-approved 0.4 source migration; never edit pinned source input.

    Use *actual reachable automated Rule choices per Benchmark* rather than
    blindly changing all 0.3 declarations. This exact-reachable policy was
    approved for the 0.4.0 samples on 2026-10-20; retain original source and
    per-Benchmark hashes in the generation manifest (Refs #232 #239).
    """
    from v04_a_benchmark_spec_migration_preview import build_preview
    report, staged = build_preview(documents)
    changes = report["benchmark_changes"]
    if (len(changes) != expected_benchmarks or report["candidate_incompatible_edges"] != 0
            or report["source_incompatible_edges"] != expected_conflicts):
        raise ValueError("six-STIG Benchmark version-migration source baseline changed")
    for item in changes:
        before = item["existing_specs"]
        after = item["reachable_automated_specs"]
        if (len(before) != 1 or before[0].get("version") != "0.3.0"
                or len(after) != 1 or after[0].get("version") != "0.4.0"
                or before[0]["id"] != after[0]["id"]):
            raise ValueError("unreviewed Benchmark specification migration: " + item["path"])
        path = item["path"]
        original = documents[path]
        proposed = staged[path]
        if set(original) != {"benchmark"} or set(proposed) != {"benchmark"}:
            raise ValueError("Benchmark root changed")
        restored = deepcopy(proposed)
        restored["benchmark"]["assessment_specifications"] = deepcopy(
            original["benchmark"]["assessment_specifications"])
        if restored != original:
            raise ValueError("Benchmark version reconciliation changed unrelated source")
    return staged, changes


def run(src,dest,manifest_path,filter_proof_path=None):
    if src.suffix!=".zip": raise ValueError("ZIP input required")
    filter_proof = (index_provenance(json.loads(filter_proof_path.read_text()),
                                     assert_six=True) if filter_proof_path else None)
    is_yaml="six-stig-yaml" in src.name
    ext=".yaml" if is_yaml else ".json"
    counts=Counter()
    path_stats={}
    with zipfile.ZipFile(src) as z:
        names=[x for x in z.namelist() if x.startswith("authoring/") and x.endswith(ext)]
        if len(names)!=4001 or len(names)!=len(set(names)):
            raise ValueError(f"Unexpected source count/duplicates: {len(names)}")
        source={}
        promoted={}
        for name in sorted(names):
            old=yaml.safe_load(z.read(name)) if is_yaml else json.loads(z.read(name))
            source[name]=old
            new,stats=promote(old)
            recover(new,old)
            if filter_proof is not None:
                canonical_before_filter=deepcopy(new)
                new, filtered_stats=migrate_proven_filter(new,name,filter_proof)
                recover_migration(new,canonical_before_filter,name,filter_proof)
                stats.update(filtered_stats)
            promoted[name]=new
            counts.update(stats)
            # An unresolved source-provenance review flag is not an edit.
            # Count changed documents only when source authoring actually moves.
            if any(value and key != "source_review_required_unchanged"
                   for key,value in stats.items()):
                path_stats[name]=dict(stats)
    # This explicit, user-approved version migration is performed *after*
    # all Test/Object exact inversions and independently verified edge closure.
    # It changes only six Benchmark declaration lists, not Assessment logic.
    versioned, version_changes=reconcile_benchmark_specifications(promoted)
    for row in version_changes:
        name=row["path"]
        path_stats.setdefault(name,{})["benchmark_version_declarations_updated"]=1
    counts["benchmark_version_declarations_updated"]=len(version_changes)
    with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as output:
        for name in sorted(names):
            new=versioned[name]
            if "benchmark" in new:
                restored=deepcopy(new)
                restored["benchmark"]["assessment_specifications"]=deepcopy(
                    source[name]["benchmark"]["assessment_specifications"])
                if restored!=source[name]:
                    raise ValueError("Benchmark migration changed non-version content")
            else:
                if filter_proof is not None:
                    before_filters,_=promote(source[name])
                    recover_migration(new,before_filters,name,filter_proof)
                    recover(before_filters,source[name])
                else:
                    recover(new,source[name])
            rendered=(yaml.safe_dump(new,sort_keys=False,allow_unicode=True,width=110)
                      if is_yaml else json.dumps(new,indent=2,ensure_ascii=False)+"\n")
            output.writestr(name,rendered)
        output.writestr("READ-ME-FIRST.txt",
            "SCAP-NG 0.4.0 six-benchmark authoring candidate. Source-exact inversion verified.\n"
            "Six Benchmark 0.3 Assessment specification declarations were replaced by exact\n"
            "reachable 0.4 declarations with owner approval; original source is preserved\n"
            "in the immutable pinned Oct 15 r3 release and SHA-256 migration manifest.\n"
            "Object capability inherits from Test; common all-match predicates live inside require.\n"
            "Remaining explicit require strings are original uncommon semantics, not inferred defaults.\n"
            "Do not interpret this authoring ZIP as a signed scanner bundle or runtime parity result.\n")
    if counts["all_items_must"]<1 or counts["inline_capabilities_removed"]<1:
        raise ValueError("Expected real migration did not happen")
    if filter_proof is not None and (
            counts["source_proven_direct_filters"] != 28
            or counts["source_review_required_unchanged"] != 8):
        raise ValueError("Proven original OVAL Filter migration baseline changed")
    report={"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
            "output_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "format":"yaml" if is_yaml else "json",
            "documents":len(names),"counts":dict(counts),
            "changed_documents":len(path_stats),
            "changed_paths":path_stats,
            "benchmark_version_policy":"owner_approved_exact_reachable_0.4_only",
            "benchmark_version_changes":[
                {**row,"path":row["path"].removesuffix(".json").removesuffix(".yaml")}
                for row in version_changes],
            "source_ast_recovered":True,
            "source_filter_proof_sha256": (hashlib.sha256(filter_proof_path.read_bytes()).hexdigest()
                                           if filter_proof_path else None),
            "source_filter_migration":"source_verified_direct_only" if filter_proof else "not_requested",
            "schema_validated":False,
            "scanner_equivalence_proven":False}
    manifest_path.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="changed_paths"},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--filter-proof",type=Path,default=None,
                   help="Pinned original OVAL six-STIG Filter classification JSON; only 28 source-proven leaves migrate")
    a=p.parse_args();run(a.source,a.out,a.manifest,a.filter_proof)
