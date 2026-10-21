#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 independent.family + constant Variable -> native 0.4.

One narrow source-XML-specified case (Self-Assertion family_test def:95).
Rejects different Boolean, Object, Variable, Item or State semantics.
The reverse XML exporter is separate; this tool alone is NOT a round trip.
Refs #248 #229 #232. No 0.4-C authoring dialect.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from v04_flat_object_authoring import dump_hybrid, digest

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
REL="agnostic/ind-def_family_test.xml"
DID="oval:org.mitre.oval.test:def:95"
OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"


def require(ok, reason):
    if not ok: raise ValueError("Unproven original family OVAL source: "+reason)


def element(root,tag):
    vals=[x for x in root if x.tag==tag]
    require(len(vals)==1,"expected exactly one "+tag)
    return vals[0]


def convert(xml_bytes,review):
    meta=review.get("source",{})
    old=review.get("A_source_compatibility_fallback",{})
    require(meta.get("revision")==PIN and meta.get("file")==REL and
            meta.get("definition_id")==DID and
            meta.get("source_file_sha256")==sha256(xml_bytes).hexdigest(),
            "pinned source identity or SHA-256 mismatch")
    root=ET.fromstring(xml_bytes)
    d=element(element(root,"{"+OD+"}definitions"),"{"+OD+"}definition")
    require(d.get("id")==DID and set(d.attrib)=={"id","version","class"} and
            d.get("class")=="miscellaneous" and int(d.get("version"))==1,
            "Definition version/class/identity changed")
    metadata=element(d,"{"+OD+"}metadata")
    title=element(metadata,"{"+OD+"}title").text
    require(title==old.get("assessment_title"),"title differs from pinned source")
    criteria=element(d,"{"+OD+"}criteria")
    ref=element(criteria,"{"+OD+"}criterion")
    require(criteria.get("operator","AND")=="AND" and
            set(criteria.attrib)<={"operator"} and
            set(ref.attrib)<={"comment","test_ref"} and
            ref.get("test_ref")=="oval:org.mitre.oval.test:tst:906",
            "source Boolean/Test reference changed")
    test=element(element(root,"{"+OD+"}tests"),"{"+IND+"}family_test")
    require(test.get("id")==ref.get("test_ref") and
            test.get("check")=="at least one" and
            test.get("check_existence")=="at_least_one_exists" and
            set(test.attrib)<={"id","version","comment","check","check_existence"} and
            test.get("comment")=="Test that the family_object is supported.",
            "source Test matching/cardinality changed")
    objref=element(test,"{"+IND+"}object")
    stateref=element(test,"{"+IND+"}state")
    ob=element(element(root,"{"+OD+"}objects"),"{"+IND+"}family_object")
    state=element(element(root,"{"+OD+"}states"),"{"+IND+"}family_state")
    require(objref.get("object_ref")==ob.get("id") and
            stateref.get("state_ref")==state.get("id") and
            len(ob)==0 and len(test)==2 and
            set(objref.attrib)=={"object_ref"} and
            set(stateref.attrib)=={"state_ref"} and
            len(state)==1, "Object/State graph changed")
    family=element(state,"{"+IND+"}family")
    require(family.get("operation")=="pattern match" and
            family.get("var_check")=="all" and
            family.get("var_ref") and
            set(family.attrib)=={"operation","var_check","var_ref"} and
            family.text in (None,""), "Variable-backed family State changed")
    original_var=element(element(root,"{"+OD+"}variables"),"{"+OD+"}constant_variable")
    source_value=element(original_var,"{"+OD+"}value")
    require(original_var.get("id")==family.get("var_ref") and
            original_var.get("datatype")=="string" and
            len(original_var)==1 and
            set(original_var.attrib)<={"id","version","comment","datatype"} and
            source_value.text is not None and
            set(source_value.attrib)==set(),
            "expected one string constant Variable, not an expression or array")
    require(len(old.get("variables",{}))==1 and len(old.get("tests",{}))==1 and
            len(old.get("states",{}))==1 and
            len(old.get("objects",{}))==1 and
            old["mode"]=="automated" and
            old["class"]=="miscellaneous" and
            old["version"]==1 and
            old["evaluate"]=={"test":next(iter(old["tests"]))},
            "previous source-compatible graph shape changed")
    varname,var=next(iter(old["variables"].items()))
    require(var.get("kind")=="constant" and var.get("datatype")=="string" and
            var.get("expression")=={"literal":source_value.text} and
            varname.endswith("-variable") and
            len(old["states"])==1 and
            next(iter(old["states"].values()))["state"]=={
                "datatype":"string",
                "entity_check":"all",
                "entity_existence":"at_least_one_exists",
                "field":"family",
                "operation":"pattern match",
                "value":{"variable":varname},
                "variable_check":"all"},
            "original State or constant Variable differs from source-compatible graph")
    tname=next(iter(old["tests"]))
    require(old["tests"][tname]["check"]=="at least one" and
            old["tests"][tname]["check_existence"]=="at_least_one_exists" and
            old["tests"][tname]["capability"]=="independent.family",
            "historical source Test/matching drift")
    native_test_name="family-collector-support-test"
    assessment={
        "id":old["id"],
        "version":1,
        "assessment_title":title,
        "mode":"automated",
        "class":"miscellaneous",
        "purpose":"assessment",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "variables":{varname:var},
        "tests":{native_test_name:{
            "test_title":test.get("comment"),
            "capability":"independent.family",
            "reported_elements":"all",
            "states":[{"family":{
                "matches_regex":{"variable":varname},
                "datatype":"string","value_match":"all",
                "require":"at_least_one_exists_and_all_match"}}],
            "require":"at_least_one_exists_and_some_match"}},
        "evaluate":{"test":native_test_name},
    }
    proof={
        "original_oval_source":REL,"source_oval_definition_id":DID,
        "pinned_source_revision":PIN,
        "original_oval_xml_sha256":sha256(xml_bytes).hexdigest(),
        "source_variable_id":original_var.get("id"),
        "source_test_id":test.get("id"),
        "source_state_id":state.get("id"),
        "source_object_id":ob.get("id"),
        "original_source_compatible_graph_sha256":digest(old),
        "current_040_authoring_sha256":digest(assessment),
        "semantics_verified_by_original_XML_importer":"CHECKED_SOURCE_GRAPH_ONLY",
        "native_schema_validation":"PENDING",
        "independent_reverse_oval_xml":"PENDING",
        "scanner_execution_equivalence":"NOT_PROVEN",
    }
    return {"assessment":assessment},proof


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-xml",type=Path,required=True)
    p.add_argument("--source-review",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    doc,proof=convert(args.source_xml.read_bytes(),
                      json.loads(args.source_review.read_text()))
    dest=args.output_dir;dest.mkdir(parents=True,exist_ok=True)
    (dest/"family-assessment.json").write_text(
        json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
    (dest/"family-assessment.yaml").write_text(dump_hybrid(doc))
    (dest/"source-import-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
    print("PASS: pinned original OVAL family source graph -> 0.4 authoring candidate")


if __name__=="__main__":
    main()
