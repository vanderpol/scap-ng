#!/usr/bin/env python3
"""Regression tests for cross-benchmark assessment reuse fingerprinting."""
from __future__ import annotations

import copy

from analyze_scapng_assessment_reuse import assessment_fingerprints


def assessment(prefix: str, literal: str) -> dict:
    obj=f"oval:{prefix}:obj:1"
    ste=f"oval:{prefix}:ste:1"
    tst=f"oval:{prefix}:tst:1"
    dfn=f"oval:{prefix}:def:1"
    return {
        "id":f"ng.{prefix}",
        "semantic_model":"scap-ng-generic-assessment-graph-0.1",
        "collect":{
            obj:{
                "source_object_id":obj,
                "source_type":"registry_object",
                "source_namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#windows",
                "query":[
                    {"kind":"element","name":"key","value":"Software\\Demo"},
                    {"kind":"element","name":"name","value":"Enabled"},
                ],
            }
        },
        "derive":{},
        "predicates":{
            ste:{
                "source_state_id":ste,
                "source_type":"registry_state",
                "source_namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#windows",
                "operator":"AND",
                "entities":[
                    {"kind":"element","name":"value","value":literal}
                ],
            }
        },
        "evaluate":{
            "tests":{
                tst:{
                    "source_test_id":tst,
                    "source_type":"registry_test",
                    "source_namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#windows",
                    "check":"all",
                    "check_existence":"at_least_one_exists",
                    "state_operator":"AND",
                    "collections":[obj],
                    "predicates":[ste],
                    "source_other":[],
                }
            },
            "definitions":{
                dfn:{
                    "source_definition_id":dfn,
                    "class":"compliance",
                    "criteria":{
                        "kind":"boolean",
                        "operator":"AND",
                        "negate":False,
                        "children":[
                            {"kind":"test_ref","test_ref":tst,"negate":False}
                        ],
                    },
                }
            },
        },
        "assert":{
            "definition_results":[dfn],
            "combination":"xccdf_source_check_semantics",
        },
    }


def main() -> int:
    a=assessment("publisher.a", "1")
    b=assessment("publisher.b", "1")
    c=assessment("publisher.c", "0")

    a_exact,a_shape=assessment_fingerprints(a)
    b_exact,b_shape=assessment_fingerprints(b)
    c_exact,c_shape=assessment_fingerprints(c)

    assert a_exact==b_exact, "source identifier changes must not defeat exact reuse"
    assert a_shape==b_shape
    assert a_exact!=c_exact, "literal semantic change must change exact fingerprint"
    assert a_shape==c_shape, "literal-only change should remain a parameterization candidate"

    d=copy.deepcopy(b)
    test=next(iter(d["evaluate"]["tests"].values()))
    test["check_existence"]="none_exist"
    d_exact,d_shape=assessment_fingerprints(d)
    assert d_exact!=a_exact
    assert d_shape!=a_shape, "existence semantics must not be abstracted as parameters"

    print("PASS: exact reuse and parameterization-candidate fingerprints")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
