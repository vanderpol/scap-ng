#!/usr/bin/env python3
"""Research #235: source-author stratified OVAL edge-case census, six pinned STIGs.

Directly inspects the original OVAL XML in NIWC 1.4 release ZIPs. Does not
interpret the parent NIWC ZIP as the author of every embedded Test/Object.
Independently measures the native 0.4 authoring corpus. A title-matched
candidate is NOT an identity/provenance linkage and is labeled accordingly.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib, json, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

SOURCE_REVISION="8c8e5dff860af6b1290ee9273a282db24278f8d5"
NATIVE_SHA="03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
STIGS={
  "rhel_9":"U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip",
  "oracle_linux_9":"U_Oracle_Linux_9_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip",
  "ms_windows_11":"U_MS_Windows_11_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip",
  "ms_windows_server_2025":"U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip",
  "ms_windows_server_dns":"U_MS_Windows_Server_DNS_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip",
  "apache_server_2-4_unix_server":"U_Apache_Server_2-4_UNIX_Server_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip",
}
NATIVE_TO_OVAL={
  "only_one_exists_and_only_one_matches":"only_one_exists",
  "only_one_exists_and_matches":"only_one_exists",
  "only_one_exists":"only_one_exists",
  "at_least_one_exists":"at_least_one_exists",
  "none_exist":"none_exist",
  "all_exist":"all_exist",
  "all_exist_and_all_match":"all_exist",
  "all_exist_and_none_match":"all_exist",
}
NONSTANDARD={"sqlext"}

def local(tag):
    return tag.rsplit("}",1)[-1]

def original_author(identity):
    if not identity: return "unknown"
    identity=identity.lower()
    if identity.startswith("oval:mil.disa.stig"):return "DISA"
    if identity.startswith("oval:navy.navwar") or identity.startswith("oval:niwc"):
        return "NIWC/NAVWAR"
    return "other_original_namespace"

def normalized_comment(value):
    return re.sub(r"\s+"," ",str(value or "").strip()).casefold()

def native_item_existence(v):
    if v in NATIVE_TO_OVAL:return NATIVE_TO_OVAL[v]
    if v and v.startswith("at_least_one_exists_and_"):return "at_least_one_exists"
    if v and v.startswith("may_be_absent"):return "any_exist"
    raise ValueError("Unsupported native Item mode: "+str(v))

def raw_checks(archive):
    """Original OVAL Tests in the six original source ZIPs; no native joins."""
    tests={}
    elemcounts=Counter()
    overlaid=Counter()
    owners=defaultdict(lambda:Counter())
    per_stig=defaultdict(lambda:Counter())
    authorship_examples=defaultdict(list)
    source_counts=Counter()
    all_raw=[]
    for stig,name in STIGS.items():
        path=archive/name
        if not path.is_file():raise FileNotFoundError(str(path))
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise ValueError("Corrupt input ZIP: "+str(path))
            source_counts[stig]=len(z.namelist())
            for member in sorted(z.namelist()):
                if not member.lower().endswith(".xml"):continue
                raw=z.read(member)
                try:root=ET.fromstring(raw)
                except ET.ParseError:
                    continue # other valid embedded parts; do not misclassify XML as OVAL
                for ov in root.iter():
                    if local(ov.tag)!="oval_definitions":continue
                    sec={local(c.tag):c for c in ov}
                    object_by_id={}
                    for s in ("objects","states","variables","definitions"):
                        parent=sec.get(s)
                        if parent is None:continue
                        for el in parent:
                            identity=el.get("id")
                            if identity:
                                elemcounts[f"{local(el.tag)}:{original_author(identity)}"]+=1
                            if s=="objects" and identity:object_by_id[identity]=el
                    ts=sec.get("tests")
                    if ts is None:continue
                    for t in ts:
                        tag=local(t.tag)
                        if not tag.endswith("_test"):continue
                        tid=t.get("id")
                        if not tid:continue
                        owner=original_author(tid)
                        exists=t.get("check_existence","at_least_one_exists")
                        exists_origin="explicit" if "check_existence" in t.attrib else "source_default"
                        check=t.get("check")
                        states=[ch.get("state_ref") for ch in t if local(ch.tag)=="state"]
                        objs=[ch.get("object_ref") for ch in t if local(ch.tag)=="object"]
                        options=[]
                        for oid in objs:
                            o=object_by_id.get(oid)
                            if o is None:continue
                            for beh in o.iter():
                                if local(beh.tag)=="behaviors" and beh.get("item_creation"):
                                    options.append(beh.get("item_creation"))
                        evidence={
                            "stig":stig,"id":tid,"author":owner,"source_xml":member,
                            "capability":tag.removesuffix("_test"),
                            "comment":t.get("comment") or "",
                            "check_existence":exists,
                            "check_existence_origin":exists_origin,
                            "check":check if check is not None else "<absent>",
                            "state_refs":len(states),"item_creation":sorted(set(options)),
                            "object_ref_authors":sorted({original_author(x) for x in objs if x}),
                            "state_ref_authors":sorted({original_author(x) for x in states if x}),
                        }
                        # Distinct Test ID across sources is a single author identity,
                        # but may have other source revisions. Do not suppress conflicts.
                        key=(stig,tid)
                        signature=(exists,check,tag,len(states),tuple(options))
                        if key in tests:
                            if tests[key]["signature"]!=signature:
                                overlaid["same_ID_conflicting_source_shape"]+=1
                            else:
                                overlaid["same_ID_duplicate_member"]+=1
                            continue
                        tests[key]={"signature":signature,**evidence}
                        owners[owner][exists]+=1
                        per_stig[stig][owner]+=1
                        per_stig[stig]["total_tests"]+=1
                        if len(authorship_examples[(owner,exists)])<5:
                            authorship_examples[(owner,exists)].append(evidence)
                        all_raw.append(evidence)
    return all_raw, {k:dict(v) for k,v in owners.items()}, {k:dict(v) for k,v in per_stig.items()}, dict(overlaid),dict(elemcounts),dict(source_counts)

def native_checks(path):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=NATIVE_SHA:
        raise ValueError("Unexpected pinned native authoring archive")
    rows=[]
    seen_assessments=0
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            if not(name.startswith("authoring/") and "/assessments/" in name and name.endswith(".yaml")):continue
            doc=(yaml.safe_load(z.read(name)) or {}).get("assessment") or {}
            tests=doc.get("tests")
            if doc.get("mode")!="automated" or not isinstance(tests,dict) or not tests:continue
            seen_assessments+=1
            for name2,t in tests.items():
                if not isinstance(t,dict): continue
                rows.append({
                    "source":name,"native_test":name2,"title":t.get("test_title") or "",
                    "capability":t.get("capability") or "",
                    "existence":native_item_existence(t.get("collected_items_require")),
                    "mode":t.get("collected_items_require"),
                    "has_state":bool(t.get("states")),
                })
    if len(rows)!=1375 or seen_assessments!=872:raise AssertionError(f"native source changed {len(rows)} {seen_assessments}")
    return rows,seen_assessments

def classify_candidate(native,source):
    """Title candidate, NEVER an authoritative Test ID join."""
    ix=defaultdict(list)
    for x in source:
        if x["comment"].strip():
            ix[(normalized_comment(x["comment"]),x["check_existence"])].append(x)
    count=Counter()
    rows=[]
    for t in native:
        candidates=ix.get((normalized_comment(t["title"]),t["existence"]),[])
        # A source check may appear in multiple original packages. Multiple
        # identical-ID appearances are not additional authoring identities.
        ids={(s["id"],s["author"]) for s in candidates}
        owners=sorted({s["author"] for s in candidates})
        if not candidates:quality="unmatched_title_mode"
        elif len(ids)==1:quality="single_original_test_id_candidate"
        elif len(owners)==1:quality="multiple_same_author_candidates"
        else:quality="mixed_author_candidates"
        count[quality]+=1
        if t["existence"]=="all_exist":
            rows.append({
                "native_source":t["source"],"native_test":t["native_test"],
                "title":t["title"],"quality":quality,"candidate_authors":owners,
                "candidate_source_test_ids":sorted({s["id"] for s in candidates})[:10],
            })
    return dict(count),rows

def build(args):
    raw,owners,by_stig,dupes,element_counts,source_members=raw_checks(Path(args.sources))
    native,doc_count=native_checks(Path(args.native))
    candidates,all_exist_join=classify_candidate(native,raw)
    # Candidate original source ID counts for all 201 native all_exist Tests.
    # Title+mode is not an authoritative converter-supplied provenance join.
    candidate_201=Counter()
    for row in all_exist_join:
        if row["quality"]=="single_original_test_id_candidate" and len(row["candidate_authors"])==1:
            candidate_201[row["candidate_authors"][0]]+=1
        else:
            candidate_201["ambiguous_or_unmatched"]+=1
    owner_rare_examples=defaultdict(list)
    for row in raw:
        if row["check_existence"] in {"all_exist","only_one_exists","any_exist"}:
            key=row["author"]+":"+row["check_existence"]
            if len(owner_rare_examples[key])<12:
                owner_rare_examples[key].append(row)
    # Native seven only_one_exists Tests: preserve real per-Test content,
    # and label comment+mode source-ID candidates as *unverified* joins.
    exact_one_candidates = []
    raw_by_title_mode = defaultdict(list)
    for row in raw:
        if row["comment"].strip():
            raw_by_title_mode[(normalized_comment(row["comment"]),row["check_existence"])].append(row)
    for row in native:
        if row["existence"]!="only_one_exists":
            continue
        matches=raw_by_title_mode.get((normalized_comment(row["title"]),row["existence"]),[])
        matches_by_identity={(m["id"],m["author"]) for m in matches}
        exact_one_candidates.append({
            "native_source":row["source"],"native_test":row["native_test"],
            "native_title":row["title"],"native_mode":row["mode"],
            "has_state":row["has_state"],
            "match_quality":("single_source_ID_candidate" if len(matches_by_identity)==1
                              else "unmatched" if not matches else "ambiguous"),
            "source_test_candidates":sorted({m["id"] for m in matches}),
            "candidate_authors":sorted({m["author"] for m in matches}),
            "original_checks":sorted({str(m["check"]) for m in matches}),
            "original_item_creation":sorted({o for m in matches for o in m["item_creation"]}),
        })
    if len(exact_one_candidates)!=7:
        raise AssertionError("Unexpected native exactly-one Test count")
    exists_source=Counter()
    for t in raw:exists_source[t["check_existence"]]+=1
    exists_native=Counter()
    for t in native:exists_native[t["existence"]]+=1
    native_source=Counter()
    for t in native:native_source[t["mode"]]+=1
    return {
      "status":"DIRECT ORIGINAL OVAL TEST ATTRIBUTION, candidate native linkage NOT verified",
      "source_revision":SOURCE_REVISION,
      "native_sha256":NATIVE_SHA,
      "units":{"raw":"unique Test IDs within each original source STIG",
               "native":"distinct compiled native Test definitions in curated 0.4 authoring",
               "candidate":"matching text comment + check_existence, NOT authoritative ID"},
      "original_source_tests":len(raw),
      "native_source_tests":len(native),
      "native_source_assessments":doc_count,
      "original_test_existence_distribution":dict(exists_source),
      "original_test_existence_by_author":owners,
      "original_test_counts_by_stig":by_stig,
      "native_test_existence_distribution":dict(exists_native),
      "native_combined_item_requirement_distribution":dict(native_source),
      "native_source_ID_join_candidate_quality":candidates,
      "all_201_native_all_exist_candidate_matches":all_exist_join,
      "all_201_native_all_exist_single_ID_candidate_author_counts":dict(candidate_201),
      "seven_native_exact_one_existence_tests":exact_one_candidates,
      "rare_original_tests_by_author_and_mode":dict(owner_rare_examples),
      "original_oval_element_distribution":element_counts,
      "source_members":source_members,
      "duplicate_test_id_observations":dupes,
      "rare_original_source_examples":[r for r in raw if r["check_existence"] in {"only_one_exists","any_exist","all_exist"}][:45],
      "cautions":[
        "Counts of all original OVAL Tests include Tests not selected in the 0.4 native six-STIG authoring; never divide one source count by the other denominator.",
        "Source namespace establishes *identity prefix*, not a verified DISA 1.3 release byte-for-byte comparison.",
        "A native descriptive Test name can match several different source IDs; title-and-mode joins are candidates only; do not call them provenance-confirmed.",
        "Original XCCDF Rule→OVAL Definition→Test ID closure is required for a provable native assessment linkage; mixed-source dependencies must be reported independently.",
        "No OVAL feature is dropped in this report and no schema, runtime, importer or source benchmark was modified."
      ],
    }

def md(v):
    lines=[
    "# Original-source OVAL rare-feature ownership vs six-STIG native authoring",
    "",
    "**Research only.** Input pinned NIWC `scap-content-library` revision",
    f"`{SOURCE_REVISION}` and exact native six-STIG r3 SHA-256 `{NATIVE_SHA}`.",
    "",
    f"Direct original OVAL source: **{v['original_source_tests']}** Test identities in six original STIG archives.",
    f"Curated native authoring: **{v['native_source_tests']}** Tests in **{v['native_source_assessments']}** automated Assessments.",
    "They are different populations: source archives contain OVAL content not necessarily selected into native authoring.",
    "",
    "## Original OVAL Test origin and existence usage","",
    "| Original ID namespace | at_least_one_exists | all_exist | any_exist | none_exist | only_one_exists |",
    "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for owner,cs in sorted(v["original_test_existence_by_author"].items()):
        lines.append("| "+owner+" | "+" | ".join(str(cs.get(m,0)) for m in ("at_least_one_exists","all_exist","any_exist","none_exist","only_one_exists"))+" |")
    lines+=["", "## Selected native authoring modes (different denominator)", "",
            "| Existence mode | Native Test occurrences |",
            "| --- | ---: |"]
    lines += [f"| `{mode}` | {qty} |" for mode,qty in sorted(v["native_test_existence_distribution"].items())]
    lines += ["", "## Native Test source-ID linkage check", "",
              "Original OVAL Test comments and original existence modes can provide",
              "candidate matches, **not verified source identities**.",
              "| Candidate quality | Native Test count |","| --- | ---: |"]
    lines += [f"| `{status}` | {qty} |" for status,qty in sorted(v["native_source_ID_join_candidate_quality"].items())]
    lines+=["", "## Original rare Test examples by original author", ""]
    for key,examples in sorted(v["rare_original_tests_by_author_and_mode"].items()):
        lines.extend(["",f"### {key}", ""])
        for row in examples[:5]:
            lines.append(f"- \`{row['id']}\`: {row['comment'] or '(no comment)'}; "
                         f"State refs={row['state_refs']}, check={row['check']}")
    lines += ["", "## Candidate origin of the 201 selected native all_exist Tests", "",
              "The test title + existence mode yields exactly one original source Test ID",
              "for the cases below, but **that is not an explicit converter lineage ID**.",
              "", "| Candidate original author | Native Tests |",
              "| --- | ---: |"]
    lines += [f"| {author} | {count} |"
              for author,count in sorted(v["all_201_native_all_exist_single_ID_candidate_author_counts"].items())]
    lines+=["", "## Seven native Test-level only_one_exists cases", "",
           "Exactly one **existing Item** is distinct from exactly one **matching Item**.",
           "Unverified joins use source Test comment and existence mode, not a converter ID.",
           "", "| Native Assessment | Has State | Original Test ID candidate | Original check |",
           "| --- | --- | --- | --- |"]
    for case in v["seven_native_exact_one_existence_tests"]:
        orig=", ".join(case["source_test_candidates"]) or "not found"
        origcheck=", ".join(case["original_checks"]) or "unknown"
        lines.append(f"| \`{case['native_source']}\` | {case['has_state']} "
                     f"| \`{orig}\` | \`{origcheck}\` |")
    lines+=["", "These seven should be reviewed for *actual resource duplication intent*;",
            "replacing exact-one with at-least-one is not a lossless simplification.",
            ""]
    lines+=["", "## Source attribution for 201 native all_exist cases", "",
            "The JSON contains each native Test with **source-ID candidates**, not proven",
            "lineage. Cases where several original IDs share a comment, or none match,",
            "require XCCDF Rule/Definition/source Test ID mapping. Do not infer author",
            "statistics for those from filenames or NIWC packaging.",
            "", "## Limitations and decision policy", ""]
    lines.extend("- "+v2 for v2 in v["cautions"])
    lines+=["", "Any rare OVAL feature needs a separate human-value/semantic review:",
        "retaining the capability to convert a source construct does not require",
        "giving native content writers a corresponding new keyword. Mark unused",
        "source features as candidates, not automatically obsolete.", ""]
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sources",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    a=p.parse_args()
    out=build(a)
    Path(a.json).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    Path(a.markdown).write_text(md(out))
    print(json.dumps({k:out[k] for k in ("original_source_tests","native_source_tests","original_test_existence_by_author","native_source_ID_join_candidate_quality")},indent=2))
