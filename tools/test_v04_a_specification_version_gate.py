#!/usr/bin/env python3
"""#232/#239: strict source declaration gate, including known six-STIG mismatch."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_specification_version_gate import inspect, main

SPEC="scap-ng.pre-alpha.assessment"


def source(bench_version="0.3.0", assessment_version="0.4.0"):
    return {
        "authoring/benchmark.json": {"benchmark": {
            "id": "ng.demo.rhel9",
            "assessment_specifications": [{"id": SPEC, "version": bench_version}]
        }},
        "authoring/auto.json": {"assessment": {
            "id": "ng.demo.home", "mode": "automated",
            "specification": {"id": SPEC, "version": assessment_version}
        }},
        "authoring/manual.json": {"assessment": {
            "id": "ng.demo.manual", "mode": "manual"
        }},
    }


class VersionGateTests(unittest.TestCase):
    def test_known_r3_style_mismatch_blocks(self):
        x=inspect(source())
        self.assertEqual(x["status"], "BLOCKED_UNDECLARED_SPECIFICATION")
        self.assertEqual(x["unmatched_automated_specs"][0]["specification"]["version"], "0.4.0")
        self.assertEqual(x["unmatched_automated_specs"][0]["automated_assessments"], 1)
        self.assertFalse(x["allowed_to_compile"])
        self.assertEqual(x["contextual_manual_assessments"], 1)

    def test_matching_versions_only_satisfy_necessary_condition(self):
        x=inspect(source("0.4.0"))
        self.assertEqual(x["status"], "DECLARATIONS_CONSISTENT_NOT_COMPILED")
        self.assertFalse(x["allowed_to_compile"])
        self.assertEqual(x["unmatched_automated_specs"], [])

    def test_original_source_is_not_edited_or_upgraded(self):
        originals=source()
        frozen=json.dumps(originals,sort_keys=True)
        inspect(originals)
        self.assertEqual(json.dumps(originals,sort_keys=True),frozen)

    def test_no_benchmark_is_error(self):
        x=source()
        del x["authoring/benchmark.json"]
        with self.assertRaisesRegex(ValueError, "no Benchmarks"):
            inspect(x)

    def test_missing_benchmark_declaration_is_error(self):
        x=source()
        del x["authoring/benchmark.json"]["benchmark"]["assessment_specifications"]
        with self.assertRaisesRegex(ValueError, "missing explicit"):
            inspect(x)

    def test_duplicate_declared_spec_is_error(self):
        x=source()
        declarations=x["authoring/benchmark.json"]["benchmark"]["assessment_specifications"]
        declarations.append(deepcopy(declarations[0]))
        with self.assertRaisesRegex(ValueError, "duplicate Benchmark"):
            inspect(x)

    def test_unknown_assessment_mode_never_accepted_as_manual(self):
        x=source("0.4.0")
        x["authoring/auto.json"]["assessment"]["mode"]="guess"
        r=inspect(x)
        self.assertEqual(r["status"], "BLOCKED_UNDECLARED_SPECIFICATION")
        self.assertEqual(r["errors"][0]["reason"], "unknown_assessment_mode")

    def test_missing_automated_spec_is_not_accepted_as_inherited(self):
        x=source("0.4.0")
        x["authoring/auto.json"]["assessment"].pop("specification")
        r=inspect(x)
        self.assertEqual(r["status"], "BLOCKED_UNDECLARED_SPECIFICATION")
        self.assertEqual(r["errors"][0]["reason"], "missing_automated_specification")

    def test_extra_spec_fields_are_not_silently_dropped(self):
        x=source()
        x["authoring/auto.json"]["assessment"]["specification"]["approved"]=True
        with self.assertRaisesRegex(ValueError,"ambiguous specification"):
            inspect(x)

    def test_duplicate_benchmark_identity_is_error(self):
        x=source()
        x["authoring/second.json"]={"benchmark":deepcopy(x["authoring/benchmark.json"]["benchmark"])}
        with self.assertRaisesRegex(ValueError, "duplicate Benchmark id"):
            inspect(x)

    def test_version_union_does_not_claim_per_rule_proof(self):
        x=source("0.4.0")
        r=inspect(x)
        self.assertEqual(r["proof_stage"], "global_declaration_necessary_condition_only")
        self.assertFalse(r["allowed_to_compile"])

    def test_cli_exit_code_blocks_real_build(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"x.zip"
            with ZipFile(path,"w") as zf:
                for name,doc in source().items():
                    zf.writestr(name,json.dumps(doc))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--json-archive",str(path)]),2)
                self.assertEqual(main(["--json-archive",str(path),"--expect-blocked"]),0)

    def test_cli_consistent_yml_and_json(self):
        import yaml
        with TemporaryDirectory() as folder:
            jp, yp=(Path(folder)/f"{x}.zip" for x in ("json","yaml"))
            with ZipFile(jp,"w") as zf:
                for path,doc in source().items():
                    zf.writestr(path,json.dumps(doc))
            with ZipFile(yp,"w") as zf:
                for path,doc in source().items():
                    zf.writestr(path.replace(".json",".yaml"),yaml.safe_dump(doc))
            buf=io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(["--json-archive",str(jp),
                                       "--yaml-archive",str(yp),
                                       "--expect-blocked"]),0)
            self.assertTrue(json.loads(buf.getvalue())["yaml_json_agree"])


if __name__=="__main__":
    unittest.main()
