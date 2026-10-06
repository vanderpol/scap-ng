#!/usr/bin/env python3
import argparse, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

def local(tag):
    return tag.split("}",1)[-1] if isinstance(tag,str) else ""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",type=Path)
    ap.add_argument("--id",action="append",default=[])
    args=ap.parse_args()
    wanted=set(args.id)
    with zipfile.ZipFile(args.package) as z:
        for name in z.namelist():
            if not name.lower().endswith(".xml"): continue
            try: root=ET.fromstring(z.read(name))
            except ET.ParseError: continue
            found=[]
            for node in root.iter():
                if node.get("id") in wanted:
                    found.append(node)
            if found:
                print(f"===== {name} =====")
                for node in found:
                    print(ET.tostring(node,encoding="unicode"))
if __name__=="__main__":
    main()
