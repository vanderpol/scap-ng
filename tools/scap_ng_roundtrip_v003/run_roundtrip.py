#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixtures",type=Path,required=True)
    ap.add_argument("--scap-content",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parent
    failures=[]
    for fixture in sorted(args.fixtures.glob("*.json")):
        data=json.loads(fixture.read_text())
        src=data.get("source",{})
        if "path" not in src:
            print(f"SKIP semantic source comparison: {fixture.name} (synthetic fixture)")
            continue
        out=args.out/(fixture.stem+".xml")
        subprocess.run([sys.executable,str(root/"ng_to_oval.py"),str(fixture),"-o",str(out)],check=True)
        source=args.scap_content/src["path"]
        print(f"COMPARE {fixture.name}")
        p=subprocess.run([sys.executable,str(root/"compare_oval_semantics.py"),str(source),str(out),"--json"],
                         text=True,capture_output=True)
        print(p.stdout)
        if p.returncode:
            failures.append(fixture.name)
            if p.stderr: print(p.stderr,file=sys.stderr)
    if failures:
        print("Semantic mismatches: "+", ".join(failures),file=sys.stderr)
        return 1
    return 0
if __name__=="__main__":
    raise SystemExit(main())
