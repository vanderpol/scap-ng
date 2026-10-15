"""Focused Rule Assessment-choice closure regressions, using tiny source archives."""
import io
import unittest
import zipfile

import yaml

from export_v04_joval_six_format_preview import (
    audit_rule_assessment_choices,
    include_shared_rule_choices,
)


def assessment(ident, mode="manual"):
    return {"assessment": {"id": ident, "mode": mode}}


def rule(default="manual", choices=None):
    if choices is None:
        choices = {"manual": {"assessment": "ng.shared.example"}}
    return {"rule": {"id": "SV-TEST", "assessment_choices": choices,
                     "default_assessment_choice": default}}


def archive(*entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as out:
        for path, document in entries:
            out.writestr(path, yaml.safe_dump(document))
    return zipfile.ZipFile(io.BytesIO(stream.getvalue()))


class ChoiceClosureTests(unittest.TestCase):
    rule_path = "authoring/rhel_9/rules/SV-TEST.rule.yaml"
    shared_path = "authoring/shared/assessments/windows/example.manual.yaml"

    def test_shared_manual_included_and_all_choices_resolve(self):
        local = "authoring/rhel_9/assessments/automated/SV-TEST.automated.yaml"
        selected = rule(choices={
            "manual": {"assessment": "ng.shared.example"},
            "automated": {"assessment": "SV-TEST.automated"}})
        entries = [(self.rule_path, selected),
                   (local, assessment("SV-TEST.automated", "automated")),
                   (self.shared_path, assessment("ng.shared.example"))]
        with archive(*entries) as src:
            docs = dict(entries[:2])
            original = {path: src.read(path) for path, _ in entries[:2]}
            self.assertEqual(include_shared_rule_choices(src, docs, original, "rhel_9"), 1)
            self.assertEqual(original[self.shared_path], src.read(self.shared_path))
            self.assertEqual(audit_rule_assessment_choices(docs),
                             {"rules": 1, "choice_links": 2, "unique_assessments": 2,
                              "unresolved_choices": 0, "duplicate_assessment_ids": 0})

    def test_missing_shared_manual_fails_closed(self):
        with archive((self.rule_path, rule())) as src:
            with self.assertRaisesRegex(ValueError, "unresolved source Rule Assessment choice"):
                include_shared_rule_choices(src, {self.rule_path: rule()},
                                            {self.rule_path: src.read(self.rule_path)}, "rhel_9")

    def test_duplicate_shared_manual_fails(self):
        second = "authoring/shared/assessments/windows/other.assessment.yaml"
        entries = [(self.rule_path, rule()),
                   (self.shared_path, assessment("ng.shared.example")),
                   (second, assessment("ng.shared.example"))]
        with archive(*entries) as src:
            with self.assertRaisesRegex(ValueError, "Ambiguous shared Assessment ID"):
                include_shared_rule_choices(src, {self.rule_path: rule()},
                                            {self.rule_path: src.read(self.rule_path)}, "rhel_9")

    def test_undeclared_default_choice_fails(self):
        source_rule = rule(default="automated")
        with archive((self.rule_path, source_rule)) as src:
            with self.assertRaisesRegex(ValueError, "default Assessment choice"):
                include_shared_rule_choices(src, {self.rule_path: source_rule},
                                            {self.rule_path: src.read(self.rule_path)}, "rhel_9")

    def test_final_archive_detects_dangling_id(self):
        with self.assertRaisesRegex(ValueError, "Unresolved packaged Rule Assessment choices"):
            audit_rule_assessment_choices({self.rule_path: rule()})

    def test_final_archive_detects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "Duplicate packaged Assessment ID"):
            audit_rule_assessment_choices({
                "a.assessment.yaml": assessment("same"),
                "b.assessment.yaml": assessment("same")})


if __name__ == "__main__":
    unittest.main()
