#!/usr/bin/env python3
"""Measure nested OVAL criteria that look like conditional/applicability authoring.

Research-only. Structural candidates are not automatically conversion-safe:
OVAL's six-state truth model can make Boolean branch trees differ from procedural
if/then/else semantics.
"""
from __future__ import annotations

import argparse, json, zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
    aggregate_operator,
)

RESULTS=(TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE)

def local(tag):
    return tag.split("}",1)[-1] if isinstance(tag,str) else ""

def as_bool(value):
    return str(value or "false").lower()=="true"

def docs(package):
    out=[]
    with zipfile.ZipFile(package) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith(".xml"): continue
            try: root=ET.fromstring(z.read(name))
            except ET.ParseError: continue
            out.append((name,root))
    return out

def rule_roots(all_docs):
    rows=[]; seen=set()
    for _,root in all_docs:
        for rule in root.iter():
            if local(rule.tag)!="Rule": continue
            rid=rule.get("id") or ""
            title=next(((x.text or "").strip() for x in rule if local(x.tag)=="title"),"")
            refs=[]
            for check in rule:
                if local(check.tag)!="check": continue
                system=(check.get("system") or "").lower()
                for ref in check:
                    if local(ref.tag)!="check-content-ref": continue
                    did=ref.get("name"); href=ref.get("href")
                    if did and did.startswith("oval:") and ("oval" in system or not system):
                        refs.append({"definition":did,"href":href})
            key=(rid,tuple((r["definition"],r.get("href")) for r in refs))
            if refs and key not in seen:
                seen.add(key); rows.append({"id":rid,"title":title,"refs":refs})
    return rows

def scoped_docs(all_docs,rule):
    hrefs={
        Path((r.get("href") or "").split("#",1)[0]).name
        for r in rule["refs"] if r.get("href")
    }
    selected=[(n,r) for n,r in all_docs if Path(n).name in hrefs]
    return selected or all_docs

def definitions(selected):
    out={}
    for _,root in selected:
        for node in root.iter():
            if local(node.tag)=="definition" and node.get("id"):
                out.setdefault(node.get("id"),node)
    return out

def criteria_root(defn):
    return next((x for x in defn if local(x.tag)=="criteria"),None)

def ast(node):
    name=local(node.tag)
    base={
        "negate":as_bool(node.get("negate")),
        "applicability_check":as_bool(node.get("applicability_check")),
    }
    if name=="criteria":
        return {**base,"kind":"group","operator":(node.get("operator") or "AND").upper(),
                "children":[ast(x) for x in node if local(x.tag) in {"criteria","criterion","extend_definition"}]}
    if name=="criterion":
        return {**base,"kind":"test","ref":node.get("test_ref"),"comment":node.get("comment")}
    if name=="extend_definition":
        return {**base,"kind":"definition","ref":node.get("definition_ref"),"comment":node.get("comment")}
    raise ValueError(name)

def walk(node):
    yield node
    for child in node.get("children",[]):
        yield from walk(child)

def leaf_key(node):
    if node.get("kind") in {"test","definition"} and node.get("ref"):
        return (node["kind"],node["ref"])
    return None

def branch_atoms(node):
    if node.get("kind")!="group" or node.get("operator")!="AND" or node.get("negate"):
        return None
    if any(c.get("kind")=="group" for c in node.get("children",[])):
        return None
    return node.get("children",[])

def binary_guard_pattern(node):
    """Detect OR(AND(G,...), AND(!G,...)) at one structural level."""
    if node.get("kind")!="group" or node.get("operator")!="OR" or node.get("negate"):
        return None
    children=node.get("children",[])
    if len(children)!=2: return None
    a=branch_atoms(children[0]); b=branch_atoms(children[1])
    if a is None or b is None: return None
    candidates=[]
    for left in a:
        lk=leaf_key(left)
        if not lk: continue
        for right in b:
            if leaf_key(right)==lk and left.get("negate") != right.get("negate"):
                candidates.append((lk,left,right))
    if len(candidates)!=1: return None
    guard,left,right=candidates[0]
    pa=[x for x in a if x is not left]
    pb=[x for x in b if x is not right]
    if not pa or not pb: return None
    common={
        leaf_key(x) for x in pa if leaf_key(x)
    } & {
        leaf_key(x) for x in pb if leaf_key(x)
    }
    return {
        "guard_kind":guard[0],
        "guard_ref":guard[1],
        "then_branch_is_positive_guard":not left.get("negate"),
        "then_payload_nodes":len(pa),
        "else_payload_nodes":len(pb),
        "shared_payload_refs":len(common),
        "guard_applicability_marked":bool(left.get("applicability_check") or right.get("applicability_check")),
    }

