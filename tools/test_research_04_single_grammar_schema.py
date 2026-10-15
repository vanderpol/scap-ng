#!/usr/bin/env python3
"""Pre-alpha SCAP-NG 0.4 one-language *fragment* JSON Schema tests.

Runs exact research-converted 0.3 authoring through candidate 0.4 field/state
validation. Only structural surface. Capability-specific fields, Objects,
redaction policy and complete versioned schema remain separate gates.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import unittest
import zipfile

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SCHEMA_PATH=ROOT/"research/assessment-simplification/compact-authoring-04/assessment-language-fragment.schema.json"
SCHEMA=json.loads(SCHEMA_PATH.read_text())
VALIDATOR=Draft202012Validator(SCHEMA)

def wrap(states=None,require="at_least_one_exists_and_all_match"):
    test={"capability":"unix.file","require":require,"reported_elements":"all"}
    if states is not None:test["states"]=states
    return {"assessment":{"tests":{"example-test":test}}}

def field(name="owner_uid",op="equals",value=0,req="at_least_one_exists_and_all_match"):
    return {name:{op:value,"require":req}}

def validate(value):
    return list(VALIDATOR.iter_errors(value))

class OneGrammarSchemaTests(unittest.TestCase):
    def test_schema_itself_is_valid(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_scalar_predicate_and_field_value_name(self):
        self.assertEqual(validate(wrap([field()])),[])
        self.assertEqual(validate(wrap([field("value", "equals", 0)])),[])
        self.assertEqual(validate(wrap([field("all", "equals", 0)])),[])
        self.assertEqual(validate(wrap([{"all":[field("value"),field("owner_uid")]}])),[])

    def test_regex_and_negative_pair(self):
        self.assertEqual(validate(wrap([{"flag":{"matches_regex":"PROMISC",
            "require":"at_least_one_exists_and_none_match"}}])),[])

    def test_array_carries_separate_value_match(self):
        a=field("owner_uid","equals",[0,1000])
        a["owner_uid"]["datatype"]="integer"
        a["owner_uid"]["value_match"]="one"
        self.assertEqual(validate(wrap([a])),[])
        # missing value_match still requires a separate semantic validation gate
        # for source arrays; the 0.4 schema snapshot MUST enforce this, too.

    def test_record_field_and_record_scope(self):
        data={"value":{"record":{
            "require":"at_least_one_exists_and_some_match",
            "fields":{"productstate":{
                "bitwise_and":4096,
                "require":"at_least_one_exists_and_all_match"
            }}}}
        self.assertEqual(validate(wrap([data])),[])

    def test_state_free_presence_names(self):
        self.assertEqual(validate(wrap(None,"only_one_exists")),[])
        self.assertEqual(validate(wrap(None,"none_exist")),[])
        self.assertTrue(validate(wrap(None,"only_one_exists_and_matches")))

    def test_unexpected_legacy_shape_and_missing_required_fields_rejected(self):
        for bad in [
            wrap([{"field":"owner_uid","value":0,"operation":"equals",
                   "existence":"one_or_more","match":"all"}]),
            wrap([{"owner_uid":{"value":0,"operation":"equals",
                                "existence":"one_or_more","match":"all"}}]),
            wrap([{"owner_uid":{"equals":0}}]),
            wrap([{"owner_uid":0}]),
            wrap([{"owner_uid":{"equals":0,"not_equal":1,
                                "require":"at_least_one_exists_and_all_match"}}]),
            wrap([{"owner_uid":{"equals":0,"require":"not_an_allowed_pair"}}]),
            wrap([{"value":{"record":{"fields":{"productstate":{
                "bitwise_and":4096,
                "require":"at_least_one_exists_and_all_match"}}}}}]),
            {"authoring_format":"scap-ng-compact-research/0.4",**wrap([field()])},
            wrap([{"field":{"equals":0,"require":"at_least_one_exists_and_all_match",
                            "existence":"one_or_more"}}]),
        ]:
            with self.subTest(bad=bad):
                self.assertTrue(validate(bad))

    def test_repeated_fields_are_separate_entries_not_duplicate_keys(self):
        data=wrap([field("owner_uid","equals",0),field("owner_uid","not_equal",1000)])
        data["assessment"]["tests"]["example-test"]["states_match"]="all"
        self.assertFalse(validate(data))

def released_source_check(source:Path):
    from research_04_one_grammar_proof import make_single,benchmark_dir
    import research_04_rhel9_compact_preview as p
    from research_04_three_benchmark_quantifier import BENCHMARKS
    counts=Counter()
    failures=[]
    with zipfile.ZipFile(source) as z:
        dirs={f.split("/")[1] for f in z.namelist() if f.startswith("authoring/") and "/rules/" in f}
        for benchmark in BENCHMARKS:
            old=p.SOURCE_PREFIX
            p.SOURCE_PREFIX="authoring/"+benchmark_dir(dirs,benchmark)+"/"
            try:docs,raw=p.archive_contents(z)
            finally:p.SOURCE_PREFIX=old
            for path,doc in docs.items():
                if not isinstance(doc,dict) or (doc.get("assessment") or {}).get("mode")!="automated":continue
                short,metrics,notes=make_single(doc)
                errors=validate(short)
                counts["assessments_seen"]+=1
                counts[f"{benchmark}_seen"]+=1
                if errors:
                    counts["assessment_failures"]+=1
                    for error in errors[:3]:
                        failures.append({
                            "benchmark":benchmark,"path":path,
                            "instance_path":list(map(str,error.path)),
                            "message":error.message[:420],
                        })
                else:
                    counts["assessment_passes"]+=1
    return dict(counts),failures[:35]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(OneGrammarSchemaTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    if args.source_zip:
        counts,errors=released_source_check(args.source_zip)
        report={"status":"research_fragment_only","counts":counts,"sample_errors":errors}
        print(json.dumps(report,indent=2))
        if args.report:
            args.report.parent.mkdir(parents=True,exist_ok=True)
            args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        if counts["assessment_failures"]:
            raise SystemExit(f"{counts['assessment_failures']} fixture Assessments fail candidate fragment; resolve before schema promotion")
if __name__=="__main__":main()
