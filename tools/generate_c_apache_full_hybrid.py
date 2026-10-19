#!/usr/bin/env python3
"""Refs #245: deterministic complete Apache SV-214268 C hybrid review export."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import yaml
from research_c_apache_hybrid_authoring import (
    present_c_apache_hybrid,compile_c_apache_hybrid,prove_c_apache_hybrid)
from research_c_apache_grouped_values import (
    present_grouped_apache,compile_grouped_apache,prove_grouped_apache)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.joinpath("research/requirements-first-language/contract-candidate/"
    "corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")
FILENAME="apache-sv214268-five-checks-nineteen-derived-values.research.yaml"

def export_review(source_path,output_dir):
    source_path=Path(source_path);output_dir=Path(output_dir)
    raw=source_path.read_bytes()
    all_data=yaml.safe_load(raw)
    if not isinstance(all_data,dict) or set(all_data)!={"assessment"}:
        raise ValueError("original source Assessment wrapper required")
    source=all_data["assessment"]
    authored=present_c_apache_hybrid(source)
    proof=prove_c_apache_hybrid(source,authored)
    if compile_c_apache_hybrid(yaml.safe_load(yaml.safe_dump(authored)))!=source:
        raise ValueError("YAML serializing authoring would change source graph")
    if (proof["source_test_count"]!=5 or proof["source_variable_count"]!=19
        or proof["source_shared_acquisition_count"]!=1):
        raise ValueError("source-backed Apache corpus changed unexpectedly")
    output_dir.mkdir(parents=True,exist_ok=True)
    body=("# 0.4-C hybrid research. NOT normative or OVAL scanner parity.\n"
          "# Source: vanderpol/scap-ng research source specimen Apache SV-214268\n"
          "# Exact original Test/Variable/shared acquisition IR reconstructed by compiler.\n"
          "# This file has 5 C checks and 19 explicit derived-value steps.\n"
          +yaml.safe_dump(authored,sort_keys=False,allow_unicode=True))
    out=output_dir/FILENAME
    out.write_text(body,encoding="utf-8")
    # Group only four independently audited *pure value* single consumers.
    # Command-acquisition dependencies remain named steps.
    grouped=present_grouped_apache(source)
    grouped_proof=prove_grouped_apache(source,grouped)
    grouped_path=output_dir/"apache-sv214268-fifteen-visible-four-nested-derived.research.yaml"
    grouped_path.write_text(
        "# C grouped-value research; 4 value-only steps nested, all 19 A Variables recoverable.\n"
        "# Original full Apache source graph and scanner caveats remain unchanged.\n"
        +yaml.safe_dump(grouped,sort_keys=False,allow_unicode=True),
        encoding="utf-8")
    if compile_grouped_apache(yaml.safe_load(
        grouped_path.read_text(encoding="utf-8")))!=source:
        raise ValueError("grouped C YAML would alter original source IR")
    original_render=out.read_text(encoding="utf-8")
    grouped_render=grouped_path.read_text(encoding="utf-8")
    presentation_comparison={
        "full":{"bytes":len(original_render.encode("utf-8")),
                "lines":len(original_render.splitlines()),
                "visible_derived_value_declarations":len(authored["derived_values"])},
        "grouped":{"bytes":len(grouped_render.encode("utf-8")),
                   "lines":len(grouped_render.splitlines()),
                   "visible_derived_value_declarations":len(grouped["derived_values"])},
        "authoring_comprehension_test_completed":False,
        "automatic_grouping_promoted":False,
        "source_graph_equal_in_both":True}
    manifest={
        "stage":"C_RESEARCH_APACHE_FULL_HYBRID_REVIEW_SOURCE_EXACT",
        "original_source_sha256":hashlib.sha256(raw).hexdigest(),
        "authored_output_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "original_repository_source":str(source_path.relative_to(ROOT)) if (
            source_path.is_relative_to(ROOT)) else str(source_path),
        "output":FILENAME,"proof":proof,
        "grouped_output":grouped_path.name,
        "grouped_output_sha256":hashlib.sha256(grouped_path.read_bytes()).hexdigest(),
        "grouped_proof":grouped_proof,
        "presentation_comparison":presentation_comparison,
        "C_normative_acceptance":False,"scanner_runtime_parity":False,
    }
    (output_dir/"proof.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args()
    print(json.dumps(export_review(x.source,x.output),sort_keys=True))
if __name__=="__main__":
    main()
