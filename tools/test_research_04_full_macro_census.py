import unittest
from collections import Counter
from research_04_full_macro_census import category, scan_test

class CensusTests(unittest.TestCase):
    def test_macos_and_shell_categories(self):
        self.assertEqual(category("unix.file","U_Apple_macOS_15.zip"),"macos_atypical")
        self.assertEqual(category("independent.shellcommand","U_RHEL_9.zip"),"shell_command")
        self.assertEqual(category("windows.registry","U_Windows_11.zip"),"structured_other")

    def test_home_rule_scopes(self):
        test={"capability":"linux.partition","existence":"one_or_more","match":"all",
              "object":{"capability":"linux.partition","select":{
                  "mount_point":{"value":"/home","operation":"equals"}}},
              "states":[{"field":"mount_options","value":"nosuid","operation":"equals",
                         "existence":"one_or_more","match":"one_or_more"}]}
        metrics=Counter()
        scan_test(test,metrics,{},"home")
        self.assertEqual(metrics["items_alias_candidate:at_least_one_all_match"],1)
        self.assertEqual(metrics["field_alias_candidate:at_least_one_some_match"],1)
        self.assertEqual(metrics["field_alias_candidate:at_least_one_all_match"],0)

    def test_absence_requires_no_state_key(self):
        bare={"capability":"windows.registry","existence":"none","match":"all"}
        present={**bare,"states":[]}
        one,two=Counter(),Counter()
        scan_test(bare,one,{},"none")
        scan_test(present,two,{},"none")
        self.assertEqual(one["state_free_absence_tests"],1)
        self.assertEqual(two["state_free_absence_tests"],0)

if __name__=="__main__":
    unittest.main()
