"""Guard the current Rule/Assessment boundary against Policy-layer regression."""
import unittest
from pathlib import Path
from build_rhel9_split_policy_review import load, resolve_source_ref

class RuleAssessmentSlice(unittest.TestCase):
    root=Path('research/iterations/003/review/test-vocabulary-slice')

    def test_no_policy_layer(self):
        self.assertFalse((self.root/'policies').exists())
        for path in (self.root/'rules').glob('*.yaml'):
            rule=load(path)['rule']
            self.assertNotIn('policy',rule)
            self.assertEqual(set(rule['assessment_choices']), {'default','automated','manual'})
            self.assertEqual(rule['default_assessment_choice'],'default')
            self.assertEqual(rule['assessment_choices']['default'],rule['assessment_choices']['automated'])

    def test_direct_paths_resolve_to_original_identities(self):
        for path in (self.root/'rules').glob('*.yaml'):
            rule=load(path)['rule']
            for selector, choice in rule['assessment_choices'].items():
                mode='manual' if selector=='manual' else 'automated'
                resolve_source_ref(self.root,path,choice['assessment'],'assessment',rule['id']+'.'+mode)

    def test_native_assessments_have_no_deprecated_attribute(self):
        for path in (self.root/'assessments').rglob('*.yaml'):
            self.assertNotIn('deprecated',load(path)['assessment'])

if __name__=='__main__': unittest.main()
