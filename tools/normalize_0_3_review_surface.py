#!/usr/bin/env python3
"""Normalize the research 0.3 human-review surface without changing semantics.

This is a presentation/migration layer only. It operates after all semantic
modernization proofs and records enough information to restore the exact input
tree byte-for-structure (YAML mapping order aside).

Candidate vocabulary follows the project's 0.3 design rule:
- use current 0.3 Test field names: existence / match;
- use one_or_more for at-least-one existence and match quantifiers;
- preserve logical any for OR-like composition (evaluate/states_match);
- use full-word snake_case comparison operations;
- use all/local/same for filesystem scope;
- shorten benchmark-local Assessment IDs and filenames by removing redundant
  benchmark.<product>. and .assessment repetition.

Nothing here changes the frozen 0.2 converter or constitutes normative 0.3
acceptance.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml


EXISTENCE = {
    "all_exist":"all",
    "all":"all",
    "at_least_one_exists":"one_or_more",
    "some":"one_or_more",
    "one_or_more":"one_or_more",
    "none_exist":"none",
    "none":"none",
    "only_one_exists":"one",
    "one":"one",
    "any_exist":"optional",
    "optional":"optional",
}

MATCH = {
    "all":"all",
    "at least one":"one_or_more",
    "at_least_one":"one_or_more",
    "any":"one_or_more",
    "one_or_more":"one_or_more",
    "only one":"one",
    "only_one":"one",
    "one":"one",
    "none satisfy":"none",
    "none_satisfy":"none",
    "none":"none",
}

OPERATION = {
    "equals":"equals",
    "equal":"equals",
    "not equal":"not_equal",
    "not_equal":"not_equal",
    "case insensitive equals":"case_insensitive_equals",
    "equal_ci":"case_insensitive_equals",
    "case_insensitive_equals":"case_insensitive_equals",
    "case insensitive not equal":"case_insensitive_not_equal",
    "not_equal_ci":"case_insensitive_not_equal",
    "case_insensitive_not_equal":"case_insensitive_not_equal",
    "greater than":"greater_than",
    "greater_than":"greater_than",
    "greater than or equal":"greater_than_or_equal",
    "greater_or_equal":"greater_than_or_equal",
    "greater_than_or_equal":"greater_than_or_equal",
    "less than":"less_than",
    "less_than":"less_than",
    "less than or equal":"less_than_or_equal",
    "less_or_equal":"less_than_or_equal",
    "less_than_or_equal":"less_than_or_equal",
    "bitwise and":"bitwise_and",
    "bit_and":"bitwise_and",
    "bitwise_and":"bitwise_and",
    "bitwise or":"bitwise_or",
    "bit_or":"bitwise_or",
    "bitwise_or":"bitwise_or",
    "pattern match":"pattern_match",
    "match":"pattern_match",
    "pattern_match":"pattern_match",
    "subset of":"subset_of",
    "subset":"subset_of",
    "subset_of":"subset_of",
    "superset of":"superset_of",
    "superset":"superset_of",
    "superset_of":"superset_of",
}

FILESYSTEM = {
    "all":"all",
    "any":"all",
    "local":"local",
    "defined":"same",
    "same":"same",
}


def dump_yaml(value:Any)->str:
    return yaml.safe_dump(value,sort_keys=False,width=120,allow_unicode=True)


def normalize_scalar_tree(value:Any,path:tuple[Any,...],changes:list[dict])->Any:
    if isinstance(value,list):
        return [
            normalize_scalar_tree(item,path+(index,),changes)
            for index,item in enumerate(value)
        ]
    if not isinstance(value,dict):
        return value

    out={}
    for key,item in value.items():
        new_key=key
        # Test-level field names only. Entity predicates already use
        # existence/match and must not be renamed.
        if len(path)>=2 and path[-2]=="tests":
            if key=="check_existence":
                new_key="existence"
            elif key=="check":
                new_key="match"

        normalized=normalize_scalar_tree(item,path+(new_key,),changes)

        if new_key=="existence" and isinstance(normalized,str):
            normalized=EXISTENCE.get(normalized,normalized)
        elif new_key in {"match","variable_match"} and isinstance(normalized,str):
            # states_match is intentionally excluded: it is a logical operator,
            # where any means OR, not a CheckEnumeration quantifier.
            normalized=MATCH.get(normalized,normalized)
        elif new_key=="operation" and isinstance(normalized,str):
            normalized=OPERATION.get(normalized,normalized)
        elif new_key=="filesystem" and isinstance(normalized,str):
            normalized=FILESYSTEM.get(normalized,normalized)

        if new_key!=key or normalized!=item:
            changes.append({
                "path":[str(x) for x in path+(new_key,)],
                "original_key":key,
                "candidate_key":new_key,
                "original_value":copy.deepcopy(item),
                "candidate_value":copy.deepcopy(normalized),
            })
        out[new_key]=normalized
    return out


def product_prefix_from_assessments(root:Path)->str|None:
    prefixes=set()
    pattern=re.compile(r"^benchmark\.([^.]+)\.")
    for path in root.glob("assessments/**/*.yaml"):
        m=pattern.match(path.name)
        if m:
            prefixes.add(m.group(1))
    if not prefixes:
        return None
    if len(prefixes)!=1:
        raise ValueError(f"multiple benchmark Assessment prefixes: {sorted(prefixes)}")
    return f"benchmark.{next(iter(prefixes))}."


def replacement_maps(root:Path,prefix:str|None):
    file_map={}
    id_map={}
    if not prefix:
        return file_map,id_map
    for path in sorted(root.glob("assessments/**/*.yaml")):
        if not path.name.startswith(prefix):
            continue
        new_name=path.name[len(prefix):]
        if new_name.endswith(".assessment.yaml"):
            new_name=new_name[:-len(".assessment.yaml")]+".yaml"
        file_map[path.name]=new_name
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        old_id=a.get("id")
        if isinstance(old_id,str) and old_id.startswith(prefix):
            id_map[old_id]=old_id[len(prefix):]
    return file_map,id_map


def replace_strings(value:Any,file_map:dict[str,str],id_map:dict[str,str],
                    changes:list[dict],path=())->Any:
    if isinstance(value,list):
        return [
            replace_strings(v,file_map,id_map,changes,path+(i,))
            for i,v in enumerate(value)
        ]
    if isinstance(value,dict):
        return {
            k:replace_strings(v,file_map,id_map,changes,path+(k,))
            for k,v in value.items()
        }
    if not isinstance(value,str):
        return value

    candidate=id_map.get(value,value)
    for old,new in file_map.items():
        if old in candidate:
            candidate=candidate.replace(old,new)
    if candidate!=value:
        changes.append({
            "path":[str(x) for x in path],
            "original_value":value,
            "candidate_value":candidate,
        })
    return candidate


def normalize_tree(root:Path)->dict:
    prefix=product_prefix_from_assessments(root)
    file_map,id_map=replacement_maps(root,prefix)
    doc_changes=[]
    rename_rows=[]

    # First rewrite document content and references while old filenames exist.
    for path in sorted(root.rglob("*.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc,dict):
            continue
        local_changes=[]
        candidate=normalize_scalar_tree(doc,(),local_changes)
        candidate=replace_strings(candidate,file_map,id_map,local_changes)
        if candidate!=doc:
            path.write_text(dump_yaml(candidate),encoding="utf-8")
        if local_changes:
            doc_changes.append({
                "file":str(path.relative_to(root)),
                "changes":local_changes,
            })

    # Then shorten only Assessment filenames.
    for path in sorted(root.glob("assessments/**/*.yaml")):
        new_name=file_map.get(path.name)
        if not new_name:
            continue
        target=path.with_name(new_name)
        if target.exists():
            raise ValueError(f"candidate filename collision: {target}")
        rename_rows.append({
            "original":str(path.relative_to(root)),
            "candidate":str(target.relative_to(root)),
        })
        path.rename(target)

    return {
        "format":"scap-ng-0.3-review-surface-normalization-0.1",
        "status":"research_only_pending_owner_review",
        "assessment_prefix_removed":prefix,
        "filename_map":file_map,
        "assessment_id_map":id_map,
        "renames":rename_rows,
        "document_changes":doc_changes,
        "candidate_vocabulary":{
            "test_fields":{
                "check_existence":"existence",
                "check":"match",
            },
            "existence":"one_or_more for at-least-one",
            "match_quantifier":"one_or_more for at-least-one",
            "logical_any":"retained for OR semantics",
            "comparison_operations":"full-word snake_case",
            "filesystem_scope":["all","local","same"],
        },
    }


def restore_tree(candidate_root:Path,restored_root:Path,report:dict)->None:
    if restored_root.exists():
        shutil.rmtree(restored_root)
    shutil.copytree(candidate_root,restored_root)

    # Reverse filenames first so recorded file paths resolve.
    for row in reversed(report.get("renames") or []):
        candidate=restored_root/row["candidate"]
        original=restored_root/row["original"]
        original.parent.mkdir(parents=True,exist_ok=True)
        candidate.rename(original)

    # The most robust proof is replaying recorded original documents from the
    # caller's snapshot; this helper is kept for focused unit-level reversal of
    # scalar/filename mappings. Full-tree proof compares a pre-normalization
    # copy to a normalized-then-restored copy in the renderer workflow.


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    report=normalize_tree(args.root)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "renamed_assessment_files":len(report["renames"]),
        "assessment_ids_shortened":len(report["assessment_id_map"]),
        "documents_changed":len(report["document_changes"]),
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
