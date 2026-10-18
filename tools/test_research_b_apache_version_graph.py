#!/usr/bin/env python3
"""#237: true source Apache SV-214273 variable DAG in offline B fixture runtime."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR
from research_b_apache_version_graph import lower_apache_version_graph
from research_b_compiled_ir import encode,decode,evaluate_json
from research_b_source_shell_snapshot import normalize,PROVIDER

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml")


class ApacheVariableGraphTests(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(SOURCE.read_text())
        self.ast=lower_apache_version_graph(self.doc)
        self.payload=encode(self.doc["assessment"]["id"],self.ast)

    def acquisition(self,using,lines,status="complete",records=None):
        if records is None:
            records=[{"stdout_line":lines,"stderr_line":[],"exit_status":0}]
        return normalize({"query":using,"status":status,"records":records},**using)

    def fixtures(self,paths=None,versions=None,discovery_flag="complete",
                 version_flag="complete",include_target=True):
        if paths is None:paths=["/usr/sbin/httpd -DFOREGROUND"]
        if versions is None:versions=["Server version: Apache/2.4.66 (Unix)"]
        source=self.acquisition(self.ast["discovery_using"],paths,discovery_flag)
        queries=[source]
        if include_target and paths:
            using={**self.ast["version_using"],"command":"/usr/sbin/httpd -V"}
            queries.append(self.acquisition(using,versions,version_flag))
        return {PROVIDER:{"acquisitions":queries}}

    def verdict(self,evidence):
        return evaluate_json(self.payload,evidence).result

    def test_real_apache_source_variables_and_executable_ir(self):
        self.assertEqual(self.doc["assessment"]["id"],"SV-214273.automated")
        node=decode(self.payload)
        self.assertEqual(node["source_kind"],"compiler-compatibility")
        self.assertEqual(node["root"],self.ast)
        self.assertEqual(self.ast["command_suffix"]," -V")
        self.assertEqual(self.ast["state"]["expected"],"2.4")
        self.assertEqual(self.ast["version_using"]["shell"],"bash")
        self.assertNotIn("command",self.ast["version_using"])
        self.assertIn("ps -e -o command",self.ast["discovery_using"]["command"])

    def test_process_path_derived_without_executing_shell(self):
        self.assertEqual(self.verdict(self.fixtures()),TRUE)
        self.assertEqual(self.verdict(self.fixtures(
            versions=["Server version: Apache/2.3.99 (Unix)"])),FALSE)
        self.assertEqual(self.verdict(self.fixtures(
            versions=["Server version: Apache/2.4 (Unix)"])),TRUE)
        self.assertEqual(self.verdict(self.fixtures(
            versions=["Server version: Apache/2.4.0 (Unix)"])),TRUE)

    def test_unresolved_dependency_not_blind_true_or_false(self):
        self.assertEqual(self.verdict(self.fixtures(paths=[])),UNKNOWN)
        self.assertEqual(self.verdict(self.fixtures(include_target=False)),UNKNOWN)
        self.assertEqual(self.verdict(self.fixtures(
            paths=["/usr/sbin/httpd -DFOREGROUND","/opt/apache2/bin/apache2 -DFOREGROUND"])),UNKNOWN)
        self.assertEqual(self.verdict(self.fixtures(discovery_flag="incomplete")),UNKNOWN)
        self.assertEqual(self.verdict(self.fixtures(version_flag="incomplete")),UNKNOWN)

    def test_multivalued_version_entity_aggregation_within_one_item(self):
        self.assertEqual(self.verdict(self.fixtures(versions=[
            "Server version: Apache/2.2.0 (Unix)",
            "Server version: Apache/2.4.1 (Unix)"])),TRUE)
        self.assertEqual(self.verdict(self.fixtures(versions=[
            "Server version: Apache/2.3.1 (Unix)",
            "Server version: Apache/2.3.9 (Unix)"])),FALSE)
        self.assertEqual(self.verdict(self.fixtures(versions=[])),FALSE)

    def test_unverified_version_suffix_and_bad_evidence_are_errors(self):
        self.assertEqual(self.verdict(self.fixtures(versions=[
            "Server version: Apache/2.4.5-beta (Unix)"])),ERROR)
        fixt=self.fixtures()
        fixt[PROVIDER]["acquisitions"].append(copy.deepcopy(
            fixt[PROVIDER]["acquisitions"][0]))
        self.assertEqual(self.verdict(fixt),ERROR)
        fixt=self.fixtures()
        fixt[PROVIDER]["acquisitions"][1]["items"][0]["fields"]["stdout_line"]="bad"
        self.assertEqual(self.verdict(fixt),ERROR)

    def test_dynamic_query_name_must_match_exact_derived_executable(self):
        f=self.fixtures()
        f[PROVIDER]["acquisitions"][1]["using"]["command"]="/bin/false -V"
        self.assertEqual(self.verdict(f),UNKNOWN)
        f=self.fixtures(paths=["/tmp/httpd;touch /tmp/unsafe -DFOREGROUND"])
        self.assertIn(self.verdict(f),{ERROR,UNKNOWN})
        f=self.fixtures()
        f[PROVIDER]["acquisitions"][0]["items"][0]["fields"]["stdout_line"]=[
            "/usr/sbin/httpd;echo bad -DFOREGROUND"]
        self.assertNotEqual(self.verdict(f),TRUE)

    def test_unknown_graph_shapes_rejected_by_lowerer(self):
        changes=[
            lambda a:a["variables"].update(extra={"expression":{"literal":"a"}}),
            lambda a:a["variables"]["command-gather-apache-version-variable"][
                "expression"]["concat"][0].update(variable="command-gather-apache-version-variable"),
            lambda a:a["tests"]["apache-usertrack-module-enabled-test"][
                "states"][0].update(operation="equals"),
            lambda a:a["tests"]["apache-usertrack-module-enabled-test"][
                "object"]["collect"].update(shell="powershell"),
            lambda a:a["variables"]["apache-path-httpd-or-apache2-variable"][
                "expression"]["regex_capture"].update(pattern=r"(foo)(bar)"),
        ]
        for change in changes:
            doc=copy.deepcopy(self.doc)
            change(doc["assessment"])
            with self.subTest(change=change):
                with self.assertRaises((ValueError,TypeError)):
                    lower_apache_version_graph(doc)

    def test_compiled_graph_tampering_rejected(self):
        for key,value in [("command_suffix"," ; rm -rf /"),
                          ("version_pattern","anything"),
                          ("source_test_id","")]:
            ast=copy.deepcopy(self.ast)
            ast[key]=value
            with self.subTest(field=key):
                with self.assertRaises(ValueError):
                    encode("forged-apache-variable-test",ast)


if __name__=="__main__":
    unittest.main()
