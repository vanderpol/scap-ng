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
           "greater_than_or_equal":"at_least","less_than_or_equal":"at_most",
           "not_equal":"is_not","case_insensitive_not_equal":"is_not_ignoring_case",
           "version_greater_than_or_equal":"version_at_least",
           "bitwise_and":"bitwise_and"}
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
 "at_least_one_exists_and_some_match":"some_values_",
 "at_least_one_exists_and_none_match":"no_values_",
 "may_be_absent_and_none_match":"when_present_no_values_",
 "at_least_one_exists_and_only_one_matches":"exactly_one_matching_value_",
 "only_one_exists_and_only_one_matches":"exactly_one_observed_value_",
 "all_exist_and_all_match":"all_values_exist_and_",
 "all_exist_and_none_match":"all_values_exist_and_no_",
 "may_be_absent_and_some_match":"when_present_some_values_",
 "none_exist":"no_values_exist",
}

def field_to_human(node, inherited=False):
 if not isinstance(node,dict):raise ValueError("State field not a mapping")
 if "datatype" in node or "value_match" in node:
  attrs={k:deepcopy(v) for k,v in node.items() if k in {"datatype","value_match"}}
  comparison=field_to_human({k:v for k,v in node.items() if k not in attrs},inherited=inherited)
  if "datatype" in attrs and (not isinstance(attrs["datatype"],str) or not attrs["datatype"]):
   raise ValueError("unsupported data type")
  if "value_match" in attrs and attrs["value_match"] not in {"all","one","one_or_more","none","odd"}:
   raise ValueError("unsupported operand value match")
  return {"compare":comparison,**({"data_type":attrs["datatype"]} if "datatype" in attrs else {}),
          **({"value_match":attrs["value_match"]} if "value_match" in attrs else {})}
 if inherited and "require" in node:
  # An explicit exceptional leaf must remain explicit even under a Test/group default.
  return {"local_override":field_to_human(node,inherited=False)}
 mode = ("inherited" if inherited else FIELD_MODES.get(node.get("require")))
 if mode is None:raise ValueError("unverified field presence/cardinality")
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
 if "compare" in node:
  if set(node)-{"compare","data_type","value_match"}:raise ValueError("unknown comparison modifier")
  raw=field_to_native(node["compare"],inherited=inherited)
  if "data_type" in node:
   if not isinstance(node["data_type"],str) or not node["data_type"]:raise ValueError("invalid datatype")
   raw["datatype"]=node["data_type"]
  if "value_match" in node:
   if node["value_match"] not in {"all","one","one_or_more","none","odd"}:
    raise ValueError("invalid operand value_match")
   raw["value_match"]=node["value_match"]
  return raw
 if inherited and set(node)=={"local_override"}:
  return field_to_native(node["local_override"],inherited=False)
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
 prefixes=[(prefix,mode) for mode,prefix in FIELD_MODES.items()
           if prefix not in {"ordinary","no_values_exist"}]
 prefixes.sort(key=lambda pair:-len(pair[0]))
 for prefix,mode in prefixes:
  base=op[len(prefix):] if op.startswith(prefix) else None
  if base in REVERSE_OPS:
   return {"require":mode,REVERSE_OPS[base]:deepcopy(val)}
 if op in REVERSE_OPS:
  return {"require":FIELD_REQ,REVERSE_OPS[op]:deepcopy(val)}
 raise ValueError("unsupported State field requirement or operator")

def state_to_human(node, inherited=False):
 if not isinstance(node,dict): raise ValueError("State not a mapping")
 if "and" in node or "or" in node:
  op="and" if "and" in node else "or"
  if set(node)-{op,"state_fields_require"}:
   raise ValueError("unsupported group fields scope")
  local_scope="state_fields_require" in node
  if local_scope and node["state_fields_require"]!=FIELD_REQ:
   raise ValueError("unsupported group field requirements")
  if not isinstance(node[op],list) or not node[op]:
   raise ValueError("empty State group")
  key="all_of" if op=="and" else "any_of_fields"
  out={key:[state_to_human(child,inherited=inherited or local_scope) for child in node[op]]}
  if local_scope:out["all_fields_must_exist"]=True
  return out
 exact(node,(next(iter(node)),),"single State")
 name,sub=next(iter(node.items()))
 if isinstance(sub,dict) and "record" in sub:
  exact(sub,("record",),"record wrapper")
  record=sub["record"]
  exact(record,("fields","require"),"record")
  record_mode={
   "at_least_one_exists_and_all_match":"every_record",
   "at_least_one_exists_and_some_match":"some_record",
   "at_least_one_exists_and_only_one_matches":"exactly_one_matching_record",
  }.get(record["require"])
  if record_mode is None:raise ValueError("unproven record cardinality")
  if not isinstance(record["fields"],dict) or not record["fields"]:
   raise ValueError("missing record fields")
  return {name:{"at_least_one_record_exists":True,record_mode:{
   key:field_to_human(value) for key,value in record["fields"].items()}}}
 return {name:field_to_human(sub,inherited=inherited)}

