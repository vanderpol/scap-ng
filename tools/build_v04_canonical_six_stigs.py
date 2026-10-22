#!/usr/bin/env python3
"""Generate six complete SCAP-NG 0.4.0 source-backed authoring sets.

Source: October 15 r3 pre-alpha archive, pinned by SHA-256 in workflow.
Promote proven scalar all-match States to canonical field_requirement and
complete conditions. Preserve Item population separately and retain explicit
source-exact uncommon, record and non-AND State fallbacks with diagnostics.
Inherit inline Object capability only for identical Test/Object capability.
Preserve all other graph content and prove parsed-source exact recovery.

Refs #251 #227 #232 #239 #246.
"""
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from v04_flat_object_authoring import dump_hybrid

from migrate_v04_oval_proven_direct_filters import (
    index_provenance, migrate as migrate_proven_filter, recover_migration,
)
from migrate_v04_additional_source_filters import (
    index_source_proof, migrate as migrate_additional_filter,
    recover_migration as recover_additional_filter,
)

from v04_field_requirement import PAIRS, PRESENCE, promote_test, restore_test


def promote(doc, *, provenance=None):
    new=deepcopy(doc)
    audit=Counter()
    a=new.get("assessment")
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return new,audit
    for tid,test in (a.get("tests") or {}).items():
        cap=test.get("capability")
        obj=test.get("object")
        if isinstance(obj,dict) and "capability" in obj:
            if obj["capability"]!=cap:
                raise ValueError("Inline Object capability conflicts with Test")
            del obj["capability"]
            audit["inline_capabilities_removed"]+=1
        updated, proof = promote_test(test)
        test.clear()
        test.update(updated)
        if proof["shape"] != "unchanged":
            audit[proof["shape"]] += 1
        if proof["diagnostic"]:
            audit["fallback:" + proof["diagnostic"]] += 1
        if provenance is not None:
            provenance[tid] = proof
    return new,audit

def recover(candidate,original):
    """Verify deterministic promotion and restore each checked source Test ledger."""
    proofs = {}
    expected, _ = promote(original, provenance=proofs)
    if candidate != expected:
        raise ValueError("Original authoring source differs after exact reverse translation")
    for tid, proof in proofs.items():
        test = candidate["assessment"]["tests"][tid]
        if restore_test(test, proof) != proof["source_test"]:
            raise ValueError("Test source reconstruction mismatch: " + tid)


def render_authoring(document, *, is_yaml):
    """Keep short canonical predicates inline without changing their data graph."""
    return (dump_hybrid(document) if is_yaml
            else json.dumps(document, indent=2, ensure_ascii=False) + "\n")


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


def run(src,dest,manifest_path,filter_proof_path=None,additional_proof_path=None):
    if src.suffix!=".zip": raise ValueError("ZIP input required")
    filter_proof = (index_provenance(json.loads(filter_proof_path.read_text()),
                                     assert_six=True) if filter_proof_path else None)
    if additional_proof_path and filter_proof is None:
        raise ValueError("Second-pass Filter source proof requires first-pass proof")
    additional_proof = (index_source_proof(json.loads(additional_proof_path.read_text()),
                                           assert_six=True) if additional_proof_path else None)
    is_yaml="six-stig-yaml" in src.name
    ext=".yaml" if is_yaml else ".json"
    counts=Counter()
    path_stats={}
    field_provenance={}
    with zipfile.ZipFile(src) as z:
        names=[x for x in z.namelist() if x.startswith("authoring/") and x.endswith(ext)]
        if len(names)!=4001 or len(names)!=len(set(names)):
            raise ValueError(f"Unexpected source count/duplicates: {len(names)}")
        source={}
        promoted={}
        for name in sorted(names):
            old=yaml.safe_load(z.read(name)) if is_yaml else json.loads(z.read(name))
            source[name]=old
            proofs={}
            new,stats=promote(old, provenance=proofs)
            if proofs:
                field_provenance[name]=proofs
            recover(new,old)
            if filter_proof is not None:
                canonical_before_filter=deepcopy(new)
                new, filtered_stats=migrate_proven_filter(new,name,filter_proof)
                recover_migration(new,canonical_before_filter,name,filter_proof)
                stats.update(filtered_stats)
            if additional_proof is not None:
                before_additional=deepcopy(new)
                new, additional_stats=migrate_additional_filter(new,name,additional_proof)
                recover_additional_filter(new,before_additional,name,additional_proof)
                stats.update(additional_stats)
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
                    prior,_=migrate_proven_filter(before_filters,name,filter_proof)
                    if additional_proof is not None:
                        recover_additional_filter(new,prior,name,additional_proof)
                    else:
                        if new!=prior:
                            raise ValueError("First-stage canonical Filter output differs")
                    recover_migration(prior,before_filters,name,filter_proof)
                    recover(before_filters,source[name])
                else:
                    recover(new,source[name])
            rendered=render_authoring(new, is_yaml=is_yaml)
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
    if additional_proof is not None and counts["source_linked_additional_direct_filters"]!=19:
        raise ValueError("Second-pass 0.4 source Filter population changed")
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
            "field_requirement_provenance":field_provenance,
            "source_filter_proof_sha256": (hashlib.sha256(filter_proof_path.read_bytes()).hexdigest()
                                           if filter_proof_path else None),
            "source_filter_migration":"source_verified_direct_only" if filter_proof else "not_requested",
            "additional_filter_source_proof_sha256":(
                hashlib.sha256(additional_proof_path.read_bytes()).hexdigest()
                if additional_proof_path else None),
            "additional_filter_migration":"source_test_object_ref_verified" if additional_proof else "not_requested",
            "schema_validated":False,
            "scanner_equivalence_proven":False}
    manifest_path.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in {"changed_paths", "field_requirement_provenance"}},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--filter-proof",type=Path,default=None,
                   help="Pinned original OVAL six-STIG Filter classification JSON; only 28 source-proven leaves migrate")
    p.add_argument("--additional-filter-proof",type=Path,default=None,
                   help="Pinned six-OVAL Test-object-ref ledger for second-pass 19 leaf Filters")
    a=p.parse_args();run(a.source,a.out,a.manifest,a.filter_proof,a.additional_filter_proof)
