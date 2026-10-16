#!/usr/bin/env python3
"""Research #235: full source-exact English-first RHEL + Windows Assessments.

A reversible source-format experiment, NOT approved syntax/scanner parity.
Only source-observed Item, record, filter and field cardinalities are allowed.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import yaml
from research_english_first_04_evaluate import TO_ENGLISH, TO_SOURCE, transform, reject_naive_wmi_alternative_merge

CASES={
 "rhel9_initialization":"focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml",
 "win11_remote_desktop":"focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml",
}
FIELD_REQ="at_least_one_exists_and_all_match"
FIELD_OPS={"equals":"is","case_insensitive_equals":"equals_ignoring_case",
           "matches_regex":"matches_regex","greater_than":"greater_than","less_than":"less_than"}
REVERSE_OPS={v:k for k,v in FIELD_OPS.items()}
ITEM_REQS={
 "at_least_one_exists_and_all_match":("at_least_one_item_exists","every_collected_item"),
 "at_least_one_exists_and_some_match":("at_least_one_item_exists","some_collected_item"),
 "may_be_absent_and_all_match":("items_may_be_absent","every_collected_item"),
}
REV_ITEMS={v:k for k,v in ITEM_REQS.items()}

def exact(node,keys,what):
 if not isinstance(node,dict) or set(node)!=set(keys):
  raise ValueError("unexpected "+what+": "+repr(node)[:160])

def field_to_human(node):
 if not isinstance(node,dict) or node.get("require")!=FIELD_REQ: raise ValueError("wrong field scope")
 ops=set(node)-{"require"}
 if len(ops)!=1 or next(iter(ops)) not in FIELD_OPS: raise ValueError("unsupported field op")
 op=next(iter(ops))
 return {FIELD_OPS[op]:deepcopy(node[op])}

def field_to_native(node):
 if not isinstance(node,dict) or len(node)!=1: raise ValueError("invalid human field")
 op,val=next(iter(node.items()))
 if op not in REVERSE_OPS: raise ValueError("unknown field operator")
 return {"require":FIELD_REQ,REVERSE_OPS[op]:deepcopy(val)}

def state_to_human(node):
 if not isinstance(node,dict): raise ValueError("State not a mapping")
 if "and" in node:
  if set(node)!={"and","state_fields_require"} or node["state_fields_require"]!=FIELD_REQ:
   raise ValueError("unsupported group fields scope")
  return {"all_of":[state_to_human(child) for child in node["and"]],
          "all_fields_must_exist":True}
 exact(node,(next(iter(node)),),"single State")
 name,sub=next(iter(node.items()))
 if name=="result":
  exact(sub,("record",),"record wrapper")
  record=sub["record"]
  exact(record,("fields","require"),"record")
  if record["require"]!=FIELD_REQ: raise ValueError("record cardinality")
  return {"result":{"at_least_one_record_exists":True,"every_record":{
   key:field_to_human(value) for key,value in record["fields"].items()}}}
 return {name:field_to_human(sub)}

def state_to_native(node):
 if not isinstance(node,dict): raise ValueError("human State not a mapping")
 if "all_of" in node:
  exact(node,("all_of","all_fields_must_exist"),"group")
  if node["all_fields_must_exist"] is not True or not node["all_of"]: raise ValueError("invalid group")
  return {"and":[state_to_native(child) for child in node["all_of"]],
          "state_fields_require":FIELD_REQ}
 exact(node,(next(iter(node)),),"single human State")
 name,sub=next(iter(node.items()))
 if name=="result":
  exact(sub,("at_least_one_record_exists","every_record"),"records")
  if sub["at_least_one_record_exists"] is not True or not sub["every_record"]:raise ValueError("record existence")
  return {"result":{"record":{"fields":{
   key:field_to_native(val) for key,val in sub["every_record"].items()},
   "require":FIELD_REQ}}}
 return {name:field_to_native(sub)}

def readable_source(src):
 if isinstance(src,str): return {"source":src}
 if not isinstance(src,dict) or "capability" not in src: raise ValueError("unsupported native source")
 allowed={"capability","object_title","select","collect","filesystem","traversal","for_each","set"}
 if set(src)-allowed: raise ValueError("unmodeled Object properties")
 out={"inspect":src["capability"]}
 if "object_title" in src:out["description"]=deepcopy(src["object_title"])
 for a,b in (("select","where"),("collect","collect"),("filesystem","filesystem"),
             ("traversal","traversal"),("for_each","for_each_source")):
  if a in src:out[b]=deepcopy(src[a])
 if "set" in src:
  spec=src["set"];exact(spec,("operator","operands"),"Object Set")
  if spec["operator"] not in {"union","difference","intersection","complement"}:raise ValueError("bad Set operator")
  parts=[]
  for operand in spec["operands"]:
   if not isinstance(operand,dict) or set(operand)-{"object","filters"} or "object" not in operand:
    raise ValueError("bad Set operand")
   element={"from":readable_source(operand["object"])}
   if "filters" in operand:
    preds=[]
    for x in operand["filters"]:
     exact(x,("exclude",),"filter action")
     if not isinstance(x["exclude"],dict) or len(x["exclude"])!=1:raise ValueError("filter field")
     key,val=next(iter(x["exclude"].items()))
     preds.append({key:field_to_human(val)})
    element["exclude_if"]=preds
   parts.append(element)
  out["combine"]={spec["operator"]:parts}
 return out

def native_source(src):
 if isinstance(src,dict) and set(src)=={"source"}:
  if not isinstance(src["source"],str) or not src["source"]:raise ValueError("missing reference")
  return src["source"]
 if not isinstance(src,dict) or "inspect" not in src: raise ValueError("missing inspect")
 allowed={"inspect","description","where","collect","filesystem","traversal","for_each_source","combine"}
 if set(src)-allowed:raise ValueError("unexpected source key")
 out={"capability":src["inspect"]}
 if "description" in src:out["object_title"]=deepcopy(src["description"])
 for a,b in (("where","select"),("collect","collect"),("filesystem","filesystem"),
             ("traversal","traversal"),("for_each_source","for_each")):
  if a in src:out[b]=deepcopy(src[a])
 if "combine" in src:
  if not isinstance(src["combine"],dict) or len(src["combine"])!=1:raise ValueError("bad combine")
  op,parts=next(iter(src["combine"].items()))
  if op not in {"union","difference","intersection","complement"} or not isinstance(parts,list) or not parts:raise ValueError("bad Set")
  operands=[]
  for item in parts:
   if not isinstance(item,dict) or set(item)-{"from","exclude_if"} or "from" not in item:raise ValueError("bad operand")
   orig={"object":native_source(item["from"])}
   if "exclude_if" in item:
    if not isinstance(item["exclude_if"],list) or not item["exclude_if"]:raise ValueError("empty filters")
    original=[]
    for f in item["exclude_if"]:
     if not isinstance(f,dict) or len(f)!=1:raise ValueError("invalid filter")
     key,val=next(iter(f.items()))
     original.append({"exclude":{key:field_to_native(val)}})
    orig["filters"]=original
   operands.append(orig)
  out["set"]={"operator":op,"operands":operands}
 return out

def human_test(test):
 supported={"test_title","capability","object","states","reported_elements",
            "collected_items_require","states_match"}
 if set(test)-supported:raise ValueError("extra Test attributes "+repr(set(test)-supported))
 if test.get("reported_elements")!="all" or test.get("collected_items_require") not in ITEM_REQS:
  raise ValueError("unproven output or Item scope")
 states=test["states"]
 if not isinstance(states,list) or not states:raise ValueError("no States")
 if "states_match" in test:
  if test["states_match"]!="any" or len(states)<2:raise ValueError("unproven State alternatives")
  predicate={"any_of":[state_to_human(x) for x in states]}
 else:
  if len(states)!=1:raise ValueError("multi State without mode")
  predicate=state_to_human(states[0])
 presence,scope=ITEM_REQS[test["collected_items_require"]]
 return {"check":test["test_title"],"inspect":test["capability"],
         "gather":readable_source(test["object"]),
         "require":{presence:True,scope:predicate},"report_elements":"all"}

def native_test(src):
 exact(src,("check","inspect","gather","require","report_elements"),"human Test")
 if src["report_elements"]!="all":raise ValueError("unsupported reporting")
 require=src["require"]
 if not isinstance(require,dict) or len(require)!=2:raise ValueError("Item requirement")
 presence=[k for k in require if k in {"at_least_one_item_exists","items_may_be_absent"}]
 aggregation=[k for k in require if k in {"every_collected_item","some_collected_item"}]
 if len(presence)!=1 or len(aggregation)!=1:raise ValueError("missing explicit Item axes")
 p,a=presence[0],aggregation[0]
 if require[p] is not True or (p,a) not in REV_ITEMS:raise ValueError("unsupported Item pair")
 expr=require[a]
 if isinstance(expr,dict) and set(expr)=={"any_of"}:
  if len(expr["any_of"])<2:raise ValueError("bad alternative states")
  states=[state_to_native(x) for x in expr["any_of"]]
  mode={"states_match":"any"}
 else:
  states=[state_to_native(expr)]
  mode={}
 return {"test_title":src["check"],"capability":src["inspect"],
         "object":native_source(src["gather"]),"states":states,
         "reported_elements":"all","collected_items_require":REV_ITEMS[(p,a)],**mode}

def to_human(a):
 meta=deepcopy(a)
 tests=meta.pop("tests"); sources=meta.pop("shared_objects",{})
 evaluate=meta.pop("evaluate")
 return {"metadata":meta,"sources":{k:readable_source(v) for k,v in sources.items()},
         "checks":{k:human_test(v) for k,v in tests.items()},
         "evaluate":transform(evaluate,TO_ENGLISH)}

def to_native(c):
 exact(c,("metadata","sources","checks","evaluate"),"whole Assessment")
 doc=deepcopy(c["metadata"])
 doc["tests"]={k:native_test(v) for k,v in c["checks"].items()}
 doc["evaluate"]=transform(c["evaluate"],TO_SOURCE)
 if c["sources"]:doc["shared_objects"]={k:native_source(v) for k,v in c["sources"].items()}
 return doc

def run(root):
 out=[];negative=0
 for label,path in CASES.items():
  with (Path(root)/path).open(encoding="utf8") as f:
   original=yaml.safe_load(f)["assessment"]
  readable=to_human(original)
  converted=to_native(readable)
  if converted!=original:
   raise AssertionError("full source mismatch "+label+"\n"+repr(converted)[:2500]+"\n"+repr(original)[:2500])
  bad=deepcopy(readable)
  first=next(iter(bad["checks"].values()))
  first["require"].pop(next(iter(first["require"])))
  try:to_native(bad)
  except ValueError:negative+=1
  else:raise AssertionError("missing Item presence accepted")
  bad=deepcopy(readable);first=next(iter(bad["checks"].values()))
  first["gather"]={"inspect":"unix.file","combine":{"xor":[]}}
  try:to_native(bad)
  except ValueError:negative+=1
  else:raise AssertionError("unknown Set accepted")
  bad=deepcopy(readable);first=next(iter(bad["checks"].values()))
  first["require"]["unknown_collected_items"]=True
  try:to_native(bad)
  except ValueError:negative+=1
  else:raise AssertionError("extra Item rule accepted")
  out.append({"case":label,"source":path,"checks":len(original["tests"]),
              "shared_sources":len(original.get("shared_objects",{})),
              "proof":"identical complete Assessment source structure",
              "readable_first_check":next(iter(readable["checks"].values()))})
 return {"status":"RESEARCH SOURCE-EXACT ONLY; NO SCANNER SEMANTIC PROOF",
         "source_fixture_commit":"99cbceae8d594c44cb509df95975ac1676a2b44a",
         "cases":out,"negative_guards":negative,
         "wmi_counterexample":reject_naive_wmi_alternative_merge()}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--fixture-root",required=True)
 p.add_argument("--report")
 args=p.parse_args()
 result=run(args.fixture_root)
 if args.report:Path(args.report).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"cases":[{k:v for k,v in case.items() if k!="readable_first_check"} for case in result["cases"]],
                   "negative_guards":result["negative_guards"]},indent=2))
if __name__=="__main__":main()
