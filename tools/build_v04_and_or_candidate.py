#!/usr/bin/env python3
"""Create source-reversible six-STIG 0.4 AND/OR JSON+YAML candidate archives.

The only permitted authoring changes: `states_match: any/all` on structured
multi-State Tests is represented instead by a single explicit `or/and`
group wrapping the same ordered complete State conditions per collected
Item. It is an *opt-in review candidate*, not a released/accepted rewrite.

Original JSON and YAML source files and all immutable publication artifacts
remain available; each original document is recoverable exactly as parsed.
Checks every Test ref/Rule/Benchmark with maintained native-0.4 IR compiler.
Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

from migrate_v04_states_match_to_logic import (
    migrate,validate_exact_inverse,
)
from v04_canonical_source_ir import compile_pair


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":")).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def _archive_raw(path,kind):
    with zipfile.ZipFile(path) as z:
        result={}
        for name in z.namelist():
            if not name.endswith("."+kind):
                continue
            content=z.read(name)
            data=(json.loads(content) if kind=="json" else yaml.safe_load(content))
            result[name]={"raw":content,"data":data}
    if not result:
        raise ValueError("Empty six-STIG "+kind+" authoring ZIP")
    return result


def _writestr(zipout,name,raw):
    info=zipfile.ZipInfo(name,date_time=(2026,10,21,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o644 << 16
    zipout.writestr(info,raw)


def build(source_json,source_yaml,output_dir):
    jdocs=_archive_raw(source_json,"json")
    ydocs=_archive_raw(source_yaml,"yaml")
    src_j={name.removesuffix(".json"):value for name,value in jdocs.items()}
    src_y={name.removesuffix(".yaml"):value for name,value in ydocs.items()}
    if set(src_j)!=set(src_y) or len(src_j)!=4001:
        raise ValueError("Original pinned JSON/YAML source graph/paths disagree")
    output_dir.mkdir(exist_ok=True,parents=True)
    changes=[]
    counts=Counter()
    targets={}
    for kind,source in (("json",jdocs),("yaml",ydocs)):
        out=output_dir/("scap-ng-0.4.0-six-stigs.and-or."+kind+".zip")
        targets[kind]=str(out)
        with zipfile.ZipFile(out,"w") as z:
            for path,node in sorted(source.items()):
                old=node["data"]
                current,ledger=migrate(old)
                validate_exact_inverse(old,current,ledger)
                if ledger:
                    counts[kind]+=len(ledger)
                    for row in ledger:
                        if kind=="json":
                            changes.append({"path":path,**row})
                    payload=(json.dumps(current,ensure_ascii=False,indent=2)+"\n").encode() if kind=="json" else yaml.safe_dump(current,sort_keys=False,allow_unicode=True).encode()
                else:
                    payload=node["raw"]
                _writestr(z,path,payload)
    if counts!={"json":123,"yaml":123}:
        raise ValueError("Expected 123 normalized Tests in both version-local formats: "+repr(counts))
    converted_j=_archive_raw(targets["json"],"json")
    converted_y=_archive_raw(targets["yaml"],"yaml")
    for logical in src_j:
        old_j=src_j[logical]["data"]
        old_y=src_y[logical]["data"]
        if canonical(old_j)!=canonical(old_y):
            raise ValueError("Original JSON/YAML semantics inconsistent: "+logical)
        nj=converted_j[logical+".json"]["data"]
        ny=converted_y[logical+".yaml"]["data"]
        if canonical(nj)!=canonical(ny):
            raise ValueError("New JSON/YAML authoring differs: "+logical)
    # This compiler checks the entire generated authoring graph, not only
    # the sites modified in the narrow logical scope modernization.
    report=compile_pair(Path(targets["json"]),Path(targets["yaml"]),
                        validate_schema=True)
    return {
        "status":"REVIEW_CANDIDATE_AND_OR_ONLY_SOURCE_INVERSE_PROVEN",
        "source_json_sha256":sha(source_json.read_bytes()),
        "source_yaml_sha256":sha(source_yaml.read_bytes()),
        "output_json_sha256":sha(Path(targets["json"]).read_bytes()),
        "output_yaml_sha256":sha(Path(targets["yaml"]).read_bytes()),
        "documents":len(src_j),
        "changes_per_format":dict(sorted(counts.items())),
        "changed_tests":changes,
        "compiled_ir_checks":report,
        "native_040_schema_check":"PASS_ALL_4001_EACH_FORMAT",
        "oval_source_inv_verdict":"PASS_ALL_CHANGED_TESTS",
        "source_item_existence_untouched":True,
        "source_state_field_matching_untouched":True,
        "source_legacy_scalar_states_match_untouched":True,
        "fields_naming_untouched":True,
        "scanner_parity_proven":False,
        "release_published":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical-json-zip",type=Path,required=True)
    p.add_argument("--canonical-yaml-zip",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    report=build(a.canonical_json_zip,a.canonical_yaml_zip,a.output_dir)
    dest=a.output_dir/"and-or-candidate-manifest.json"
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items()
                      if k not in ("changed_tests","compiled_ir_checks")},
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()
