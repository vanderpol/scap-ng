#!/usr/bin/env python3
"""#237 test source-capability/feature overlap and blocker denominators."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_conversion_backlog import describe_assessment,assess_backlog,render_markdown
from research_b_six_stream_compiler import READY_STATUS


def cap(aid,capabilities,mode="automated",extra=None):
    tests={f"check-{n}":{"capability":c,"states":[{"record":{"x":1}}]}
           for n,c in enumerate(capabilities)}
    assessment={"id":aid,"mode":mode,"tests":tests}
    if extra: assessment.update(extra)
    return {"source_document":{"assessment":assessment}}


class BlockerCensusTests(unittest.TestCase):
    def setUp(self):
        self.caps={
            "a":cap("a",["windows.registry","windows.wmi.query"],extra={
                "variables":{"local_var":{"expression":{"concat":[]}}},
                "shared_objects":{"obj":{"filter":{"field":"x"}}}}),
            "b":cap("b",["windows.registry"]),
            "c":cap("c",["linux.partition"]),
            "m":cap("m",[],"manual"),
        }
        self.report={
            "source_tag":"pinned-fixture",
            "assessments":[
                {"assessment_id":"a","source_path":"a.yaml",
                 "benchmark_streams":["win11","server"],
                 "conversion_status":"unsupported_source_semantics",
                 "reason":"variable chain unsupported"},
                {"assessment_id":"b","source_path":"b.yaml",
                 "benchmark_streams":["server"],
                 "conversion_status":"unsupported_source_semantics",
                 "reason":"state field unsupported"},
                {"assessment_id":"c","source_path":"c.yaml",
                 "benchmark_streams":["linux"],
                 "conversion_status":READY_STATUS,"reason":"bounded conversion"},
                {"assessment_id":"m","source_path":"m.yaml",
                 "benchmark_streams":["linux"],
                 "conversion_status":"manual_procedure_ir_compiled",
                 "reason":"human only"},
            ],
        }

    def test_per_capability_overlapping_counts_are_not_unique_totals(self):
        result=assess_backlog(self.report,self.caps)
        self.assertEqual(result["unsupported_automated_assessments"],2)
        self.assertEqual(result["capability_assessment_counts"],
                         {"windows.registry":2,"windows.wmi.query":1})
        self.assertEqual(result["by_stream_capability_counts"]["win11"]["windows.registry"],1)
        self.assertEqual(result["by_stream_capability_counts"]["server"]["windows.registry"],2)
        self.assertNotIn("linux.partition",result["capability_assessment_counts"])

    def test_source_features_found_in_nested_records_and_vars(self):
        caps,flags,total=describe_assessment(self.caps["a"])
        self.assertEqual(total,2)
        self.assertTrue(flags["multiple_tests"])
        self.assertTrue(flags["states"])
        self.assertTrue(flags["record"])
        self.assertTrue(flags["variables"])
        self.assertTrue(flags["shared_objects"])
        self.assertTrue(flags["set_or_filter"])

    def test_ledger_missing_source_is_fatal(self):
        broken=dict(self.caps)
        del broken["b"]
        with self.assertRaisesRegex(ValueError,"disagree"):
            assess_backlog(self.report,broken)

    def test_readable_backlog_has_nonparity_warning(self):
        report=assess_backlog(self.report,self.caps)
        md=render_markdown(report)
        self.assertIn("Unsupported automated Assessments: 2",md)
        self.assertIn("not a reason to discard",md)
        self.assertIn("scanner semantics",md)

if __name__=="__main__":
    unittest.main()
