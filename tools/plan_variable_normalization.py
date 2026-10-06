#!/usr/bin/env python3
"""Classify native SCAP-NG Variable normalization opportunities.

Research-only. This does not rewrite content. It uses the deduplicated Variable
inventory produced by audit_for_each_candidates.py and deliberately keeps
lossless conversion proof separate from authoring/readability recommendations.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path


def classify(v):
    shape=v.get("shape")
    usage=v.get("usage_class")
    consumers=v.get("consumers") or []
    root=v.get("root_operator")

    if shape=="external":
        return {
            "disposition":"keep_named_input",
            "automatic_normalization":False,
            "reason":"External Variables are explicit runtime/policy inputs and should retain stable named identity and provenance.",
        }

    if shape=="constant":
        return {
            "disposition":"keep_or_inline_constant_after_policy_review",
            "automatic_normalization":False,
            "reason":"Constant value sets are ordinary data, not iteration. Single-use literals may be authoring-simplified later, but named constants can carry useful reuse and migration identity.",
        }

    if shape=="pure_object_projection":
        if usage=="single_use_direct_variable_test":
            return {
                "disposition":"keep_named_projection_for_direct_test",
                "automatic_normalization":False,
                "reason":"The projected value set is the direct subject of a Variable Test. Current native variable.value Test semantics consume a named Variable; do not erase that identity until a direct-expression Test contract is independently proven.",
            }
        if usage in {"single_use_object_selector","single_use_state_expected_value"}:
            return {
                "disposition":"candidate_inline_flattened_projection",
                "automatic_normalization":False,
                "reason":"Single-use object_component is projection plumbing. A native Collection-field value expression could remove the named Variable only if it preserves OVAL flattening, zero/missing-field error behavior, datatype/status propagation and consumer var_check semantics.",
            }
        if usage=="single_use_variable_input":
            return {
                "disposition":"candidate_inline_projection_into_expression",
                "automatic_normalization":False,
                "reason":"Projection is used only as an input to another Variable expression. It may be safely inlinable only after function/error/datatype propagation is proven.",
            }
        if usage=="multi_use":
            return {
                "disposition":"keep_named_projection_for_reuse",
                "automatic_normalization":False,
                "reason":"The same projected value set has multiple consumers; a named reusable value is likely clearer and avoids duplicated dependency expressions.",
            }
        return {
            "disposition":"review_projection",
            "automatic_normalization":False,
            "reason":"Projection usage does not fit a currently proven simplification shape.",
        }

    if shape=="transform":
        if usage=="single_use_direct_variable_test":
            return {
                "disposition":"keep_named_transform_for_direct_test",
                "automatic_normalization":False,
                "reason":"The computed value set is directly tested. Current native variable.value Test semantics use a named Variable, so this is not temporary selector plumbing.",
            }
        if usage and usage.startswith("single_use_"):
            return {
                "disposition":"candidate_inline_transform_expression",
                "automatic_normalization":False,
                "reason":"Single-use computed Variable may be temporary authoring plumbing. Inlining is only safe if the exact OVAL function AST, Cartesian-product semantics, datatype conversion, errors and consumer quantifiers remain unchanged.",
            }
        return {
            "disposition":"keep_named_transform_for_reuse",
            "automatic_normalization":False,
            "reason":"Reusable computed value should remain a named value unless later evidence shows an editor/compiler-only temporary is clearer.",
        }

    if shape=="pure_variable_alias":
        return {
            "disposition":"review_alias_elimination",
            "automatic_normalization":False,
            "reason":"A pure Variable alias may be removable, but datatype/status/provenance semantics must be compared before eliminating the identity.",
        }

    if shape=="pure_literal":
        return {
            "disposition":"review_literal_inline",
            "automatic_normalization":False,
            "reason":"A local Variable wrapping one literal is likely authoring plumbing, but effective datatype and reuse must be retained.",
        }

    return {
        "disposition":"preserve_unclassified_variable",
        "automatic_normalization":False,
        "reason":"No safe normalization class has been established.",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    audit=json.loads(Path(args.audit).read_text())
    rows=[]
    for v in audit.get("unique_variable_inventory",[]):
        decision=classify(v)
        rows.append({**v,**decision})

    summary=Counter(r["disposition"] for r in rows)
    root=Counter((r.get("root_operator") or "unknown") for r in rows)
    single_use=Counter()
    for r in rows:
        if (r.get("usage_class") or "").startswith("single_use_"):
            single_use[r.get("shape") or "unknown"]+=1

    report={
        "label":audit.get("label"),
        "policy":{
            "automatic_normalization_enabled":False,
            "principle":"Named Variables should represent inputs, reusable values, or meaningful transformations; single-use projection/expression plumbing may be simplified only with exact semantic proof.",
        },
        "summary":dict(summary),
        "root_operator_counts":dict(root),
        "single_use_by_shape":dict(single_use),
        "variables":rows,
    }
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "label":report["label"],
        "summary":report["summary"],
        "single_use_by_shape":report["single_use_by_shape"],
    },indent=2))


if __name__=="__main__":
    main()
