#!/usr/bin/env python3
"""Owner-approved 0.3 Assessment default alias and tailoring regression."""
from pathlib import Path
import tempfile
import unittest
import zipfile
import yaml

from drop_redundant_default import rewrite_rule, curate


def rule(default="automated", distinct=False):
    automated="check.auto"
    legacy="check.unique" if distinct else ("check.auto" if default=="automated" else "check.manual")
    choices=f"""  assessment_choices:
    default:
      assessment: {legacy}
"""
    if default=="automated" or distinct:
        choices+=f"""    automated:
      assessment: {automated}
"""
    choices+="""    manual:
      assessment: check.manual
"""
    return f"""rule:
  id: rule.example
{choices}  default_assessment_choice: default
""".encode("utf-8")


class DefaultChoiceTests(unittest.TestCase):
    def test_automated_default_semantics_and_tailoring(self):
        original=rule()
        output, selector=rewrite_rule(original,"auto.rule.yaml")
        self.assertEqual(selector,"automated")
        before=yaml.safe_load(original)["rule"]
        after=yaml.safe_load(output)["rule"]
        self.assertNotIn("default",after["assessment_choices"])
        self.assertEqual(before["assessment_choices"]["default"],after["assessment_choices"][after["default_assessment_choice"]])
        self.assertEqual(before["assessment_choices"]["manual"],after["assessment_choices"]["manual"])
        self.assertEqual(after["default_assessment_choice"],"automated")

    def test_manual_only_default(self):
        source=rule(default="manual")
        output,selector=rewrite_rule(source,"manual.rule.yaml")
        self.assertEqual(selector,"manual")
        after=yaml.safe_load(output)["rule"]
        self.assertEqual(set(after["assessment_choices"]),{"manual"})
        self.assertEqual(after["default_assessment_choice"],"manual")

    def test_preserve_unique_legacy_default_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"unique meaning"):
            rewrite_rule(rule(distinct=True),"distinct.rule.yaml")

    def test_already_native_and_bad_selection(self):
        source=b"""rule:
  id: rule.example
  assessment_choices:
    manual:
      assessment: check.manual
  default_assessment_choice: manual
"""
        self.assertEqual(rewrite_rule(source,"native.rule.yaml"),(source,None))
        with self.assertRaisesRegex(ValueError,"invalid publisher default"):
            rewrite_rule(source.replace(b"default_assessment_choice: manual",b"default_assessment_choice: automated"),"bad.rule.yaml")

    def test_archive_preserves_other_content_and_assessments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            infile=root/"in.zip"; outfile=root/"out.zip"
            blob=b"assessment:\n  id: check.manual\n  version: 1\n"
            with zipfile.ZipFile(infile,"w") as z:
                z.writestr("authoring/fixture/rules/rule.example.rule.yaml",rule())
                z.writestr("authoring/shared/assessments/common/check.yaml",blob)
                z.writestr("README.md",b"Original release identity")
            result=curate(infile,outfile,expected_rules=1)
            self.assertEqual(result["removed_aliases"],1)
            self.assertEqual(result["assessments_unmodified"],1)
            with zipfile.ZipFile(outfile) as z:
                self.assertEqual(z.read("authoring/shared/assessments/common/check.yaml"),blob)
                self.assertEqual(z.read("README.md"),b"Original release identity")


if __name__=="__main__":
    unittest.main()
