#!/usr/bin/env python3
"""Preserve every OVAL XSD annotation in scanner-guide source archives.

Input: a checked-out, version-pinned OVAL schema directory. The output never
changes SCAP-NG authoring JSON Schemas. No upstream annotations are discarded.
"""
import argparse, hashlib, json, pathlib, re, xml.etree.ElementTree as ET
X="{http://www.w3.org/2001/XMLSchema}"
def extract_file(path, root):
    data=path.read_bytes()
    tree=ET.fromstring(data)
    out=[]
    def walk(node, ancestors):
        name=node.attrib.get("name") or node.attrib.get("ref") or node.tag.removeprefix(X)
        current=ancestors+[name]
        for child in node:
            if child.tag==X+"annotation":
                docs=["".join(d.itertext()).strip() for d in child if d.tag in (X+"documentation",X+"appinfo")]
                docs=[x for x in docs if x]
                if docs:
                    out.append({"xml_path":"/".join(current),"documentation":docs})
            else:walk(child,current)
    walk(tree,[])
    return {"source":str(path.relative_to(root)),"sha256":hashlib.sha256(data).hexdigest(),
            "annotation_count":len(out),"annotations":out}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--oval-xsd-dir",type=pathlib.Path,required=True)
    p.add_argument("--output-dir",type=pathlib.Path,required=True)
    p.add_argument("--tag",default="v5.12.3")
    a=p.parse_args()
    if a.tag!="v5.12.3":raise ValueError("Version must be explicitly reviewed before changing")
    paths=sorted(a.oval_xsd_dir.rglob("*.xsd"))
    if not paths:raise SystemExit("No OVAL XSD input; nothing archived")
    a.output_dir.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for path in paths:
        record=extract_file(path,a.oval_xsd_dir)
        dest=a.output_dir/(path.name+".annotations.json")
        dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
        manifest.append({"source":record["source"],"sha256":record["sha256"],
                         "annotation_count":record["annotation_count"],"archive":dest.name})
    (a.output_dir/"manifest.json").write_text(json.dumps({"pinned_oval_tag":a.tag,
       "source_files":len(paths),"total_annotations":sum(x["annotation_count"] for x in manifest),
       "files":manifest},indent=2)+"\n")
    print(f"Preserved {sum(x['annotation_count'] for x in manifest)} annotation records across {len(paths)} XSD files.")
if __name__=="__main__":main()
