import unittest
from check_current_authoring_contract import violations

class CurrentDesignGuards(unittest.TestCase):
    def test_publisher_profile_selection_contract(self):
        self.assertTrue(violations({'benchmark':{'profiles':[{'enabled_rules':[]}]}}))
        self.assertFalse(violations({'benchmark':{'profiles':[{'disabled_rules':[]}]}}))
        self.assertTrue(violations({'benchmark':{'profiles':[{'id':'unchanged'}]}}))
        self.assertFalse(violations({'benchmark':{'profiles':[{'disabled_rules':['SV-1']}]}}))
        self.assertFalse(violations({'tailoring':{'enabled_rules':['SV-1']}}))
    def test_assessment_presentation_order_with_optional_sections(self):
        self.assertFalse(violations({'assessment':{
            'objects':{}, 'variables':{}, 'states':{}, 'tests':{}, 'evaluate':{}}}))
        self.assertFalse(violations({'assessment':{'tests':{}, 'evaluate':{}}}))
        self.assertTrue(violations({'assessment':{
            'tests':{}, 'evaluate':{}, 'variables':{}, 'objects':{}, 'states':{}}}))

    def test_rejects_superseded_policy_and_deprecated_false(self):
        self.assertTrue(violations({'rule':{'policy':'p.yaml'}}))
        self.assertTrue(violations({'policy':{'id':'p'}}))
        self.assertTrue(violations({'assessment':{'deprecated':False}}))

    def test_rejects_stale_pre_alignment_vocabulary(self):
        a={'assessment':{'variables':{'v':{'expression':{'object_values':{'collection':{'collection_title':'x'}}}}}}}
        self.assertEqual(len(violations(a)),3)

    def test_native_object_collect_is_allowed_but_test_collect_is_stale(self):
        self.assertFalse(violations({'assessment':{
            'objects':{'object-q':{
                'capability':'windows.wmi.query',
                'collect':{'namespace':'root\\cimv2','query':'SELECT Caption FROM Win32_OperatingSystem'},
            }},
            'tests':{'test-q':{'object':'object-q'}},
        }}))
        self.assertTrue(violations({'assessment':{
            'tests':{'test-q':{'collect':'legacy-collection'}},
        }}))

    def test_test_identity_and_unambiguous_current_vocabulary(self):
        self.assertTrue(violations({'assessment':{'tests':{'arbitrary':{}}}}))
        self.assertFalse(violations({'assessment':{'objects':{'object-x':{'capability':'unix.file'}},'tests':{'test-x':{'object':'object-x'}}}}))

    def test_named_object_requires_own_capability(self):
        self.assertTrue(violations({'assessment':{'objects':{'object-x':{'select':{}}}}}))
        self.assertFalse(violations({'assessment':{'objects':{'object-x':{'capability':'unix.file','select':{}}}}}))

if __name__=='__main__': unittest.main()
