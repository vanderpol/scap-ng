#!/usr/bin/env python3
"""#245 Original OVAL 5.12.3 exact multi-value constant evidence gate."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_inline_source_constants import (
    lower_inline_expected_values, project_source_constant_consumer)
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"board/review-content/0.2.0/sources/filter.xml"
IDENTITY="oval:org.mitre.oval.test:var:134"
EXPECTED=["/opt/support/txt/txtfile",
          "/opt/support/txt/txtfile/subtxtfile"]

class CInlineSourceConstantTests(unittest.TestCase):
    def test_source_oval_string_constant_becomes_inline_without_authored_variable(self):
        root=ET.parse(ORIGINAL).getroot()
        report=project_source_constant_consumer(root,IDENTITY)
        self.assertEqual(report["C_authoring_predicate"],{
            "field":"path","equals":EXPECTED,"value_match":"one"})
        compiled=report["A_compiled_compatibility"]
        self.assertEqual(compiled["authoring_variable_declarations"],0)
        self.assertEqual(compiled["compiler_only_variable_count"],1)
        self.assertEqual(compiled["source_oval_var_check"],"only one")
        self.assertEqual(compiled["compiled_variables"][IDENTITY],{
            "kind":"constant","datatype":"string","value":EXPECTED})
        self.assertEqual(compiled["compiled_comparison"],{
            "field":"path","datatype":"string","operation":"equals",
            "value":{"variable":IDENTITY},"value_match":"one"})
        self.assertIn("string values",report["source_variable_comment"])
        self.assertFalse(report["source_runtime_semantics_proven"])

    def test_independently_authored_literal_list_preserves_order_duplicates(self):
        doc={"field":"path","equals":["/a","/a","/b"],"value_match":"one"}
        before=deepcopy(doc)
        result=lower_inline_expected_values(doc,compiler_variable_identity=IDENTITY)
        self.assertEqual(doc,before)
        self.assertEqual(result["compiled_variables"][IDENTITY]["value"],
                         ["/a","/a","/b"])
        self.assertEqual(result["source_oval_var_check"],"only one")

    def test_all_oval_expected_value_quantifiers_map_explicitly(self):
        for mode,src in [
            ("one","only one"),("one_or_more","at least one"),
            ("all","all"),("none","none satisfy")
        ]:
            with self.subTest(mode=mode):
                result=lower_inline_expected_values({
                    "field":"path","equals":["/a"],"value_match":mode},
                    compiler_variable_identity=IDENTITY)
                self.assertEqual(result["source_oval_var_check"],src)

    def test_missing_and_invalid_literal_cardinality_rejected(self):
        docs=[
            {"field":"path","equals":[],"value_match":"one"},
            {"field":"path","equals":["/a"]},
            {"field":"path","equals":["/a"],"value_match":"any"},
            {"field":"path","equals":[1],"value_match":"one"},
            {"field":"path","equals":["/a"],"value_match":"one","guess":True},
        ]
        for d in docs:
            with self.subTest(case=d):
                with self.assertRaises(ValueError):
                    lower_inline_expected_values(d,compiler_variable_identity=IDENTITY)
        with self.assertRaisesRegex(ValueError,"source provenance"):
            lower_inline_expected_values({
                "field":"path","equals":["/a"],"value_match":"one"},
                compiler_variable_identity="meaningless")

    def test_shared_constant_or_non_string_source_is_explicitly_blocked(self):
        root=ET.parse(ORIGINAL).getroot()
        state=next(n for n in root.iter() if n.attrib.get("var_ref")==IDENTITY)
        root2=deepcopy(root)
        # Original-only extra reference: do not remove shared scope by inlining.
        target=next(n for n in root2.iter() if n.attrib.get("var_ref")==IDENTITY)
        parent=next(n for n in root2.iter() if target in list(n))
        parent.append(deepcopy(target))
        with self.assertRaisesRegex(ValueError,"shared/missing"):
            project_source_constant_consumer(root2,IDENTITY)
        var=next(n for n in root.iter() if n.attrib.get("id")==IDENTITY)
        var.attrib["datatype"]="int"
        with self.assertRaisesRegex(ValueError,"non-string"):
            project_source_constant_consumer(root,IDENTITY)

    def test_comparison_orientation_and_only_one_are_not_guessed(self):
        root=ET.parse(ORIGINAL).getroot()
        state=next(n for n in root.iter() if n.attrib.get("var_ref")==IDENTITY)
        state.set("operation","pattern match")
        with self.assertRaisesRegex(ValueError,"non-equality"):
            project_source_constant_consumer(root,IDENTITY)
        state.set("operation","equals")
        state.set("var_check","unproven")
        with self.assertRaisesRegex(ValueError,"unproven"):
            project_source_constant_consumer(root,IDENTITY)

if __name__=="__main__":
    unittest.main()
