#!/usr/bin/env python3
"""Reject unsafe source-graph imports; permit only exact 0.3 expansion."""
import unittest
from copy import deepcopy
from research_04_apache_source_import import (
    MODULE_ID, MODULE_VERSION, sha, source_authoring, lower_source,
    validated_module, extract_refs,
)

def fixture():
    module={"source_module":{
        "id":MODULE_ID, "version":MODULE_VERSION,
        "objects":{"shared-source":{"capability":"unix.file","select":{"path":"/etc/a"}}},
        "variables":{
            "intermediate":{"kind":"local","datatype":"string",
                "expression":{"object":"shared-source"}},
            "output":{"kind":"local","datatype":"string",
                "expression":{"variable":"intermediate"}},
        },
        "exports":{"config":{"type":"variable","name":"output","datatype":"string"}},
    }}
    doc={"assessment":{
        "id":"SV-TEST","mode":"automated",
        "objects":{"shared-source":deepcopy(module["source_module"]["objects"]["shared-source"]),
                   "target":{"capability":"unix.file","select":{
                       "path":{"value":{"variable":"output"}}}}},
        "variables":deepcopy(module["source_module"]["variables"]),
        "tests":{"target-test":{"object":"target"}},
    }}
    return module,doc

class SourceGraphImportTests(unittest.TestCase):
    def test_roundtrip_and_two_explicit_exports(self):
        mod,doc=fixture()
        author, refs=source_authoring(doc,mod)
        self.assertEqual(len(refs),1)
        self.assertEqual(lower_source(author,mod),doc)
        self.assertNotIn("shared-source",author["assessment"]["objects"])
        self.assertNotIn("variables",author["assessment"])
        self.assertEqual(author["assessment"]["imports"]["apache_discovery"]["sha256"],sha(mod))
        self.assertNotIn("imports",lower_source(author,mod)["assessment"])

    def test_module_type_tamper_refused(self):
        mod,doc=fixture()
        mod["source_module"]["exports"]["config"]["datatype"]="boolean"
        with self.assertRaisesRegex(ValueError,"datatype"):
            source_authoring(doc,mod)

    def test_consumer_cannot_access_private_intermediate(self):
        mod,doc=fixture()
        doc["assessment"]["objects"]["target"]["select"]["path"]={"variable":"intermediate"}
        with self.assertRaisesRegex(ValueError,"private"):
            source_authoring(doc,mod)

    def test_mutated_module_content_must_fail(self):
        mod,doc=fixture()
        author,_=source_authoring(doc,mod)
        mod["source_module"]["objects"]["shared-source"]["select"]["path"]="/bad"
        with self.assertRaisesRegex(ValueError,"digest"):
            lower_source(author,mod)

    def test_mutated_module_identity_must_fail(self):
        mod,doc=fixture()
        author,_=source_authoring(doc,mod)
        author["assessment"]["imports"]["apache_discovery"]["version"]=999
        with self.assertRaisesRegex(ValueError,"contract"):
            lower_source(author,mod)

    def test_collision_refused(self):
        mod,doc=fixture()
        author,_=source_authoring(doc,mod)
        author["assessment"]["objects"]["shared-source"]={"capability":"wrong"}
        with self.assertRaisesRegex(ValueError,"collision"):
            lower_source(author,mod)

    def test_source_graph_not_closed_is_refused(self):
        mod,doc=fixture()
        doc["assessment"]["variables"]["intermediate"]["expression"]={"object":"other-source"}
        with self.assertRaisesRegex(ValueError,"differs"):
            source_authoring(doc,mod)

    def test_missing_export_refused(self):
        mod,doc=fixture()
        mod["source_module"]["exports"]["config"]["name"]="unknown"
        with self.assertRaisesRegex(ValueError,"missing"):
            source_authoring(doc,mod)

    def test_import_unused_refused(self):
        mod,doc=fixture()
        doc["assessment"]["objects"]["target"]["select"]["path"]="/literal"
        with self.assertRaisesRegex(ValueError,"Unused"):
            source_authoring(doc,mod)

    def test_for_each_source_reference_detected(self):
        refs=extract_refs({"for_each":{"item":"user","in":"shared-source"}},"objects")
        self.assertEqual(refs,[("shared-source",("for_each","in"))])

    def test_no_scanner_runtime_model_property(self):
        mod,doc=fixture()
        author,_=source_authoring(doc,mod)
        lower=lower_source(author,mod)
        self.assertNotIn("imports",lower["assessment"])
        self.assertEqual(lower["assessment"]["tests"],doc["assessment"]["tests"])

if __name__=="__main__":
    unittest.main()
