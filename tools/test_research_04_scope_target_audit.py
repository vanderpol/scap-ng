#!/usr/bin/env python3
"""#235: scope-target distinctions for source structures and authoring boundaries."""
import unittest
from research_04_scope_target_audit import collect_field_modes

R='at_least_one_exists_and_all_match'
S='at_least_one_exists_and_some_match'
N='none_exist'

class ScopeTargets(unittest.TestCase):
 def test_shared_test_policy_and_override(self):
  st=[{'and':[{'exit_status':{'equals':0}},
              {'stdout_line':{'matches_regex':'ok'}},
              {'stderr_line':{'equals':'','require':N}}]}]
  fields,records,missing,scopes=collect_field_modes(st,R)
  self.assertEqual([R,R,N],[v for _,v in fields]);self.assertEqual(records,0);self.assertEqual(missing,[])
 def test_record_does_not_inherit_scalar_policy(self):
  st=[{'result':{'record':{'fields':{'domainrole':{'require':N,'equals':'1'}},'require':S}}}]
  fields,records,missing,scopes=collect_field_modes(st,R)
  self.assertEqual((fields,records,missing),([],1,[]))
 def test_group_policy_overrides_test_policy(self):
  st=[{'or':[{'name':{'equals':'a'}},{'name':{'equals':'b'}}],
       'state_fields_require':N}]
  fields,records,missing,scopes=collect_field_modes(st,R)
  self.assertEqual([N,N],[v for _,v in fields]);self.assertEqual(scopes['group'],1)
 def test_detect_missing_and_different_field_match_modes(self):
  st=[{'mount_options':{'equals':'nosuid','require':S}},{'fs_type':{'equals':'x'}}]
  fields,records,missing,scopes=collect_field_modes(st)
  self.assertEqual([S],[v for _,v in fields]);self.assertEqual(['fs_type'],missing)
 def test_parent_requirement_does_not_transform_true_boolean_value(self):
  f,_,_,_=collect_field_modes([{'setuid':{'equals':False}}],R)
  self.assertEqual(f,[('setuid',R)])

if __name__=='__main__': unittest.main()