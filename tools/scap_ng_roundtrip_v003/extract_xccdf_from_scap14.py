#!/usr/bin/env python3
"""Extract the authoritative embedded XCCDF Benchmark from a SCAP 1.4 source ZIP."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from lxml import etree

TOOLS_DIR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS_DIR))
import scap14_rule_splitter as split

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_zip",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    _,_,root=split.find_datastream(a.source_zip)
    components,_=split.embedded_components(root)
    rows=[(cid,node) for cid,node in components.items() if split.component_kind(node)=="xccdf"]
    if len(rows)!=1:
        raise ValueError(f"expected exactly one XCCDF Benchmark component, found {len(rows)}")
    cid,node=rows[0]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(etree.tostring(node,encoding="UTF-8",xml_declaration=True,pretty_print=True))
    print(f"component={cid}")
    print(f"output={a.output}")

if __name__=="__main__":main()
