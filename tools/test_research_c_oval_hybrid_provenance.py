#!/usr/bin/env python3
"""Refs #245 OVAL Set/Filter source-binder tests, not original scanner oracle."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_hybrid_provenance import (
    present_oval_set_provenance,compile_oval_set_provenance,
    prove_oval_set_provenance)
from test_research_c_hybrid_must_overlay import source

class OVALTypedSetSourceProvenanceTests(unittest.TestCase):
    def test_original_set_filter_constant_rehydrates_with_no_authored_source_ids(self):
        native=source();old=deepcopy(native)
        author,sidecar=present_oval_set_provenance(native)
        self.assertEqual(old,native)
        self.assertEqual(len(author["observations"]),2)
        self.assertEqual(len(author["expected_values"]),1)
        self.assertEqual(len(author["checks"]),2)
        self.assertEqual(len(sidecar["object_source_ids"]),2)
        self.assertEqual(len(sidecar["test_source_ids"]),2)
        self.assertEqual(len(sidecar["constant_sources"]),1)
        self.assertEqual(set(author["checks"]["complement"]),{
            "description","observation","capability","must"})
        self.assertEqual(set(author["expected_values"].values().__iter__().__next__()),{
            "description","field","equals","value_match"})
        self.assertTrue(all(not x.startswith("test-") for x in author["checks"]))
        self.assertEqual(compile_oval_set_provenance(author,sidecar),native)
        proof=prove_oval_set_provenance(native,author,sidecar)
        self.assertEqual(proof["original_Test_count"],2)
        self.assertEqual(proof["original_Set_count"],1)
        self.assertEqual(proof["original_Variable_count"],1)
        self.assertEqual(proof["legacy_source_object_ids_in_authoring"],0)
        self.assertFalse(proof["original_scanner_parity_proven"])

    def test_yaml_roundtrip_is_independent_of_original_source(self):
        native=source()
        author,provenance=present_oval_set_provenance(native)
        serialized_author=yaml.safe_load(yaml.safe_dump(author))
        serialized_prov=yaml.safe_load(yaml.safe_dump(provenance))
        self.assertEqual(compile_oval_set_provenance(
            serialized_author,serialized_prov),native)

    def test_source_set_and_filter_semantics_cannot_be_silently_mutated(self):
        native=source()
        author,provenance=present_oval_set_provenance(native)
        key=next(name for name,obj in author["observations"].items()
                 if "set" in obj)
        author["observations"][key]["set"]["filters"][0]["action"]="include"
        self.assertNotEqual(compile_oval_set_provenance(author,provenance),native)
        with self.assertRaisesRegex(ValueError,"authoring changed"):
            prove_oval_set_provenance(native,author,provenance)

    def test_missing_source_binding_rejected_as_missing_not_guessed(self):
        native=source();author,provenance=present_oval_set_provenance(native)
        broken=deepcopy(provenance)
        broken["object_source_ids"].pop(next(iter(broken["object_source_ids"])))
        with self.assertRaisesRegex(ValueError,"bindings missing"):
            compile_oval_set_provenance(author,broken)
        broken=deepcopy(provenance)
        values=list(broken["object_source_ids"])
        broken["object_source_ids"][values[1]]=broken["object_source_ids"][values[0]]
        with self.assertRaisesRegex(ValueError,"bindings missing"):
            compile_oval_set_provenance(author,broken)

    def test_unsupported_original_value_match_not_repaired(self):
        native=source()
        author,provenance=present_oval_set_provenance(native)
        k=next(iter(author["expected_values"]))
        author["expected_values"][k]["value_match"]="some"
        with self.assertRaises(ValueError):
            compile_oval_set_provenance(author,provenance)

    def test_author_modified_test_requirement_never_proves_source_equivalence(self):
        native=source()
        author,provenance=present_oval_set_provenance(native)
        author["checks"]["complement"]["must"]["items_exist"]="one_or_more"
        changed=compile_oval_set_provenance(author,provenance)
        self.assertNotEqual(changed,native)
        with self.assertRaisesRegex(ValueError,"authoring changed"):
            prove_oval_set_provenance(native,author,provenance)

    def test_remove_source_constant_sidecar_is_rejected_by_original_compiler(self):
        native=source();author,provenance=present_oval_set_provenance(native)
        provenance["constant_sources"]={}
        with self.assertRaises(ValueError):
            compile_oval_set_provenance(author,provenance)

if __name__=="__main__":
    unittest.main()
