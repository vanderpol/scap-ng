#!/usr/bin/env python3
"""#237: lower Boolean trees of fully-supported converted-source B Tests.

Every original Test must be referenced and fully lowered. Supports source
AND/OR and direct Test leaf only; no short-circuit assumption or NOT/ONE/XOR.
No attempt to infer missing or unsupported OVAL branches as TRUE.
"""
from __future__ import annotations

from research_b_source_textfile_lowering import lower_state_free_textfile_assessment
from research_b_source_partition_lowering import lower_state_free_partition_assessment
from research_b_source_textfile_state_lowering import lower_single_capture_textfile_assessment
from research_b_source_wmi_lowering import lower_state_free_wmi_assessment
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_shell_lowering import lower_source_shell_assessment


LEAF_LOWERERS=(
    lower_state_free_textfile_assessment,
    lower_single_capture_textfile_assessment,
    lower_state_free_partition_assessment,
    lower_state_free_wmi_assessment,
    lower_source_registry_assessment,
    lower_source_shell_assessment,
)
METADATA={"id","version","assessment_title","mode","class","purpose",
          "specification","tests","evaluate"}


def lower_source_boolean_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("one converted source Assessment required")
    a=source["assessment"]
    if (not isinstance(a,dict) or a.get("mode")!="automated" or
            set(a)-METADATA):
        raise ValueError("Boolean source has unsupported shared/Variable/input metadata")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)<2:
        raise ValueError("Boolean source lowerer requires two or more Tests")
    cache={}
    active=set()
    visiting_count=[0]

    def lower_leaf(name):
        if not isinstance(name,str) or name not in tests:
            raise ValueError("unknown or invalid referenced source Test "+str(name))
        if name in cache:return cache[name]
        doc={"assessment":{k:v for k,v in a.items() if k not in ("tests","evaluate")}}
        doc["assessment"]["tests"]={name:tests[name]}
        doc["assessment"]["evaluate"]={"test":name}
        errors=[]
        for lower in LEAF_LOWERERS:
            try:
                out=lower(doc)
                if out["source_test_id"]!=name:
                    raise ValueError("source Test ID changed during lowering")
                cache[name]=out
                return out
            except (ValueError,KeyError,TypeError) as exc:
                errors.append(str(exc)[:100])
        raise ValueError("unlowerable source Test "+name+": "+" | ".join(errors))

    def compile_expression(node,depth=0):
        visiting_count[0]+=1
        if depth>64 or visiting_count[0]>2000:
            raise ValueError("source expression exceeds bounded size/depth")
        if not isinstance(node,dict) or len(node)!=1:
            raise ValueError("source evaluate branch must have one operator")
        if "test" in node:
            lowered=lower_leaf(node["test"])
            active.add(node["test"])
            return lowered
        operator=next(iter(node))
        if operator not in {"all","any"}:
            raise ValueError("unsupported source Boolean operator "+str(operator))
        children=node[operator]
        if not isinstance(children,list) or len(children)<2:
            raise ValueError("source Boolean group must have two or more branches")
        return {"kind":"logic","operator":operator,
                "children":[compile_expression(c,depth+1) for c in children]}

    result=compile_expression(a.get("evaluate"))
    if active!=set(tests):
        raise ValueError("source Test definitions not all reachable from evaluate: "+
                         repr(sorted(set(tests)-active)))
    return result
