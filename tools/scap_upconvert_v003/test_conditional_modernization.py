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
                         ["no_exact_complementary_guard"])

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
