import unittest
from check_current_authoring_contract import violations

class CurrentDesignGuards(unittest.TestCase):
    def test_publisher_profile_selection_contract(self):
        self.assertTrue(violations({'benchmark':{'profiles':[{'enabled_rules':[]}]}}))
        self.assertTrue(violations({'benchmark':{'profiles':[{'disabled_rules':[]}]}}))
        self.assertFalse(violations({'benchmark':{'profiles':[{'disabled_rules':['SV-1']}]}}))
        self.assertFalse(violations({'tailoring':{'enabled_rules':['SV-1']}}))
    def test_assessment_presentation_order_with_optional_sections(self):
        self.assertFalse(violations({'assessment':{
            'collections':{}, 'variables':{}, 'tests':{}, 'evaluate':{}}}))
        self.assertFalse(violations({'assessment':{'tests':{}, 'evaluate':{}}}))
        self.assertTrue(violations({'assessment':{
            'tests':{}, 'evaluate':{}, 'variables':{}, 'collections':{}}}))

    def test_rejects_superseded_policy_and_deprecated_false(self):
        self.assertTrue(violations({'rule':{'policy':'p.yaml'}}))
        self.assertTrue(violations({'policy':{'id':'p'}}))
        self.assertTrue(violations({'assessment':{'deprecated':False}}))

    def test_rejects_old_object_names_and_nested_variable_collections(self):
        a={'assessment':{'variables':{'v':{'expression':{'object_values':{'collect':{'object_title':'x'}}}}}}}
        self.assertEqual(len(violations(a)),3)

    def test_test_identity_and_unambiguous_current_vocabulary(self):
        self.assertTrue(violations({'assessment':{'tests':{'arbitrary':{}}}}))
        self.assertFalse(violations({'assessment':{'tests':{'test-x':{'collection':'x-collection'}}}}))

if __name__=='__main__': unittest.main()
