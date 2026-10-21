#!/usr/bin/env python3
"""Actually execute original OVAL XML→fresh NG 0.4→independent OVAL XML.

The source is the pinned NIWC Windows 11 original OVAL component. A separately
pinned, previous six-STIG NG build is used ONLY as an independent comparison,
never an importer input. All four native Assessments are generated from XML
now, not copied from the archive.

Every source-derived Test must match the independent canonical native Test,
then the native->OVAL emitter must produce semantic graph equal to original
and schema-valid 5.12.3 XML. Four deliberate actual-output mutations remain
a separate CI gate. This is a strict four-case subset, not full OVAL support.

Refs #248 #229.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from import_v04_oval_leaf_pilot import convert
from compare_v04_fresh_oval_import import compare as compare_native
from audit_v04_original_oval_forward import compare as compare_original_to_native
from export_v04_oval_shellcommand_pilot import emit as shell_export
from export_v04_oval_registry_pilot import emit as registry_export
from audit_v04_oval_xml_roundtrip import audit as audit_xml, FORMAT
from validate_v04_oval_5123 import check as xsd
from combine_v04_oval_xml_proofs import combine
from v04_flat_object_authoring import load_catalog, flatten_document, restore_document

DEFS={
    "bluetooth":{
        "definition":"oval:navy.navwar.niwcatlantic.scc.windows:def:102",
        "canonical":"bluetooth-native-v04.json",
        "exporter":shell_export,"platform":"independent"},
    "camera":{
        "definition":"oval:navy.navwar.niwcatlantic.scc.windows:def:201",
        "canonical":"camera-native-v04.json",
        "exporter":shell_export,"platform":"independent"},
    "SV-253291":{
        "definition":"oval:navy.navwar.niwcatlantic.scc.windows:def:253291",
        "canonical":"SV-253291-native-v04.json",
        "exporter":registry_export,"platform":"windows"},
    "SV-253350":{
        "definition":"oval:navy.navwar.niwcatlantic.scc.windows:def:253350",
        "canonical":"SV-253350-native-v04.json",
        "exporter":registry_export,"platform":"windows"},
}


def run(folder,schema_dir):
    folder.mkdir(parents=True,exist_ok=True)
    source=folder/"source-oval.xml"
    payload=source.read_bytes()
    records=[]
    xsd_reports=[]
    catalog=load_catalog(Path(__file__).resolve().parents[1] /
                         "schema/v0.4.0/capability-mappings/supported")
    for name,config in DEFS.items():
        imported=convert(payload,config["definition"],
                         assessment_id="v04-oval-forward-"+name.lower()+".assessment")
        report=compare_original_to_native(payload,imported,config["definition"])
        if report["status"]!="SOURCE_TO_NATIVE_040_EXACT_FOR_SUPPORTED_TEST":
            raise ValueError("Forward import differs from original OVAL: "+name)
        canonical=json.loads((folder/config["canonical"]).read_text())
        canonical_report=compare_native(imported,canonical)
        if canonical_report["status"]!="TRUE_FRESH_OVAL_IMPORT_MATCHES_CANONICAL_040_TEST":
            raise ValueError("Fresh importer diverges from six-STIG candidate: "+name)
        # The pinned source importer and previous six-STIG baseline are
        # independently verified in their historical input representation.
        # Only then apply the owner-approved 0.4 flat Object mapping. The
        # independent OVAL exporter now REQUIRES that canonical flat Object.
        flat,proof=flatten_document(imported,catalog)
        if not proof["edits"] or restore_document(flat,proof)!=imported:
            raise ValueError("Original XML native Object flattening not invertible: "+name)
        native_path=folder/(name+"-fresh-native-v04.json")
        native_path.write_text(json.dumps(flat,indent=2)+"\n")
        (folder/(name+"-flat-object-source-inverse.json")).write_text(
            json.dumps(proof,indent=2)+"\n")
        tree,exported_def=config["exporter"](flat)
        xml_path=folder/(name+"-fresh-exported-oval.xml")
        tree.write(xml_path,encoding="utf-8",xml_declaration=True)
        schema_report=xsd(schema_dir,xml_path,config["platform"])
        (folder/(name+"-fresh-exported-xsd.json")).write_text(
            json.dumps(schema_report,indent=2)+"\n")
        if schema_report["status"]!="PASS":
            raise ValueError("Recreated original OVAL XML failed pinned XSD: "+name+
                             "; ".join(schema_report["diagnostics"][:4]))
        xsd_reports.append(schema_report)
        row={"case_id":name+" fresh import",
             "status":"converted",
             "forward_profile":"0.4.0","reverse_profile":"0.4.0",
             "source_definition":config["definition"],
             "regenerated_definition":exported_def}
        for key,path in (("original",source),("native_assessment",native_path),
                         ("regenerated",xml_path)):
            row[key]=path.name
            row[key+"_sha256"]=sha256(path.read_bytes()).hexdigest()
        records.append(row)
        (folder/(name+"-original-to-native.json")).write_text(
            json.dumps({"source_check":report,"canonical_parity":canonical_report},indent=2)+"\n")
    manifest={"format":FORMAT,"profile":"0.4.0","cases":records}
    (folder/"fresh-oval-roundtrip-manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    semantic=audit_xml(manifest,folder,expected=len(DEFS))
    (folder/"fresh-oval-semantic-result.json").write_text(
        json.dumps(semantic,sort_keys=True,indent=2)+"\n")
    joined=combine(semantic,xsd_reports)
    joined["actual_native_forward_import"]="RUN_FROM_PINNED_ORIGINAL_OVAL_XML"
    joined["original_test_and_filter_field_parity"]="PASS"
    joined["independent_approved_canonical_v04_output_parity"]="PASS"
    joined["source_case_count"]=len(DEFS)
    joined["full_oval_language_coverage"]=False
    (folder/"fresh-end-to-end-evidence.json").write_text(
        json.dumps(joined,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in joined.items() if k!="cases"},
                     sort_keys=True,indent=2))
    return joined


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-and-canonical-dir",type=Path,required=True)
    p.add_argument("--oval-schemas",type=Path,required=True)
    a=p.parse_args()
    run(a.original_and_canonical_dir,a.oval_schemas)


if __name__=="__main__":
    main()
