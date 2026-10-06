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
    risk=[]
    if correlated: risk.append("correlated_binding")
    if nested: risk.append("nested_dependency")
    if multiproj: risk.append("multi_projection")
    if functions: risk.append("variable_function")
    if any(e["var_check"] not in {"at least one","all(default)"} for e in edges): risk.append("nontrivial_var_check")
    disposition="candidate_for_equivalence_proof" if edges and not risk else "review_required_before_rewrite"
    return {"file":str(path),"rule_id":rid,"title":title,"definitions":len(defs),"tests":len(tests),"objects":len(objects),"states":len(states),"variables":len(variables),"object_component_variables":sum(bool(var_lineages(v,variables,memo)) for v in variables),"dependent_object_edges":edges,"correlated_candidates":correlated,"nested_dependency_paths":nested,"multi_projection_sources":multiproj,"variable_functions":functions,"rewrite_risk":risk,"preliminary_disposition":disposition}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--output',required=True)
    ap.add_argument('--label',default='corpus')
    args=ap.parse_args()
    root=Path(args.corpus)
    files=sorted(root.rglob('oval.xml'))
    rows=[analyze_file(p) for p in files]
    candidates=[r for r in rows if not r.get('parse_error') and (r['dependent_object_edges'] or r['correlated_candidates'] or r['nested_dependency_paths'] or r['multi_projection_sources'])]
    classes=Counter()
    for r in candidates:
        if r['correlated_candidates']: classes['correlated_binding_risk']+=1
        if r['nested_dependency_paths']: classes['nested_dependency']+=1
        if r['multi_projection_sources']: classes['multi_projection']+=1
        if r['dependent_object_edges']: classes['dependent_collection']+=1
    report={"label":args.label,"closure_files":len(files),"candidate_closures":len(candidates),"class_counts":dict(classes),"candidates":candidates}
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ('label','closure_files','candidate_closures','class_counts')},indent=2))

if __name__=='__main__': main()
