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
 "dns_zone_signing":"focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml",
 "apache_configuration":"focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml",
}
FIELD_REQ="at_least_one_exists_and_all_match"
FIELD_OPS={"equals":"is","case_insensitive_equals":"equals_ignoring_case",
           "matches_regex":"matches_regex","greater_than":"greater_than","less_than":"less_than",
           "greater_than_or_equal":"at_least","less_than_or_equal":"at_most"}
REVERSE_OPS={v:k for k,v in FIELD_OPS.items()}
ITEM_REQS={
 "at_least_one_exists_and_all_match":("at_least_one_item_exists","every_collected_item"),
 "at_least_one_exists_and_some_match":("at_least_one_item_exists","some_collected_item"),
 "may_be_absent_and_all_match":("items_may_be_absent","every_collected_item"),
 "all_exist_and_all_match":("all_collected_items_exist","every_collected_item"),
 "at_least_one_exists_and_only_one_matches":("at_least_one_item_exists","exactly_one_collected_item"),
 "only_one_exists_and_only_one_matches":("exactly_one_item_exists","exactly_one_collected_item"),
 "only_one_exists_and_matches":("exactly_one_item_exists","every_collected_item"),
 "may_be_absent_and_none_match":("items_may_be_absent","no_collected_item"),
 "may_be_absent_and_some_match":("items_may_be_absent","some_collected_item"),
 "all_exist_and_none_match":("all_collected_items_exist","no_collected_item"),
}
REV_ITEMS={v:k for k,v in ITEM_REQS.items()}
STATELESS_PRESENCE={
 "at_least_one_exists":"at_least_one",
 "only_one_exists":"exactly_one",
 "none_exist":"none",
 "all_exist":"all_exist",
 "may_be_absent":"may_be_absent",
}
REV_STATELESS={v:k for k,v in STATELESS_PRESENCE.items()}

def exact(node,keys,what):
 if not isinstance(node,dict) or set(node)!=set(keys):
  raise ValueError("unexpected "+what+": "+repr(node)[:160])

FIELD_MODES={
 "at_least_one_exists_and_all_match":"ordinary",
 "may_be_absent_and_all_match":"when_present_",
 "only_one_exists_and_matches":"exactly_one_",
 "none_exist":"no_values_exist",
}

def field_to_human(node, inherited=False):
 if not isinstance(node,dict):raise ValueError("State field not a mapping")
 mode = ("inherited" if inherited else FIELD_MODES.get(node.get("require")))
 if mode is None:raise ValueError("unverified field presence/cardinality")
 if inherited and "require" in node:raise ValueError("cannot silently override inherited fields")
 operations=set(node)-{"require"}
 if len(operations)!=1 or next(iter(operations)) not in FIELD_OPS:
  raise ValueError("unmodeled field comparator")
 op=next(iter(operations))
 value=deepcopy(node[op])
 if mode=="no_values_exist":
  return {"no_values_exist":True,"source_comparison":{FIELD_OPS[op]:value}}
 if mode=="ordinary" or mode=="inherited":
  return {FIELD_OPS[op]:value}
 return {mode+FIELD_OPS[op]:value}

def field_to_native(node, inherited=False):
 if not isinstance(node,dict) or not node:raise ValueError("empty human field")
 if set(node)=={"no_values_exist","source_comparison"}:
  if inherited or node["no_values_exist"] is not True:raise ValueError("invalid absence mode")
  expr=node["source_comparison"]
  if not isinstance(expr,dict) or len(expr)!=1:raise ValueError("must retain source absent comparison")
  op,val=next(iter(expr.items()))
  if op not in REVERSE_OPS:raise ValueError("unsupported absence comparator")
  return {"require":"none_exist",REVERSE_OPS[op]:deepcopy(val)}
 if len(node)!=1:raise ValueError("field expects one value operator")
 op,val=next(iter(node.items()))
 if inherited:
  if op not in REVERSE_OPS:raise ValueError("inherited State field op")
  return {REVERSE_OPS[op]:deepcopy(val)}
 for mode,req in (
  ("when_present_","may_be_absent_and_all_match"),
  ("exactly_one_","only_one_exists_and_matches"),
  ("","at_least_one_exists_and_all_match")):
  base=op[len(mode):] if op.startswith(mode) else None
  if base in REVERSE_OPS:
   return {"require":req,REVERSE_OPS[base]:deepcopy(val)}
 raise ValueError("unsupported State field requirement or operator")

