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
from validate_v04_fields_condition_preview import native_schema_projection


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def candidate_schema(root):
    original=Path(__file__).resolve().parents[1]/"schema/v0.4.0"
    shutil.copytree(original,root)
    file=root/"expression.schema.json"
    doc=json.loads(file.read_text())
    seen=Counter()
    branches=doc["$defs"]["expression"]["oneOf"]
    # Active 0.4.0 now accepts preferred logical names alongside
    # deprecated historical source aliases. This *temporary* candidate
    # validator is deliberately stricter: reject the old names entirely,
    # without altering the maintained versioned schema.
    names=[next(iter(x.get("required") or ()),None) for x in branches]
    for old,modern in (("all","and"),("any","or"),("odd","xor")):
        if names.count(old)!=1 or names.count(modern)!=1:
            raise ValueError("Versioned expression aliases drifted: "+old+"/"+modern)
    strict=[]
    for choice in branches:
        old=next(iter(choice.get("required") or ()),None)
        if old in ("all","any","odd"):
            if set(choice.get("properties",{}))!={old}:
                raise ValueError("Malformed deprecated Test operator alias: "+old)
            seen[old]+=1
            continue
        strict.append(choice)
    if seen!={"all":1,"any":1,"odd":1}:
        raise ValueError("Missing deprecated source-alias proof")
    doc["$defs"]["expression"]["oneOf"]=strict
    file.write_text(json.dumps(doc,indent=2)+"\n")
    return root,doc


def validate_candidate_evaluate(a):
    """Independent strict new-operator reference closure, without old scanner."""
    e=a.get("evaluate")
    tests=a.get("tests") or {}
    dependencies=a.get("dependencies") or {}
    count=0
    def scan(node,location):
        nonlocal count
        if not isinstance(node,dict) or not node:
            raise ValueError("Invalid candidate expression at "+location)
        keys=set(node)
        if keys=={"test"}:
            if node["test"] not in tests:
                raise ValueError("Unresolved Test in candidate new AND/OR: "+str(node["test"]))
            count+=1
            return
        if keys=={"assessment"}:
            if node["assessment"] not in dependencies:
                raise ValueError("Unresolved Assessment dependency in candidate")
            count+=1
            return
        if keys=={"not_applicable"}:
            v=node["not_applicable"]
            if not isinstance(v,dict) or not isinstance(v.get("reason"),str):
                raise ValueError("Invalid not_applicable reason")
            return
        if keys=={"not"}:
            scan(node["not"],location+".not")
            return
        if keys=={"if","then","else"}:
            for k in ("if","then","else"):
                scan(node[k],location+"."+k)
            return
        if len(keys)==1 and next(iter(keys)) in ("and","or","one","xor"):
            op=next(iter(keys))
            values=node[op]
            if not isinstance(values,list) or not values:
                raise ValueError("Empty Boolean operand in candidate "+location)
            for i,value in enumerate(values):
                scan(value,location+"."+op+"["+str(i)+"]")
            return
        raise ValueError("Mixed, unknown or legacy evaluate operator "+str(keys))
    scan(e,"evaluate")
    return count


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
            validate_docs(native_schema_projection({path:d["data"] for path,d in results[kind].items()}),
                          validators)
        (destination/"expression.candidate-only.schema.json").write_text(
            json.dumps(schema,indent=2)+"\n")
    # Candidate AND/OR Test expression reference closure is checked under
    # the NEW grammar directly. The frozen graph scanner still expects the
    # OLD all/any tokens; it must not be misrepresented as accepting the
    # new grammar. The exact inverse has already verified every Test
    # expression against the original first-pass source.
    ref_counts={}
    for kind in ("json","yaml"):
        ref_counts[kind]=sum(
            validate_candidate_evaluate(node["data"]["assessment"])
            for node in results[kind].values()
            if isinstance(node["data"].get("assessment"),dict)
            and node["data"]["assessment"].get("mode")=="automated")
    if ref_counts["json"]!=ref_counts["yaml"] or not ref_counts["json"]:
        raise ValueError("New-grammar candidate Test references diverge by format")
    # Run the maintained v0.4 source graph compiler against the source
    # authoring we can EXACTLY reconstruct, not the as-yet-unaccepted
    # new-wire-grammar. Both old input source formats passed active schema.
    _,rep=compile_pair(source_json,source_yaml,validate_schema=True,legacy_review=True)
    if (rep.get("source_reconstruction")!="PASS" or
        rep.get("yaml_json_byte_parity")!="PASS" or
        rep.get("documents")!=4001):
        raise ValueError("Exact-inverse source failed maintained typed IR compiler")
    # The versioned 0.4.0 schema now accepts AND/OR/XOR alongside
    # deprecated all/any/odd spellings. Require the maintained full
    # source-IR compiler to consume the NEW candidate archives directly,
    # not only a reconstructed copy of the pre-migration files.
    _,candidate_ir=compile_pair(generated["json"],generated["yaml"],validate_schema=True,legacy_review=True)
    if (candidate_ir.get("source_reconstruction")!="PASS" or
        candidate_ir.get("yaml_json_byte_parity")!="PASS" or
        candidate_ir.get("native_source_schema")!="PASS" or
        candidate_ir.get("documents")!=4001 or
        candidate_ir.get("tests")!=1375 or
        candidate_ir.get("rule_choice_links")!=rep.get("rule_choice_links")):
        raise ValueError("Direct new-grammar candidate failed current typed-source compiler")
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
        "schema_validation_view": candidate_ir["schema_validation_view"],
        "legacy_source_inverse": candidate_ir["legacy_source_inverse"],
        "published_040_schema_changed":False,
        "source_assessment_field_requirements_changed":False,
        "source_item_cardinality_changed":False,
        "maintained_compiler_source_view_ir":rep,
        "maintained_compiler_candidate_ir":candidate_ir,
        "candidate_new_grammar_test_references":ref_counts,
        "candidate_executable_compiler_support":"OPEN_EXECUTABLE_BACKEND",
        "candidate_typed_source_ir_compiler":"PASS_NEW_AND_OR_XOR_GRAMMAR",
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
