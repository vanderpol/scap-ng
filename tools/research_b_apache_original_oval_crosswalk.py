#!/usr/bin/env python3
"""#237: exact source XML vs converted 0.3 Apache SV-214268 lexical crosswalk.

This checks graph/attribute preservation from ORIGINAL OVAL 5.12.3 XML to
converted-source YAML and source variable operation fixtures. It is neither
a full SCAP 1.4 converter nor a runtime differential equality proof.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

from research_b_variable_value_ops import capture,merge,values

ROOT=Path(__file__).resolve().parents[1]
XML=ROOT/("research/assessment-simplification/evidence/"
          "apache_server_2-4_unix_server/SV-214268/source-oval.xml")
YAML=ROOT/("research/requirements-first-language/contract-candidate/"
           "corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")
NAMESPACE="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OVAL_COMMON="http://oval.mitre.org/XMLSchema/oval-common-5"


def _node(name):
    return "{"+NAMESPACE+"}"+name


def crosswalk(xml_bytes,converted):
    xml_root=ET.fromstring(xml_bytes)
    if xml_root.tag!=_node("oval_definitions"):
        raise ValueError("original OVAL XML root is invalid")
    v=xml_root.find(".//{"+OVAL_COMMON+"}schema_version")
    if v is None or v.text!="5.12.3":
        raise ValueError("original OVAL XML must explicitly be 5.12.3")
    a=converted.get("assessment")
    if not isinstance(a,dict) or a.get("id")!="SV-214268.automated":
        raise ValueError("source converted Apache Assessment identity differs")
    tests=a.get("tests")
    vtab=a.get("variables")
    if not isinstance(tests,dict) or not isinstance(vtab,dict):
        raise ValueError("converted Assessment missing Test/Variable tables")
    original_vars=xml_root.findall(".//"+_node("local_variable"))
    if len(original_vars)!=19 or len(vtab)!=19:
        raise ValueError("original/conversion 19-source-Variable closure mismatch")
    criteria=xml_root.findall(".//"+_node("definition")+"/"+_node("criteria")+"/"+_node("criterion"))
    if len(criteria)!=5 or len(tests)!=5:
        raise ValueError("original and converted source 5-Test criteria mismatch")
    if not isinstance(a.get("evaluate"),dict) or set(a["evaluate"])!={"all"} or (
            len(a["evaluate"]["all"])!=5):
        raise ValueError("converted Boolean root no longer references five Tests")
    referenced=[e.get("test") for e in a["evaluate"]["all"]]
    if len(set(referenced))!=5 or set(referenced)!=set(tests):
        raise ValueError("converted Test closure omits/duplicates a branch")
    by_comment={v.get("comment"):v for v in original_vars}
    original_regex=by_comment["Apache base install directories (unix)"].find(_node("regex_capture"))
    if original_regex is None:
        raise ValueError("original Apache source regex_capture missing")
    original_pattern=original_regex.get("pattern")
    converted_regex=vtab["apache-base-install-directories-unix-variable"][
        "expression"]["regex_capture"]["pattern"]
    if original_pattern!=converted_regex:
        raise ValueError("original source regex_capture pattern changed in conversion")
    cases=[
        ("merged included conf files from Include refernces in httd.conf",
         "merged-included-conf-files-from-include-refernces-in-httd-conf-variable",
         "21426841"),
        ("Merged list of all loaded config files",
         "merged-list-all-loaded-config-files-variable",
         "21426851"),
    ]
    merge_rows=[]
    for comment,source_name,reference in cases:
        original=by_comment[comment].find(_node("merge"))
        if original is None:
            raise ValueError("original Apache merge operator not found")
        source=vtab[source_name]["expression"]["merge"]
        expected={
            "delimiter":original.get("delimiter",""),
            "sort":original.get("sort","document"),
            "order":original.get("order","ascending"),
        }
        actual={k:source.get(k) for k in expected}
        if expected!=actual:
            raise ValueError("converted Apache merge attributes diverge from original XML")
        ref=original.find(_node("variable_component"))
        if ref is None or not ref.get("var_ref","").endswith(":"+reference):
            raise ValueError("original OVAL merge Variable reference changed")
        merge_rows.append({
            "source_local_variable_id":by_comment[comment].get("id"),
            "converted_variable":source_name,
            "source_dependency_id":ref.get("var_ref"),
            "literal_attributes_agree":True,
            "attributes":expected,
        })
    return {
        "format":"scap-ng-b-apache-original-oval-crosswalk/0.1",
        "rule_id":"SV-214268",
        "source_oval_schema":"5.12.3",
        "original_source_xml_sha256":sha256(xml_bytes).hexdigest(),
        "source_test_count":len(criteria),
        "source_variable_count":len(original_vars),
        "converted_variable_count":len(vtab),
        "original_regex_capture_pattern":original_pattern,
        "regex_pattern_preserved":True,
        "merge_rows":merge_rows,
        "merge_is_native_OVAL_5_12_3":True,
        "source_graph_structural_parity_for_checked_fields":True,
        "original_OVAL_result_parity_verified":False,
        "source_System_Characteristics_item_order_verified":False,
        "scanner_executable":False,
    }


def main():
    doc=yaml.safe_load(YAML.read_text())
    result=crosswalk(XML.read_bytes(),doc)
    out=ROOT/"research/requirements-first-language/contract-candidate/corpus/apache-original-oval-crosswalk.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"rule":result["rule_id"],"merge":len(result["merge_rows"]),
                      "source_lexical_crosswalk":True,
                      "scanner_parity":False},sort_keys=True))


if __name__=="__main__":
    main()
