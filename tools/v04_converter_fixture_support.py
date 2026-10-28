"""Constructed package wrappers for converter-only regression Tests.

No original Benchmark, platform, Rule policy or scanner claim is created.
The original Assessment is embedded unchanged for compiled-package checking.
"""


def fixture_documents(assessment):
    # Explicitly constructed packaging metadata. This is not an original
    # SCAP Benchmark/Rule conversion or an additional production proof.
    benchmark = {'id': 'converter-integration-fixture', 'ng_schema_version': '0.4.0',
        'use_case': 'compliance', 'version': {'value': '1'},
        'assessment_specifications': [{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}],
        'title': [{'text': 'Constructed converter compilation fixture', 'language': 'en'}],
        'description': [], 'language': 'en', 'status': [], 'metadata': {'constructed_wrapper': True},
        'notices': [], 'front_matter': [], 'rear_matter': [], 'references': [], 'text_blocks': [],
        'platform': {'id': 'fixture-platform', 'title': 'No platform claim', 'applicability': {}},
        'applicability_catalog': 'fixture-applicability', 'scoring': [], 'parameters': [],
        'default_selection': True, 'groups': [], 'profiles': [], 'rules': ['fixture-rule']}
    rule = {'id': 'fixture-rule', 'version': '1', 'title': 'Constructed packaging wrapper',
        'severity': 'unknown', 'role': 'full', 'weight': 1, 'discussion': '', 'rationale': None,
        'extensions': {}, 'warnings': [], 'identifiers': [], 'references': [], 'requires': [],
        'conflicts': [], 'applicability': [], 'parameters': {}, 'remediation': {},
        'organizational_input_requirements': {},
        'assessment_choices': {'automated': {'assessment': assessment['id']}},
        'default_assessment_choice': 'automated'}
    prefix = 'authoring/converter-integration-fixture/'
    documents = {prefix + 'benchmark.json': {'benchmark': benchmark},
        prefix + 'rules/fixture-rule.json': {'rule': rule},
        prefix + 'applicability.json': {'applicability': {'id': 'fixture-applicability', 'conditions': {}}},
        prefix + 'assessments/original.json': {'assessment': assessment}}
    return documents
