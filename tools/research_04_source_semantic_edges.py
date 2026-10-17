#!/usr/bin/env python3
"""Research #235: unusual original OVAL features beyond Test existence.

Six pinned NIWC-enhanced STIG packages, source OVAL IDs stratified by origin.
Each logical source element (id) counted once per STIG, not per XML reference.
No 65-package scan and no normative removals.
"""
from collections import Counter,defaultdict
from pathlib import Path
import argparse, json, xml.etree.ElementTree as ET, zipfile
from research_04_source_author_edge_census import STIGS, SOURCE_REVISION, local, original_author

def census(root):
    counts=Counter()
    examples=defaultdict(list)
    exceptional=defaultdict(list)
    version_conflicts=[]
    ids=defaultdict(dict)
    for stig,filename in STIGS.items():
        path=Path(root)/filename
        if not path.is_file():raise FileNotFoundError(path)
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise ValueError("source ZIP invalid: "+filename)
            for member in sorted(z.namelist()):
                if not member.lower().endswith(".xml"):continue
                try:xml=ET.fromstring(z.read(member))
                except ET.ParseError:continue
                for root_def in xml.iter():
                    if local(root_def.tag)!="oval_definitions":continue
                    for sect in root_def:
                        category=local(sect.tag)
                        if category not in {"definitions","tests","objects","states","variables"}:continue
                        for elm in sect:
                            eid=elm.get("id")
                            if not eid:continue
                            key=(stig,eid)
                            # Same ID must not be counted twice inside the same archive.
                            if key in ids[category]:
                                old=ids[category][key]
                                if old!=local(elm.tag):version_conflicts.append(eid)
                                continue
                            ids[category][key]=local(elm.tag)
                            author=original_author(eid)
                            counts[(author,category,"_elements_total")]+=1
                            def record(group,label):
                                counts[(author,group,label)]+=1
                                exkey=(author,group,label)
                                if len(examples[exkey])<4:
                                    examples[exkey].append({
                                      "id":eid,"type":local(elm.tag),
                                      "source_stig":stig,"source_xml":member,
                                      "comment":elm.get("comment","")[:170],
                                    })
                            if category=="tests":
                                record("test_check",elm.get("check","<absent>"))
                                if "check_existence" not in elm.attrib:
                                    record("test_existence_explicitness","default_unspecified")
                                else:record("test_existence_explicitness","explicit")
                                if local(elm.tag) in {"shellcommand_test","unknown_test"}:
                                    record("test_family",local(elm.tag))
                                if any(local(c.tag)=="state" for c in elm):
                                    record("test_state_reference","with_state")
                            elif category=="definitions":
                                for x in elm.iter():
                                    lx=local(x.tag)
                                    if lx=="criteria":
                                        record("criteria_operator",x.get("operator","AND (default)"))
                                    if lx=="extend_definition":
                                        record("definition_extension","extend_definition")
                                    if lx=="criterion" and x.get("negate","false").lower()=="true":
                                        record("definition_negation","negate")
                            elif category=="objects":
                                for x in elm.iter():
                                    lx=local(x.tag)
                                    if lx=="set":
                                        record("object_set",x.get("set_operator","UNION (default)"))
                                    if lx=="filter":
                                        record("object_filter",x.get("action","exclude (default)"))
                                    if lx=="behaviors":
                                        v=x.get("item_creation")
                                        if v is not None:record("item_creation_explicit",v)
                                    if x.get("var_ref"):
                                        record("object_variable_reference","var_ref")
                            elif category=="states":
                                for child in elm:
                                    if not isinstance(child.tag,str) or local(child.tag) in {"notes","metadata"}:
                                        continue
                                    for attribute in ("check","check_existence","entity_check","var_check","operation"):
                                        if attribute in child.attrib:
                                            val=child.get(attribute)
                                            record("state_"+attribute,val)
                                    if child.get("var_ref"):
                                        record("state_variable_reference","var_ref")
                            elif category=="variables":
                                kind=local(elm.tag)
                                record("variable_type",kind)
                                for x in elm.iter():
                                    lx=local(x.tag)
                                    if lx.endswith("_component") or lx in {"arithmetic","concat","split",
                                          "substring","time_difference","regex_capture","begin",
                                          "end","escape_regex","unique","count","glob_to_regex"}:
                                        record("variable_function",lx)
    if sum(v for (o,c,k),v in counts.items() if c=="tests" and k=="_elements_total")!=2140:
        raise AssertionError("Source Test count does not match authoritative source audit")
    # Convert tuple keys for JSON
    groups=defaultdict(lambda:defaultdict(dict))
    for (author,group,feature),n in counts.items():
        groups[author][group][feature]=n
    samples={}
    for key,data in examples.items():
        author,group,feature=key
        samples[f"{author}/{group}/{feature}"]=data
    return {
        "status":"SOURCE OVAL SEMANTIC EDGE INVENTORY; no claim of universal OVAL usage",
        "revision":SOURCE_REVISION,
        "counts_by_original_author":{author:dict(groups[author]) for author in sorted(groups)},
        "examples_by_origin_feature":samples,
        "duplicate_ID_tag_conflicts":version_conflicts[:30],
        "unit":"unique original OVAL element ID per source STIG archive (not per reference), grouped by original namespace",
        "cautions":[
            "The six selected STIG archives are not the full 65-benchmark corpus and not the OVAL Self-Assertion test suite.",
            "Native 0.4 authoring is a separate 1,375-Test population; do not equate source and native counts.",
            "All counts derive from original XML declared attributes and IDs; defaults are labeled only where inspected.",
            "A State entity's operation is counted at State-element occurrence level; a repeated attribute can count multiple times within one State.",
            "Low-use operators may have important security consequences; no support is removed by this census.",
        ]
    }

