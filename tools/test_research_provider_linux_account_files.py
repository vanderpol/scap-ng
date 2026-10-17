#!/usr/bin/env python3
"""Real filesystem fixtures for typed account-derived Linux file provider.

No /etc/passwd enumeration, no real user home collection, no mutation outside
temporary test directories; no scanner/OVAL parity claim.
"""
from __future__ import annotations
import os
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_provider_linux_account_files import collect
from research_linux_init_permissions import evaluate, per_user_required_root_files,mode_complies

class LinuxAccountHomeFilesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.one=self.base/"root1"
        self.two=self.base/"root2"
        self.one.mkdir()
        self.two.mkdir()
        self.accounts=[
            {"id":"uid0a","username":"rootA","uid":0,"home_dir":str(self.one)},
            {"id":"uid0b","username":"rootB","uid":0,"home_dir":str(self.two)}
        ]
    def write(self,base,name,mode):
        file=base/name
        file.write_text("fixture")
        os.chmod(file,mode)
        return file
    def get(self,accounts=None,**opts):
        return collect(accounts if accounts is not None else self.accounts,
                       filename_pattern=r"^\.[^\s\.]+",**opts)
    def test_root_global_union_not_per_root_minimum(self):
        self.write(self.two,".profile",0o600)
        result=self.get()
        self.assertEqual(result["status"],"complete")
        self.assertEqual(len(result["items"]),1)
        self.assertEqual(result["items"][0]["account_id"],"uid0b")
        snap={"accounts":self.accounts,"files":result["items"],
              "accounts_status":"complete","files_status":result["status"]}
        self.assertEqual(evaluate(snap,"root").result,"true")
        self.assertFalse(per_user_required_root_files(snap))
    def test_bitmask_with_real_stat_mode(self):
        self.write(self.one,".bashrc",0o644)
        result=self.get()
        self.assertEqual(len(result["items"]),1)
        self.assertEqual(result["items"][0]["mode"],0o644)
        self.assertFalse(mode_complies(result["items"][0]["mode"]))
    def test_hidden_prefix_and_excluded_directories(self):
        self.write(self.one,"normal",0o777)
        self.write(self.one,".bashrc",0o600)
        (self.one/".config").mkdir()
        result=self.get()
        self.assertEqual([x["name"] for x in result["items"]],[".bashrc"])
    def test_missing_home_directory_yields_incomplete_not_empty_pass(self):
        bad=[{"id":"missing","username":"rootA","uid":0,
              "home_dir":str(self.base/"does-not-exist")}]
        result=self.get(bad)
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["items"],[])
        self.assertEqual(result["diagnostics"][0]["reason"],"home enumeration failed")
    def test_max_items_truncation_is_not_complete(self):
        self.write(self.one,".a",0o600)
        self.write(self.one,".b",0o600)
        result=self.get(max_items=1)
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["items"]),1)
        self.assertTrue(any(x["reason"]=="max_items reached" for x in result["diagnostics"]))
    def test_namespaced_account_references_do_not_collapse_shared_home(self):
        shared=[
            {"id":"uid0a","username":"rootA","uid":0,"home_dir":str(self.one)},
            {"id":"uid0b","username":"rootB","uid":0,"home_dir":str(self.one)}
        ]
        self.write(self.one,".profile",0o600)
        result=self.get(shared)
        self.assertEqual(len(result["items"]),2)
        self.assertEqual({x["account_id"] for x in result["items"]},{"uid0a","uid0b"})
        self.assertEqual(len({x["path"] for x in result["items"]}),1)
        self.assertEqual(len({x["id"] for x in result["items"]}),2)
        # Distinct per-account evidence links are intentional, but original
        # union/deduplication semantics need independent SCAP 1.4 proof.
    def test_symlink_to_file_is_explicit_provider_option(self):
        real=self.write(self.one,"target",0o600)
        (self.one/".link").symlink_to(real)
        nofollow=self.get(follow_symlinks=False)
        follow=self.get(follow_symlinks=True)
        self.assertEqual(len(nofollow["items"]),1)
        self.assertEqual(len(follow["items"]),1)
        self.assertEqual(follow["items"][0]["mode"],0o600)
        self.assertTrue(follow["items"][0]["is_symlink"])
        self.assertFalse(nofollow["symlink_files_followed"])
    def test_input_validation(self):
        with self.assertRaises(ValueError):
            self.get(max_items=0)
        with self.assertRaises(ValueError):
            self.get([{"id":"bad","username":"bad","home_dir":"relative"}])
        with self.assertRaises(ValueError):
            self.get([{"id":"bad","username":"bad","home_dir":"/"}],follow_symlinks="yes")
    def test_manifest_matches_real_emitted_schema(self):
        import yaml
        manifest=yaml.safe_load((Path(__file__).resolve().parents[1]/
            "research/requirements-first-language/providers/linux.files_from_account_homes.v0.1.yaml").read_text())
        self.write(self.one,".profile",0o600)
        observed=self.get()
        self.assertEqual(manifest["provider"],observed["provider"])
        self.assertEqual(manifest["version"],observed["version"])
        self.assertEqual(set(manifest["collection"]["exposed_fields"]),set(observed["items"][0]))
        self.assertEqual(manifest["collection"]["max_items_reached"],"incomplete")
        self.assertEqual(manifest["scope"]["directory"],"immediate_children_only")

    def test_non_system_absent_files_known_complete(self):
        users=[{"id":"u","username":"jane","uid":1001,"home_dir":str(self.one)}]
        result=self.get(users)
        snap={"accounts":users,"files":result["items"],
              "accounts_status":"complete","files_status":result["status"]}
        self.assertEqual(evaluate(snap,"non_system").result,"true")

if __name__=="__main__": unittest.main()
