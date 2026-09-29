#!/usr/bin/env python3
"""Compare original RHEL9 XCCDF semantic IR with regenerated test XCCDF."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from lxml import etree as E

X="http://checklists.nist.gov/xccdf/1.2"
NS={"x":X}
RULE_SRC=re.compile(r"_rule_(SV-\d+)(r\d+)_rule$")
RULE_GEN=re.compile(r"_rule_(SV-\d+)(r\d+)_rule$")
PROFILE_SRC="xccdf_mil.disa.stig_profile_"
PROFILE_GEN="xccdf_scap-ng_profile_"

def source_rule_id(x):
    m=RULE_SRC.search(x); return (m.group(1),m.group(2)) if m else None
def generated_rule_id(x):
    m=RULE_GEN.search(x); return (m.group(1),m.group(2)) if m else None
def boolv(v,default=True):
    if v is None:return default
    return str(v).lower() in {"true","1"}
def profile_name(x):
    if x.startswith(PROFILE_SRC): return x[len(PROFILE_SRC):]
    if x.startswith(PROFILE_GEN): return x[len(PROFILE_GEN):]
    return x

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_ir",type=Path)
    ap.add_argument("regenerated_xccdf",type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    src=json.loads(a.source_ir.read_text())
    root=E.parse(str(a.regenerated_xccdf)).getroot()
    issues=[]

    # Rule core and selector surface.
    grules={}
    for e in root.findall("x:Rule",NS):
        ident=generated_rule_id(e.get("id"))
        if not ident:
            issues.append({"kind":"unrecognized_generated_rule_id","id":e.get("id")}); continue
        grules[ident[0]]=(ident[1],e)
    srules={source_rule_id(r["id"])[0]:(source_rule_id(r["id"])[1],r) for r in src["rules"]}
    if set(grules)!=set(srules):
        issues.append({"kind":"rule_set_mismatch",
                       "missing":sorted(set(srules)-set(grules)),
                       "extra":sorted(set(grules)-set(srules))})
    for rid,(rev,sr) in srules.items():
        if rid not in grules: continue
        grev,g=grules[rid]
        if grev!=rev: issues.append({"kind":"rule_revision_mismatch","rule":rid,"source":rev,"generated":grev})
        if g.get("severity","unknown")!=sr.get("severity","unknown"):
            issues.append({"kind":"severity_mismatch","rule":rid})
        if float(g.get("weight","1.0"))!=float(sr.get("weight") or 1.0):
            issues.append({"kind":"weight_mismatch","rule":rid})
        gt=g.findtext("x:title",namespaces=NS)
        if gt!=sr.get("title"): issues.append({"kind":"title_mismatch","rule":rid})
        expected={c.get("selector") or "default" for c in sr.get("checks",[])}
        actual={c.get("selector") or "default" for c in g.findall("x:check",NS)}
        if expected!=actual:
            issues.append({"kind":"selector_mismatch","rule":rid,"source":sorted(expected),"generated":sorted(actual)})

    # Effective profile selection, ignoring verbose explicit true selections.
    group_members={g["id"]:g.get("members",{}).get("rules",[]) for g in src["groups"]}
    src_profiles={}
    for p in src["resolved_profiles"]:
        selected={source_rule_id(r["id"])[0]:r.get("selected_default",True) for r in src["rules"]}
        for act in p.get("effective_actions",[]):
            if act.get("kind")!="select": continue
            val=boolv(act.get("attributes",{}).get("selected"),True)
            for target in act.get("targets",[]):
                if target["kind"]=="rule":
                    selected[source_rule_id(target["id"])[0]]=val
                elif target["kind"]=="group":
                    for x in group_members[target["id"]]:
                        selected[source_rule_id(x)[0]]=val
        src_profiles[profile_name(p["id"])]={k for k,v in selected.items() if not v}

    gen_profiles={}
    for p in root.findall("x:Profile",NS):
        disabled=set()
        for s in p.findall("x:select",NS):
            if not boolv(s.get("selected"),True):
                rr=generated_rule_id(s.get("idref"))
                if rr: disabled.add(rr[0])
        gen_profiles[profile_name(p.get("id"))]=disabled
    if set(src_profiles)!=set(gen_profiles):
        issues.append({"kind":"profile_set_mismatch",
                       "missing":sorted(set(src_profiles)-set(gen_profiles)),
                       "extra":sorted(set(gen_profiles)-set(src_profiles))})
    source_profile_meta={profile_name(p["id"]):p for p in src.get("profiles",[])}
    generated_profile_meta={profile_name(p.get("id")):p for p in root.findall("x:Profile",NS)}
    for pid in set(src_profiles)&set(gen_profiles):
        sp=source_profile_meta.get(pid,{})
        gp=generated_profile_meta.get(pid)
        if gp is not None:
            st=sp.get("title")
            gt=gp.findtext("x:title",namespaces=NS)
            if gt!=st:
                issues.append({"kind":"profile_title_mismatch","profile":pid,"source":st,"generated":gt})
            sd=sp.get("description")
            if sd=="<ProfileDescription></ProfileDescription>": sd=None
            gd=gp.findtext("x:description",namespaces=NS)
            if gd!=sd:
                issues.append({"kind":"profile_description_mismatch","profile":pid,"source":sd,"generated":gd})
        if src_profiles[pid]!=gen_profiles[pid]:
            issues.append({"kind":"profile_selection_mismatch","profile":pid,
                           "source_disabled":sorted(src_profiles[pid]),
                           "generated_disabled":sorted(gen_profiles[pid])})

    # Benchmark direct CPE target set.
    source_platforms=set(src["benchmark"].get("platforms") or [])
    generated_platforms={x.get("idref") for x in root.findall("x:platform",NS)}
    if source_platforms!=generated_platforms:
        issues.append({"kind":"benchmark_platform_mismatch",
                       "source":sorted(source_platforms),"generated":sorted(generated_platforms)})

    out={"pass":not issues,"issue_count":len(issues),"issues":issues,
         "stats":{"rules":len(grules),"profiles":len(gen_profiles)}}
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.output:
        a.output.write_text(text,encoding="utf-8")
    print(text,end="")
    raise SystemExit(0 if out["pass"] else 1)

if __name__=="__main__":main()
