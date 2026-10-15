#!/usr/bin/env python3
"""0.4 research: one discoverable field-key/require/operator-key grammar.

Semantic source preservation tiers:
  EXACT: lowering reconstructs identical parsed published 0.3 Assessment.
  MODEL_EQUIVALENT: State-free Test check is inert per pinned OVAL 5.12.3
                    truth tables; lower with check all, retain audit record.
No native scanner parity is claimed for normalized cases.
"""
from collections import Counter,defaultdict
from copy import deepcopy
import argparse,json,zipfile
from pathlib import Path
from research_04_three_benchmark_quantifier import BENCHMARKS
import research_04_rhel9_compact_preview as legacy
from research_04_field_key_authoring import fold_document,unfold_document,fold_node,unfold_node
from oval_result_truth_tables import evaluate_collected_object_test

EXISTS={
    "none":"none_exist",
    "one":"only_one_exists",
    "one_or_more":"at_least_one_exists",
    "all":"all_exist",
    "optional":"may_be_absent",
}
MATCHES={"all":"all_match","one":"only_one_matches",
         "one_or_more":"some_match","none":"none_match"}
CODES={(e,m):f"{EXISTS[e]}_and_{MATCHES[m]}" for e in EXISTS for m in MATCHES}
CODES[("one","all")]="only_one_exists_and_matches"
CODES[("one_or_more","all")]="at_least_one_exists_and_all_match"
CODES[("one_or_more","one_or_more")]="at_least_one_exists_and_some_match"
CODES[("none","all")]="none_exist"
CODES[("optional","all")]="may_be_absent_and_all_match"
CODES[("all","all")]="all_exist_and_all_match"
# The field-level none/all and Test none/all use identical source pair, though
# they evaluate different populations. No hidden scope inference.
PAIR_BY_NAME={}
for pair,name in CODES.items():
    if name in PAIR_BY_NAME and pair!=PAIR_BY_NAME[name]:
        raise AssertionError(f"Alias collision: {name}")
    PAIR_BY_NAME[name]=pair

LOGIC={"all","any","one","odd"}
PRESENCE_LABEL={e:EXISTS[e] for e in EXISTS}
PRESENCE_BACK={v:k for k,v in PRESENCE_LABEL.items()}
OP_ALIAS={"pattern_match":"matches_regex"}
OP_BACK={"matches_regex":"pattern_match"}

def from_source_pair(node, *, scope, with_states, notes, label):
    out=deepcopy(node)
    exist=out.get("existence")
    match=out.get("match")
    if exist is None or match is None:
        raise ValueError(f"Missing explicit existence/match at {label}: {exist}/{match}")
    if exist not in EXISTS or match not in MATCHES:
        raise ValueError(f"Unrecognized source pair at {label}: {exist}/{match}")
    if "require" in out:
        raise ValueError(f"Mixing require and existence at {label}")
    if scope=="test" and not with_states:
        name=PRESENCE_LABEL[exist]
        if match!="all":
            notes.append({"site":label,"old_existence":exist,"old_match":match,
                          "canonical_check_normalized_to":"all",
                          "proof":"State-free Test check never consulted in OVAL generic results model"})
    else:
        name=CODES[(exist,match)]
    out.pop("existence")
    out.pop("match")
    out["require"]=name
    return out

def back_to_source_pair(node, *, scope, with_states):
    out=deepcopy(node)
    name=out.pop("require",None)
    if name is None:
        return out
    if "existence" in out or "match" in out:
        raise ValueError("Mixed pair semantics are not allowed in one-grammar authoring")
    if scope=="test" and not with_states and name in PRESENCE_BACK:
        pair=(PRESENCE_BACK[name],"all")
    elif name in PAIR_BY_NAME:
        pair=PAIR_BY_NAME[name]
        if scope=="test" and not with_states:
            raise ValueError(f"State-free Test should use presence-only form: {name}")
    else:
        raise ValueError(f"Unknown or context-invalid require: {name}, scope={scope}")
    out["existence"],out["match"]=pair
    return out

