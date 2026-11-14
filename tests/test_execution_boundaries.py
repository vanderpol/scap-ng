"""Existing frozen-schema guards; these are not collector/evaluation proofs."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry,Resource

ROOT=Path(__file__).resolve().parents[1]


class ExecutionBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        docs=[json.loads(p.read_text()) for p in (ROOT/'schema').glob('*.schema.json')]
        cls.docs={d['$id']:d for d in docs}
        cls.registry=Registry().with_resources((d['$id'],Resource.from_contents(d)) for d in docs)

    def validator(self,name):
        return Draft202012Validator(self.docs['https://scap-ng.dev/schema/v0.4.1/'+name+'.schema.json'],registry=self.registry)

    def test_source_locations_and_honest_status(self):
        d=json.loads((ROOT/'conformance/0.4/execution-boundaries/requirements.json').read_text())
        self.assertEqual(len(d['requirements']),10)
        for row in d['requirements']:
            self.assertIn(row['classification'],{'equivalent','intentionally_different','unsupported_by_RI','unresolved'})
            self.assertIn('not executed',row['runtime_witness_status'])
            for source in row['native']:
                raw=(ROOT/source['file']).read_bytes();self.assertEqual(sha256(raw).hexdigest(),source['sha256']);v=json.loads(raw)
                for token in source['pointer'].lstrip('/').split('/'):
                    token=token.replace('~1','/').replace('~0','~');v=v[int(token)] if isinstance(v,list) else v[token]

    def test_existing_redaction_excludes_value(self):
        schema={'$ref':'https://scap-ng.dev/schema/v0.4.1/result-types.schema.json#/$defs/typed_value'}
        validator=Draft202012Validator(schema,registry=self.registry)
        value={'datatype':'integer','status':'exists','redacted':True}
        validator.validate(value)
        for payload in (0,'<redacted>',None):
            changed=dict(value,value=payload)
            self.assertTrue(list(validator.iter_errors(changed)))

    def test_field_result_root_and_no_extra_reason_code(self):
        ref='/tests/source-test/require/fields/owner_uid'
        value={'field':'owner_uid','require_ref':ref,'requirement_ref':ref,'outcome':'true',
               'operation':'equals','values_found':'one_or_more','values_matching':'every',
               'observed_values':[{'datatype':'integer','status':'exists','redacted':True}],
               'expected_values':[{'datatype':'integer','status':'exists','redacted':True}],
               'observation_complete':True}
        validator=self.validator('field-result');validator.validate(value)
        for name in ('require_ref','requirement_ref'):
            changed=deepcopy(value);changed[name]='/assessment'+ref
            self.assertTrue(list(validator.iter_errors(changed)))
        changed=dict(value,reason_code='private_renderer_code')
        self.assertTrue(list(validator.iter_errors(changed)))

    def test_internal_capture_fields_do_not_enter_native_collection(self):
        value={'id':'supplied-collection','capability':'unix.file','status':'complete',
               'item_refs':[],'logical_complete':True,'population_complete':True}
        validator=self.validator('collection-result');validator.validate(value)
        for name in ('observation_state','authority_token','capture_epoch','candidate_count'):
            changed=dict(value);changed[name]='internal-only'
            self.assertTrue(list(validator.iter_errors(changed)))
