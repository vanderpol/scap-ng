#!/usr/bin/env python3
"""Independent 0.4 review-archive reference audit (not evaluator conformance)."""
import argparse
from collections import Counter
import json
import unittest
import zipfile

def scan(documents):
    ids, rules, problems, counts = {}, [], [], Counter()
    for path,doc in documents.items():
        a=doc.get("assessment")
        if isinstance(a,dict):
            ident=a.get("id")
            if not ident: problems.append((path,"missing Assessment ID"))
            elif ident in ids: problems.append((path,"duplicate Assessment ID",ident,ids[ident]))
            else: ids[ident]=path
        if isinstance(doc.get("rule"),dict): rules.append((path,doc["rule"]))
    counts.update(documents=len(documents),assessments=len(ids),rules=len(rules))
    for path,rule in rules:
        choices=rule.get("assessment_choices") or {}
        if rule.get("default_assessment_choice") not in choices:
            problems.append((path,"undeclared default choice"))
        for label,choice in choices.items():
            counts["rule_choice_links"]+=1
            ident=choice.get("assessment") if isinstance(choice,dict) else None
            if ident not in ids:problems.append((path,"unresolved Rule choice",label,ident))
    for path,doc in documents.items():
        a=doc.get("assessment")
        if not isinstance(a,dict):continue
        tests=a.get("tests") or {}
        objects=a.get("shared_objects") or {}
        variables=a.get("variables") or {}
        deps=a.get("dependencies") or {}
        def eval_refs(node,where):
            if not isinstance(node,dict):
                problems.append((path,"invalid evaluation node",where));return
            for key,val in node.items():
                if key=="test":
                    counts["evaluate_test_leaves"]+=1
                    if val not in tests:problems.append((path,"unresolved evaluate Test",where,val))
                elif key=="assessment":
                    counts["evaluate_assessment_leaves"]+=1
                    if val not in deps:problems.append((path,"unresolved evaluate Assessment dependency",where,val))
                elif key in ("all","any","one","odd"):
                    if not isinstance(val,list):problems.append((path,"invalid evaluate group",where,key))
                    else:
                        for i,child in enumerate(val):eval_refs(child,where+"/"+key+"/"+str(i))
                elif key in ("not","if","then","else"):eval_refs(val,where+"/"+key)
                else:problems.append((path,"unknown evaluate construct",where,key))
        if a.get("evaluate") is not None:eval_refs(a["evaluate"],"evaluate")
        for name,test in tests.items():
            obj=test.get("object")
            if isinstance(obj,str):
                counts["shared_object_references"]+=1
                if obj not in objects:problems.append((path,"unresolved Test Object",name,obj))
        def vars_refs(node,where):
            if isinstance(node,dict):
                for key,val in node.items():
                    if key=="variable" and isinstance(val,str):
                        counts["variable_references"]+=1
                        if val not in variables:problems.append((path,"unresolved Variable",where,val))
                    vars_refs(val,where+"/"+str(key))
            elif isinstance(node,list):
                for i,val in enumerate(node):vars_refs(val,where+"/"+str(i))
        for key in ("tests","shared_objects","variables"):vars_refs(a.get(key),key)
    counts["unresolved"]=len(problems)
    return dict(counts),problems

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.d={
          "a.json":{"assessment":{"id":"a","tests":{"x":{"object":"o","collect":{"variable":"v"}}},
             "shared_objects":{"o":{}},"variables":{"v":{}},"evaluate":{"test":"x"}}},
          "rule.json":{"rule":{"assessment_choices":{"automated":{"assessment":"a"}},
             "default_assessment_choice":"automated"}}}
    def test_valid(self):
        counts,bad=scan(self.d)
        self.assertEqual(bad,[])
        self.assertEqual(counts["variable_references"],1)
    def test_missing_rule_choice(self):
        self.d["rule.json"]["rule"]["assessment_choices"]["automated"]["assessment"]="missing"
        self.assertIn("unresolved Rule choice",str(scan(self.d)[1]))
    def test_missing_evaluate_test(self):
        self.d["a.json"]["assessment"]["evaluate"]={"test":"missing"}
        self.assertIn("unresolved evaluate Test",str(scan(self.d)[1]))
    def test_missing_object(self):
        self.d["a.json"]["assessment"]["tests"]["x"]["object"]="missing"
        self.assertIn("unresolved Test Object",str(scan(self.d)[1]))
    def test_missing_variable(self):
        self.d["a.json"]["assessment"]["tests"]["x"]["collect"]["variable"]="missing"
        self.assertIn("unresolved Variable",str(scan(self.d)[1]))
    def test_duplicate_id(self):
        self.d["b.json"]={"assessment":{"id":"a"}}
        self.assertIn("duplicate Assessment ID",str(scan(self.d)[1]))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json-archive")
    parser.add_argument("--report")
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(GraphTests)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():raise SystemExit(1)
    if args.json_archive:
        with zipfile.ZipFile(args.json_archive) as archive:
            docs={n:json.loads(archive.read(n)) for n in archive.namelist()
                  if n.startswith("authoring/") and n.endswith(".json")}
        counts,bad=scan(docs)
        report={"status":"PASS" if not bad else "FAIL","counts":counts,"issues":bad[:20],
                "scope":"Static authoring reference integrity only; not evaluator or scanner"}
        print(json.dumps(report,indent=2))
        if args.report:
            with open(args.report,"w",encoding="utf-8") as file:json.dump(report,file,indent=2)
        if bad:raise SystemExit(1)

if __name__=="__main__":main()