def encode_states(states, *, notes, path, counters):
    out=[]
    for i,entry in enumerate(states):
        site=f"{path}[{i}]"
        if isinstance(entry,dict) and len(entry)==1:
            name,payload=next(iter(entry.items()))
            if name in LOGIC and isinstance(payload,list):
                out.append({name:encode_states(payload,notes=notes,path=site+"."+name,counters=counters)})
                continue
            if isinstance(payload,dict):
                counters["field_key"]+=1
                item=deepcopy(payload)
                record=item.get("record")
                if isinstance(record,dict):
                    counters["record_wrapper"]+=1
                    if "existence" in record and "match" in record:
                        item["record"]=from_source_pair(record,scope="record",with_states=True,
                            notes=notes,label=site+".record")
                        counters["record_require"]+=1
                    else:
                        raise ValueError(f"Record missing required native pair: {site}")
                    rec=item["record"]
                    fields=rec.get("fields")
                    if not isinstance(fields,dict):
                        raise ValueError(f"Malformed record fields: {site}")
                    rec["fields"]={}
                    for field,sub in fields.items():
                        rec["fields"][field]=from_source_pair(sub,scope="record_field",
                            with_states=True,notes=notes,label=site+".record.fields."+field)
                        counters["record_field_require"]+=1
                else:
                    item=from_source_pair(item,scope="field",with_states=True,notes=notes,label=site)
                    counters["scalar_field_require"]+=1
                out.append({name:item})
                continue
        out.append(deepcopy(entry))
    return out

def decode_states(states):
    out=[]
    for entry in states:
        if isinstance(entry,dict) and len(entry)==1:
            key,val=next(iter(entry.items()))
            if key in LOGIC and isinstance(val,list):
                out.append({key:decode_states(val)})
                continue
            if isinstance(val,dict):
                node=deepcopy(val)
                rec=node.get("record")
                if isinstance(rec,dict):
                    orig=back_to_source_pair(rec,scope="record",with_states=True)
                    if not isinstance(orig.get("fields"),dict):
                        raise ValueError("Record.fields missing")
                    orig["fields"]={name:back_to_source_pair(sub,scope="record_field",with_states=True)
                                    for name,sub in orig["fields"].items()}
                    node["record"]=orig
                else:
                    node=back_to_source_pair(node,scope="field",with_states=True)
                out.append({key:node})
                continue
        out.append(deepcopy(entry))
    return out

def encode_filter_tree(node,notes,counters,path="assessment"):
    """Object Set filters use the SAME field predicate and require grammar.

    Example:
      - action: exclude
        field: mode
        operation: greater_than
        value: 493
        existence: one_or_more
        match: all
    becomes:
      - exclude:
          mode:
            greater_than: 493
            require: at_least_one_exists_and_all_match
    No change to Set filter selection or error propagation.
    """
    if isinstance(node,list):
        return [encode_filter_tree(item,notes,counters,f"{path}[{i}]")
                for i,item in enumerate(node)]
    if not isinstance(node,dict):
        return deepcopy(node)
    out={}
    for key,value in node.items():
        if key=="filters" and isinstance(value,list):
            updated=[]
            for i,entry in enumerate(value):
                if not isinstance(entry,dict):
                    raise ValueError(f"Filter at {path}[{i}] is not a mapping")
                action=entry.get("action")
                if action not in ("include","exclude"):
                    raise ValueError(f"Filter missing explicit include/exclude at {path}[{i}]")
                if "field" not in entry and not any(k in entry for k in LOGIC):
                    raise ValueError(f"Filter without field or logical predicate at {path}[{i}]")
                original_pred={k:deepcopy(v) for k,v in entry.items() if k!="action"}
                folded=fold_node(original_pred,Counter())
                single=encode_states([folded],notes=notes,
                    path=f"{path}.filters[{i}]",counters=counters)[0]
                updated.append({action:single})
                counters["object_set_filter_verbs"]+=1
            out[key]=updated
        else:
            out[key]=encode_filter_tree(value,notes,counters,f"{path}.{key}")
    return out


