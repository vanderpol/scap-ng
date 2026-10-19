#!/usr/bin/env python3
"""Refs #245 complete Apache C authoring/provenance distinction regression."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_provenance_split import (
    present_apache_provenance_split,compile_apache_split,prove_apache_split)
from research_c_apache_hybrid_authoring import present_c_apache_hybrid

SOURCE=(Path(__file__).resolve().parents[1]/
  "research/requirements-first-language/contract-candidate/corpus/"
  "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")

def source():
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]

def split():
    original=source()
    authored,sidecar=present_apache_provenance_split(original)
    return original,authored,sidecar

class ProvenanceBoundApacheTests(unittest.TestCase):
    def test_compiles_exact_full_apache_from_authoring_plus_separate_sidecar(self):
        original,authored,sidecar=split()
        snapshot=deepcopy(original)
        self.assertEqual(len(authored["derived_values"]),19)
        self.assertEqual(len(authored["checks"]),5)
        self.assertEqual(len(authored["observations"]),1)
        self.assertEqual(authored["assessment"]["id"],"SV-214268.automated")
        self.assertEqual(set(authored["derived_values"][0]),{
            "name","description","derive"})
        self.assertFalse(any("source_id" in step or "kind" in step or
            "datatype" in step or "title" in step
            for step in authored["derived_values"]))
        self.assertTrue(all(set(chk)=={"description","from","must"} for chk
                            in authored["checks"].values()))
        self.assertEqual(compile_apache_split(authored,sidecar),original)
        self.assertEqual(original,snapshot)
        proof=prove_apache_split(original,authored,sidecar)
        self.assertEqual(proof["source_variable_count"],19)
        self.assertEqual(proof["source_test_count"],5)
        self.assertEqual(proof["legacy_source_ids_in_authoring"],0)
        self.assertFalse(proof["scanner_runtime_parity_proven"])

    def test_independent_yaml_roundtrip_keeps_source_test_and_value_equality(self):
        native,author,provenance=split()
        loaded_author=yaml.safe_load(yaml.safe_dump(author,sort_keys=False))
        loaded_provenance=yaml.safe_load(yaml.safe_dump(provenance,sort_keys=False))
        self.assertEqual(compile_apache_split(loaded_author,loaded_provenance),
                         native)

    def test_missing_or_crosswired_provenance_fails_closed(self):
        original,author,p=split()
        with self.assertRaisesRegex(ValueError,"separate complete"):
            compile_apache_split(author,{})
        p2=deepcopy(p)
        p2["value_sources"].pop(next(iter(p2["value_sources"])))
        with self.assertRaisesRegex(ValueError,"catalog differs"):
            compile_apache_split(author,p2)
        p2=deepcopy(p)
        names=list(p2["value_sources"])
        p2["value_sources"][names[0]]["source_id"]=p2[
            "value_sources"][names[1]]["source_id"]
        with self.assertRaisesRegex(ValueError,"same source Variable"):
            compile_apache_split(author,p2)
        p2=deepcopy(p)
        aliases=list(p2["check_sources"])
        p2["check_sources"][aliases[0]]=p2["check_sources"][aliases[1]]
        with self.assertRaisesRegex(ValueError,"reuse one"):
            compile_apache_split(author,p2)

    def test_changed_author_values_need_explicit_edit_mode_no_false_source_parity(self):
        original,author,p=split()
        first=next(iter(author["checks"]))
        field=author["checks"][first]["must"]["fields"][0]
        field["matches_regex"]="this is deliberately changed"
        with self.assertRaisesRegex(ValueError,"source equivalence not proven"):
            compile_apache_split(author,p)
        modified=compile_apache_split(author,p,require_original_source=False)
        self.assertNotEqual(modified,original)
        self.assertEqual(modified["tests"][p["check_sources"][first]]["states"][
            0]["value"],"this is deliberately changed")
        with self.assertRaisesRegex(ValueError,"original source proof invalid"):
            prove_apache_split(original,author,p)

    def test_changed_dynamic_acquisition_still_typechecked_in_edit_mode(self):
        original,author,p=split()
        first=next(iter(author["checks"]))
        collection=author["checks"][first]["from"][
            "independent.shellcommand"]["collect"]
        collection["command"]={"use":"does-not-exist"}
        with self.assertRaisesRegex(ValueError,"unresolved"):
            compile_apache_split(author,p,require_original_source=False)

    def test_managed_digest_is_not_a_signature_and_cannot_silently_fix_changes(self):
        original,author,p=split()
        k=next(iter(author["derived_values"]))
        # Value-array mutation must never be accepted by strict source mode
        author["derived_values"][0]["description"]="Changed author description"
        with self.assertRaisesRegex(ValueError,"source equivalence not proven"):
            compile_apache_split(author,p)
        altered=deepcopy(p)
        altered["original_authoring_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"source equivalence not proven"):
            compile_apache_split(author,altered)
        self.assertNotEqual(compile_apache_split(author,p,require_original_source=False),
                            original)

    def test_authoring_counts_measure_editable_vs_managed_fields(self):
        original,authored,sidecar=split()
        full=present_c_apache_hybrid(original)
        full_text=yaml.safe_dump(full,sort_keys=False)
        core=yaml.safe_dump(authored,sort_keys=False)
        managed=yaml.safe_dump(sidecar,sort_keys=False)
        self.assertLess(len(core.splitlines()),len(full_text.splitlines()))
        self.assertLess(len(core.encode("utf-8")),len(full_text.encode("utf-8")))
        self.assertGreater(len(managed),0)
        self.assertEqual(len(sidecar["value_sources"]),19)
        self.assertEqual(len(sidecar["check_sources"]),5)
        self.assertEqual(len(sidecar["observation_sources"]),1)
        self.assertFalse(any(
            "source_object" in ob for ob in authored["observations"].values()))

if __name__=="__main__":
    unittest.main()
