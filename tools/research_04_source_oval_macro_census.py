#!/usr/bin/env python3
"""Direct original OVAL 5.12.3 quantifier census across pinned NIWC source ZIPs.

No reliance on a historic NG authoring dialect. Retains source vs defaulted
attribute origin and distinguishes Tests from State entity fields.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

MACOS=re.compile(r"mac[_ .-]?os|macos|os[_-]?x|apple",re.I)
EXIST={
    "all_exist":"all",
    "at_least_one_exists":"one_or_more",
    "none_exist":"none",
    "only_one_exists":"one",
    "any_exist":"optional",
}
CHECK={
    "all":"all",
    "at least one":"one_or_more",
    "only one":"one",
    "none satisfy":"none",
}
NONSTANDARD={"sqlext"}


def local(tag):
    return tag.rsplit("}",1)[-1]


def family(tag):
    if not tag.startswith("{"):
        return "unknown"
    ns=tag[1:].split("}",1)[0]
    return ns.rsplit("#",1)[-1].rsplit("/",1)[-1]


def kind(source,capability):
    if MACOS.search(source):
        return "macos_atypical"
    if "shellcommand" in capability.lower():
        return "shell_command"
    if capability.startswith("independent.sqlext"):
        return "unsupported_sqlext"
    return "structured_other"


def test_pairs(node):
    existence=node.get("check_existence")
    existence_origin="source" if existence is not None else "schema_default"
    if existence is None:
        existence="at_least_one_exists"
    check=node.get("check")
    check_origin="source" if check is not None else "missing"
    # No implicit check default: the test/check attribute must be explicitly
    # accounted for, so an absent check remains an audit category.
    return existence,check,existence_origin,check_origin


def analyze_package(src:Path):
    counts=defaultdict(Counter)
    source_name=src.name
    tests_seen={}
    states_seen={}
    unmatched=[]
    source_docs=0
    parsed_xml=0
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:
            raise ValueError(f"ZIP failed CRC: {src.name}")
        for member in sorted(z.namelist()):
            if not member.lower().endswith(".xml"):
                continue
            raw=z.read(member)
            try:
                root=ET.fromstring(raw)
            except ET.ParseError:
                unmatched.append({"member":member,"issue":"XML parse failure"})
                continue
            parsed_xml+=1
            for doc in root.iter():
                if local(doc.tag)!="oval_definitions":
                    continue
                source_docs+=1
                children={local(x.tag):x for x in doc}
                t_section=children.get("tests")
                if t_section is not None:
                    for test in t_section:
                        if not local(test.tag).endswith("_test"):
                            continue
                        capability=family(test.tag)+"."+local(test.tag).removesuffix("_test")
                        identity=test.get("id") or "<unidentified>"
                        original=ET.tostring(test,encoding="utf-8")
                        key=(capability,identity)
                        fingerprint=hashlib.sha256(original).hexdigest()
                        if key in tests_seen and tests_seen[key]==fingerprint:
                            continue
                        if key in tests_seen and tests_seen[key]!=fingerprint:
                            unmatched.append({"identity":identity,"issue":"Test ID reused with different XML"})
                        tests_seen[key]=fingerprint
                        stratum=kind(source_name,capability)
                        c=counts[stratum]
                        c["tests"]+=1
                        c[f"capability:{capability}"]+=1
                        existence,match,e_origin,m_origin=test_pairs(test)
                        p=(EXIST.get(existence),CHECK.get(match))
                        if p[0] is None or p[1] is None:
                            c[f"unresolved_test_pair:{existence}/{match}"]+=1
                            continue
                        c[f"items_pair:{p[0]}/{p[1]}"]+=1
                        c[f"existence_origin:{e_origin}"]+=1
                        c[f"check_origin:{m_origin}"]+=1
                        if p==("one_or_more","all"):
                            c["item_common_all_match"]+=1
                        has_state_ref=any(local(child.tag)=="state" for child in test)
                        if not has_state_ref and p[0]=="none":
                            c["state_free_none_exist"]+=1
                            c[f"state_free_none_original_match:{p[1]}"]+=1
                        if not has_state_ref:
                            c["tests_no_state_ref"]+=1
                state_section=children.get("states")
                if state_section is not None:
                    for state in state_section:
                        if not local(state.tag).endswith("_state"):
                            continue
                        capability=family(state.tag)+"."+local(state.tag).removesuffix("_state")
                        identity=state.get("id") or "<unidentified>"
                        serialized=ET.tostring(state,encoding="utf-8")
                        key=(capability,identity)
                        fp=hashlib.sha256(serialized).hexdigest()
                        if key in states_seen and states_seen[key]==fp:
                            continue
                        if key in states_seen and states_seen[key]!=fp:
                            unmatched.append({"identity":identity,"issue":"State ID reused with different XML"})
                        states_seen[key]=fp
                        c=counts[kind(source_name,capability)]
                        c["states"]+=1
                        for entity in state:
                            if not isinstance(entity.tag,str):
                                continue
                            if local(entity.tag) in ("notes","metadata"):
                                continue
                            # State entity directly beneath State. Record fields
                            # nested within record-valued entities are different
                            # and not silently counted in this scope.
                            c["state_field_entities"]+=1
                            existence=entity.get("check_existence","at_least_one_exists")
                            match=entity.get("entity_check","all")
                            if "check_existence" not in entity:
                                c["entity_existence_origin:schema_default"]+=1
                            else:
                                c["entity_existence_origin:source"]+=1
                            if "entity_check" not in entity:
                                c["entity_check_origin:schema_default"]+=1
                            else:
                                c["entity_check_origin:source"]+=1
                            pair=(EXIST.get(existence),CHECK.get(match))
                            if None in pair:
                                c[f"unresolved_entity_pair:{existence}/{match}"]+=1
                                continue
                            c[f"field_pair:{pair[0]}/{pair[1]}"]+=1
                            if pair==("one_or_more","all"):
                                c["field_common_all_match"]+=1
    return {
        "source":source_name,
        "source_oval_documents":source_docs,
        "source_xml_files_parsed":parsed_xml,
        "distinct_source_test_identities":len(tests_seen),
        "distinct_source_state_identities":len(states_seen),
        "strata":{k:dict(v) for k,v in sorted(counts.items())},
        "warnings":unmatched[:35],
        "total_warnings":len(unmatched),
    }


def aggregate(packages:list[Path]):
    strata=defaultdict(Counter)
    per_package=[]
    for source in packages:
        r=analyze_package(source)
        per_package.append(r)
        for k,c in r["strata"].items():
            strata[k].update(c)
    total=Counter()
    for c in strata.values():
        total.update(c)
    strata["all_sources"]=total
    strata["primary_structured"]=Counter(strata.get("structured_other",{}))
    return {
        "format":"scap-ng-04-source-oval-quantifier-census-v1",
        "package_count":len(packages),
        "pin":"8c8e5dff860af6b1290ee9273a282db24278f8d5",
        "strata":{k:dict(v) for k,v in sorted(strata.items())},
        "per_package":per_package,
        "limitations":[
            "This is a direct source OVAL 5.12.3 Test and State-field entity census, not a runtime NG scanner result.",
            "Counts unique OVAL Test/State identities within each individual benchmark. Shared references are not duplicated within that package.",
            "Unspecified OVAL check_existence and State-entity entity_check use their documented effective defaults; missing Test.check is reported as unresolved.",
            "macOS and independent.shellcommand are excluded from primary structured rankings.",
            "Four known independent.sqlext packages are included in source accounting, but that test type is not an NG conversion success.",
            "Source-mapping names are the published OVAL test family, not claims that the current native converter on main passes all sources.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("sources",type=Path,help="Pinned NIWC Current directory")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    packages=sorted(x for x in args.sources.glob("*SCAP_1-4_Benchmark*.zip") if "Consolidated" not in x.name)
    if len(packages)!=65:
        raise SystemExit(f"Expected 65 source packages, got {len(packages)}")
    result=aggregate(packages)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_BENCHMARKS",result["package_count"])
    for k in ("primary_structured","shell_command","macos_atypical","unsupported_sqlext","all_sources"):
        c=result["strata"].get(k,{})
        print("SOURCE_STRATUM",k,"TESTS",c.get("tests",0),"STATES",c.get("states",0),
              "STATE_FIELDS",c.get("state_field_entities",0))
        for label in ("item_common_all_match","field_common_all_match",
                      "state_free_none_exist"):
            print(" ",label,c.get(label,0))
        for prefix in ("items_pair:","field_pair:","unresolved_test_pair:","unresolved_entity_pair:"):
            values=sorted(((name,n) for name,n in c.items() if name.startswith(prefix)),
                          key=lambda x:(-x[1],x[0]))
            print(" ",prefix,values[:18])
    print("WARNINGS",sum(x["total_warnings"] for x in result["per_package"]))
if __name__=="__main__":
    main()
