"""Regression for the full review's shared manual-selector source binding."""
import unittest
import xml.etree.ElementTree as ET
from scap_upconvert_v003.convert_collection_review import manual_procedure, NS
from scap_upconvert_v003.convert_full_review import render_profiles, profile_description
X=NS['x']

class ManualBinding(unittest.TestCase):
    def check(self, selector='', procedure=None, href='manual.xml', name='questionnaire-1'):
        node=ET.Element('{'+X+'}check',system='manual',selector=selector)
        ET.SubElement(node,'{'+X+'}check-content-ref',href=href,name=name)
        if procedure is not None: ET.SubElement(node,'{'+X+'}check-content').text=procedure
        return node

    def test_default_and_manual_share_same_verified_binding(self):
        default=self.check();manual=self.check('manual','Read the setting.')
        rec={'id':'SV-1','checks':[default,manual]}
        self.assertEqual(manual_procedure(rec,default),manual_procedure(rec,manual))
        rec['checks'].reverse()
        self.assertEqual(manual_procedure(rec,default)[1],'Read the setting.')

    def test_different_source_binding_does_not_supply_missing_procedure(self):
        for field in ('href','name'):
            with self.subTest(field=field):
                default=self.check();manual=self.check('manual','Different requirement.',**{field:'other'})
                with self.assertRaisesRegex(ValueError,'no verified inline procedure'):
                    manual_procedure({'id':'SV-1','checks':[default,manual]},default)

    def test_conflicting_procedures_on_same_binding_fail(self):
        a=self.check('default','First procedure.');b=self.check('manual','Different procedure.')
        with self.assertRaisesRegex(ValueError,'conflicting procedures'):
            manual_procedure({'id':'SV-1','checks':[a,b]},a)

class ProfileRendering(unittest.TestCase):
    def fixture(self):
        root=ET.Element('{'+X+'}Benchmark')
        for pid in ('parent','child'):
            p=ET.SubElement(root,'{'+X+'}Profile',id='xccdf_profile_'+pid)
            ET.SubElement(p,'{'+X+'}description').text='<ProfileDescription></ProfileDescription>'
        baseline={'SV-1':True,'SV-2':True}
        resolved=[{'id':'xccdf_profile_parent','effective_actions':[]},
                  {'id':'xccdf_profile_child','extends':'xccdf_profile_parent','effective_actions':[]}]
        expected={pid:{'enabled':dict(baseline),'problems':[]} for pid in ('parent','child')}
        return root,resolved,baseline,expected

    def test_unchanged_profile_shows_empty_disables_and_no_xml_wrapper(self):
        root,resolved,baseline,expected=self.fixture()
        p=render_profiles(root,resolved,baseline,expected)[0]
        self.assertNotIn('enabled_rules',p);self.assertEqual(p['disabled_rules'],[])
        self.assertIsNone(p['description'])

    def test_subtractive_child_preserves_inheritance_and_only_additional_disables(self):
        root,resolved,baseline,expected=self.fixture()
        expected['parent']['enabled']['SV-1']=False
        expected['child']['enabled']={'SV-1':False,'SV-2':False}
        child=render_profiles(root,resolved,baseline,expected)[1]
        self.assertEqual(child['extends'],'parent');self.assertEqual(child['disabled_rules'],['SV-2'])

    def test_reenabling_ancestor_disabled_rule_is_blocked(self):
        root,resolved,baseline,expected=self.fixture()
        expected['parent']['enabled']['SV-1']=False
        with self.assertRaisesRegex(ValueError,'re-enables'):
            render_profiles(root,resolved,baseline,expected)

    def test_disabled_source_baseline_is_not_silently_changed(self):
        root,resolved,baseline,expected=self.fixture();baseline['SV-1']=False
        with self.assertRaisesRegex(ValueError,'Source baseline disables'):
            render_profiles(root,resolved,baseline,expected)

    def test_description_keeps_meaningful_text(self):
        e=ET.Element('description');e.text='<ProfileDescription>Review <p>these Rules.</p></ProfileDescription>'
        self.assertEqual(profile_description(e),'Review these Rules.')
        e.text='A plain description.';self.assertEqual(profile_description(e),e.text)

if __name__=='__main__':unittest.main()
