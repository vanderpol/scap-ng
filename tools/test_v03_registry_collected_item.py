import copy
import unittest
from validate_v03_registry_collected_item import diagnostics


def item(kind, value, datatype="string"):
    return {
        "id": "reg-1", "capability": "windows.registry", "status": "exists",
        "provenance": {},
        "fields": {
            "type": {"datatype": "string", "status": "exists", "value": kind},
            "value": value if isinstance(value,list) else
                {"datatype": datatype, "status": "exists", "value": value}
        }
    }


def scalar(value,datatype="string"):
    return {"datatype":datatype,"status":"exists","value":value}


class RegistryCollectedItemTests(unittest.TestCase):
    def test_multisz_array_retains_elements(self):
        self.assertEqual([],diagnostics(item("multi_string",[scalar("a"),scalar("b")])))
    def test_multisz_flat_string_rejected(self):
        self.assertIn("registry.multistring_requires_value_array",
            [x["code"] for x in diagnostics(item("multi_string","a b"))])
    def test_multisz_member_datatype_rejected(self):
        self.assertIn("registry.item_value_datatype",
            [x["code"] for x in diagnostics(item("multi_string",[scalar(42,"integer")]))])
    def test_dword_integer_passes(self):
        self.assertEqual([],diagnostics(item("dword",1,"integer")))
    def test_dword_string_rejected(self):
        self.assertIn("registry.item_value_datatype",
            [x["code"] for x in diagnostics(item("dword","1","string"))])
    def test_bool_is_not_integer(self):
        self.assertIn("registry.item_integer_representation",
            [x["code"] for x in diagnostics(item("dword",True,"integer"))])
    def test_scalar_cannot_hold_two_elements(self):
        self.assertIn("registry.scalar_unexpected_multiple_values",
            [x["code"] for x in diagnostics(item("string",[scalar("a"),scalar("b")]))])
    def test_registry_type_not_discovered(self):
        f=item("dword","1")
        del f["fields"]["type"]
        self.assertEqual([],diagnostics(f))


if __name__ == "__main__":
    unittest.main()
