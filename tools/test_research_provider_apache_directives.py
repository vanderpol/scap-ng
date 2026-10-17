#!/usr/bin/env python3
"""Adversarial Apache multi-file fixture tests, no real Apache invocation."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_provider_apache_directives import collect

class ApacheConfigProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.conf=self.base/"httpd.conf"

    def write(self, name, content):
        f=self.base/name
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(content)
        return f

    def read(self, **kwargs):
        return collect(self.conf,server_root=self.base,**kwargs)

    def test_single_primary_config_preserves_raw_line_and_source(self):
        self.write("httpd.conf","# ignored\nKeepAlive On\nMaxKeepAliveRequests 125\n")
        result=self.read()
        self.assertEqual(result["status"],"complete")
        self.assertEqual([(x["fields"]["name"],x["fields"]["raw_value"])
                          for x in result["items"]],
                         [("KeepAlive","On"),("MaxKeepAliveRequests","125")])
        self.assertEqual([x["fields"]["source_line"] for x in result["items"]],[2,3])
        self.assertFalse(result["effective_values_supported"])
        self.assertEqual(result["items"][0]["fields"]["source_file"],str(self.conf))

    def test_recursive_include_and_optional_missing_are_distinct(self):
        self.write("httpd.conf",
                   "Include conf.d/*.conf\nIncludeOptional conf.d/not-there-*.conf\n")
        self.write("conf.d/one.conf","KeepAlive On\nInclude nested/two.conf\n")
        self.write("nested/two.conf","MaxKeepAliveRequests 120\n")
        result=self.read()
        self.assertEqual(result["status"],"complete",result["diagnostics"])
        self.assertEqual(len(result["files"]),3)
        self.assertEqual([x["fields"]["name"] for x in result["items"]],
                         ["KeepAlive","MaxKeepAliveRequests"])
        self.assertEqual(result["items"][1]["fields"]["source_file"],
                         str(self.base/"nested/two.conf"))

    def test_missing_required_include_forces_incomplete(self):
        self.write("httpd.conf","KeepAlive On\nInclude nonexistent.conf\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)
        self.assertIn("required_include_unmatched",
                      {d["reason"] for d in result["diagnostics"]})

    def test_missing_optional_include_does_not_trigger_diagnostic(self):
        self.write("httpd.conf","KeepAlive On\nIncludeOptional nowhere/*.conf\n")
        result=self.read()
        self.assertEqual(result["status"],"complete")

    def test_conditional_config_does_not_claim_known_effective_directive(self):
        self.write("httpd.conf",
                   "<IfModule unknown_module>\nKeepAlive Off\n</IfModule>\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)
        self.assertFalse(result["effective_values_supported"])
        self.assertEqual(result["items"][0]["fields"]["raw_value"],"Off")
        self.assertIn("conditional_or_container_context_unsupported",
                      {x["reason"] for x in result["diagnostics"]})

    def test_conflicting_duplicate_values_both_retained(self):
        self.write("httpd.conf","KeepAlive On\nInclude conf.d/late.conf\n")
        self.write("conf.d/late.conf","KeepAlive Off\n")
        result=self.read()
        self.assertEqual(result["status"],"complete")
        self.assertEqual([x["fields"]["raw_value"] for x in result["items"]],["On","Off"])
        self.assertEqual(len(set(x["fields"]["source_file"] for x in result["items"])),2)

    def test_lookalike_directive_does_not_get_normalized_to_keepalive(self):
        self.write("httpd.conf","KeepAliveTimeout 15\nKeepAlive On\n")
        result=self.read()
        self.assertEqual(len(result["items"]),1)
        self.assertEqual(result["items"][0]["fields"]["name"],"KeepAlive")

    def test_missing_root_file_is_incomplete_not_known_empty(self):
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["items"],[])

    def test_include_cycle_reports_incomplete(self):
        self.write("httpd.conf","Include conf.d/a.conf\n")
        self.write("conf.d/a.conf","KeepAlive On\nInclude httpd.conf\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("include_cycle",{x["reason"] for x in result["diagnostics"]})
        self.assertEqual(len(result["items"]),1)

    def test_duplicate_include_status_is_not_silently_deduplicated(self):
        self.write("httpd.conf","Include conf.d/a.conf\nInclude conf.d/a.conf\n")
        self.write("conf.d/a.conf","KeepAlive On\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("duplicate_include_ambiguous",
                      {x["reason"] for x in result["diagnostics"]})

    def test_dynamic_include_does_not_disappear_as_no_matches(self):
        self.write("httpd.conf","Include conf.d/$"+"{SERVER_NAME}.conf\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("dynamic_include_unresolved",
                      {x["reason"] for x in result["diagnostics"]})

    def test_path_escape_is_marked_incomplete(self):
        self.write("httpd.conf","Include ../outside.conf\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("path_outside_server_root",
                      {x["reason"] for x in result["diagnostics"]})

    def test_max_file_limit_marks_partial(self):
        self.write("httpd.conf","Include conf.d/a.conf\n")
        self.write("conf.d/a.conf","KeepAlive On\n")
        result=self.read(max_files=1)
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("file_limit",{x["reason"] for x in result["diagnostics"]})

    def test_max_directive_limit_marks_partial(self):
        self.write("httpd.conf","KeepAlive On\nKeepAlive Off\n")
        result=self.read(max_directives=1)
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("directive_limit",{x["reason"] for x in result["diagnostics"]})

    def test_unparsed_line_does_not_silently_validate_file(self):
        self.write("httpd.conf","KeepAlive On\nbad!directive value\n")
        result=self.read()
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("unparsed_config_line",
                      {x["reason"] for x in result["diagnostics"]})

    def test_maxkeepalive_raw_value_not_automatically_typed(self):
        self.write("httpd.conf","MaxKeepAliveRequests 100garbage\n")
        result=self.read()
        self.assertEqual(result["status"],"complete")
        self.assertEqual(result["items"][0]["fields"]["raw_value"],"100garbage")

if __name__=="__main__":unittest.main()