def decode_filter_tree(node):
    if isinstance(node,list):
        return [decode_filter_tree(item) for item in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    out={}
    for key,value in node.items():
        if key=="filters" and isinstance(value,list):
            updated=[]
            for entry in value:
                if not isinstance(entry,dict) or len(entry)!=1:
                    raise ValueError("Filter must be one include/exclude mapping")
                action,expr=next(iter(entry.items()))
                if action not in ("include","exclude"):
                    raise ValueError("Unknown filter action")
                original=unfold_node(decode_states([expr])[0])
                if not isinstance(original,dict) or "action" in original:
                    raise ValueError("Filter payload is not valid inline State")
                updated.append({"action":action,**original})
            out[key]=updated
        else:
            out[key]=decode_filter_tree(value)
    return out

def encode_auxiliary_pairs(node,notes,counters,path="assessment"):
    """The one grammar must include nested Object collection/select field pairs.

    Unlike Test pairs, these are field/value predicates inside collectors,
    e.g., Windows WMI cmdlet Object.collect.select.fields.property. Preserve
    their original pair exactly; no Test/State-free shortcut applies.
    """
    if isinstance(node,list):
        return [encode_auxiliary_pairs(v,notes,counters,f"{path}[{i}]")
                for i,v in enumerate(node)]
    if not isinstance(node,dict):
        return deepcopy(node)
    out={k:encode_auxiliary_pairs(v,notes,counters,f"{path}.{k}")
         for k,v in node.items()}
    if "existence" in out or "match" in out:
        out=from_source_pair(out,scope="collector_field",with_states=True,
                             notes=notes,label=path)
        counters["other_typed_field_require"]+=1
        counters[f"other_typed_field_location:{path.split('.fields.')[0] if '.fields.' in path else path}"]+=1
    return out


def decode_auxiliary_pairs(node):
    if isinstance(node,list):
        return [decode_auxiliary_pairs(v) for v in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    out={k:decode_auxiliary_pairs(v) for k,v in node.items()}
    if isinstance(out.get("require"),str) and out["require"] in PAIR_BY_NAME:
        out=back_to_source_pair(out,scope="collector_field",with_states=True)
    return out

def operator_enum():
    # Use pinned 0.3 authoritative operator vocabulary, not freehand aliases.
    schema=json.loads((Path(__file__).resolve().parents[1]/
        "schema/v0.3.0/capability-common.schema.json").read_text())
    ops=schema["$defs"]["comparison_operation"]["enum"]
    if "matches_regex" in ops:raise AssertionError("Aliased operation collision")
    return set(ops),{OP_ALIAS.get(x,x) for x in ops}

def encode_operations(tree,counters,operations):
    if isinstance(tree,list):
        return [encode_operations(x,counters,operations) for x in tree]
    if not isinstance(tree,dict):
        return deepcopy(tree)
    if "operation" in tree and "value" in tree:
        if tree["operation"] not in operations:
            raise ValueError(f"Nonstandard comparison operator: {tree['operation']}")
        op=tree["operation"]
        key=OP_ALIAS.get(op,op)
        if key in tree:
            raise ValueError(f"Comparator key collision: {key}")
        counters[f"comparison:{key}"]+=1
        # Preserve value type, array value_match, Variable/Input, datum and
        # reported_elements; no operator coercion or default inference.
        return {**{k:encode_operations(v,counters,operations) for k,v in tree.items()
                   if k not in ("operation","value")},key:deepcopy(tree["value"])}
    return {k:encode_operations(v,counters,operations) for k,v in tree.items()}

def decode_operations(tree,normalized_ops):
    if isinstance(tree,list):
        return [decode_operations(x,normalized_ops) for x in tree]
    if not isinstance(tree,dict):
        return deepcopy(tree)
    present=[k for k in tree if k in normalized_ops]
    if len(present)==1 and "operation" not in tree and "value" not in tree:
        k=present[0]
        value=deepcopy(tree[k])
        op=OP_BACK.get(k,k)
        return {**{name:decode_operations(v,normalized_ops) for name,v in tree.items()
                   if name!=k},"value":value,"operation":op}
    return {k:decode_operations(v,normalized_ops) for k,v in tree.items()}

def make_single(original):
    out,counts=fold_document(original)
    notes=[]
    a=out["assessment"]
    tests=a.get("tests") or {}
    for tid,test in list(tests.items()):
        if not isinstance(test,dict):continue
        has_states="states" in test and test["states"] is not None
        if isinstance(test.get("states"),list):
            test["states"]=encode_states(test["states"],notes=notes,
                path=f"tests.{tid}.states",counters=counts)
        tests[tid]=from_source_pair(test,scope="test",with_states=has_states,
            notes=notes,label=f"tests.{tid}")
        counts["test_require"]+=1
    out=encode_filter_tree(out,notes,counts)
    out=encode_auxiliary_pairs(out,notes,counts)
    ops,normalized_ops=operator_enum()
    out=encode_operations(out,counts,ops)
    return out,counts,notes

def lower_single(compact):
    _,normalized_ops=operator_enum()
    out=decode_operations(compact,normalized_ops)
    out=decode_filter_tree(out)
    tests=out["assessment"].get("tests") or {}
    for tid,test in list(tests.items()):
        if not isinstance(test,dict):continue
        has_states="states" in test and test["states"] is not None
        test=back_to_source_pair(test,scope="test",with_states=has_states)
        if isinstance(test.get("states"),list):
            test["states"]=decode_states(test["states"])
        tests[tid]=test
    out=unfold_document(out)
    return decode_auxiliary_pairs(out)

def normalize_inert_source_checks(original,notes):
    out=deepcopy(original)
    for note in notes:
        # The only model-equivalent normalization is State-free Test match.
        prefix="tests."
        if not note["site"].startswith(prefix):
            raise ValueError(f"Unexpected semantic rewrite request: {note}")
        tid=note["site"][len(prefix):]
        test=out["assessment"]["tests"][tid]
        if "states" in test and test["states"] is not None:
            raise ValueError("Refusing to drop matching aggregation from State-bearing Test")
        if test["existence"]!=note["old_existence"] or test["match"]!=note["old_match"]:
            raise ValueError("Provenance mismatch for source normalization")
        test["match"]="all"
    return out

def check_no_parallel_comparison_or_cardinality_grammar(tree,location="assessment"):
    """Fail closed if a proposed compact Assessment still embeds legacy pairs.

    A Set's operator (union/difference) is not a comparison operator/value,
    and cannot be conflated with an observed State/selector comparison.
    """
    if isinstance(tree,list):
        for i,item in enumerate(tree):
            check_no_parallel_comparison_or_cardinality_grammar(item,f"{location}[{i}]")
    elif isinstance(tree,dict):
        if "existence" in tree or "match" in tree:
            raise ValueError(f"Parallel longhand quantifier in unified source at {location}")
        if "operation" in tree and "value" in tree:
            raise ValueError(f"Parallel longhand comparator in unified source at {location}")
        for key,item in tree.items():
            check_no_parallel_comparison_or_cardinality_grammar(item,f"{location}.{key}")

def benchmark_dir(names,target):
    selectors={"rhel_9":lambda n:"rhel" in n and "9" in n,
               "windows_11":lambda n:"windows" in n and "11" in n and "server" not in n,
               "windows_server_2025":lambda n:"windows" in n and "2025" in n}
    found=[n for n in names if selectors[target](n)]
    if len(found)!=1:raise ValueError(f"Unresolved {target}: {found}")
    return found[0]

def audit(source):
    aggregated={}
    with zipfile.ZipFile(source) as z:
        folders={name.split("/")[1] for name in z.namelist()
                 if name.startswith("authoring/") and "/rules/" in name}
        for benchmark in BENCHMARKS:
            original_prefix=legacy.SOURCE_PREFIX
            legacy.SOURCE_PREFIX="authoring/"+benchmark_dir(folders,benchmark)+"/"
            try:
                docs,raw=legacy.archive_contents(z)
            finally:
                legacy.SOURCE_PREFIX=original_prefix
            rules=legacy.benchmark_rule_paths(docs)
            selected={}
            defaults=Counter()
            for rid,(_,rule) in rules.items():
                defaults[rule["default_assessment_choice"]]+=1
                choice=(rule.get("assessment_choices") or {}).get("automated")
                if choice:
                    selected[rid]=choice["assessment"]
            coverage={}
            metrics=Counter()
            notes_all=[]
            sample={}
            for path,doc in docs.items():
                if not isinstance(doc,dict) or (doc.get("assessment") or {}).get("mode")!="automated":
                    continue
                short,counts,notes=make_single(doc)
                check_no_parallel_comparison_or_cardinality_grammar(short)
                recovered=lower_single(short)
                expected=normalize_inert_source_checks(doc,notes)
                if recovered!=expected:
                    raise ValueError(f"Normalized reconstructed mismatch: {path}")
                if notes and any("states" in doc["assessment"]["tests"][n["site"].split("tests.",1)[1]] for n in notes):
                    raise ValueError(f"Unexpected hidden State rewrite: {path}")
                metrics.update(counts)
                metrics["assessments_verified"]+=1
                metrics["exact_source_assessments"]+=not bool(notes)
                metrics["model_normalized_assessments"]+=bool(notes)
                notes_all.extend([{"assessment_file":path,**n} for n in notes])
                aid=doc["assessment"]["id"]
                if aid in coverage:raise ValueError(f"Duplicate id: {aid}")
                coverage[aid]={"path":path,"notes":notes,"compact":short}
                if len(sample)<5 and any("record_wrapper"==k for k in counts):
                    sample[path]=short
            for rid,aid in selected.items():
                if aid not in coverage:raise ValueError(f"{rid} missing {aid}")
            aggregated[benchmark]={
                "rules":len(rules),
                "default_counts":dict(defaults),
                "automated_rules":len(selected),
                "automated_rules_covered_by_single_syntax":len(selected),
                "assessments_compiled":metrics["assessments_verified"],
                "assessments_exact_source":metrics["exact_source_assessments"],
                "assessments_with_state_free_model_normalizations":metrics["model_normalized_assessments"],
                "field_key_predicates":metrics["field_key"],
                "object_set_filters_compacted":metrics["object_set_filter_verbs"],
                "auxiliary_collector_fields_compacted":metrics["other_typed_field_require"],
                "record_wrappers":metrics["record_wrapper"],
                "record_field_requirements":metrics["record_field_require"],
                "source_match_normalizations":notes_all,
                "no_unrepresented_quantifier_pairs":True,
                "literal_operators_covered":sum(v for k,v in metrics.items() if k.startswith("comparison:")),
                "top_comparators":sorted(((k,v) for k,v in metrics.items() if k.startswith("comparison:")),key=lambda x:-x[1])[:12],
                "sample_records":list(sample)[:4],
            }
    return {"status":"ONE_GRAMMAR_RESEARCH_NOT_APPROVED",
            "source":"published 0.3 six-STIG authoring",
            "core_comparator_shape":"field_name: {operation_name: typed_operand, require: natural_enum}",
            "require_semantics":"20 existence/match pairs; State-free check normalized only on reference-model proof",
            "benchmarks":aggregated,
            "full_require_vocabulary":{f"{e}/{m}":CODES[(e,m)] for e in EXISTS for m in MATCHES},
            "limitations":[
                "Exact parsed source lowering unless a State-free Test used non-all check; for those normalization uses pinned six-valued OVAL reference helper, not a live scanner differential.",
                "No 0.4 normative schema yet; this only proves a structurally unambiguous source grammar and lowering.",
                "The source 0.3 Test with none-existence and a State remains State-bearing; no automatic removal of State.",
                "Dynamic capability field validation and full OVAL family support remain implementation gates.",
                "Existing published 0.3 release remains unchanged.",
            ]}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=audit(args.authoring_zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    for b,r in report["benchmarks"].items():
        print("SINGLE_STANDARD",b,json.dumps({k:v for k,v in r.items() if k not in ("source_match_normalizations","top_comparators","sample_records")},sort_keys=True),flush=True)
        print("NORMALIZATION_CASES",b,r["source_match_normalizations"],flush=True)
    print("COMPLETE_REQUIRE_PAIRS",len(report["full_require_vocabulary"]))
