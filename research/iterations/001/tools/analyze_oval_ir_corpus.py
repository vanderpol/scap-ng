#!/usr/bin/env python3
"""Aggregate semantic coverage across generated per-rule OVAL IR files."""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    files=sorted(args.root.glob("*/rules/*/oval-ir.json"))
    element_counts=Counter()
    attr_counts=defaultdict(Counter)
    variable_status=Counter()
    variable_types=Counter()
    dependency_kinds=Counter()
    rules_with_variables=0
    rules_with_unsupported_variable_functions=0
    unsupported_ops=Counter()
    variable_ast_ops=Counter()
    per_benchmark=defaultdict(lambda:{
        "rules":0,"rules_with_variables":0,"variables":0,
        "exact_static_variables":0,"unsupported_variable_resolutions":0
    })


    def count_ast_ops(node):
        if not isinstance(node, dict):
            return
        op=node.get("op")
        if op:
            variable_ast_ops[op]+=1
        for arg in node.get("args",[]):
            count_ast_ops(arg)

    for path in files:
        ir=json.loads(path.read_text())
        benchmark=path.parts[-4]
        b=per_benchmark[benchmark]
        b["rules"]+=1

        for k,v in ir.get("features",{}).get("elements",{}).items():
            element_counts[k]+=v
        for attr,vals in ir.get("features",{}).get("attributes",{}).items():
            for value,count in vals.items():
                attr_counts[attr][value]+=count
        for edge in ir.get("dependency_edges",[]):
            dependency_kinds[edge.get("kind","unknown")]+=1

        for variable in ir.get("variables",[]):
            ast=variable.get("semantic_ast",{})
            if "expression" in ast:
                count_ast_ops(ast["expression"])

        vr=ir.get("variable_resolution",{})
        if vr:
            rules_with_variables+=1
            b["rules_with_variables"]+=1
        rule_has_unsupported=False
        for var_id,res in vr.items():
            status=res.get("status","unknown")
            variable_status[status]+=1
            b["variables"]+=1
            vtype=res.get("variable_type","unknown")
            variable_types[vtype]+=1
            if status=="exact_static":
                b["exact_static_variables"]+=1
            else:
                b["unsupported_variable_resolutions"]+=1
                rule_has_unsupported=True
                op=res.get("operation") or res.get("reason") or status
                unsupported_ops[op]+=1
        if rule_has_unsupported:
            rules_with_unsupported_variable_functions+=1

    out={
      "format":"scap-ng-iteration001-oval-semantic-inventory-0.1",
      "ir_files":len(files),
      "rules_with_variables":rules_with_variables,
      "rules_with_nonstatic_or_unsupported_variable_resolution":rules_with_unsupported_variable_functions,
      "variable_resolution_status":dict(sorted(variable_status.items())),
      "variable_types":dict(sorted(variable_types.items())),
      "variable_expression_operations":dict(sorted(variable_ast_ops.items())),
      "variable_function_model":{
        "oval_5_12_3_component_operations":[
          "arithmetic","begin","concat","count","end","escape_regex",
          "glob_to_regex","literal_component","merge","object_component",
          "regex_capture","split","substring","time_difference","unique",
          "variable_component"
        ],
        "explicit_ast_operations":sorted(variable_ast_ops.keys()),
        "static_evaluator_operations":[
          "arithmetic","begin","concat","count","end","escape_regex",
          "literal_component","split","substring","unique","variable_component"
        ],
      },
      "unsupported_or_dynamic_variable_operations":dict(sorted(unsupported_ops.items())),
      "dependency_edge_kinds":dict(sorted(dependency_kinds.items())),
      "element_counts":dict(sorted(element_counts.items())),
      "semantic_attribute_values":{
        a:dict(sorted(v.items())) for a,v in sorted(attr_counts.items())
      },
      "by_benchmark":dict(sorted(per_benchmark.items())),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "ir_files":out["ir_files"],
      "rules_with_variables":out["rules_with_variables"],
      "variable_resolution_status":out["variable_resolution_status"],
      "unsupported_or_dynamic_variable_operations":out["unsupported_or_dynamic_variable_operations"],
    },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
