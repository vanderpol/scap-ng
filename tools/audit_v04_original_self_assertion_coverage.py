#!/usr/bin/env python3
"""Account for *every* pinned OVAL Self-Assertion source before 0.4 conversion.

Reads original SCAP_1.4/OVAL_Test_Content XML only. This is an inventory and
release-gate denominator, NOT successful conversion, back-export or scanner
conformance. A later actual v0.4 importer/exporter must join the exact source
(file, Definition ID) identities, never drop unsupported cases.

Refs #248 #229.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
OVAL_NS="http://oval.mitre.org/XMLSchema/oval-definitions-5"
EXPECTED={"files":144,"definitions":167,"tests":785}
BLOCKERS={
    ("ios/ios-def_version55_test.xml",
     "oval:navy.navwar.niwcatlantic.scc.ios:def:1"):"deprecated_oval_test",
    ("junos/junos-def_xml_config_test.xml",
     "oval:org.joval.junos.test:def:1"):"deprecated_oval_test",
    ("macos/ind-def_environmentvariable58_test_mac.xml",
     "oval:navy.navwar.niwcatlantic.scc.test:def:1"):"var_ref_datatype_mismatch",
    ("solaris/sol-def_package511_test.xml",
     "oval:navy.navwar.niwcatlantic.scc.test:def:1"):"var_ref_datatype_mismatch",
    ("windows/win-def_wuaupdatesearcher_test.xml",
     "oval:navy.navwar.niwcatlantic.scc.windows.update:def:1"):"var_ref_datatype_mismatch",
}


def local(tag):
    return tag.rsplit("}",1)[-1]


def children(parent,name):
    target=parent.find("{"+OVAL_NS+"}"+name)
    return list(target) if target is not None else []


def audit(corpus,*,assert_pinned=False):
    paths=sorted(corpus.rglob("*.xml"))
    files=[]
    rows=[]
    total_tests=0
    capability=Counter()
    features=Counter()
    actual_blockers=set()
    for path in paths:
        name=path.relative_to(corpus).as_posix()
        raw=path.read_bytes()
        root=ET.fromstring(raw)
        if root.tag!="{"+OVAL_NS+"}oval_definitions":
            raise ValueError(name+": not an OVAL Definitions source document")
        definitions=children(root,"definitions")
        tests=children(root,"tests")
        objects=children(root,"objects")
        states=children(root,"states")
        variables=children(root,"variables")
        if len({d.get("id") for d in definitions})!=len(definitions):
            raise ValueError(name+": duplicate original Definition IDs")
        if len({t.get("id") for t in tests})!=len(tests):
            raise ValueError(name+": duplicate original Test IDs")
        for section,label in ((definitions,"Definition"),(tests,"Test"),
                               (objects,"Object"),(states,"State"),(variables,"Variable")):
            if any(not isinstance(node.get("id"),str) or not node.get("id")
                   for node in section):
                raise ValueError(name+": missing source "+label+" ID")
        file_features=Counter()
        for node in root.iter():
            tag=local(node.tag)
            if tag=="set":
                file_features["set"]+=1
            elif tag=="filter":
                file_features["filter_"+node.get("action","exclude")]+=1
            elif tag.endswith("_variable"):
                file_features[tag]+=1
            elif tag=="object_component":
                file_features["object_component"]+=1
            elif tag=="variable_component":
                file_features["variable_component"]+=1
            elif tag=="field":
                file_features["record_field"]+=1
            elif tag=="extend_definition":
                file_features["extend_definition"]+=1
        features.update(file_features)
        test_features={}
        for test in tests:
            family=test.tag[1:].split("}",1)[0].split("#")[-1]
            kind=local(test.tag)
            capability[f"{family}.{kind.removesuffix('_test')}"]+=1
            test_features[test.get("id")]={"capability":f"{family}.{kind.removesuffix('_test')}",
                 "check":test.get("check"),"check_existence":test.get("check_existence")}
        total_tests+=len(tests)
        files.append({"file":name,"original_sha256":sha256(raw).hexdigest(),
                      "definitions":len(definitions),"tests":len(tests),
                      "objects":len(objects),"states":len(states),
                      "variables":len(variables),"features":dict(sorted(file_features.items()))})
        for definition in definitions:
            did=definition.get("id")
            key=(name,did)
            known_blocker=BLOCKERS.get(key)
            if known_blocker:
                actual_blockers.add(key)
            direct_tests=sorted({
                node.get("test_ref") for node in definition.iter()
                if local(node.tag)=="criterion" and node.get("test_ref")
            })
            for test_ref in direct_tests:
                if test_ref not in test_features:
                    raise ValueError(name+": Definition references unknown Test "+test_ref)
            rows.append({
                "source_file":name,"source_file_sha256":sha256(raw).hexdigest(),
                "source_definition_id":did,
                "referenced_tests":direct_tests,
                "test_kinds":[test_features[t]["capability"] for t in direct_tests],
                "original_oval_stage":"source_present",
                "prior_converter_blocker":known_blocker,
                "current_040_import":"NOT_RUN",
                "current_040_export":"NOT_RUN",
                "oval_xml_semantic_roundtrip":"NOT_RUN",
                "oval_5123_xsd":"NOT_RUN",
                "scanner_result_parity":"NOT_RUN",
            })
    summary={"files":len(files),"definitions":len(rows),"tests":total_tests,
             "prior_source_blockers":len(actual_blockers),
             "current_040_converted_and_proven":0,
             "current_040_unverified":len(rows)}
    if assert_pinned and (any(summary[k]!=v for k,v in EXPECTED.items())
                          or actual_blockers!=set(BLOCKERS)):
        raise ValueError("Pinned Self-Assertion original OVAL denominator or baseline exceptions changed: "+
                         repr(summary))
    return {"status":"SOURCE_INVENTORY_COMPLETE_V04_CONVERSION_UNPROVEN",
            "source_repository":"OVAL-Community/SCAP-Self-Assertion",
            "source_revision":PIN,
            "summary":summary,
            "test_capabilities":dict(sorted(capability.items())),
            "source_feature_occurrences":dict(sorted(features.items())),
            "files":files,"definitions":rows,
            "current_040_semantic_roundtrip_proven":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--assert-pinned",action="store_true")
    args=p.parse_args()
    out=audit(args.source,assert_pinned=args.assert_pinned)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k not in ("files","definitions")},
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
