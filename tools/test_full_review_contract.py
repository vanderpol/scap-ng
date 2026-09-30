"""Regression for the full review's shared manual-selector source binding."""
import unittest
import xml.etree.ElementTree as ET
from scap_upconvert_v003.convert_collection_review import manual_procedure, NS
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

if __name__=='__main__':unittest.main()
