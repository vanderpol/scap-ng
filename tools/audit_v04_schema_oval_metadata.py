#!/usr/bin/env python3
"""Audit SCAP-NG 0.4.0 JSON Schema annotations against pinned OVAL 5.12.3 XSD.

Supply checked-out OVAL 5.12.3 XSD paths explicitly; no unpinned network reads.
Outputs gaps rather than inventing missing schema descriptions.
"""
import argparse, collections, json, pathlib, xml.etree.ElementTree as ET
XSD="{http://www.w3.org/2001/XMLSchema}"
SCHEMA_NAMES=("assessment-language.schema.json","assessment.schema.json","capability-common.schema.json")
TYPES=("OperationEnumeration","CheckEnumeration","ExistenceEnumeration","OperatorEnumeration")
def get_enums(path):
    root=ET.parse(path).getroot()
    found={}
    for node in root.iter(XSD+"simpleType"):
        name=node.get("name")
        if name not in TYPES:continue
        docs=[" ".join(n.itertext()).strip() for n in node.iter(XSD+"documentation")]
        names=[n.get("value") for n in node.iter(XSD+"enumeration")]
        found[name]={"description":" ".join(docs),"values":names}
    missing=set(TYPES)-set(found)
    if missing:raise ValueError(f"OVAL types missing: {sorted(missing)}")
    return found
def walk(node,path=()):
    if isinstance(node,list):
        for i,x in enumerate(node):yield from walk(x,path+(str(i),))
    elif isinstance(node,dict):
        if "properties" in node and isinstance(node["properties"],dict):
            for k,v in node["properties"].items():
                if isinstance(v,dict) and not k.startswith("$"):
                    yield path+("properties",k),v
        for k,v in node.items():yield from walk(v,path+(k,))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--oval-common",type=pathlib.Path,required=True)
    ap.add_argument("--schema-dir",type=pathlib.Path,default=pathlib.Path("schema/v0.4.0"))
    ap.add_argument("--report",type=pathlib.Path,required=True)
    args=ap.parse_args()
    oval=get_enums(args.oval_common)
    report={"oval_version":"5.12.3","oval_common_types":oval,"schema_counts":{},"annotation_gaps":{}}
    for file in SCHEMA_NAMES:
        d=json.loads((args.schema_dir/file).read_text())
        paths=list(walk(d))
        misses=[{"path":".".join(k),"missing":[v for v in ("title","description") if not x.get(v)]} for k,x in paths if not x.get("title") or not x.get("description")]
        report["schema_counts"][file]={"property_sites":len(paths),"annotation_gaps":len(misses)}
        report["annotation_gaps"][file]=misses
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report["schema_counts"],indent=2))
    if not oval["OperationEnumeration"]["values"]:raise ValueError("Official OVAL enum has no values")
if __name__=="__main__":main()
