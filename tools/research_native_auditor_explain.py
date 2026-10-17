#!/usr/bin/env python3
"""#235 deterministic auditor-readable rendering of the real native AST.

Generates ONE human explanation from the same compiled structure evaluated by
research_native_contract_evaluator.py. No AI-written second source of truth,
no runtime scan and no assertion of source/Oval/SCAP 1.4 equivalence.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from research_native_contract_candidate import EXAMPLES,read

NAMES={
  "linux.mounts":"Linux mount",
  "linux.textfile_matches":"Linux text-file regex match",
  "windows.accounts":"Windows account",
  "windows.registry_value":"Windows registry value",
  "windows.computer_role":"Windows computer role",
  "windows.user_rights":"Windows user-right assignment",
  "apache.config_directives":"Apache configuration directive observation",
  "windows.dns.zones":"Windows DNS zone",
  "linux.files_from_account_homes":"Linux file collected from selected account homes",
  "$zone.zone_signing_keys":"zone-signing key belonging to the same DNS zone",
  "$zone.key_signing_keys":"key-signing key belonging to the same DNS zone"
}
PRETTY={
  "mount_point":"mount point",
  "mount_options":"mount options",
  "directory_integration":"directory integration",
  "raw_value":"raw directive value",
  "validity_hours":"validity (hours)",
  "mode":"POSIX mode bits",
  "principal":"principal",
  "signed":"signed",
  "category":"category",
}
def value(v):
    if isinstance(v,bool):return "true" if v else "false"
    if isinstance(v,list):return ", ".join(value(x) for x in v)
    return str(v)

def pred(p):
    name=PRETTY.get(p["field"],p["field"].replace("_"," "))
    op=p["operator"]
    wanted=value(p["value"])
    if op=="equals":return name+" equals "+wanted
    if op=="not_equals":return name+" does not equal "+wanted
    if op=="contains":return name+" contains "+wanted
    if op=="between":return name+" is between "+wanted.replace(", "," and ")
    if op=="at_least":return name+" is at least "+wanted
    if op=="matches_regex":return name+" matches the exact authored regex "+wanted
    if op=="only_these_bits":return name+" contains only bits allowed by octal "+wanted
    return name+" "+op+" "+wanted

def explain(ast,indent=0):
    prefix="  "*indent
    kind=ast["kind"]
    if kind=="logic":
        beginning="ALL of these conditions must hold:" if ast["operator"]=="all" else "AT LEAST ONE of these alternatives must hold:"
        lines=[prefix+beginning]
        for node in ast["children"]:
            child=explain(node,indent+1)
            lines.extend(child)
        return lines
    if kind=="fields":
        return [prefix+"- "+", and ".join(map(pred,ast["predicates"]))]
    if kind!="collection":raise ValueError("unknown AST")
    name=NAMES.get(ast["provider"],ast["provider"])
    who="The uniquely identified "+name if ast["singleton"] else "Every selected "+name
    if ast.get("exists_only") and ast["provider"]=="linux.textfile_matches":
        who="At least one matching passage must exist in "+ast["using"]["path"]
    elif ast.get("exists_only"):who="At least one "+name
    elif ast["mode"]=="some":who="At least one selected "+name
    if ast["mode"]=="none":who="No selected "+name+" may exist"
    if ast["mode"]=="exactly_one" and not ast["singleton"]:
        who="Exactly one selected "+name
    if ast["where"]:
        who+=" whose "+", and ".join(map(pred,ast["where"]))
    if ast.get("exists_only") and ast["provider"]!="linux.textfile_matches":
        who+=" must exist."
    if ast["using"]:
        using=", ".join(str(k)+"="+value(v) for k,v in sorted(ast["using"].items()))
        who+=" (provider inputs: "+using+")"
    lines=[prefix+"- "+who]
    if ast["mode"]=="each":
        if ast["min_count"]:
            minimum="one" if ast["min_count"]==1 else str(ast["min_count"])
            lines.append(prefix+"  At least "+minimum+
                         " matching resource must exist in this selected population." if ast["min_count"]==1
                         else prefix+"  At least "+minimum+
                         " matching resources must exist in this selected population.")
        else:
            lines.append(prefix+"  No matching resource is required to exist if selection is confirmed complete.")
    if ast.get("nested") is not None:
        lines.extend(explain(ast["nested"],indent+1))
    elif ast["predicates"]:
        lines.append(prefix+"  Required: "+", and ".join(map(pred,ast["predicates"])))
    return lines

def render(doc):
    lines=["# Native auditor explanation: "+doc["title"],"",
           "**Research-only compiled policy.** This is a deterministic explanation",
           "of the same AST used by fixture tests, not separate executable prose.","",
           "## What must be true",""]
    lines.extend(explain(doc["ast"]))
    lines.extend(["","## Evidence and status rules","",
      "Resource counts refer to fully selected resource Items, not only Items that passed.",
      "Confirmed complete-empty, incomplete/unknown selection, unreadable fields and",
      "acquisition errors are distinct. A proven violation can be decisive even",
      "when other evidence is incomplete. Named singleton resources must be",
      "uniquely identified by their provider contract; duplicate candidates",
      "are a provider error, not a convenient selection of one passing record.",
      "Nested key/file evidence is scoped to the parent Item and requires its",
      "own explicit completeness and identity status.","",
      "**Source-conversion boundary:** Nothing here proves that this native",
      "policy reproduces an original SCAP 1.4 / OVAL assessment.",""])
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",default="")
    args=parser.parse_args()
    for sample in sorted(EXAMPLES.glob("*.yaml")):
        doc=read(sample)
        report=render(doc)
        if args.output_dir:
            target=Path(args.output_dir)/(sample.stem+".md")
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(report)
            print(target)
        else:
            print(report)

if __name__=="__main__":main()