def state_to_human(node, inherited=False):
 if not isinstance(node,dict): raise ValueError("State not a mapping")
 if "and" in node:
  if set(node)!={"and","state_fields_require"} or node["state_fields_require"]!=FIELD_REQ:
   raise ValueError("unsupported group fields scope")
  return {"all_of":[state_to_human(child, inherited=True) for child in node["and"]],
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
 return {name:field_to_human(sub,inherited=inherited)}

def state_to_native(node, inherited=False):
 if not isinstance(node,dict): raise ValueError("human State not a mapping")
 if "all_of" in node:
  exact(node,("all_of","all_fields_must_exist"),"group")
  if node["all_fields_must_exist"] is not True or not node["all_of"]: raise ValueError("invalid group")
  return {"and":[state_to_native(child,inherited=True) for child in node["all_of"]],
          "state_fields_require":FIELD_REQ}
 exact(node,(next(iter(node)),),"single human State")
 name,sub=next(iter(node.items()))
 if name=="result":
  exact(sub,("at_least_one_record_exists","every_record"),"records")
  if sub["at_least_one_record_exists"] is not True or not sub["every_record"]:raise ValueError("record existence")
  return {"result":{"record":{"fields":{
   key:field_to_native(val) for key,val in sub["every_record"].items()},
   "require":FIELD_REQ}}}
 return {name:field_to_native(sub,inherited=inherited)}

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
    if not isinstance(item["exclude_if"],list):raise ValueError("filters must be a list")
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
            "collected_items_require","states_match","state_fields_require"}
 if set(test)-supported:raise ValueError("extra Test attributes "+repr(set(test)-supported))
 if test.get("reported_elements")!="all":
  raise ValueError("unproven output")
 item_mode=test.get("collected_items_require")
 if "states" not in test:
  if item_mode not in STATELESS_PRESENCE or "states_match" in test or "state_fields_require" in test:
   raise ValueError("unsupported State-free Item mode")
  result={"check":test["test_title"],"inspect":test["capability"],
          "require":{"collected_items":STATELESS_PRESENCE[item_mode]},
          "report_elements":"all"}
  if "object" in test:
   result["gather"]=readable_source(test["object"])
  return result
 if item_mode not in ITEM_REQS:
  raise ValueError("unproven output or Item scope")
 states=test["states"]
 if not isinstance(states,list) or not states:raise ValueError("no States")
 inherited=("state_fields_require" in test)
 if inherited and test["state_fields_require"]!=FIELD_REQ:
  raise ValueError("unproven Test-level field inheritance")
 mode=test.get("states_match")
 if mode in {"any","all"}:
  if len(states)<2:raise ValueError("State aggregation needs at least two States")
  readable_key="any_of" if mode=="any" else "all_states"
  predicate={readable_key:[state_to_human(x,inherited=inherited) for x in states]}
 elif mode is None:
  if len(states)!=1:raise ValueError("multi-State requires explicit mode")
  predicate=state_to_human(states[0],inherited=inherited)
 else:
  raise ValueError("unproven State match")
 presence,scope=ITEM_REQS[test["collected_items_require"]]
 readable={"check":test["test_title"],"inspect":test["capability"],
         "require":{presence:True,scope:predicate},"report_elements":"all"}
 if "object" in test:
  readable["gather"]=readable_source(test["object"])
 if inherited:
  readable["all_state_fields_exist"]=True
 return readable