def structural_metrics(tree):
    nodes=list(walk(tree))
    groups=[n for n in nodes if n["kind"]=="group"]
    nested=sum(1 for n in groups for c in n.get("children",[]) if c.get("kind")=="group")
    mixed=sum(
        1 for n in groups
        if any(c.get("kind")=="group" and c.get("operator")!=n.get("operator") for c in n.get("children",[]))
    )
    ors=sum(n.get("operator")=="OR" for n in groups)
    ands=sum(n.get("operator")=="AND" for n in groups)
    apps=sum(bool(n.get("applicability_check")) for n in nodes)
    binary=[binary_guard_pattern(n) for n in groups]
    binary=[x for x in binary if x]
    branch_like=sum(
        1 for n in groups
        if n.get("operator")=="OR"
        and len(n.get("children",[]))>=2
        and all(c.get("kind")=="group" and c.get("operator")=="AND" for c in n.get("children",[]))
    )
    applicability_guard_groups=sum(
        1 for n in groups
        if n.get("operator")=="AND"
        and any(c.get("applicability_check") for c in n.get("children",[]))
        and any(not c.get("applicability_check") for c in n.get("children",[]))
    )
    return {
        "groups":len(groups),
        "and_groups":ands,
        "or_groups":ors,
        "nested_group_edges":nested,
        "mixed_operator_groups":mixed,
        "applicability_marked_nodes":apps,
        "branch_like_or_of_ands":branch_like,
        "binary_guard_patterns":binary,
        "applicability_guard_groups":applicability_guard_groups,
    }

def closure_defs(index, roots):
    seen=set(); q=list(roots); out=[]
    while q:
        did=q.pop()
        if did in seen: continue
        seen.add(did)
        d=index.get(did)
        if d is None: continue
        out.append(d)
        cr=criteria_root(d)
        if cr is None: continue
        for n in cr.iter():
            if local(n.tag)=="extend_definition" and n.get("definition_ref"):
                q.append(n.get("definition_ref"))
    return out

def negate_result(value):
    if value==TRUE: return FALSE
    if value==FALSE: return TRUE
    return value

def conditional_truth_comparison():
    """Compare generic binary guard Boolean tree with proposed conditional semantics."""
    mismatches=[]
    matches=0
    for g in RESULTS:
        for p in RESULTS:
            for q in RESULTS:
                oval=aggregate_operator("OR",[
                    aggregate_operator("AND",[g,p]),
                    aggregate_operator("AND",[negate_result(g),q]),
                ])
                conditional=p if g==TRUE else q if g==FALSE else g
                if oval==conditional:
                    matches+=1
                elif len(mismatches)<12:
                    mismatches.append({"guard":g,"then":p,"else":q,"oval":oval,"conditional":conditional})
    return {
        "cases":len(RESULTS)**3,
        "equal_cases":matches,
        "mismatch_cases":len(RESULTS)**3-matches,
        "universally_equivalent":matches==len(RESULTS)**3,
        "sample_mismatches":mismatches,
        "conditional_semantics":"true->then, false->else, other guard outcomes propagate",
    }

def analyze(package):
    all_docs=docs(package)
    rows=[]
    for rule in rule_roots(all_docs):
        selected=scoped_docs(all_docs,rule)
        idx=definitions(selected)
        defs=closure_defs(idx,[r["definition"] for r in rule["refs"]])
        per=[]
        for d in defs:
            cr=criteria_root(d)
            if cr is None: continue
            tree=ast(cr)
            m=structural_metrics(tree)
            if (
                m["nested_group_edges"] or m["or_groups"] or
                m["applicability_marked_nodes"] or m["binary_guard_patterns"]
            ):
                per.append({"definition":d.get("id"),**m})
        if not per: continue
        rows.append({
            "rule_id":rule["id"],
            "title":rule["title"],
            "definitions":per,
            "has_nested":any(x["nested_group_edges"] for x in per),
            "has_or":any(x["or_groups"] for x in per),
            "has_branch_like":any(x["branch_like_or_of_ands"] for x in per),
            "has_binary_guard_pattern":any(x["binary_guard_patterns"] for x in per),
            "has_applicability_marker":any(x["applicability_marked_nodes"] for x in per),
            "has_applicability_guard_group":any(x["applicability_guard_groups"] for x in per),
        })
    all_rules=rule_roots(all_docs)
    return {
        "package":package.name,
        "automated_oval_rule_count":len(all_rules),
        "rules_with_relevant_criteria":len(rows),
        "counts":{
            "rules_with_nested_criteria":sum(r["has_nested"] for r in rows),
            "rules_with_or":sum(r["has_or"] for r in rows),
            "rules_with_or_of_and_branches":sum(r["has_branch_like"] for r in rows),
            "rules_with_binary_guard_shape":sum(r["has_binary_guard_pattern"] for r in rows),
            "rules_with_applicability_marker":sum(r["has_applicability_marker"] for r in rows),
            "rules_with_applicability_guard_group":sum(r["has_applicability_guard_group"] for r in rows),
        },
        "rules":rows,
        "generic_binary_guard_truth_comparison":conditional_truth_comparison(),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",type=Path)
    ap.add_argument("--label")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    report=analyze(args.package)
    report["label"]=args.label or args.package.stem
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"label":report["label"],"automated_oval_rule_count":report["automated_oval_rule_count"],**report["counts"],
                      "truth":report["generic_binary_guard_truth_comparison"]},indent=2))
if __name__=="__main__":
    main()
