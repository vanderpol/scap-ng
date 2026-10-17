#!/usr/bin/env python3
"""Negative/provenance tests: generated auditor notes must never invent policy."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import research_04_auditor_preview as report

class SourceDerivedPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d={}
        for name in report.CASES:
            cls.d[name]=report.yaml.load(
                (report.BASE/(name+'.revised.research.yaml')).read_text(),
                Loader=report.StrictLoader)

    def test_five_full_assessments_render_from_parsed_source(self):
        previews=report.build()
        self.assertEqual(set(previews),{'INDEX.md','SEMANTIC-BOUNDARY-LEDGER.md'} |
                         {x+'.md' for x in report.CASES})
        for name in report.CASES:
            self.assertIn(self.d[name]['metadata']['id'],previews[name+'.md'])
            self.assertIn('What remains unverified?',previews[name+'.md'])

    def test_seven_windows_checks_all_present_and_repeated_ref_retained(self):
        result,n,leaves=report.render('windows-wmi-rights',self.d['windows-wmi-rights'])
        self.assertEqual((n,leaves),(7,8))
        self.assertIn('Repeated references retained:',result)
        self.assertIn('matching_records',result)
        self.assertIn('SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME',result)

    def test_linux_dependency_and_different_existence_modes(self):
        r,n,l=report.render('linux-files',self.d['linux-files'])
        self.assertEqual((n,l),(2,2))
        self.assertIn('for_each_source',r)
        self.assertIn('if_present',r)
        self.assertIn('at_least_one',r)
        self.assertIn('field_presence',r)

    def test_error_precedence_is_generic_only(self):
        result=report.boundary_ledger()
        self.assertIn('AND(False,Error)',result)
        self.assertIn('OR(True,Error)',result)
        self.assertIn('NOT Assessment execution',result)

    def test_unknown_evaluate_check_fails_closed(self):
        d=deepcopy(self.d['linux-home'])
        d['evaluate']={'test':'made-up-check'}
        with self.assertRaises(ValueError):
            report.render('linux-home',d)

    def test_missing_check_in_evaluate_fails_closed(self):
        d=deepcopy(self.d['windows-wmi-rights'])
        d['evaluate']={'test':next(iter(d['checks']))}
        with self.assertRaisesRegex(ValueError,'checks omitted'):
            report.render('windows-wmi-rights',d)

    def test_undefined_foreach_source_fails_closed(self):
        d=deepcopy(self.d['linux-files'])
        def corrupt(obj):
            if isinstance(obj,dict):
                if 'for_each_source' in obj:
                    obj['for_each_source']['in']='undefined-source'
                    return True
                return any(corrupt(v) for v in obj.values())
            if isinstance(obj,list):
                return any(corrupt(v) for v in obj)
            return False
        self.assertTrue(corrupt(d['checks']))
        with self.assertRaisesRegex(ValueError,'missing source for foreach'):
            report.render('linux-files',d)

    def test_duplicate_yaml_mapping_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate YAML key'):
            report.yaml.load('x: 1\nx: 2\n',Loader=report.StrictLoader)

if __name__=='__main__':
    unittest.main()
