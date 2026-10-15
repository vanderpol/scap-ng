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

if __name__=="__main__":
    unittest.main()