def markdown(d):
    lines=["# Non-cardinality edge cases in six original OVAL STIG streams",
           "", "**Research-only source inventory, no schema change.**",
           "",f"Source pinned to `niwc-atlantic/scap-content-library` at `{d['revision']}`.",
           "Element counts use original DISA and NIWC OVAL IDs and are unique per",
           "package, not de-duplicated across Linux packages that reuse an identical ID.",
           "", "## Distribution by author and feature family"]
    for origin,groups in d["counts_by_original_author"].items():
        lines+=["",f"### {origin}", ""]
        for group,attrs in sorted(groups.items()):
            if group in {"definitions","tests","objects","states","variables"}:continue
            lines.extend([f"**{group}**", "", "| Source feature | Instances |",
                          "| --- | ---: |"])
            for v,n in sorted(attrs.items(),key=lambda e:(-e[1],e[0])):
                lines.append(f"| `{v}` | {n} |")
            lines.append("")
    lines.extend(["", "## Interpretation and recommendation", "",
      "This inventory shows **usage, not necessity**. The native grammar should",
      "only expose a specialized keyword if a readable composition or typed capability",
      "cannot express the actual requirement correctly. Original Test/State/Set/Variable",
      "meaning remains an import conformance concern until equivalent lowering is proven.",
      "",
      "A zero or low count in these six STIGs does not justify dropping an OVAL 5.12.3",
      "feature from generic conversion: OVAL Self-Assertion and other benchmarks",
      "can exercise it. Conversely, a feature common in inherited DISA 1.3-origin",
      "content does not establish that it belongs in the new authoring vocabulary.",
      "", "## Limits", ""])
    lines.extend("- "+x for x in d["cautions"])
    lines.append("")
    return "\n".join(lines)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sources",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    a=p.parse_args()
    d=census(a.sources)
    Path(a.json).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    Path(a.markdown).write_text(markdown(d))
    print(json.dumps({"groups":{k:{g:len(v) for g,v in vv.items()}
                                 for k,vv in d["counts_by_original_author"].items()}},indent=2))
