from copy import deepcopy
#!/usr/bin/env python3
import unittest
from migrate_v04_enum_selectors import migrate,restore

MAP={
 "windows.registry":{"native":{"selector_value_enums":{
     "hive":["local_machine","current_user"]}}},
 "windows.userright":{"native":{"selector_value_enums":{
     "userright":["SE_NETWORK_LOGON_NAME"]}}},
}

class NativeEnumSelectorMigration(unittest.TestCase):
    def test_registry_hive_source_scalar_lowered_explicitly(self):
        old={"assessment":{"tests":{"t":{"capability":"windows.registry",
              "object":{"capability":"windows.registry",
                        "select":{"hive":"local_machine",
                                  "key":{"equals":"SOFTWARE\\Microsoft"},
                                  "name":{"equals":"Policy"}}}}}}}
        new,notes=migrate(old,MAP)
        self.assertEqual(new["assessment"]["tests"]["t"]["object"]["select"]["hive"],
                         {"equals":"local_machine"})
        self.assertEqual(len(notes),1)
        self.assertEqual(restore(new,notes),old)

    def test_nested_object_sets_keep_type_and_identity(self):
        old={"assessment":{"tests":{"t":{"capability":"windows.userright",
              "object":{"capability":"windows.userright","set":{"operator":"union",
               "operands":[{"object":{"capability":"windows.userright",
                         "select":{"userright":"SE_NETWORK_LOGON_NAME"}}}]}}}}}}
        new,notes=migrate(old,MAP)
        self.assertEqual(len(notes),1)
        self.assertEqual(restore(new,notes),old)

    def test_unknown_enum_literal_is_not_guessed(self):
        old={"capability":"windows.registry","select":{"hive":"unknown_hive"}}
        with self.assertRaisesRegex(ValueError,"Non-enumerated"):
            migrate(old,MAP)

    def test_regular_typed_comparison_and_null_preserved(self):
        old={"capability":"windows.registry",
             "select":{"hive":{"equals":"local_machine"},"name":None}}
        new,notes=migrate(old,MAP)
        self.assertEqual(notes,[])
        self.assertEqual(new,old)

    def test_constant_full_enum_variable_is_expanded_with_exact_inverse(self):
        old={"assessment":{
            "variables":{"all-rights-variable":{
                "kind":"constant","datatype":"string",
                "expression":{"literal":["SE_NETWORK_LOGON_NAME"]},
                "title":"All reviewed rights in fixture"}},
            "tests":{"one-test":{
                "capability":"windows.userright",
                "object":{"capability":"windows.userright",
                          "select":{"userright":{"variable":"all-rights-variable"}}}
            }}
        }}
        new,notes=migrate(old,MAP)
        selector=new["assessment"]["tests"]["one-test"]["object"]["select"]["userright"]
        self.assertEqual(selector,{"equals":["SE_NETWORK_LOGON_NAME"],
                                   "datatype":"string","value_match":"one"})
        self.assertEqual(len(notes),1)
        self.assertEqual(notes[0]["classification"],"constant_full_enum_model_pending")
        self.assertEqual(restore(new,notes),old)
        tampered=deepcopy(new)
        tampered["assessment"]["tests"]["one-test"]["object"]["select"]["userright"]["value_match"]="all"
        with self.assertRaisesRegex(ValueError,"source proof mismatch"):
            restore(tampered,notes)

    def test_unverified_variable_definitions_are_not_silently_coerced(self):
        for variant in (
            {"kind":"external","datatype":"string",
             "expression":{"literal":["SE_NETWORK_LOGON_NAME"]}},
            {"kind":"constant","datatype":"integer",
             "expression":{"literal":["SE_NETWORK_LOGON_NAME"]}},
            {"kind":"constant","datatype":"string",
             "expression":{"literal":[]}},
            {"kind":"constant","datatype":"string",
             "expression":{"literal":["UNKNOWN_RIGHT"]}},
            {"kind":"constant","datatype":"string",
             "expression":{"literal":["SE_NETWORK_LOGON_NAME","SE_NETWORK_LOGON_NAME"]}},
            {"kind":"constant","datatype":"string",
             "expression":{"variable":"indirect-variable"}},
        ):
            with self.subTest(variant=variant):
                old={"assessment":{
                    "variables":{"all-rights-variable":variant},
                    "tests":{"one-test":{
                        "capability":"windows.userright",
                        "object":{"capability":"windows.userright",
                            "select":{"userright":{"variable":"all-rights-variable"}}}
                    }}
                }}
                converted,notes=migrate(old,MAP)
                self.assertEqual(notes,[])
                self.assertEqual(converted,old)

if __name__=="__main__":
    unittest.main()
