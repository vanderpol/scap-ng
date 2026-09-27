#!/usr/bin/env python3
"""Normalize a recognized OVAL Linux audit xattr-syscall rule into native semantics.

This is deliberately a narrow, conservative normalizer. It consumes the faithful
OVAL semantic IR and only succeeds when the source graph matches the expected
semantic pattern. A successful result remains requires_review until differential
execution proves equivalence.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, re
from pathlib import Path

XATTR_SYSCALL_RE = re.compile(r"\b(?:f|l)?(?:remove|set)xattr\b")
ARCHES = ("b32", "b64")


def sha256_json(value):
    data=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def walk_criteria(node, definitions, tests, seen_defs):
    if not node:
        return
    kind=node.get("kind")
    if kind=="test_ref":
        ref=node.get("test_ref")
        if ref:
            tests.add(ref)
        return
    if kind=="definition_ref":
        ref=node.get("definition_ref")
        if not ref or ref in seen_defs:
            return
        seen_defs.add(ref)
        target=definitions.get(ref)
        if target:
            walk_criteria(target.get("criteria"),definitions,tests,seen_defs)
        return
    if kind=="boolean":
        for child in node.get("children",[]):
            walk_criteria(child,definitions,tests,seen_defs)


def entity(obj, name):
    matches=[x for x in obj.get("children",[]) if x.get("name")==name]
    if len(matches)!=1:
        raise ValueError(f"{obj.get('id')}: expected one {name}, found {len(matches)}")
    return matches[0]


def resolve_entity_value(node, variable_resolution):
    if "value" in node:
        return node["value"]
    attrs=node.get("attributes",{})
    ref=attrs.get("var_ref")
    if not ref:
        raise ValueError(f"{node.get('name')}: no literal value or var_ref")
    resolved=variable_resolution.get(ref)
    if not resolved:
        raise ValueError(f"missing variable resolution for {ref}")
    if resolved.get("status")!="exact_static":
        raise ValueError(f"{ref}: variable is not statically resolved: {resolved.get('status')}")
    values=resolved.get("values",[])
    if len(values)!=1:
        raise ValueError(f"{ref}: expected one resolved value, found {len(values)}")
    return values[0]


def cell_from_pattern(pattern):
    syscalls=sorted(set(XATTR_SYSCALL_RE.findall(pattern)))
    if len(syscalls)!=1:
        raise ValueError(f"could not identify exactly one xattr syscall from pattern: {syscalls}")
    arches=[a for a in ARCHES if f"arch={a}" in pattern]
    if len(arches)!=1:
        raise ValueError(f"could not identify exactly one architecture from pattern: {arches}")
    if "auid=0" in pattern:
        subject="root"
    elif "auid>=1000" in pattern and "auid!=" in pattern:
        subject="interactive_users"
    else:
        raise ValueError("could not identify required AUID subject scope")
    if "always,exit" not in pattern or "exit,always" not in pattern:
        raise ValueError("pattern does not accept both audit action orderings")
    return {
        "syscall":syscalls[0],
        "architecture":arches[0],
        "subject":subject,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("ir",type=Path)
    ap.add_argument("provenance",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    ir=json.loads(args.ir.read_text())
    prov=json.loads(args.provenance.read_text())
    primary=prov.get("definition_ids",[])
    if len(primary)!=1:
        raise ValueError(f"expected one primary OVAL definition, found {primary}")
    primary_id=primary[0]

    definitions={x["id"]:x for x in ir.get("definitions",[])}
    tests={x["id"]:x for x in ir.get("tests",[])}
    objects={x["id"]:x for x in ir.get("objects",[])}
    if primary_id not in definitions:
        raise ValueError(f"primary definition {primary_id} is absent from IR")

    reachable_tests=set()
    walk_criteria(definitions[primary_id].get("criteria"),definitions,reachable_tests,{primary_id})
    if not reachable_tests:
        raise ValueError("primary definition reaches no tests")

    cells=[]
    source_checks=[]
    filepaths=set()
    for test_id in sorted(reachable_tests):
        test=tests.get(test_id)
        if not test:
            raise ValueError(f"missing reachable test {test_id}")
        if test.get("type")!="textfilecontent54_test":
            raise ValueError(f"{test_id}: unsupported test type {test.get('type')}")
        if test.get("states"):
            raise ValueError(f"{test_id}: normalizer expects no state references")
        refs=[x.get("object_ref") for x in test.get("objects",[])]
        if len(refs)!=1:
            raise ValueError(f"{test_id}: expected one object reference, found {refs}")
        obj=objects.get(refs[0])
        if not obj:
            raise ValueError(f"{test_id}: missing object {refs[0]}")
        if obj.get("type")!="textfilecontent54_object":
            raise ValueError(f"{refs[0]}: unsupported object type {obj.get('type')}")

        filepath=resolve_entity_value(entity(obj,"filepath"),ir.get("variable_resolution",{}))
        pattern=resolve_entity_value(entity(obj,"pattern"),ir.get("variable_resolution",{}))
        instance=entity(obj,"instance")
        if instance.get("attributes",{}).get("operation")!="greater than or equal" or str(instance.get("value"))!="1":
            raise ValueError(f"{obj['id']}: expected instance >= 1")

        filepaths.add(filepath)
        cell=cell_from_pattern(pattern)
        cells.append(tuple(cell[k] for k in ("syscall","architecture","subject")))
        source_checks.append({
            "test_id":test_id,
            "object_id":obj["id"],
            "cell":cell,
            "pattern_sha256":hashlib.sha256(pattern.encode()).hexdigest(),
        })

    if filepaths != {"/etc/audit/audit.rules"}:
        raise ValueError(f"unexpected audit rule sources: {sorted(filepaths)}")

    cell_set=set(cells)
    if len(cell_set)!=len(cells):
        raise ValueError("duplicate semantic matrix cells detected")

    syscalls=sorted({c[0] for c in cell_set})
    arches=sorted({c[1] for c in cell_set})
    subjects=sorted({c[2] for c in cell_set})
    expected=set(itertools.product(syscalls,arches,subjects))
    if cell_set != expected:
        missing=sorted(expected-cell_set)
        extra=sorted(cell_set-expected)
        raise ValueError(f"coverage is not a complete Cartesian matrix; missing={missing}, extra={extra}")

    if set(subjects)!={"interactive_users","root"} or set(arches)!={"b32","b64"}:
        raise ValueError(f"unexpected matrix dimensions: arches={arches}, subjects={subjects}")

    semantic={
        "capability":"linux.audit.configured_rules",
        "source":{"type":"audit_rules_file","path":"/etc/audit/audit.rules"},
        "required_coverage":{
            "syscalls":syscalls,
            "architectures":["b32","b64"],
            "subjects":[
                {
                    "name":"interactive_users",
                    "all":[
                        {"field":"auid","op":"ge","value":1000},
                        {"field":"auid","op":"not_in","value":[-1,4294967295,"unset"]},
                    ],
                },
                {"name":"root","field":"auid","op":"eq","value":0},
            ],
            "action_equivalent_to":["always,exit","exit,always"],
            "matrix_cell_count":len(cell_set),
        },
        "assertion":{"quantifier":"every","predicate":"covered_by_audit_rule"},
    }
    result={
        "format":"scap-ng-native-normalization-0.1",
        "normalizer":"linux_audit_xattr_syscall_matrix",
        "migration_status":"requires_review",
        "source":{
            "rule_id":prov.get("xccdf_rule_id"),
            "title":prov.get("xccdf_title"),
            "definition_id":primary_id,
            "oval_ir_sha256":ir.get("semantic_ir_sha256"),
            "published_source":prov.get("source"),
        },
        "semantic":semantic,
        "semantic_fingerprint_sha256":sha256_json(semantic),
        "source_checks":source_checks,
        "normalization_evidence":{
            "reachable_test_count":len(reachable_tests),
            "matrix_cell_count":len(cell_set),
            "all_patterns_resolved":True,
            "complete_cartesian_matrix":True,
            "note":"Candidate native normalization; differential execution required for exact_normalized.",
        },
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "rule":result["source"]["rule_id"],
        "tests":len(reachable_tests),
        "cells":len(cell_set),
        "fingerprint":result["semantic_fingerprint_sha256"],
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
