#!/usr/bin/env python3
"""#235: trace one native none_exist+State contradiction back to original OVAL.

Original six NIWC enhanced STIG ZIPs, original Test IDs, object and State
references. No converter change or silently deleted condition.
"""
import argparse, json, xml.etree.ElementTree as ET, zipfile
from pathlib import Path
from research_04_source_author_edge_census import STIGS, SOURCE_REVISION, local, original_author

def scan(root):
    matches=[]
    all_none_with_states=[]
    for stig,name in STIGS.items():
        path=Path(root)/name
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise ValueError("source STIG zip corrupt")
            for member in z.namelist():
                if not member.endswith(".xml"):continue
                try:doc=ET.fromstring(z.read(member))
                except ET.ParseError:continue
                for oval in doc.iter():
                    if local(oval.tag)!="oval_definitions":continue
                    parents={local(x.tag):x for x in oval}
                    tests=parents.get("tests")
                    objs=parents.get("objects")
                    states=parents.get("states")
                    if tests is None or objs is None:continue
                    object_map={o.get("id"):o for o in objs if o.get("id")}
                    state_map={v.get("id"):v for v in states} if states is not None else {}
                    for test in tests:
                        if not local(test.tag).endswith("_test"):continue
                        test_id=test.get("id") or ""
                        object_refs=[x.get("object_ref") for x in test
                                     if local(x.tag)=="object" and x.get("object_ref")]
                        state_refs=[x.get("state_ref") for x in test
                                    if local(x.tag)=="state" and x.get("state_ref")]
                        comment=test.get("comment","")
                        object_snippets=[ET.tostring(object_map[o],encoding="unicode")
                                         if o in object_map else "" for o in object_refs]
                        object_text=" ".join(object_snippets).lower()
                        # Match by actual OVAL pattern path or the distinctive
                        # rule intent, not by normalized SCAP-NG filename.
                        boot_obj=("/etc/grub2.cfg" in object_text and
                                  ("superusers" in object_text or "admin" in object_text))
                        boot_comment=("boot" in comment.lower() and
                                      ("admin" in comment.lower() or "superuser" in comment.lower()))
                        payload={
                            "stig":stig,"original_oval_xml":member,
                            "test_id":test_id,"test_author":original_author(test_id),
                            "test_type":local(test.tag),
                            "comment":comment,
                            "check_existence":test.get("check_existence","<implicit default>"),
                            "check":test.get("check","<implicit default>"),
                            "state_refs":state_refs,
                            "state_xml":[ET.tostring(state_map[a],encoding="unicode")[:2500]
                                         for a in state_refs if a in state_map],
                            "object_refs":object_refs,
                            "object_xml":[s[:3200] for s in object_snippets],
                        }
                        if test.get("check_existence")=="none_exist" and state_refs:
                            all_none_with_states.append({
                               **{k:payload[k] for k in ("stig","original_oval_xml",
                                  "test_id","test_author","test_type","comment",
                                  "check_existence","check","state_refs","object_refs")},
                               "matching_boot_rule":boot_obj or boot_comment})
                        if boot_obj or boot_comment:
                            payload["matched_by"]="object selector" if boot_obj else "test comment"
                            matches.append(payload)
    return {
      "status":"DIRECT ORIGINAL OVAL SOURCE INVESTIGATION — no source modifications",
      "source_revision":SOURCE_REVISION,
      "matching_original_bootloader_tests":matches,
      "source_tests_with_none_exist_and_state":all_none_with_states,
      "counts":{
          "boot_rule_matches":len(matches),
          "explicit_none_exist_plus_state":len(all_none_with_states),
          "matched_boot_none_exist_state":sum(x["check_existence"]=="none_exist" and bool(x["state_refs"]) for x in matches)
      },
      "interpretation_limits":[
         "The original OVAL XML is direct evidence about original Test/State shape.",
         "A source-to-native identity join is still needed to prove which original Test maps to the exact native ID.",
         "Other original Test instances may be omitted from the curated native authoring set.",
         "If original source includes none_exist plus a State, the source itself uses a form prohibited by OVAL 5.12.3 Schematron; migration must error or explicitly resolve with a reviewed equivalence proof.",
         "If original source omits a State but native has one, inspect the converter for accidental State attachment.",
      ]
    }

def md(r):
    lines=["# Bootloader none_exist + State: original OVAL investigation", "",
       "**Research only.** Pinned original NIWC-enhanced SCAP 1.4 ZIPs. No source or normative 0.4 change.",
       "",
       "## Counts","",
       f"- Original bootloader candidate Tests: **{r['counts']['boot_rule_matches']}**",
       f"- Original OVAL Tests with explicit `none_exist` + State: **{r['counts']['explicit_none_exist_plus_state']}**",
       f"- Bootloader candidates using that combination: **{r['counts']['matched_boot_none_exist_state']}**",
       "",
       "## Original source candidates",""]
    for x in r["matching_original_bootloader_tests"]:
        lines.extend([
          f"### `{x['test_id']}` ({x['stig']})","",
          f"- Original author namespace: `{x['test_author']}`",
          f"- Test existence: `{x['check_existence']}`; match: `{x['check']}`",
          f"- Comment: {x['comment']}",
          f"- Referenced Objects: `{', '.join(x['object_refs'])}`",
          f"- Referenced States: `{', '.join(x['state_refs']) or '(none)'}`",
          f"- Located via: {x['matched_by']}",""])
    lines+=["", "## Required disposition", "",
      "Compare the original Test/State references to the single native 0.4",
      "`verify-boot-loader-root-admin-adminstrator` Assessment and test both",
      "complete zero Items and incomplete/error outcomes. Do not silently erase",
      "a State, turn `none_exist` into `none match`, or claim 100% conversion.",
      "", "## Limitations", ""]
    lines.extend("- "+x for x in r["interpretation_limits"])
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sources",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    args=p.parse_args()
    obj=scan(args.sources)
    Path(args.json).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    Path(args.markdown).write_text(md(obj))
    print(json.dumps(obj["counts"],indent=2))
