#!/usr/bin/env python3
"""#245 Verify permanently published C examples equal pinned full-corpus output.

A syntactically pleasing example must not quietly drift from the source-backed
C compiler's original-Oval-to-A-checked result. This is a publication integrity
gate, not a scanner test or a guarantee that all OVAL features are converted.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys
import yaml

NAME=re.compile(r"^[a-z][a-z0-9-]*\.research\.yaml$")
HEADER_FILE=re.compile(r"^# Original: (.+)$",re.M)
HEADER_DEF=re.compile(r"^# Definition: (oval:[a-zA-Z0-9_.-]+:def:[a-zA-Z0-9_.-]+)$",re.M)
HEADER_PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"

def _strict_yaml(txt):
    class Strict(yaml.SafeLoader): pass
    def reject_duplicate(loader,node):
        result={}
        for key_node,val_node in node.value:
            k=loader.construct_object(key_node)
            if not isinstance(k,str) or k in result:
                raise ValueError("duplicate or non-text YAML mapping key")
            result[k]=loader.construct_object(val_node)
        return result
    Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,reject_duplicate)
    values=list(yaml.load_all(txt,Loader=Strict))
    if len(values)!=1 or not isinstance(values[0],dict):
        raise ValueError("single YAML C authoring document required")
    return values[0]

def compare_published(published,generated,manifest):
    import json
    table=json.loads(Path(manifest).read_text(encoding="utf-8"))
    if table.get("stage")!="SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY":
        raise ValueError("untrusted original OVAL converter manifest")
    index={(e["file"],e["definition_id"]):e for e in table["native_C_converted"]}
    if len(index)!=len(table["native_C_converted"]):
        raise ValueError("duplicated source identity in C manifest")
    files=sorted(Path(published).glob("*.research.yaml"))
    if len(files)!=8:
        raise ValueError("expected exactly eight published verified original C examples")
    found=set()
    for path in files:
        if not NAME.fullmatch(path.name):
            raise ValueError("ambiguous published example filename")
        text=path.read_text(encoding="utf-8")
        src=HEADER_FILE.search(text)
        ident=HEADER_DEF.search(text)
        if not src or not ident or HEADER_PIN not in text:
            raise ValueError("missing original source identity or pin: "+path.name)
        key=(src.group(1),ident.group(1))
        if key not in index or key in found:
            raise ValueError("original source C conversion not found or duplicated")
        found.add(key)
        source_path=Path(generated)/index[key]["c_source"]
        if _strict_yaml(text)!=_strict_yaml(source_path.read_text(encoding="utf-8")):
            raise ValueError("published C representation drifted from source compiler: "+path.name)
    if len(found)!=8:
        raise ValueError("published sample coverage is not eight source Definitions")
    return {"verified_published_C_examples":8,
            "original_source_revision":HEADER_PIN,
            "generated_native_C_Definitions":table["native_C_Definitions"],
            "scanner_parity_proven":False}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--published",type=Path,required=True)
    ap.add_argument("--generated",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    args=ap.parse_args(argv)
    print(compare_published(args.published,args.generated,args.manifest))
    return 0

if __name__=="__main__":
    sys.exit(main())
