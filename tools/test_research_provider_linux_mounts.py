#!/usr/bin/env python3
"""Prototype provider contract tests; synthetic strings plus read-only CI smoke."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_provider_linux_mounts import (
    parse_mountinfo_line,parse_mountinfo_text,collect_current_linux_mounts)
from research_requirements_first_evidence import evaluate

NAMESPACE="mnt:[test]"
NORMAL="201 101 8:17 / /home rw,nosuid,relatime shared:8 - ext4 /dev/sdb1 rw,data=ordered"
BAD="202 101 8:18 / /home rw,relatime shared:8 - ext4 /dev/sdb2 rw"
OTHER="203 101 8:19 / /var rw,nosuid,relatime - ext4 /dev/sdc rw"

class MountProviderContractTests(unittest.TestCase):
    def test_decode_and_separate_vfs_from_superblock(self):
        x=parse_mountinfo_line(NORMAL,NAMESPACE)
        self.assertEqual(x["id"],NAMESPACE+":201")
        self.assertEqual(x["fields"]["mount_id"],201)
        self.assertEqual(x["fields"]["mount_point"],"/home")
        self.assertIn("nosuid",x["fields"]["mount_options"])
        self.assertNotIn("data=ordered",x["fields"]["mount_options"])
        self.assertIn("data=ordered",x["fields"]["super_options"])
        self.assertEqual(x["fields"]["source"],"/dev/sdb1")
        self.assertEqual(x["fields"]["optional_fields"],["shared:8"])

    def test_mountpoint_decode_space_tab_newline_literal_backslash(self):
        sample=r"211 101 0:43 / /spaces\040tabs\011newlines\012slash\134dir rw - tmpfs tmpfs rw"
        x=parse_mountinfo_line(sample,NAMESPACE)
        self.assertEqual(x["fields"]["mount_point"],"/spaces tabs\tnewlines\nslash\\dir")

    def test_bad_escape_rejected_as_incomplete_not_omitted(self):
        sample=r"222 101 0:43 / /bad\999escape rw - tmpfs tmpfs rw"
        result=parse_mountinfo_text(NORMAL+"\n"+sample,NAMESPACE)
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)
        self.assertEqual(result["items"][0]["id"],NAMESPACE+":201")
        self.assertEqual(result["diagnostics"][0]["line"],2)

    def test_missing_separator_causes_incomplete(self):
        result=parse_mountinfo_text(NORMAL+"\n"+"not mountinfo",NAMESPACE)
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)

    def test_same_path_not_deduped_by_path(self):
        result=parse_mountinfo_text(NORMAL+"\n"+BAD,NAMESPACE)
        self.assertEqual(result["status"],"complete")
        self.assertEqual(len(result["items"]),2)
        self.assertEqual([x["fields"]["mount_point"] for x in result["items"]],["/home","/home"])
        self.assertNotEqual(result["items"][0]["id"],result["items"][1]["id"])

    def test_duplicate_identity_forces_incomplete(self):
        result=parse_mountinfo_text(NORMAL+"\n"+NORMAL,NAMESPACE)
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)
        self.assertIn("duplicate mount identity",result["diagnostics"][0]["reason"])

    def test_no_real_home_mount_is_a_valid_complete_zero_selection(self):
        result=parse_mountinfo_text(OTHER,NAMESPACE)
        verdict=evaluate(result,where={"mount_point":{"equals":"/home"}},
            must={"mount_options":{"contains":"nosuid"}},minimum_resources=1)
        self.assertEqual((verdict.verdict,verdict.observed,verdict.selected),("false",1,0))

    def test_real_parsed_evidence_exposes_same_path_failure(self):
        result=parse_mountinfo_text(NORMAL+"\n"+BAD,NAMESPACE)
        verdict=evaluate(result,where={"mount_point":{"equals":"/home"}},
            must={"mount_options":{"contains":"nosuid"}},minimum_resources=1)
        self.assertEqual(verdict.verdict,"false")

    def test_partial_parsed_mountinfo_does_not_pass_by_partial_success(self):
        result=parse_mountinfo_text(NORMAL+"\n"+"bad incomplete line",NAMESPACE)
        verdict=evaluate(result,where={"mount_point":{"equals":"/home"}},
            must={"mount_options":{"contains":"nosuid"}},minimum_resources=1)
        self.assertEqual(verdict.verdict,"unknown")

    def test_namespace_is_part_of_identity(self):
        first=parse_mountinfo_line(NORMAL,"mnt:[first]")
        second=parse_mountinfo_line(NORMAL,"mnt:[second]")
        self.assertNotEqual(first["id"],second["id"])

    def test_versioned_manifest_matches_real_parsed_record(self):
        import yaml
        contract=(Path(__file__).resolve().parents[1]/
                  "research/requirements-first-language/providers/linux.mounts.v0.1.yaml")
        manifest=yaml.safe_load(contract.read_text())
        item=parse_mountinfo_line(NORMAL,NAMESPACE)
        self.assertEqual(manifest["provider"],"linux.mounts")
        self.assertEqual(manifest["version"],"0.1.0")
        self.assertEqual(manifest["resources"]["identity"],["namespace","mount_id"])
        self.assertEqual(set(manifest["resources"]["field_types"]),set(item["fields"]))
        self.assertEqual(manifest["selection"]["missing_selector"],"unresolved")
        self.assertEqual(manifest["collection_status"]["incomplete"],"at_least_one_line_failed_parsing")

    def test_ci_linux_runner_actual_mountinfo_smoke(self):
        path=Path("/proc/self/mountinfo")
        if not path.exists():
            self.skipTest("Linux /proc not available")
        r=collect_current_linux_mounts()
        self.assertEqual(r["provider"],"linux.mounts")
        self.assertEqual(r["provider_version"],"0.1.0")
        self.assertEqual(r["status"],"complete",r["diagnostics"])
        self.assertGreater(len(r["items"]),0)
        self.assertTrue(r["namespace"].startswith("mnt:["))
        ids={x["id"] for x in r["items"]}
        self.assertEqual(len(ids),len(r["items"]))

if __name__=="__main__":unittest.main()
