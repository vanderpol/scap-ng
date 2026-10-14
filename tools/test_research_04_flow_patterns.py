#!/usr/bin/env python3
"""Fail-closed tests for apparent Apache shared-Variable producer graphs."""
import unittest
from copy import deepcopy
from research_04_flow_patterns import resolved_graph_fingerprint, graph_markdown

def assessment():
    return {
        "objects": {
            "config-path-object": {"capability":"unix.file",
                "select":{"path":{"value":"/etc/httpd/httpd.conf",
                                   "datatype":"string","operation":"equals"}}},
        },
        "variables": {
            "config-path-variable": {"kind":"local","datatype":"string",
                "expression":{"values":{"object":"config-path-object","field":"path"}},
                "title":"Read config path"},
            "config-directory-variable": {"kind":"local","datatype":"string",
                "expression":{"concat":[
                    {"variable":"config-path-variable"},
                    {"literal":".d"}]}},
        },
    }

class DataflowReuseProofTest(unittest.TestCase):
    def test_identical_graph_matches(self):
        a=assessment()
        b=deepcopy(a)
        self.assertEqual(resolved_graph_fingerprint("config-directory-variable",a),
                         resolved_graph_fingerprint("config-directory-variable",b))
        self.assertFalse(resolved_graph_fingerprint("config-directory-variable",a)[1])

    def test_same_variable_expression_different_collector_does_not_match(self):
        a=assessment()
        b=deepcopy(a)
        b["objects"]["config-path-object"]["select"]["path"]["value"]="/etc/other.conf"
        self.assertNotEqual(resolved_graph_fingerprint("config-directory-variable",a)[0],
                            resolved_graph_fingerprint("config-directory-variable",b)[0])

    def test_same_top_variable_different_inner_variable_does_not_match(self):
        a=assessment()
        b=deepcopy(a)
        b["variables"]["config-path-variable"]["expression"]={"literal":"other"}
        self.assertNotEqual(resolved_graph_fingerprint("config-directory-variable",a)[0],
                            resolved_graph_fingerprint("config-directory-variable",b)[0])

    def test_missing_collector_cannot_claim_closed_graph(self):
        a=assessment()
        del a["objects"]["config-path-object"]
        _, missing=resolved_graph_fingerprint("config-directory-variable",a)
        self.assertIn("object-missing:config-path-object",missing)

    def test_for_each_source_collector_is_included(self):
        a=assessment()
        a["objects"]["target-object"]={
            "capability":"unix.file",
            "for_each":{"item":"config","in":"config-path-object"},
            "select":{"path":{"from":"config.path"}}}
        a["variables"]["config-path-variable"]["expression"]={
            "values":{"object":"target-object","field":"path"}}
        base=resolved_graph_fingerprint("config-directory-variable",a)
        b=deepcopy(a)
        b["objects"]["config-path-object"]["select"]["path"]["value"]="/etc/other.conf"
        different=resolved_graph_fingerprint("config-directory-variable",b)
        self.assertNotEqual(base[0],different[0])
        self.assertFalse(base[1])

    def test_presentation_is_explicitly_non_normative(self):
        doc={"assessment":{"id":"sample","mode":"automated",
             **assessment()}}
        md=graph_markdown(doc,"SV-000001","rhel_9")
        self.assertIn("original standalone OVAL",md)
        self.assertIn("config-directory-variable",md)
        self.assertIn("NOT authoring syntax",md)

if __name__=="__main__":
    unittest.main()
