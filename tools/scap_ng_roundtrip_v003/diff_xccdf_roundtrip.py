#!/usr/bin/env python3
"""Create canonical/normalized XCCDF diffs for benchmark round-trip review."""
from __future__ import annotations
import argparse,difflib,re
from pathlib import Path
from lxml import etree as E

X="http://checklists.nist.gov/xccdf/1.2"

def parse(p):
    return E.parse(str(p),E.XMLParser(remove_blank_text=True,remove_comments=False))

def c14n_lines(tree):
    return E.tostring(tree,method="c14n",with_comments=True).decode().splitlines()

def local(tag):
    return E.QName(tag).localname if isinstance(tag,str) else ""

def strip_noise(tree):
    root=tree.getroot()

    # signatures and TestResults are packaging/run artifacts, not policy semantics.
    for e in list(root.iter()):
        if local(e.tag) in {"signature","TestResult"}:
            p=e.getparent()
            if p is not None:p.remove(e)

    # Normalize benchmark/rule/profile/group IDs to readable suffixes where
    # possible. Exact legacy namespaces are serialization/provenance, not policy.
    idmap={}
    def canon(v):
        if v in idmap:return idmap[v]
        out=v
        patterns=[
            (r".*_rule_(SV-\d+)(r\d+)_rule$",lambda m:f"rule:{m.group(1)}:{m.group(2)}"),
            (r".*_profile_(.+)$",lambda m:f"profile:{m.group(1)}"),
            (r".*_group_(V-\d+)$",lambda m:f"group:{m.group(1)}"),
        ]
        for pat,fn in patterns:
            m=re.match(pat,v or "")
            if m:
                out=fn(m);break
        idmap[v]=out;return out

    # First declarations then idrefs.
    for e in root.iter():
        if "id" in e.attrib:e.attrib["id"]=canon(e.attrib["id"])
    for e in root.iter():
        for a in ("idref","extends"):
            if a in e.attrib:e.attrib[a]=canon(e.attrib[a])

    # Remove purely presentational comments/metadata timestamps from the review
    # diff only. The fidelity auditor checks preserved benchmark metadata.
    for e in root.xpath("//comment()"):
        e.getparent().remove(e)

    return tree

def diff(a,b,fa,fb):
    return "\n".join(difflib.unified_diff(a,b,fromfile=fa,tofile=fb,lineterm=""))+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("regenerated",type=Path)
    ap.add_argument("--out-dir",type=Path,required=True)
    a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)

    raw=diff(c14n_lines(parse(a.source)),c14n_lines(parse(a.regenerated)),
             "source-xccdf-c14n.xml","regenerated-xccdf-c14n.xml")
    (a.out_dir/"raw-c14n.diff").write_text(raw,encoding="utf-8")

    sa=strip_noise(parse(a.source)); sb=strip_noise(parse(a.regenerated))
    spa=E.tostring(sa,pretty_print=True,encoding="unicode")
    spb=E.tostring(sb,pretty_print=True,encoding="unicode")
    (a.out_dir/"source-normalized.xml").write_text(spa,encoding="utf-8")
    (a.out_dir/"regenerated-normalized.xml").write_text(spb,encoding="utf-8")
    nd=diff(spa.splitlines(),spb.splitlines(),"source-normalized.xml","regenerated-normalized.xml")
    (a.out_dir/"normalized-structural.diff").write_text(nd,encoding="utf-8")
    print(f"raw_diff_lines={len(raw.splitlines())}")
    print(f"normalized_diff_lines={len(nd.splitlines())}")

if __name__=="__main__":main()
