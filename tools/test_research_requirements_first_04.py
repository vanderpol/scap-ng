#!/usr/bin/env python3
"""Adversarial structural checks for research-only auditor authoring candidate."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import research_requirements_first_04 as grammar

class RequirementsFirstAuthorabilityTests(unittest.TestCase):
    def test_all_example_assessments_are_structurally_valid(self):
        for path in sorted(grammar.SAMPLES.glob('*.yaml')):
            with self.subTest(path=path.name):
                doc=grammar.yaml.load(path.read_text(),Loader=grammar.Loader)
                self.assertTrue(grammar.validate(doc,str(path)))

    def test_incomplete_every_has_no_hidden_empty_policy(self):
        document={'id':'x','title':'x','require':{
            'every':'linux.mounts','must':{'mount_options':{'contains':'nosuid'}}}}
        with self.assertRaisesRegex(ValueError,'MUST explicitly declare if_empty'):
            grammar.validate(document)

    def test_where_and_must_cannot_be_confused(self):
        document={'id':'x','title':'x','require':{
            'every':'linux.mounts','where':{'mount_point':{'matches_regex':'home'}},
            'if_empty':'fail'}}
        with self.assertRaisesRegex(ValueError,'requires a must assertion'):
            grammar.validate(document)

    def test_undefined_nested_alias_rejected(self):
        doc={'id':'x','title':'x','require':{
            'every':'linux.files','if_empty':'pass',
            'using':{'directory':'$user.home_dir'},
            'must':{'owner':{'equals':'root'}}}}
        with self.assertRaisesRegex(ValueError,'unbound lexical'):
            grammar.validate(doc)

    def test_lexical_variable_shadowing_rejected(self):
        doc={'id':'x','title':'x','require':{
            'every':'linux.accounts','as':'user','if_empty':'pass',
            'must':{'every':'linux.files','as':'user','if_empty':'pass',
                     'must':{'owner':{'equals':'$user.username'}}}}}
        with self.assertRaisesRegex(ValueError,'shadowing'):
            grammar.validate(doc)

    def test_fake_provider_is_rejected(self):
        doc={'id':'x','title':'x','require':{
            'every':'apache.config.magic','if_empty':'fail',
            'must':{'value':{'equals':'On'}}}}
        with self.assertRaisesRegex(ValueError,'unregistered typed evidence provider'):
            grammar.validate(doc)

    def test_oval_backdoor_shapes_rejected(self):
        doc={'id':'x','title':'x','require':{'matching_items':'all'}}
        with self.assertRaises(ValueError):
            grammar.validate(doc)

    def test_unknown_conditional_requires_explicit_status(self):
        doc={'id':'x','title':'x','require':{
            'if':{
                'fact':'windows.computer.is_domain_controller',
                'equals':True,
                'then':{'exactly_one':'windows.time_source',
                        'must':{'configured_server':{'equals':'$site.server'}}},
                'otherwise':{'exactly_one':'windows.time_source',
                        'must':{'configured_server':{'equals':'$site.server'}}}
            }}}
        with self.assertRaisesRegex(ValueError,'on_unknown'):
            grammar.validate(doc)

    def test_duplicate_yaml_mapping_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate key'):
            grammar.yaml.load('id: x\nid: y\n',Loader=grammar.Loader)

    def test_empty_automatic_conformance_not_claimed(self):
        doc={'id':'x','title':'x','require':{
            'none':'windows.user_right_assignments',
            'where':{'principal':{'equals_ignore_case':'Unknown'}}}}
        self.assertTrue(grammar.validate(doc))

if __name__=='__main__':unittest.main()
