#!/usr/bin/env python3
"""Independent 0.4 review-archive reference audit (not evaluator conformance)."""
import argparse
from collections import Counter
import json
import unittest
import zipfile

def scan(documents):
    ids, rules, catalogs, problems, counts = {}, [], [], [], Counter()
    for path,doc in documents.items():
        a=doc.get("assessment")
        if isinstance(a,dict):
            ident=a.get("id")
            if not ident: problems.append((path,"missing Assessment ID"))
            elif ident in ids: problems.append((path,"duplicate Assessment ID",ident,ids[ident]))
            else: ids[ident]=path
        if isinstance(doc.get("rule"),dict): rules.append((path,doc["rule"]))
        if isinstance(doc.get("applicability"),dict):
            catalogs.append((path,doc["applicability"]))
    counts.update(documents=len(documents),assessments=len(ids),rules=len(rules))
    for path,rule in rules:
        choices=rule.get("assessment_choices") or {}
        if rule.get("default_assessment_choice") not in choices:
            problems.append((path,"undeclared default choice"))
        for label,choice in choices.items():
            counts["rule_choice_links"]+=1
            ident=choice.get("assessment") if isinstance(choice,dict) else None
            if ident not in ids:problems.append((path,"unresolved Rule choice",label,ident))
    for path,catalog in catalogs:
        for label,condition in (catalog.get("conditions") or {}).items():
            counts["applicability_assessment_links"]+=1
            ident=condition.get("assessment") if isinstance(condition,dict) else None
            if ident not in ids:
                problems.append((path,"unresolved Applicability Assessment",label,ident))
    for path,doc in documents.items():
        a=doc.get("assessment")
        if not isinstance(a,dict):continue
        tests=a.get("tests") or {}
        objects=a.get("shared_objects") or {}
        variables=a.get("variables") or {}
        deps=a.get("dependencies") or {}
        def eval_refs(node,where):
            if not isinstance(node,dict) or not node:
                problems.append((path,"invalid evaluation node",where));return
            # Logical groups and leaves have exactly one key. The ONLY
            # multi-key expression is IF/THEN/ELSE, whose branches must be
            # complete. Avoid silently scanning two competing operators.
            conditional = ({'if', 'then', 'else'} <= set(node)
                           and not set(node) - {'if', 'then', 'else', 'else_if'})
            if len(node)!=1 and not conditional:
                problems.append((path,"ambiguous evaluate operator scope",where,sorted(node)));return
            for key,val in node.items():
                if key=="test":
                    counts["evaluate_test_leaves"]+=1
                    if val not in tests:problems.append((path,"unresolved evaluate Test",where,val))
                elif key=="assessment":
                    counts["evaluate_assessment_leaves"]+=1
                    if val not in deps:problems.append((path,"unresolved evaluate Assessment dependency",where,val))
                elif key in ("all","any","one","odd","and","or","xor"):
                    if not isinstance(val,list) or not val:
                        problems.append((path,"invalid evaluate group",where,key))
                    else:
                        for i,child in enumerate(val):eval_refs(child,where+"/"+key+"/"+str(i))
                elif key in ("not_applicable", "not_evaluated"):
                    if not isinstance(val,dict) or set(val)!={'reason'} or not isinstance(val.get("reason"),str) or not val["reason"].strip():
                        problems.append((path,"invalid " + key + " reason",where))
                elif key == 'else_if':
                    if not isinstance(val, list) or not val:
                        problems.append((path, 'invalid ordered else_if', where))
                    else:
                        for i, branch in enumerate(val):
                            if not isinstance(branch, dict) or set(branch) != {'if', 'then'}:
                                problems.append((path, 'invalid else_if entry', where, i))
                                continue
                            for part in ('if', 'then'):
                                eval_refs(branch[part], where + '/else_if/' + str(i) + '/' + part)
                elif key in ("not","if","then","else"):
                    eval_refs(val,where+"/"+key)
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
    def test_applicability_assessment_closure(self):
        self.d["applicability.json"]={"applicability":{"id":"catalog", "conditions":{
            "condition.valid":{"assessment":"a"}}}}
        counts,bad=scan(self.d)
        self.assertEqual(bad,[])
        self.assertEqual(counts["applicability_assessment_links"],1)
        self.d["applicability.json"]["applicability"]["conditions"]["condition.missing"]={
            "assessment":"ng.shared.absent"}
        counts,bad=scan(self.d)
        self.assertEqual(counts["applicability_assessment_links"],2)
        self.assertTrue(any("unresolved Applicability Assessment" in str(item) and
                            "ng.shared.absent" in str(item) for item in bad))
    def test_missing_evaluate_test(self):
        self.d["a.json"]["assessment"]["evaluate"]={"test":"missing"}
        self.assertIn("unresolved evaluate Test",str(scan(self.d)[1]))
    def test_new_evaluate_and_or_xor_with_legacy_source_compatibility(self):
        self.d["a.json"]["assessment"]["evaluate"]={"and":[
            {"test":"x"},{"or":[{"test":"x"},
                {"xor":[{"test":"x"},{"test":"x"},{"test":"x"}]}]},
            {"all":[{"test":"x"},{"odd":[{"test":"x"}]}]}]}
        counts,bad=scan(self.d)
        self.assertEqual(bad,[])
        self.assertEqual(counts["evaluate_test_leaves"],7)

    def test_mixed_evaluate_operators_and_empty_groups_fail_closed(self):
        for invalid in (
            {"and":[{"test":"x"}],"or":[{"test":"x"}]},
            {"and":[]},
            {"or":"one_or_more"},
            {"xor":[]},
            {"if":{"test":"x"},"then":{"test":"x"}},
            {"not_applicable":{"reason":""}},
        ):
            with self.subTest(invalid=invalid):
                self.d["a.json"]["assessment"]["evaluate"]=invalid
                self.assertTrue(scan(self.d)[1])

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
