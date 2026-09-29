#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixtures",type=Path,required=True)
    ap.add_argument("--repo-root",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parent
    failures=[]
    for fixture in sorted(args.fixtures.glob("*.json")):
        data=json.loads(fixture.read_text())
        src=data.get("source",{})
        if "local_path" not in src:
            print(f"SKIP semantic source comparison: {fixture.name} (synthetic fixture)")
            continue
        out=args.out/(fixture.stem+".xml")
        subprocess.run([sys.executable,str(root/"ng_to_oval.py"),str(fixture),"-o",str(out)],check=True)
        source=args.repo_root/src["local_path"]
        print(f"COMPARE {fixture.name}")
        cmd=[sys.executable,str(root/"compare_oval_semantics.py"),str(source),str(out),"--json"]
        if src.get("root_definition"):
            cmd.extend(["--source-root",src["root_definition"]])
        p=subprocess.run(cmd,text=True,capture_output=True)
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
