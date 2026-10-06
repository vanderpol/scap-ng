#!/usr/bin/env python3
"""Measure OVAL feature usage and authoring-locality opportunities in SCAP 1.4 content."""
from __future__ import annotations

import argparse, json, zipfile, hashlib
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

FUNCTIONS={
    "arithmetic","begin","concat","count","end","escape_regex","glob_to_regex",
    "merge","object_component","regex_capture","split","substring",
    "time_difference","unique","variable_component",
}

def local(tag):
    return tag.split("}",1)[-1] if isinstance(tag,str) else ""

def text(node):
    return (node.text or "").strip() if node is not None else ""

def xml_docs(package):
    docs=[]
    with zipfile.ZipFile(package) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith(".xml"): continue
            try: root=ET.fromstring(z.read(name))
            except ET.ParseError: continue
            docs.append((name,root))
    return docs

def index_oval(docs):
    idx={}
    duplicates=set()
    for _,root in docs:
        for section in root.iter():
            if local(section.tag) not in {"definitions","tests","objects","states","variables"}: continue
            for node in section:
                ident=node.get("id")
                if not ident: continue
                if ident in idx and ET.tostring(idx[ident]) != ET.tostring(node):
                    duplicates.add(ident)
                else: idx.setdefault(ident,node)
    return idx,duplicates

def automated_roots(docs):
    rows=[]
    seen=set()
    for _,root in docs:
        for rule in root.iter():
            if local(rule.tag)!="Rule": continue
            rid=rule.get("id") or ""
            title=text(next((x for x in rule if local(x.tag)=="title"),None))
            checks=[]
            for check in rule:
                if local(check.tag)!="check": continue
                system=(check.get("system") or "").lower()
                for ref in check:
                    if local(ref.tag)!="check-content-ref": continue
                    name=ref.get("name")
                    href=ref.get("href")
                    if name and name.startswith("oval:") and ("oval" in system or not system):
                        checks.append({"definition":name,"href":href})
            unique=[]
            observed=set()
            for item in checks:
                key2=(item["definition"],item.get("href"))
                if key2 not in observed:
                    observed.add(key2); unique.append(item)
            checks=unique
            if not checks: continue
            key=(rid,tuple((x["definition"],x.get("href")) for x in checks))
            if key in seen: continue
            seen.add(key)
            rows.append({
                "rule_id":rid,
                "title":title,
                "checks":checks,
                "definitions":[x["definition"] for x in checks],
            })
    return rows

def scoped_index(docs, rule, fallback):
    """Build the OVAL ID index from the component(s) referenced by this Rule."""
    hrefs={
        Path((item.get("href") or "").split("#",1)[0]).name
        for item in rule.get("checks",[])
        if item.get("href")
    }
    selected=[
        (name,root)
        for name,root in docs
        if Path(name).name in hrefs
    ]
    if not selected:
        return fallback, []
    idx,conflicts=index_oval(selected)
    return idx, sorted(conflicts)


def node_kind(node):
    n=local(node.tag)
    if n=="definition": return "definition"
    for k in ("test","object","state","variable"):
        if n.endswith("_"+k): return k
    return None

def refs(node):
    out=[]
    k=node_kind(node)
    if k=="definition":
        for x in node.iter():
            n=local(x.tag)
            if n=="criterion" and x.get("test_ref"): out.append(("test",x.get("test_ref")))
            elif n=="extend_definition" and x.get("definition_ref"): out.append(("definition",x.get("definition_ref")))
    elif k=="test":
        for x in node:
            n=local(x.tag)
            if n=="object" and x.get("object_ref"): out.append(("object",x.get("object_ref")))
            elif n=="state" and x.get("state_ref"): out.append(("state",x.get("state_ref")))
    elif k in {"object","state"}:
        for x in node.iter():
            if x is node: continue
            n=local(x.tag)
            if x.get("var_ref"): out.append(("variable",x.get("var_ref")))
            if k=="object" and n=="object_reference" and text(x): out.append(("object",text(x)))
            if k=="object" and n=="filter":
                ref=x.get("state_ref") or text(x)
                if ref: out.append(("state",ref))
            if k=="object" and n=="var_ref" and text(x): out.append(("variable",text(x)))
    elif k=="variable":
        for x in node.iter():
            if x is node: continue
            n=local(x.tag)
            if n=="object_component" and x.get("object_ref"): out.append(("object",x.get("object_ref")))
            if x.get("var_ref"): out.append(("variable",x.get("var_ref")))
    return out

def closure(idx, roots):
    q=[("definition",x) for x in roots]
    seen=set(); nodes={}; missing=[]; edges=[]
    while q:
        expected,ident=q.pop()
        if ident in seen: continue
        seen.add(ident)
        node=idx.get(ident)
        if node is None:
            missing.append({"kind":expected,"id":ident}); continue
        nodes[ident]=node
        for kind,target in refs(node):
            edges.append((ident,target,kind))
            if target not in seen: q.append((kind,target))
    return nodes,edges,missing