def state_to_native(node, inherited=False):
 if not isinstance(node,dict): raise ValueError("human State not a mapping")
 if "all_of" in node or "any_of_fields" in node:
  key="all_of" if "all_of" in node else "any_of_fields"
  if set(node)-{key,"all_fields_must_exist"}:raise ValueError("unrecognized State group attributes")
  local_scope="all_fields_must_exist" in node
  if local_scope and node["all_fields_must_exist"] is not True:raise ValueError("invalid local group scope")
  children=node[key]
  if not isinstance(children,list) or not children:raise ValueError("empty group")
  op="and" if key=="all_of" else "or"
  result={op:[state_to_native(child,inherited=inherited or local_scope) for child in children]}
  if local_scope:result["state_fields_require"]=FIELD_REQ
  return result
 exact(node,(next(iter(node)),),"single human State")
 name,sub=next(iter(node.items()))
 if isinstance(sub,dict) and "at_least_one_record_exists" in sub:
  record_keys=set(sub)&{"every_record","some_record","exactly_one_matching_record"}
  if len(record_keys)!=1:raise ValueError("ambiguous record matching")
  record_mode=next(iter(record_keys))
  exact(sub,("at_least_one_record_exists",record_mode),"records")
  if sub["at_least_one_record_exists"] is not True or not isinstance(sub[record_mode],dict) or not sub[record_mode]:
   raise ValueError("record existence")
  source_mode={"every_record":"at_least_one_exists_and_all_match",
               "some_record":"at_least_one_exists_and_some_match",
               "exactly_one_matching_record":"at_least_one_exists_and_only_one_matches"}[record_mode]
  return {name:{"record":{"fields":{
   key:field_to_native(val) for key,val in sub[record_mode].items()},
   "require":source_mode}}}
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
    filters=operand["filters"]
    if not isinstance(filters,list):raise ValueError("filter list not an array")
    sequence=[]
    for x in filters:
     if not isinstance(x,dict) or len(x)!=1:raise ValueError("filter action")
     action,condition=next(iter(x.items()))
     if action not in {"include","exclude"}:raise ValueError("unsupported filter action")
     if not isinstance(condition,dict) or len(condition)!=1:raise ValueError("filter field")
     key,val=next(iter(condition.items()))
     sequence.append((action,{key:field_to_human(val)}))
    actions={action for action,_ in sequence}
    if len(actions)==1:
     action=sequence[0][0]
     element[action+"_if"]=[pred for _,pred in sequence]
    elif not sequence:
     element["exclude_if"]=[]
    else:
     element["ordered_filters"]=[{action+"_if":pred} for action,pred in sequence]
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
   if not isinstance(item,dict) or set(item)-{"from","exclude_if","include_if","ordered_filters"} or "from" not in item:
    raise ValueError("bad operand")
   flags=set(item)&{"exclude_if","include_if","ordered_filters"}
   if len(flags)>1:raise ValueError("cannot mix filter presentation modes")
   orig={"object":native_source(item["from"])}
   if flags:
    action=next(iter(flags))
    if not isinstance(item[action],list):raise ValueError("filters must be a list")
    original=[]
    if action in {"exclude_if","include_if"}:
     mode=action[:-3]
     for field in item[action]:
      if not isinstance(field,dict) or len(field)!=1:raise ValueError("invalid filter")
      key,val=next(iter(field.items()))
      original.append({mode:{key:field_to_native(val)}})
    else:
     for entry in item[action]:
      if not isinstance(entry,dict) or len(entry)!=1:raise ValueError("invalid ordered filter")
      key,field=next(iter(entry.items()))
      if key not in {"exclude_if","include_if"} or not isinstance(field,dict) or len(field)!=1:
       raise ValueError("invalid ordered action")
      name,value=next(iter(field.items()))
      original.append({key[:-3]:{name:field_to_native(value)}})
    orig["filters"]=original
   operands.append(orig)
  out["set"]={"operator":op,"operands":operands}
 return out

def human_test(test):
 supported={"test_title","capability","object","states","reported_elements",
            "collected_items_require","states_match","state_fields_require","variable"}
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
  if "variable" in test:
   if not isinstance(test["variable"],str) or not test["variable"]:raise ValueError("invalid direct Test Variable")
   result["input_from"]={"variable":test["variable"]}
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
 if "variable" in test:
  if not isinstance(test["variable"],str) or not test["variable"]:raise ValueError("invalid direct Test Variable")
  readable["input_from"]={"variable":test["variable"]}
 return readable

def native_test(src):
 mandatory={"check","inspect","require","report_elements"}
 permitted=mandatory|{"all_state_fields_exist","gather","input_from"}
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
  if "input_from" in src:
   exact(src["input_from"],("variable",),"Test input")
   var=src["input_from"]["variable"]
   if not isinstance(var,str) or not var:raise ValueError("invalid Test Variable source")
   native["variable"]=var
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
 if "input_from" in src:
  exact(src["input_from"],("variable",),"Test input")
  var=src["input_from"]["variable"]
  if not isinstance(var,str) or not var:raise ValueError("invalid Test Variable source")
  native["variable"]=var
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
