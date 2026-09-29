#!/usr/bin/env python3
"""Regenerate an XCCDF 1.2 policy surrogate from iteration-003 NG RHEL9 source.

This is a conformance test bridge, not a production SCAP exporter. Assessment
semantics are tested independently by the OVAL round-trip harness.
"""
from __future__ import annotations
import argparse,re
from pathlib import Path
from lxml import etree as E
import yaml

X="http://checklists.nist.gov/xccdf/1.2"
OVAL="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OCIL="http://scap.nist.gov/schema/ocil/2"
E.register_namespace("xccdf",X)

def q(local): return f"{{{X}}}{local}"
def load(p): return yaml.safe_load(p.read_text(encoding="utf-8"))
def norm_id(s): return re.sub(r"[^A-Za-z0-9_.-]+","-",s)
def rule_xid(rule):
    return f"xccdf_scap-ng_rule_{rule['id']}{rule['version']}_rule"
def profile_xid(pid):
    return f"xccdf_scap-ng_profile_{norm_id(pid)}"
def condition_ref(cid):
    # Test-only stable reference; semantic comparator maps this back to NG ID.
    return f"urn:scap-ng:applicability:{cid}"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("ng_root",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    b=load(a.ng_root/"benchmark.yaml")["benchmark"]
    rules={}
    for p in sorted((a.ng_root/"rules").glob("*.yaml")):
        r=load(p)["rule"]; rules[r["id"]]=r

    root=E.Element(q("Benchmark"),nsmap={None:X},id=f"xccdf_scap-ng_benchmark_{norm_id(b['id'])}",resolved="true")
    st=(b.get("status") or [{"value":"draft"}])[0]
    se=E.SubElement(root,q("status"))
    if st.get("date"): se.set("date",str(st["date"]))
    se.text=st.get("value") or "draft"
    for title in b.get("title") or []:
        e=E.SubElement(root,q("title")); e.text=title.get("text")
    for desc in b.get("description") or []:
        e=E.SubElement(root,q("description")); e.text=desc.get("text")

    # Benchmark target identifiers remain direct CPE references.
    for ident in (b.get("platform") or {}).get("identifiers",[]) or []:
        if ident.get("scheme")=="cpe":
            E.SubElement(root,q("platform"),idref=ident["value"])

    version=b.get("version") or {}
    E.SubElement(root,q("version")).text=str(version.get("value") or "1")

    # Profiles: default selection is true, so only disabled deltas need emitting.
    for p in b.get("profiles") or []:
        pe=E.SubElement(root,q("Profile"),id=profile_xid(p["id"]))
        E.SubElement(pe,q("title")).text=p.get("title") or p["id"]
        if p.get("description"):
            E.SubElement(pe,q("description")).text=p["description"]
        for rid in p.get("disabled_rules") or []:
            if rid not in rules: raise ValueError(f"profile {p['id']} references missing {rid}")
            E.SubElement(pe,q("select"),idref=rule_xid(rules[rid]),selected="false")

    for rid in b.get("rules") or []:
        r=rules[rid]
        attrs={"id":rule_xid(r),"severity":r.get("severity") or "unknown","weight":str(r.get("weight",1.0))}
        if r.get("role") is not None: attrs["role"]=str(r["role"])
        relem=E.SubElement(root,q("Rule"),**attrs)

        # XCCDF Rule version is publisher/STIG identity in this DISA profile.
        stig=next((x.get("value") for x in r.get("identifiers",[]) if x.get("scheme")=="disa-stig-id"),None)
        if stig: E.SubElement(relem,q("version")).text=stig
        E.SubElement(relem,q("title")).text=r.get("title")
        if r.get("discussion"):
            E.SubElement(relem,q("description")).text=r["discussion"]
        if r.get("rationale"):
            E.SubElement(relem,q("rationale")).text=r["rationale"]
        for cid in r.get("applicability") or []:
            E.SubElement(relem,q("platform"),idref=condition_ref(cid))

        for ident in r.get("identifiers",[]) or []:
            if ident.get("scheme")=="cci":
                ie=E.SubElement(relem,q("ident"),system="http://cyber.mil/cci")
                ie.text=str(ident["value"])

        guidance=(r.get("remediation") or {}).get("guidance")
        if guidance: E.SubElement(relem,q("fixtext")).text=guidance

        checks=r.get("checks") or {}
        for selector,assessment in checks.items():
            if selector=="automated" or (selector=="default" and str(assessment).endswith(".automated")):
                system=OVAL
            elif selector=="manual" or (selector=="default" and str(assessment).endswith(".manual")):
                system=OCIL
            else:
                raise ValueError(f"cannot infer check system for {rid}/{selector}: {assessment}")
            attrs={"system":system}
            if selector!="default": attrs["selector"]=selector
            ce=E.SubElement(relem,q("check"),**attrs)
            E.SubElement(ce,q("check-content-ref"),
                         href=f"urn:scap-ng:assessment:{assessment}",
                         name=str(assessment))

    tree=E.ElementTree(root)
    E.indent(tree,space="  ")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(str(a.output),encoding="UTF-8",xml_declaration=True,pretty_print=True)

if __name__=="__main__": main()