def classify_extend_definition(nodes):
    """Classify whether extend_definition contributes semantics or only indirection."""
    out={
        "occurrences":0,
        "wrapper_only":0,
        "multiple_extends_only":0,
        "extend_plus_direct_tests":0,
        "extend_plus_nested_criteria":0,
        "negated_extend":0,
        "or_composition":0,
        "other_mixed":0,
    }
    for node in nodes.values():
        if node_kind(node)!="definition":
            continue
        criteria=[x for x in list(node) if local(x.tag)=="criteria"]
        for crit in criteria:
            children=[x for x in list(crit) if local(x.tag) in {"criterion","criteria","extend_definition"}]
            extends=[x for x in children if local(x.tag)=="extend_definition"]
            if not extends:
                continue
            n=len(extends)
            out["occurrences"] += n
            operator=(crit.get("operator") or "AND").upper()
            negate=(crit.get("negate") or "false").lower()=="true"
            direct_tests=any(local(x.tag)=="criterion" for x in children)
            nested=any(local(x.tag)=="criteria" for x in children)
            if negate:
                out["negated_extend"] += n
            if operator=="OR":
                out["or_composition"] += n
            if len(children)==1 and n==1 and operator=="AND" and not negate:
                out["wrapper_only"] += 1
            elif len(children)==n and n>1 and not nested and not direct_tests and not negate:
                out["multiple_extends_only"] += n
            elif direct_tests:
                out["extend_plus_direct_tests"] += n
            elif nested:
                out["extend_plus_nested_criteria"] += n
            else:
                out["other_mixed"] += n
    return out


def analyze_root(idx, rule):
    nodes,edges,missing=closure(idx,rule["definitions"])
    kinds=Counter(node_kind(n) for n in nodes.values())
    inbound=Counter(target for _,target,_ in edges)
    inbound_kinds=defaultdict(set)
    for src,target,kind in edges: inbound_kinds[target].add(node_kind(nodes.get(src)) or "?")

    feats=set(); funcs=Counter(); test_types=Counter(); checks=Counter(); exist=Counter()
    direct_object_refs=[]; direct_state_refs=[]
    nested_criteria=False; negation=False; extends=False
    for n in nodes.values():
        kind=node_kind(n); name=local(n.tag)
        if kind=="definition":
            if any(local(x.tag)=="extend_definition" for x in n.iter()): extends=True
            criteria=[x for x in n.iter() if local(x.tag)=="criteria"]
            if len(criteria)>1: nested_criteria=True
            if any((x.get("negate") or "false").lower()=="true" for x in n.iter()): negation=True
        elif kind=="test":
            test_types[name]+=1
            checks[n.get("check") or "<missing>"]+=1
            exist[n.get("check_existence") or "<default>"]+=1
            objs=[x.get("object_ref") for x in n if local(x.tag)=="object" and x.get("object_ref")]
            sts=[x.get("state_ref") for x in n if local(x.tag)=="state" and x.get("state_ref")]
            direct_object_refs += objs; direct_state_refs += sts
            if len(sts)>1: feats.add("multiple_states")
            if not sts: feats.add("existence_only")
            if "shellcommand" in name: feats.add("shellcommand")
        if kind=="object":
            if any(local(x.tag)=="set" for x in n.iter()): feats.add("set")
            if any(local(x.tag)=="filter" for x in n.iter()): feats.add("filter")
            if any(local(x.tag)=="behaviors" for x in n.iter()): feats.add("behaviors")
        if kind=="variable":
            feats.add("variable")
            for x in n.iter():
                if local(x.tag) in FUNCTIONS:
                    funcs[local(x.tag)]+=1
                    feats.add("function:"+local(x.tag))
        for x in n.iter():
            if x.get("var_ref"): feats.add("var_ref")

    if kinds["test"]>1: feats.add("multiple_tests")
    if nested_criteria: feats.add("nested_criteria")
    if negation: feats.add("negation")
    if extends: feats.add("extend_definition")

    objects=[i for i,n in nodes.items() if node_kind(n)=="object"]
    states=[i for i,n in nodes.items() if node_kind(n)=="state"]
    variables=[i for i,n in nodes.items() if node_kind(n)=="variable"]
    obj_reused=[i for i in objects if inbound[i]>1]
    state_reused=[i for i in states if inbound[i]>1]
    var_reused=[i for i in variables if inbound[i]>1]

    direct_objects_single=sum(inbound[x]==1 for x in direct_object_refs)
    direct_states_single=sum(inbound[x]==1 for x in direct_state_refs)
    direct_objects_total=len(direct_object_refs)
    direct_states_total=len(direct_state_refs)

    function_features={x for x in feats if x.startswith("function:")}
    dataflow_complex=bool(
        {"variable","set","filter"} & feats or function_features
    )
    evaluation_complex=bool(
        {"multiple_tests","multiple_states","nested_criteria","negation"} & feats
    )
    simple_linear=(
        kinds["test"]==1
        and direct_objects_total==1
        and direct_states_total<=1
        and direct_objects_single==direct_objects_total
        and direct_states_single==direct_states_total
        and not dataflow_complex
        and not ({"nested_criteria","negation"} & feats)
    )
    local_multi_test=(
        direct_objects_single==direct_objects_total
        and direct_states_single==direct_states_total
        and not dataflow_complex
        and not ({"nested_criteria","negation"} & feats)
    )
    no_reuse_barrier=not obj_reused and not state_reused

    extend_usage=classify_extend_definition(nodes)

    return {
        **rule,
        "counts":dict(kinds),
        "features":sorted(feats),
        "functions":dict(funcs),
        "test_types":dict(test_types),
        "test_check":dict(checks),
        "test_existence":dict(exist),
        "missing_refs":missing,
        "extend_definition_usage":extend_usage,
        "reuse":{
            "objects_reused":len(obj_reused),
            "states_reused":len(state_reused),
            "variables_reused":len(var_reused),
            "direct_test_object_refs":direct_objects_total,
            "direct_test_object_refs_single_use":direct_objects_single,
            "direct_test_state_refs":direct_states_total,
            "direct_test_state_refs_single_use":direct_states_single,
        },
        "classification":{
            "simple_linear":simple_linear,
            "local_multi_test":local_multi_test,
            "no_object_state_reuse_barrier":no_reuse_barrier,
            "dataflow_complex":dataflow_complex,
            "evaluation_complex":evaluation_complex,
        },
    }

