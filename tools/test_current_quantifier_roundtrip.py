"""Current OVAL-aligned Test/Object/State grammar must preserve distinct OVAL quantifiers."""
import sys
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).parent))
from test_state_entity_roundtrip import SOURCE, OD, UNIX
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from check_current_authoring_contract import violations
from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary

class CurrentQuantifiers(unittest.TestCase):
    def roundtrip(self, root):
        native, error = lower_definition(root, "oval:example:def:1", "current-quantifiers", collection_graph=True)
        self.assertIsNone(error)
        native = align_assessment_vocabulary(native)
        for test in native.get("assessment", {}).get("tests", {}).values():
            test["reported_elements"] = "all"
        self.assertEqual(violations(native), [])
        regenerated, rid = build(native)
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"source.xml", Path(tmp)/"regenerated.xml"
            ET.ElementTree(root).write(a, encoding="utf-8")
            regenerated.write(b, encoding="utf-8")
            result = compare(a, b, "oval:example:def:1", rid, root_only=True)
        self.assertTrue(result["equal"], result)
        return regenerated.getroot()

    def test_test_existence_and_item_quantifiers(self):
        for existence in ("all_exist", "any_exist", "at_least_one_exists", "none_exist", "only_one_exists"):
            for check in ("all", "at least one", "none satisfy", "only one"):
                with self.subTest(existence=existence, check=check):
                    root = ET.fromstring(SOURCE)
                    test = root.find(f".//{{{UNIX}}}file_test")
                    test.set("check_existence", existence)
                    test.set("check", check)
                    self.roundtrip(root)

    def test_state_entity_quantifiers_remain_independent(self):
        for existence in ("all_exist", "any_exist", "at_least_one_exists", "none_exist", "only_one_exists"):
            for entity_check in ("all", "at least one", "none satisfy", "only one"):
                with self.subTest(existence=existence, entity_check=entity_check):
                    root = ET.fromstring(SOURCE)
                    entity = root.find(f".//{{{UNIX}}}file_state/{{{UNIX}}}filename")
                    entity.set("check_existence", existence)
                    entity.set("entity_check", entity_check)
                    self.roundtrip(root)

    def test_multiple_states_and_state_operators(self):
        for operator in ("AND", "OR"):
            with self.subTest(operator=operator):
                root = ET.fromstring(SOURCE)
                duplicate = ET.fromstring(ET.tostring(root.find(f".//{{{UNIX}}}file_state")))
                duplicate.set("id", "oval:example:ste:2")
                duplicate.find(f"{{{UNIX}}}filename").text = "other"
                root.find(f"{{{OD}}}states").append(duplicate)
                test = root.find(f".//{{{UNIX}}}file_test")
                test.set("state_operator", operator)
                ET.SubElement(test, f"{{{UNIX}}}state", state_ref="oval:example:ste:2")
                self.roundtrip(root)

if __name__ == "__main__":
    unittest.main()
