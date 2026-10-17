#!/usr/bin/env python3
"""#235: source-backed OVAL 5.12.3 Item creation modes in all 201 Test all_exist uses.

Research only. Collection behavior is not inferred from an Object name or a
source Test existence mode. Native behavior changes require conformance proof.
"""
import argparse, hashlib, json, zipfile
from pathlib import Path
from collections import Counter, defaultdict
import yaml
from research_04_all_exist_intent_census import PINNED, resolved_source

def modes(node):
    if not isinstance(node,(dict,list)):return []
    if isinstance(node,list):
        return [v for elem in node for v in modes(elem)]
    result=[]
    if "collect" in node and isinstance(node["collect"],dict):
        value=node["collect"].get("item_creation")
        if value is not None:result.append(str(value))
    for key,value in node.items():
        if key!="collect": result.extend(modes(value))
    return result

def audit(archive):
    sha=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if sha!=PINNED:raise ValueError("six-STIG archive does not match pinned digest")
    total=Counter()
    cap_modes=defaultdict(Counter)
    important=[]
    by_population=defaultdict(list)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError("corrupt source ZIP")
        for path in sorted(z.namelist()):
            if not(path.startswith("authoring/") and "/assessments/" in path and path.endswith(".yaml")):
                continue
            doc=(yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if doc.get("mode")!="automated" or not isinstance(doc.get("tests"),dict):
                continue
            for tid,test in doc["tests"].items():
                mode=test.get("collected_items_require")
                if not (mode=="all_exist" or isinstance(mode,str) and mode.startswith("all_exist_and_")):
                    continue
                obj,origin=resolved_source(doc,test)
                cap=test.get("capability") or "<missing>"
                choices=modes(obj)
                values=choices or ["<not specified>"]
                total["all_exist_tests"]+=1
                for v in values:
                    cap_modes[cap][v]+=1
                    total["item_creation:"+v]+=1
                if cap in {"windows.ntuser","independent.textfilecontent54",
                           "independent.xmlfilecontent"}:
                    row={"source":path,"test":tid,"check":test.get("test_title"),
                         "capability":cap,"collection":values,
                         "object_origin":origin,
                         "source_requirement":mode,
                         "selector_source":(str(obj)[:450] if isinstance(obj,dict) else repr(obj))}
                    by_population[f"{cap}: {','.join(values)}"].append(row)
                    if cap=="windows.ntuser":
                        important.append(row)
    if total["all_exist_tests"]!=201:raise AssertionError("source set is not the full 201")
    return {
        "status":"SOURCE CONTENT ITEM-CREATION CHOICES, NOT EVALUATED COLLECTION SEMANTICS",
        "source_sha256":sha,
        "counts":dict(total),
        "capability_item_creation_modes":{k:dict(v) for k,v in sorted(cap_modes.items())},
        "windows_ntuser_all_exist_tests":important,
        "examples_by_capability_and_behavior":{
            key:rows[:8] for key,rows in by_population.items()
        },
        "cautions":[
            "OVAL source behavior is not necessarily native Item identity policy.",
            "Many capabilities do not expose a named item_creation setting.",
            "A collection option that preserves existing file Items can change the tested Item population; it is not a safe blind rewrite of all_object_elements_fullfilled.",
            "The number of returned Items is different from the number of explicitly enumerated expected resource identities.",
            "Each absent/error/not_collected source outcome still requires six-state preservation.",
        ]
    }

def markdown(r):
    lines=["# Item creation choices inside the 201 Test-level all_exist cases",
           "","**Research only; no collector or authoring schema changed.**",
           "","The historical six-STIG Test existence choice and collection Item creation behavior are separate.",
           "","## Observed capability/behavior combinations","",
           "| Capability | Item creation behavior | Count |",
           "| --- | --- | ---: |"]
    for cap,ms in r["capability_item_creation_modes"].items():
        for mode,count in ms.items():
            lines.append(f"| `{cap}` | `{mode}` | {count} |")
    lines+=["","## Windows NTUSER source Tests", ""]
    for row in r["windows_ntuser_all_exist_tests"]:
        lines.append(f"- `{row['source']}` — {row['check']} — Item creation `{', '.join(row['collection'])}`")
    lines+=["","## Interpretation", "",
            "- `windows.ntuser`: creating an Item for an existing `ntuser.dat` even if its requested value is missing is conceptually sound, but it changes what Items are selected compared with key/name-only creation.",
            "- `independent.textfilecontent54`: `filepath_exists` and `all_object_elements_fullfilled` select different Item populations.",
            "- Under the proposed native rule, missing fields on a real resource are recorded as absent fields, rather than adding phantom missing Items.",
            "- Changing the Item creation choice during migration must be evaluated for both source Test results and the evidence it emits. An exact YAML roundtrip does not establish this.",
            "", "## Limits", ""]
    lines.extend("- "+x for x in r["cautions"])
    lines.append("")
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    a=p.parse_args()
    r=audit(a.archive)
    Path(a.json).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    Path(a.markdown).write_text(markdown(r))
    print(json.dumps({"counts":r["counts"],
                      "ntuser":r["windows_ntuser_all_exist_tests"],
                      "capability_mode":r["capability_item_creation_modes"]},indent=2))
