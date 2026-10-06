#!/usr/bin/env python3
"""Audit per-rule OVAL closures for iteration/correlation patterns.

Research-only: detects dataflow shapes that may benefit from native scoped iteration.
It does not rewrite content or claim author intent.
"""
from __future__ import annotations
import argparse, json, re
from collections import defaultdict, Counter
from pathlib import Path
from lxml import etree as ET

def local(el):
    try: return ET.QName(el).localname
    except Exception: return ""

def attrs_local(el):
    return {ET.QName(k).localname if k.startswith('{') else k:v for k,v in el.attrib.items()}

def index_section(root, section):
    out={}
    for sec in root.iter():
        if local(sec)==section:
            for el in sec:
                i=el.get('id')
                if i: out[i]=el
            break
    return out

def var_refs(el):
    out=[]
    for x in el.iter():
        a=attrs_local(x)
        if a.get('var_ref'):
            out.append({"variable":a['var_ref'],"entity":local(x),"operation":a.get('operation'),"var_check":a.get('var_check')})
    return out

def var_lineages(vid, variables, memo, stack=()):
    if vid in memo: return memo[vid]
    if vid in stack: return set()
    el=variables.get(vid)
    ans=set()
    if el is None:
        memo[vid]=ans
        return ans
    for x in el.iter():
        n=local(x); a=attrs_local(x)
        if n=='object_component' and a.get('object_ref'):
            ans.add((a['object_ref'], a.get('item_field') or a.get('record_field') or ''))
        elif n=='variable_component' and a.get('var_ref'):
            ans |= var_lineages(a['var_ref'],variables,memo,stack+(vid,))
    memo[vid]=ans
    return ans


def variable_shape(el):
    kind=local(el)
    if kind=="constant_variable":
        return "constant"
    if kind=="external_variable":
        return "external"
    children=[x for x in el if isinstance(x.tag,str) and local(x)!="notes"]
    if kind!="local_variable" or len(children)!=1:
        return "other"
    root=local(children[0])
    if root=="object_component":
        return "pure_object_projection"
    if root=="variable_component":
        return "pure_variable_alias"
    if root=="literal_component":
        return "pure_literal"
    return "transform"


def variable_root_operator(el):
    kind=local(el)
    if kind in {"constant_variable","external_variable"}:
        return kind
    children=[x for x in el if isinstance(x.tag,str) and local(x)!="notes"]
    if kind=="local_variable" and len(children)==1:
        return local(children[0])
    return "other"

def variable_consumer_roles(vid, objects, states, variables):
    roles=[]
    for oid,el in objects.items():
        for x in el.iter():
            a=attrs_local(x)
            if a.get("var_ref")==vid:
                roles.append({"kind":"object_selector","consumer":oid,"entity":local(x),"var_check":a.get("var_check") or "all(default)"})
    for sid,el in states.items():
        for x in el.iter():
            a=attrs_local(x)
            if a.get("var_ref")==vid:
                roles.append({"kind":"state_expected_value","consumer":sid,"entity":local(x),"var_check":a.get("var_check") or "all(default)"})
    for other,el in variables.items():
        if other==vid:
            continue
        for x in el.iter():
            a=attrs_local(x)
            if local(x)=="variable_component" and a.get("var_ref")==vid:
                roles.append({"kind":"variable_input","consumer":other,"entity":"variable_component"})
    return roles

