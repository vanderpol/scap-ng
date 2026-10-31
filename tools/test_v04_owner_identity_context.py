"""Owner Decisions 6/10/18/23: bounded current-native compatibility (#255/#268)."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from generate_capability_schema_v04 import generate
from test_generate_capability_schema_v04 import validate as generated_errors
from test_v04_owner_decision_schema_lock import assessment
from scap_ng_library.documents import canonical_yaml, validate
from scap_ng_library.index import Library
from v04_a_lossless_ir import _check_assessment_dependency_targets
from v04_native_bundle_compiler import compile_assessment_program, compile_test_instruction
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]


class OwnerIdentityContext(unittest.TestCase):
    def test_current_assessment_and_local_ids_fail_closed_in_schema_and_compiler(self):
        original = assessment()['assessment']
        compile_assessment_program(original)
        validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        for identity in ('Uppercase', 'spaces are invalid', 'x' * 65, '../escape', ''):
            item = deepcopy(original); item['id'] = identity
            with self.subTest(identity=identity):
                self.assertTrue(list(document_errors(validator, {'assessment': item})))
                with self.assertRaisesRegex(ValueError, 'Assessment ID'):
                    compile_assessment_program(item)
        for section, name in (('tests', 'incorrect'), ('shared_objects', 'incorrect'),
                              ('variables', 'incorrect'), ('inputs', 'incorrect'), ('dependencies', 'BadAlias')):
            item = deepcopy(original); item[section] = {name: {}}
            with self.subTest(section=section), self.assertRaisesRegex(ValueError, 'ID'):
                compile_assessment_program(item)
        with self.assertRaisesRegex(ValueError, 'Test ID'):
            compile_test_instruction('x' * 60 + '-test', next(iter(original['tests'].values())))

    def test_intrinsic_purpose_rejected_even_by_direct_program_api(self):
        original = assessment()['assessment']; original['purpose'] = 'assessment'
        with self.assertRaisesRegex(ValueError, 'purpose.*invocation'):
            compile_assessment_program(original)

    def test_dependency_resolution_has_no_target_intrinsic_purpose(self):
        target = assessment()['assessment']; target['id'] = 'target-assessment'
        source = deepcopy(target); source['id'] = 'source-assessment'
        source['dependencies'] = {'target-result': {'assessment': target['id'], 'expected_version': target['version']}}
        documents = {'authoring/example/assessments/target.json': {'assessment': target},
                     'authoring/example/assessments/source.json': {'assessment': source}}
        _check_assessment_dependency_targets(documents)
        source['dependencies']['target-result']['expected_version'] = 999
        with self.assertRaisesRegex(ValueError, 'version mismatch'):
            _check_assessment_dependency_targets(documents)

    def test_library_rejects_duplicate_assessment_ids_across_private_benchmarks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for scope in ('linux-one', 'linux-two'):
                path = root / scope / 'assessments' / 'same-assessment.yaml'
                path.parent.mkdir(parents=True)
                doc = assessment(); validate(doc)
                path.write_bytes(canonical_yaml(doc))
            library = Library(root)
            try:
                library.refresh(full=True)
                self.assertIn('duplicate-assessment-identity', {d['code'] for d in library.check()['diagnostics']})
            finally:
                library.close()

    def test_cmdlet_module_version_is_quoted_semantic_version_not_unconstrained_text(self):
        mapping = json.loads((ROOT / 'schema/v0.4.0/capability-mappings/supported/windows.cmdlet.json').read_text())
        schema = generate(mapping, ROOT)
        obj = {'module_name': None, 'module_id': None, 'module_version': '1.2.3',
               'verb': 'Get', 'noun': 'Example', 'parameters': None, 'select': None}
        for value in ('1', '1.2.3', '1-2c3', None, {'variable': 'module-version-variable'}):
            obj['module_version'] = value
            with self.subTest(value=value): self.assertFalse(generated_errors(schema, 'object', obj))
        for value in ('garbage', '1..2', '1.2.', '-1', '', 1.2, 1, True):
            obj['module_version'] = value
            with self.subTest(value=value): self.assertTrue(generated_errors(schema, 'object', obj))
        obj['module_version'] = {'equals': '1.2', 'datatype': 'string'}
        self.assertTrue(generated_errors(schema, 'object', obj))
        # A declared Variable stays deferred; this test does not coerce or
        # evaluate the Variable's runtime result or PowerShell API behavior.


if __name__ == '__main__': unittest.main()
