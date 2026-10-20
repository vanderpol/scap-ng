#!/usr/bin/env python3
"""Stale authoring-sample Markdown gate fixtures."""
from pathlib import Path
import tempfile
import unittest

from audit_current_markdown_samples import CURRENT,NEEDS_CURRENT_RELEASE,RELEASE,check


class CurrentMarkdownSampleAuditTests(unittest.TestCase):
    def create(self,root):
        for relative in CURRENT:
            f=root/relative
            f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text("# SCAP-NG 0.4.0 current examples\\n"
                         + (RELEASE if relative in NEEDS_CURRENT_RELEASE else "")
                         + "\\n",encoding="utf-8")
        f=root/"archive/0.3.0/README.md"
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text("# Historical v0.3.0-six-stig-typed-operators\\n")

    def test_valid_current_and_preserved_history(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            self.create(r)
            count,errors=check(r)
            self.assertEqual(count,len(CURRENT))
            self.assertEqual(errors,[])

    def test_old_sample_release_cannot_be_recommended_as_current(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            self.create(r)
            f=r/"specification/examples/assessments.md"
            f.write_text(f.read_text()+"\\nhttps://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig/old.zip\\n")
            _,errors=check(r)
            self.assertTrue(any("stale 0.3" in e for e in errors))

    def test_old_status_and_missing_version_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            self.create(r)
            f=r/"README.md"
            f.write_text("# SCAP-NG 0.3 examples\\n0.3.0 remains the active baseline.")
            _,errors=check(r)
            self.assertTrue(any("approved 0.4" in e for e in errors))
            self.assertTrue(any("current status" in e for e in errors))

    def test_missing_archive_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            self.create(r)
            (r/"archive/0.3.0/README.md").unlink()
            _,errors=check(r)
            self.assertTrue(any("historic" in e for e in errors))


if __name__=="__main__":
    unittest.main()
