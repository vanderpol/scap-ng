#!/usr/bin/env python3
"""Opt-in complete v0.4 AND/OR/ONE/XOR Test-result expression preview.

Input is the already independently proven 123-Test AND/OR *State* candidate.
Replace only the historical evaluate.all/any/odd Boolean operator spellings,
keeping original Test Item existence, state fields, Variables, and source
content untouched. Schema validation uses a TEMPORARY candidate-local copy
of the versioned expression schema, never edits the accepted 0.4.0 schema.

This is a research candidate for owner review, NOT a 0.4.0 release rewrite.
Refs #248 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import yaml
import zipfile
from hashlib import sha256

from migrate_v04_evaluate_and_or import migrate,assert_inverse
from build_v04_and_or_candidate import _archive_raw,_writestr,canonical
from v04_canonical_source_ir import _schema_validators,validate_docs,compile_pair


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def candidate_schema(root):
    original=Path(__file__).resolve().parents[1]/"schema/v0.4.0"
    shutil.copytree(original,root)
    file=root/"expression.schema.json"
    doc=json.loads(file.read_text())
    seen=Counter()
    for choice in doc["$defs"]["expression"]["oneOf"]:
        old=next(iter(choice.get("required") or ()),None)
        replacement={"all":"and","any":"or","odd":"xor"}.get(old)
        if replacement:
            if set(choice["properties"])!={old}:
                raise ValueError("Unexpected original versioned expression schema choice")
            choice["required"]=[replacement]
            choice["properties"][replacement]=choice["properties"].pop(old)
            seen[old]+=1
    if seen!={"all":1,"any":1,"odd":1}:
        raise ValueError("Original expression schema names unexpectedly changed")
    file.write_text(json.dumps(doc,indent=2)+"\n")
    return root,doc


def build(source_json,source_yaml,destination):
    destination.mkdir(parents=True,exist_ok=True)
    originals={}
    results={}
    changes=Counter()
    ledgers=[]
    generated={}
    for format,path in (("json",source_json),("yaml",source_yaml)):
        docs=_archive_raw(path,format)
        if len(docs)!=4001:
            raise ValueError("Expected all 4,001 real six-STIG candidate documents")
        originals[format]=docs
        target=destination/("scap-ng-0.4.0-six-stigs.complete-boolean."+format+".zip")
        generated[format]=target
        with zipfile.ZipFile(target,"w") as outfile:
            for name,source in sorted(docs.items()):
                doc,ledger=migrate(source["data"])
                assert_inverse(source["data"],doc,ledger)
                if ledger:
                    changes[format]+=sum(len(row["replaced_operators"]) for row in ledger)
                    if format=="json":
                        for row in ledger:
                            ledgers.append({"path":name,**row})
                    raw=(json.dumps(doc,indent=2,ensure_ascii=False)+"\n").encode() \
                        if format=="json" else yaml.safe_dump(
                          doc,sort_keys=False,allow_unicode=True).encode()
                else:
                    raw=source["raw"]
                _writestr(outfile,name,raw)
        results[format]=_archive_raw(target,format)
    if changes!={"json":346,"yaml":346}:
        raise ValueError("Real six-STIG evaluate operator census changed: "+repr(changes))
    if len(results["json"])!=len(results["yaml"]):
        raise ValueError("Candidate JSON/YAML document count mismatch")
    for logical in originals["json"]:
        ypath=logical.removesuffix(".json")+".yaml"
        if (canonical(originals["json"][logical]["data"])!=
                canonical(originals["yaml"][ypath]["data"])):
            raise ValueError("Original JSON/YAML logical source differs: "+logical)
        if (canonical(results["json"][logical]["data"])!=
                canonical(results["yaml"][ypath]["data"])):
            raise ValueError("AND/OR candidate JSON/YAML differs: "+logical)
    with TemporaryDirectory(prefix="v04-boolean-operator-schema-") as td:
        _,schema=candidate_schema(Path(td)/"v0.4.0")
        validators=_schema_validators(Path(td)/"v0.4.0")
        for kind in ("json","yaml"):
            validate_docs({path:d["data"] for path,d in results[kind].items()},
                          validators)
        (destination/"expression.candidate-only.schema.json").write_text(
            json.dumps(schema,indent=2)+"\n")
    # The maintained compiler validates exact full source graph, YAML/JSON
    # and 2,958 links. Candidate schema was checked separately.
    _,rep=compile_pair(generated["json"],generated["yaml"],validate_schema=False)
    if (rep.get("source_reconstruction")!="PASS" or
        rep.get("yaml_json_byte_parity")!="PASS" or
        rep.get("documents")!=4001):
        raise ValueError("Complete candidate failed maintained typed IR reconstruction")
    status={
        "status":"FULL_SIX_STIG_AND_OR_XOR_REVIEW_CANDIDATE_NOT_ACCEPTED_SCHEMA",
        "changes_per_format":dict(changes),
        "source_first_pass_state_rewrites":123,
        "original_evaluate_operators_replaced":346,
        "source_json_sha256":digest(source_json),
        "source_yaml_sha256":digest(source_yaml),
        "candidate_json_sha256":digest(generated["json"]),
        "candidate_yaml_sha256":digest(generated["yaml"]),
        "documents":4001,
        "reversible_evaluate_sites":ledgers,
        "candidate_expression_schema":"STRICT_NEW_SPELLINGS_ONLY_PASS",
        "published_040_schema_changed":False,
        "source_assessment_field_requirements_changed":False,
        "source_item_cardinality_changed":False,
        "maintained_compiler_ir":rep,
        "scanner_equivalence_proven":False,
        "release_published":False
    }
    (destination/"complete-boolean-preview-manifest.json").write_text(
        json.dumps(status,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in status.items()
                      if k not in ("reversible_evaluate_sites","maintained_compiler_ir")},
                     indent=2,sort_keys=True))
    return status


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--first-pass-json",type=Path,required=True)
    p.add_argument("--first-pass-yaml",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    build(a.first_pass_json,a.first_pass_yaml,a.out_dir)


if __name__=="__main__":
    main()