def pct(n,d): return round(100*n/d,1) if d else 0.0

def summarize(rows):
    features=Counter(); functions=Counter(); test_types=Counter()
    totals=Counter(); reuse=Counter(); classes=Counter(); extend_usage=Counter()
    for r in rows:
        features.update(r["features"]); functions.update(r["functions"]); test_types.update(r["test_types"])
        for k,v in r["counts"].items(): totals[k]+=v
        for k,v in r["reuse"].items(): reuse[k]+=v
        for k,v in r["classification"].items(): classes[k]+=int(bool(v))
        extend_usage.update(r.get("extend_definition_usage",{}))
    n=len(rows)
    return {
        "automated_rules_with_oval":n,
        "rule_feature_counts":dict(features),
        "rule_feature_percent":{k:pct(v,n) for k,v in sorted(features.items())},
        "variable_function_counts":dict(functions),
        "test_type_occurrences":dict(test_types),
        "closure_node_occurrences":dict(totals),
        "reuse_totals":dict(reuse),
        "extend_definition_usage":dict(extend_usage),
        "locality":{
            "simple_linear_rules":classes["simple_linear"],
            "simple_linear_percent":pct(classes["simple_linear"],n),
            "rules_without_object_state_reuse_barrier":classes["no_object_state_reuse_barrier"],
            "rules_without_object_state_reuse_barrier_percent":pct(classes["no_object_state_reuse_barrier"],n),
            "dataflow_complex_rules":classes["dataflow_complex"],
            "dataflow_complex_percent":pct(classes["dataflow_complex"],n),
            "evaluation_complex_rules":classes["evaluation_complex"],
            "evaluation_complex_percent":pct(classes["evaluation_complex"],n),
            "local_multi_test_rules":classes["local_multi_test"],
            "local_multi_test_percent":pct(classes["local_multi_test"],n),
            "direct_test_object_single_use_percent":pct(reuse["direct_test_object_refs_single_use"],reuse["direct_test_object_refs"]),
            "direct_test_state_single_use_percent":pct(reuse["direct_test_state_refs_single_use"],reuse["direct_test_state_refs"]),
        },
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",type=Path)
    ap.add_argument("--label",default=None)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    docs=xml_docs(args.package)
    idx,duplicates=index_oval(docs)
    roots=automated_roots(docs)
    rows=[]
    scoped_conflicts={}
    for rule in roots:
        rule_idx,conflicts=scoped_index(docs,rule,idx)
        if conflicts:
            scoped_conflicts[rule["rule_id"]]=conflicts
        rows.append(analyze_root(rule_idx,rule))
    report={
        "format":"scap-ng-oval-authoring-complexity-0.1",
        "package":args.package.name,
        "label":args.label or args.package.stem,
        "sha256":hashlib.sha256(args.package.read_bytes()).hexdigest(),
        "xml_files":len(docs),
        "indexed_oval_nodes":len(idx),
        "global_duplicate_conflicting_ids":sorted(duplicates),
        "scoped_duplicate_conflicting_ids":scoped_conflicts,
        "summary":summarize(rows),
        "rules":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"label":report["label"],**report["summary"]["locality"],
                      "automated_rules_with_oval":len(rows)},indent=2))
    return 0 if not scoped_conflicts else 1

if __name__=="__main__":
    raise SystemExit(main())
