#!/usr/bin/env python3
"""Fixed-result execution does not exempt current authoring from Test.require.

The approved schema requires structured require for every Test. Historical
minimal/scalar-require fixtures are negative inputs, not a second dialect.
No scanner execution or outcome semantics are changed. Refs #251 #248.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import unittest
from zipfile import ZipFile

import yaml

from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs


ROOT = Path(__file__).resolve().parent.parent


def assessment(test):
    return {"assessment": {
        "id": "source-unknown-assessment", "version": 2,
        "assessment_title": "Unknown Result", "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {"fixed-unknown-test": test},
        "evaluate": {"test": "fixed-unknown-test"},
    }}


class FixedUnknownSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = _schema_validators(ROOT / "schema/v0.4.0")
        cls.capability = materialize("independent.unknown")

    def check_doc(self, test):
        validate_docs({"authoring/source-unknown.assessment.json": assessment(test)},
                      self.validators)

    def test_minimal_fixed_result_still_requires_structured_require(self):
        test = {"test_title": "Always unknown", "capability": "independent.unknown"}
        with self.assertRaisesRegex(ValueError, 'required property'):
            self.check_doc(test)
        self.assertTrue(validate(self.capability, "test", test))

    def test_canonical_explicit_form_valid_and_historical_scalar_rejected(self):
        test = {"test_title": "Always unknown", "capability": "independent.unknown",
                "reported_elements": "all", "require": {"items_found": "one_or_more"}}
        self.check_doc(test)
        self.assertEqual(validate(self.capability, "test", test), [])
        test['require'] = 'at_least_one_exists'
        with self.assertRaisesRegex(ValueError, 'schema failure'):
            self.check_doc(test)
        self.assertTrue(validate(self.capability, 'test', test))

    def test_other_capabilities_still_require_explicit_fields(self):
        test = {"test_title": "Must inspect system family", "capability": "independent.family"}
        with self.assertRaisesRegex(ValueError, "required property"):
            self.check_doc(test)
        family = materialize("independent.family")
        self.assertTrue(validate(family, "test", test))

    def test_unknown_rejects_invented_runtime_result_and_object(self):
        test = {"test_title": "Always unknown", "capability": "independent.unknown",
                "require": {"items_found": "one_or_more"}}
        for bad_field, value in (("result", "pass"), ("object", {"shell": "bash"}),
                                 ("states", [{"value": {"equals": 1}}])):
            bad = deepcopy(test)
            bad[bad_field] = value
            self.assertTrue(validate(self.capability, "test", bad), bad_field)


def verify_published_archive(zip_path):
    with ZipFile(zip_path) as source:
        names = sorted(n for n in source.namelist()
                       if n.startswith("authoring/") and n.endswith(".yaml"))
        if len(names) != 4001:
            raise ValueError(f"expected 4,001 published authoring YAMLs, got {len(names)}")
        docs = {name: yaml.safe_load(source.read(name)) for name in names}
    validate_docs(docs, _schema_validators(ROOT / "schema/v0.4.0"))
    return {"published_yaml_documents_validated": len(docs),
            "runtime_parity_claimed": False}


def verify_current_archives(json_path, yaml_path):
    """Current format coverage, not original OVAL equivalence or a release build.

    The 4,012-document reviewed migration is distinct from the immutable 4,001
    October 21 archive. Keep counts/format parity explicit; never silently repair
    input in this validator or claim whole-corpus original-source proof.
    """
    from collections import Counter
    from v04_a_authoring_graph_index import read_authoring_archive
    json_docs = read_authoring_archive(json_path, 'json')
    yaml_docs = read_authoring_archive(yaml_path, 'yaml')
    if len(json_docs) != 4012 or len(yaml_docs) != 4012:
        raise ValueError('expected complete 4,012-document current review in both formats')
    if json_docs != {name.removesuffix('.yaml') + '.json': doc for name, doc in yaml_docs.items()}:
        raise ValueError('current review JSON/YAML native graphs differ')
    validators = _schema_validators(ROOT / 'schema/v0.4.0')
    validate_docs(json_docs, validators)
    validate_docs(yaml_docs, validators)
    kinds = Counter(next(iter(doc)) for doc in json_docs.values())
    assessments = [doc['assessment'] for doc in json_docs.values() if 'assessment' in doc]
    modes = Counter(a['mode'] for a in assessments)
    if kinds != {'benchmark': 6, 'applicability': 6, 'rule': 1567, 'assessment': 2433} or modes != {
            'automated': 883, 'manual': 1550}:
        raise ValueError('current review inventory differs from accepted checkpoint')
    return {'current_documents_per_format': 4012, 'yaml_json_parity': True,
            'kinds': dict(kinds), 'assessment_modes': dict(modes),
            'original_oval_equivalence_claimed': False, 'runtime_parity_claimed': False,
            'benchmark_packages_built': 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published-yaml-zip", type=Path)
    parser.add_argument('--current-json-zip', type=Path)
    parser.add_argument('--current-yaml-zip', type=Path)
    args, unittest_args = parser.parse_known_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FixedUnknownSchema)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.published_yaml_zip:
        print(json.dumps(verify_published_archive(args.published_yaml_zip), sort_keys=True))
    if args.current_json_zip or args.current_yaml_zip:
        if not (args.current_json_zip and args.current_yaml_zip):
            parser.error('both current-format archives are required')
        print(json.dumps(verify_current_archives(args.current_json_zip, args.current_yaml_zip), sort_keys=True))
