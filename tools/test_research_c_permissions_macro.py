#!/usr/bin/env python3
"""#245 0.4-C permission shorthand: real RHEL9 source and all 4096 mode cases.

The source-based check covers only the 8 permission booleans, NOT the
full home-directory collector and its two distinct existence requirements.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_permissions_macro import (
    lower_no_more_permissive_than,evaluate_mode_against_C_macro,
    OVAL_BITS)
from research_c_require_language import compile_c_requirement

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/assessment-simplification/compact-authoring-04"
SOURCE=ROOT/("research/assessment-simplification/samples/rhel_9/assessments/"
             "automated/niwc.rhel_9.SV-257889.automated.assessment.yaml")

class PosixPermissionMacroAgainstRealSource(unittest.TestCase):
    def setUp(self):
        self.raw=yaml.safe_load(SOURCE.read_text())["assessment"]
        self.c=yaml.safe_load((BASE/"c-permissions-0740.research.yaml").read_text())
        self.macro=lower_no_more_permissive_than(
            self.c["must"]["every_item"]["permission_bits"])
        self.native=compile_c_requirement(self.c)["test"]

    def test_real_source_8_flags_exactly_match_a_native_macro(self):
        original=self.raw["states"]["state-mode-0740-or-less-permissive"]["state"]["all"]
        original_names=set()
        for f in original:
            self.assertEqual(f["value"],"false")
            self.assertEqual(f["operation"],"equals")
            self.assertEqual(f["datatype"],"boolean")
            original_names.add(f["field"])
        self.assertEqual(len(original_names),8)
        self.assertEqual(original_names,
                         {x["source_field"] for x in self.macro["forbidden"]})
        self.assertEqual(len(self.native["states"]),8)
        self.assertEqual(self.native["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(self.native["states_match"],"all")
        self.assertFalse(self.macro["scanner_executed"])
        self.assertFalse(self.macro["source_parity_verified"])

    def test_every_12_bit_posix_mode_vs_original_eight_independent_booleans(self):
        source_names={x["field"] for x in
            self.raw["states"]["state-mode-0740-or-less-permissive"]["state"]["all"]}
        source_bits=[bit for name,bit in OVAL_BITS if name in source_names]
        self.assertEqual(len(source_bits),8)
        forbidden={row["octal_bit"] for row in self.macro["forbidden"]}
        self.assertEqual(forbidden,{format(bit,"04o") for bit in source_bits})
        for mode in range(0o10000):  # Exactly all 4,096 twelve-bit modes.
            # Source State terms evaluated as eight separately observed
            # booleans; C uses one mask-subset operation, then lowers to
            # the identical native State fields. No numeric <= operator.
            original=all((mode & bit)==0 for bit in source_bits)
            rewritten=evaluate_mode_against_C_macro(mode,self.macro)
            self.assertEqual(original,rewritten,
                             f"0{mode:o} source/C permissions differ")
        for mode,expected in (
            (0o740,True),(0o700,True),(0o604,False),
            (0o600,True),(0o750,False),(0o4740,False),(0o7777,False)
        ):
            self.assertEqual(evaluate_mode_against_C_macro(mode,self.macro),expected)
        self.assertLess(0o604,0o740)  # Shows why numeric <= is NOT equivalent.
        self.assertFalse(evaluate_mode_against_C_macro(0o604,self.macro))

    def test_macro_fails_closed_on_unknown_fields_types_and_masks(self):
        for invalid in (
            "0748","0780","-0740","77400","0o740",740,True,None,"7777","00000"
        ):
            c=deepcopy(self.c)
            c["must"]["every_item"]["permission_bits"]={
                "no_more_permissive_than":invalid
            }
            with self.subTest(mask=invalid):
                with self.assertRaises(ValueError):
                    compile_c_requirement(c)
        for wrong in (
            {"more_permissive_than":"0740"},
            {"no_more_permissive_than":"0740","other":"ignored"},
        ):
            with self.assertRaises(ValueError):
                lower_no_more_permissive_than(wrong)

    def test_macro_cannot_be_claimed_for_windows_or_other_capabilities(self):
        c=deepcopy(self.c)
        c["from"]={"windows.registry":{"hive":"local_machine","key":"Example","name":"Setting"}}
        with self.assertRaisesRegex(ValueError,"only valid"):
            compile_c_requirement(c)

    def test_real_source_accounts_cannot_be_overwritten_by_one_file_target(self):
        a=self.raw
        tests=a["tests"]
        self.assertEqual(len(tests),2)
        by_existence={t["check_existence"]:name for name,t in tests.items()}
        self.assertEqual(set(by_existence),{"any_exist","at_least_one_exists"})
        self.assertEqual(a["evaluate"],{"all":[{"test":name} for name in tests]})
        self.assertEqual(set(a["variables"]),{
            "home-directories-non-system-users-variable",
            "home-directory-root-user-variable"})
        # The simplified macro is ONLY a value requirement. The original
        # variable-scoped file populations and existence remain separate.
        self.assertEqual(self.c["from"]["unix.file"]["full_path"],"/etc/passwd")
        self.assertNotEqual(
            self.c["from"]["unix.file"]["full_path"],
            "home-directories-non-system-users-variable")

if __name__=="__main__":
    unittest.main()