def native_test(src):
 mandatory={"check","inspect","require","report_elements"}
 permitted=mandatory|{"all_state_fields_exist","gather"}
 if not isinstance(src,dict) or set(src)-permitted or not mandatory.issubset(src):
  raise ValueError("unrecognized check shape")
 if src["report_elements"]!="all":raise ValueError("unsupported reporting")
 inherited=("all_state_fields_exist" in src)
 if inherited and src["all_state_fields_exist"] is not True:
  raise ValueError("state-fields inheritance must be explicit")
 require=src["require"]
 if not isinstance(require,dict):raise ValueError("Item requirement")
 if set(require)=={"collected_items"}:
  if inherited:raise ValueError("State-free cannot define State fields")
  item_mode=REV_STATELESS.get(require["collected_items"])
  if item_mode is None:raise ValueError("unsupported State-free existence")
  native={"test_title":src["check"],"capability":src["inspect"],
          "reported_elements":"all","collected_items_require":item_mode}
  if "gather" in src:native["object"]=native_source(src["gather"])
  return native
 if len(require)!=2:raise ValueError("Item existence and matching must be explicit")
 presence=[k for k in require if k in {"at_least_one_item_exists","items_may_be_absent",
                                       "all_collected_items_exist","exactly_one_item_exists"}]
 aggregation=[k for k in require if k in {"every_collected_item","some_collected_item",
                                          "exactly_one_collected_item","no_collected_item"}]
 if len(presence)!=1 or len(aggregation)!=1:raise ValueError("missing explicit Item axes")
 p,a=presence[0],aggregation[0]
 if require[p] is not True or (p,a) not in REV_ITEMS:raise ValueError("unsupported Item pair")
 expr=require[a]
 if isinstance(expr,dict) and set(expr)=={"any_of"}:
  if len(expr["any_of"])<2:raise ValueError("bad alternative States")
  states=[state_to_native(x,inherited=inherited) for x in expr["any_of"]]
  mode={"states_match":"any"}
 elif isinstance(expr,dict) and set(expr)=={"all_states"}:
  if len(expr["all_states"])<2:raise ValueError("bad conjunctive States")
  states=[state_to_native(x,inherited=inherited) for x in expr["all_states"]]
  mode={"states_match":"all"}
 else:
  states=[state_to_native(expr,inherited=inherited)]
  mode={}
 native={"test_title":src["check"],"capability":src["inspect"],
         "states":states,
         "reported_elements":"all","collected_items_require":REV_ITEMS[(p,a)],**mode}
 if "gather" in src:
  native["object"]=native_source(src["gather"])
 if inherited:native["state_fields_require"]=FIELD_REQ
 return native

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

def run(root, examples_dir=None):
 out=[];negative=0
 if examples_dir:
  Path(examples_dir).mkdir(parents=True,exist_ok=True)
 for label,path in CASES.items():
  with (Path(root)/path).open(encoding="utf8") as f:
   original=yaml.safe_load(f)["assessment"]
  readable=to_human(original)
  converted=to_native(readable)
  if converted!=original:
   raise AssertionError("full source mismatch "+label+"\n"+repr(converted)[:2500]+"\n"+repr(original)[:2500])
  if examples_dir:
   text_header=(
    "# RESEARCH ONLY - experimental English-first YAML, NOT current SCAP-NG v0.4\n"
    "# Exact full source-Assessment structure reconstruction verified by CI.\n"
    "# NOT scanner runnable; no OVAL six-state runtime/evidence proof.\n"
    "# Pinned original: vanderpol/scap-ng-editor-sample-data@99cbceae8d594c44cb509df95975ac1676a2b44a\n"
    "# File: "+path+"\n\n"
   )
   (Path(examples_dir)/(label+".research.yaml")).write_text(
    text_header+yaml.safe_dump(readable,sort_keys=False,allow_unicode=True,width=105),
    encoding="utf8")
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
 p.add_argument("--examples-dir")
 args=p.parse_args()
 result=run(args.fixture_root,examples_dir=args.examples_dir)
 if args.report:Path(args.report).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"cases":[{k:v for k,v in case.items() if k!="readable_first_check"} for case in result["cases"]],
                   "negative_guards":result["negative_guards"]},indent=2))
if __name__=="__main__":main()