def analyze_file(path):
    title=None
    prov=path.parent/"provenance.json"
    if prov.exists():
        try: title=json.loads(prov.read_text()).get("xccdf_title")
        except Exception: pass
    try: root=ET.parse(str(path)).getroot()
    except Exception as e: return {"file":str(path),"parse_error":str(e)}
    defs=index_section(root,'definitions'); tests=index_section(root,'tests'); objects=index_section(root,'objects'); states=index_section(root,'states'); variables=index_section(root,'variables')
    memo={}
    obj_consumers={oid:var_refs(el) for oid,el in objects.items()}
    state_consumers={sid:var_refs(el) for sid,el in states.items()}
    edges=[]
    for oid,refs in obj_consumers.items():
        for r in refs:
            for src,field in var_lineages(r['variable'],variables,memo):
                edges.append({"source_object":src,"source_object_type":local(objects[src]) if src in objects else None,"source_field":field,"variable":r['variable'],"target_object":oid,"target_object_type":local(objects[oid]),"target_entity":r['entity'],"operation":r['operation'],"var_check":r['var_check'] or "all(default)"})
    correlated=[]
    for tid,t in tests.items():
        a=attrs_local(t); oid=a.get('object_ref'); sids=[]
        if a.get('state_ref'): sids.append(a['state_ref'])
        for x in t.iter():
            xa=attrs_local(x)
            if xa.get('state_ref') and xa['state_ref'] not in sids: sids.append(xa['state_ref'])
        if not oid: continue
        orefs=obj_consumers.get(oid,[])
        for orf in orefs:
            ol=var_lineages(orf['variable'],variables,memo)
            for sid in sids:
                for srf in state_consumers.get(sid,[]):
                    sl=var_lineages(srf['variable'],variables,memo)
                    for so,sf in ol:
                        for to,tf in sl:
                            if so==to and (sf!=tf or orf['variable']!=srf['variable']):
                                correlated.append({"kind":"selector_vs_state","test":tid,"target_object":oid,"state":sid,"source_object":so,"selector_field":sf,"state_field":tf,"selector_variable":orf['variable'],"state_variable":srf['variable']})
    for oid,refs in obj_consumers.items():
        for i in range(len(refs)):
            for j in range(i+1,len(refs)):
                for so,sf in var_lineages(refs[i]['variable'],variables,memo):
                    for to,tf in var_lineages(refs[j]['variable'],variables,memo):
                        if so==to and (sf!=tf or refs[i]['variable']!=refs[j]['variable']):
                            correlated.append({"kind":"two_target_selectors","target_object":oid,"source_object":so,"left_field":sf,"right_field":tf,"left_variable":refs[i]['variable'],"right_variable":refs[j]['variable']})
    adj=defaultdict(set)
    for e in edges: adj[e['source_object']].add(e['target_object'])
    nested=[]
    for a,bs in adj.items():
        for b in bs:
            for c in adj.get(b,()): nested.append([a,b,c])
    intra_variable_multi_field=[]
    for vid,vel in variables.items():
        by_source=defaultdict(set)
        for x in vel.iter():
            if local(x)=="object_component":
                xa=attrs_local(x)
                if xa.get("object_ref"):
                    by_source[xa["object_ref"]].add(xa.get("item_field") or xa.get("record_field") or "")
        for source,fields in by_source.items():
            if len(fields)>1:
                intra_variable_multi_field.append({
                    "variable":vid,
                    "source_object":source,
                    "source_object_type":local(objects[source]) if source in objects else None,
                    "fields":sorted(fields),
                })
    projections=defaultdict(list)
    for vid in variables:
        for o,f in var_lineages(vid,variables,memo):
            projections[o].append((vid,f))
    multiproj=[]
    for o,pairs in projections.items():
        uniq=sorted(set(pairs))
        used=[x for x in uniq if any(e['variable']==x[0] for e in edges) or any(x[0]==r['variable'] for rs in state_consumers.values() for r in rs)]
        if len(used)>=2: multiproj.append({"source_object":o,"projections":[{"variable":v,"field":f} for v,f in used]})
    rid=None
    for part in path.parts:
        m=re.search(r'SV-\d+',part)
        if m: rid=m.group(0); break
    functions=sorted({local(x) for v in variables.values() for x in v.iter() if local(x) in {"arithmetic","begin","concat","count","end","escape_regex","glob_to_regex","merge","regex_capture","split","substring","time_difference","unique"}})
    variable_roles=[]
    for vid,vel in variables.items():
        variable_roles.append({
            "variable":vid,
            "shape":variable_shape(vel),
            "root_operator":variable_root_operator(vel),
            "consumers":variable_consumer_roles(vid,objects,states,variables),
            "lineage":[{"source_object":o,"field":f} for o,f in sorted(var_lineages(vid,variables,memo))],
        })
    risk=[]
    if correlated: risk.append("correlated_binding")
    if nested: risk.append("nested_dependency")
    if multiproj: risk.append("multi_projection")
    if intra_variable_multi_field: risk.append("same_item_field_correlation")
    if functions: risk.append("variable_function")
    if any(e["var_check"] not in {"at least one","all(default)"} for e in edges): risk.append("nontrivial_var_check")
    disposition="candidate_for_equivalence_proof" if edges and not risk else "review_required_before_rewrite"
    return {"file":str(path),"rule_id":rid,"title":title,"definitions":len(defs),"tests":len(tests),"objects":len(objects),"states":len(states),"variables":len(variables),"object_component_variables":sum(bool(var_lineages(v,variables,memo)) for v in variables),"dependent_object_edges":edges,"correlated_candidates":correlated,"nested_dependency_paths":nested,"multi_projection_sources":multiproj,"intra_variable_multi_field_sources":intra_variable_multi_field,"variable_functions":functions,"variable_roles":variable_roles,"rewrite_risk":risk,"preliminary_disposition":disposition}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--output',required=True)
    ap.add_argument('--label',default='corpus')
    args=ap.parse_args()
    root=Path(args.corpus)
    files=sorted(root.rglob('oval.xml'))
    rows=[analyze_file(p) for p in files]
    candidates=[r for r in rows if not r.get('parse_error') and (r['dependent_object_edges'] or r['correlated_candidates'] or r['nested_dependency_paths'] or r['multi_projection_sources'] or r['intra_variable_multi_field_sources'])]
    classes=Counter()
    for r in candidates:
        if r['correlated_candidates']: classes['correlated_binding_risk']+=1
        if r['nested_dependency_paths']: classes['nested_dependency']+=1
        if r['multi_projection_sources']: classes['multi_projection']+=1
        if r['intra_variable_multi_field_sources']: classes['same_item_field_correlation']+=1
        if r['dependent_object_edges']: classes['dependent_collection']+=1
    role_counts=Counter()
    role_consumers=Counter()
    unique_variables={}
    all_rows=[r for r in rows if not r.get("parse_error")]
    for row in all_rows:
        for vr in row.get("variable_roles",[]):
            role_counts[vr["shape"]]+=1
            for consumer in vr["consumers"]:
                role_consumers[(vr["shape"],consumer["kind"])]+=1

            # Per-rule closures repeat shared OVAL dependencies. Merge by OVAL
            # Variable ID within the benchmark so authoring-shape counts are not
            # inflated merely because several rules reuse one Variable.
            entry=unique_variables.setdefault(vr["variable"],{
                "shape":vr["shape"],
                "root_operator":vr.get("root_operator"),
                "consumers":set(),
                "lineage":set(),
            })
            if entry["shape"]!=vr["shape"] or entry.get("root_operator")!=vr.get("root_operator"):
                raise ValueError(f"Variable shape/operator changed across closures: {vr['variable']}")
            for consumer in vr["consumers"]:
                entry["consumers"].add((
                    consumer["kind"],
                    consumer["consumer"],
                    consumer.get("entity"),
                    consumer.get("var_check"),
                ))
            for lineage in vr["lineage"]:
                entry["lineage"].add((lineage["source_object"],lineage["field"]))

    unique_shapes=Counter(v["shape"] for v in unique_variables.values())
    unique_root_operators=Counter(v.get("root_operator") or "unknown" for v in unique_variables.values())
    projection_usage=Counter()
    usage_by_shape=Counter()
    root_usage=Counter()
    for vid,v in unique_variables.items():
        kinds={x[0] for x in v["consumers"]}
        if len(v["consumers"])==1:
            only=next(iter(v["consumers"]))
            usage=f"single_use_{only[0]}"
        elif len(v["consumers"])>1:
            usage="multi_use"
        else:
            usage="unused_in_reachable_closures"
        usage_by_shape[(v["shape"],usage)]+=1
        root_usage[(v.get("root_operator") or "unknown",usage)]+=1

        if v["shape"]=="pure_object_projection":
            projection_usage[usage]+=1
            projection_usage["consumer_kind_set:"+"+".join(sorted(kinds))]+=1

    unique_inventory=[]
    for vid,v in sorted(unique_variables.items()):
        consumers=[
            {"kind":kind,"consumer":consumer,"entity":entity,"var_check":var_check}
            for kind,consumer,entity,var_check in sorted(v["consumers"])
        ]
        lineage=[
            {"source_object":source_object,"field":field}
            for source_object,field in sorted(v["lineage"])
        ]
        if len(consumers)==1:
            usage_class="single_use_"+consumers[0]["kind"]
        elif len(consumers)>1:
            usage_class="multi_use"
        else:
            usage_class="unused_in_reachable_closures"
        unique_inventory.append({
            "variable":vid,
            "shape":v["shape"],
            "root_operator":v.get("root_operator"),
            "usage_class":usage_class,
            "consumers":consumers,
            "lineage":lineage,
        })

    report={
        "label":args.label,
        "closure_files":len(files),
        "candidate_closures":len(candidates),
        "class_counts":dict(classes),
        "variable_shape_counts":dict(role_counts),
        "variable_consumer_counts":{"|".join(k):v for k,v in sorted(role_consumers.items())},
        "unique_variable_shape_counts":dict(unique_shapes),
        "unique_variable_root_operator_counts":dict(unique_root_operators),
        "unique_variable_usage_by_shape":{"|".join(k):v for k,v in sorted(usage_by_shape.items())},
        "unique_variable_usage_by_root_operator":{"|".join(k):v for k,v in sorted(root_usage.items())},
        "unique_pure_projection_usage":dict(projection_usage),
        "unique_variable_inventory":unique_inventory,
        "candidates":candidates,
    }
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ('label','closure_files','candidate_closures','class_counts')},indent=2))

if __name__=='__main__': main()
