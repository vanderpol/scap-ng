#!/usr/bin/env python3
import unittest

from scap_upconvert_v003.conditional_modernization import modernize_conditionals_v1


class ConditionalModernizationTests(unittest.TestCase):
    def doc(self, evaluate):
        return {
            "assessment":{
                "id":"example",
                "version":1,
                "mode":"automated",
                "class":"compliance",
                "purpose":"assessment",
                "specification":{
                    "id":"scap-ng.pre-alpha.assessment",
                    "version":"0.3.0",
                },
                "tests":{
                    "g":{"test_title":"guard","reported_elements":"all","capability":"x"},
                    "p":{"test_title":"then","reported_elements":"all","capability":"x"},
                    "q":{"test_title":"else","reported_elements":"all","capability":"x"},
                    "r":{"test_title":"other","reported_elements":"all","capability":"x"},
                },
                "evaluate":evaluate,
            }
        }

    def test_rewrites_exact_complementary_guard(self):
        source=self.doc({
            "any":[
                {"all":[{"test":"g"},{"test":"p"}]},
                {"all":[{"not":{"test":"g"}},{"test":"q"}]},
            ]
        })
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],{
            "if":{"test":"g"},
            "then":{"test":"p"},
            "else":{"test":"q"},
        })
        self.assertTrue(report["rewrite_performed"])
        self.assertEqual(len(report["applied"]),1)
        self.assertFalse(report["rule_id_allowlist"])

    def test_reversed_branches_preserve_then_else_meaning(self):
        source=self.doc({
            "any":[
                {"all":[{"not":{"test":"g"}},{"test":"q"}]},
                {"all":[{"test":"g"},{"test":"p"}]},
            ]
        })
        result,_=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],{
            "if":{"test":"g"},
            "then":{"test":"p"},
            "else":{"test":"q"},
        })

    def test_multiple_payload_terms_remain_all(self):
        source=self.doc({
            "any":[
                {"all":[{"test":"g"},{"test":"p"},{"test":"r"}]},
                {"all":[{"not":{"test":"g"}},{"test":"q"}]},
            ]
        })
        result,_=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"]["then"],{
            "all":[{"test":"p"},{"test":"r"}]
        })

    def enum_doc(self, left_values, right_values, *, overlap=False, existence="some"):
        doc=self.doc({
            "any":[
                {"all":[{"test":"guard-a"},{"test":"p"}]},
                {"all":[{"test":"guard-b"},{"test":"q"}]},
            ]
        })
        a=doc["assessment"]
        a["objects"]={
            "role-object":{
                "capability":"windows.wmi.query",
                "collect":{"namespace":"root\\cimv2","query":"SELECT DomainRole FROM win32_computersystem"},
            }
        }
        a["states"]={}
        for prefix,values in (("a",left_values),("b",right_values)):
            ids=[]
            for index,value in enumerate(values):
                sid=f"state-{prefix}-{index}"
                ids.append(sid)
                a["states"][sid]={
                    "state_title":f"state {prefix} {value}",
                    "capability":"windows.wmi.query",
                    "state":{
                        "field":"result",
                        "record":{
                            "match":"all",
                            "existence":"some",
                            "fields":{
                                "domainrole":{
                                    "value":str(value),
                                    "operation":"equal",
                                    "datatype":"string",
                                    "match":"all",
                                    "existence":"some",
                                }
                            },
                        },
                    },
                }
            tid=f"guard-{prefix}"
            a["tests"][tid]={
                "test_title":f"guard {prefix}",
                "reported_elements":"all",
                "capability":"windows.wmi.query",
                "object":"role-object",
                "check_existence":existence,
                "check":"all",
                "states":ids,
                "states_match":"any",
            }
        return doc

    def test_rewrites_mutually_exclusive_enum_guards_without_assuming_exhaustive(self):
        source=self.enum_doc([2,3],[4,5])
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],{
            "if":{"test":"guard-a"},
            "then":{"test":"p"},
            "else":{"all":[{"test":"guard-b"},{"test":"q"}]},
        })
        self.assertTrue(report["rewrite_performed"])
        applied=report["applied"][0]
        self.assertEqual(applied["pattern_class"],"mutually_exclusive_enum_guards")
        self.assertTrue(applied["else_retains_guard"])
        self.assertEqual(applied["enum_proof"]["left_values"],["2","3"])
        self.assertEqual(applied["enum_proof"]["right_values"],["4","5"])
        self.assertFalse(applied["enum_proof"]["exhaustive"])

    def test_overlapping_enum_guards_are_not_rewritten(self):
        source=self.enum_doc([2,3],[3,4])
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],source["assessment"]["evaluate"])
        self.assertFalse(report["rewrite_performed"])

    def test_enum_guard_requires_positive_existence(self):
        source=self.enum_doc([2,3],[4,5],existence="optional")
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],source["assessment"]["evaluate"])
        self.assertFalse(report["rewrite_performed"])

    def test_alternative_compliance_paths_are_not_rewritten(self):
        evaluate={
            "any":[
                {"all":[{"test":"p"},{"test":"r"}]},
                {"all":[{"test":"q"},{"test":"g"}]},
            ]
        }
        source=self.doc(evaluate)
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],evaluate)
        self.assertFalse(report["rewrite_performed"])
        self.assertEqual(report["review_required"][0]["reasons"],
                         ["no_proven_conditional_guard_pattern"])

    def test_ambiguous_two_complementary_guards_fail_closed(self):
        evaluate={
            "any":[
                {"all":[{"test":"g"},{"test":"p"}]},
                {"all":[{"not":{"test":"g"}},{"not":{"test":"p"}}]},
            ]
        }
        source=self.doc(evaluate)
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],evaluate)
        self.assertFalse(report["rewrite_performed"])
        self.assertEqual(report["review_required"][0]["reasons"],
                         ["ambiguous_multiple_complementary_guards"])

    def test_nested_candidate_rewrites_without_touching_outer_all(self):
        source=self.doc({
            "all":[
                {"test":"r"},
                {"any":[
                    {"all":[{"test":"g"},{"test":"p"}]},
                    {"all":[{"not":{"test":"g"}},{"test":"q"}]},
                ]},
            ]
        })
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result["assessment"]["evaluate"],{
            "all":[
                {"test":"r"},
                {"if":{"test":"g"},"then":{"test":"p"},"else":{"test":"q"}},
            ]
        })
        self.assertEqual(report["applied"][0]["path"],"/assessment/evaluate/all/1")

    def test_disabled_is_identity(self):
        source=self.doc({
            "any":[
                {"all":[{"test":"g"},{"test":"p"}]},
                {"all":[{"not":{"test":"g"}},{"test":"q"}]},
            ]
        })
        result,report=modernize_conditionals_v1(source,enabled=False)
        self.assertEqual(result,source)
        self.assertFalse(report["rewrite_performed"])

    def test_requires_030(self):
        source=self.doc({"test":"g"})
        source["assessment"]["specification"]["version"]="0.2.0"
        result,report=modernize_conditionals_v1(source,enabled=True)
        self.assertEqual(result,source)
        self.assertEqual(report["review_required"][0]["reasons"],
                         ["conditional_v1_requires_0.3.0"])


if __name__=="__main__":
    unittest.main()
