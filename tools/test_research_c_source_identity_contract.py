#!/usr/bin/env python3
"""Refs #245 cross-source C alias/typed A identity and digest conformance."""
from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_source_identity_contract import (
    source_digest,require_author_binding_catalog,require_pinned_authoring)

class CSourceIdentityContractTests(unittest.TestCase):
    def test_source_digest_canonical_json_key_order_without_hidden_defaults(self):
        left={"checks":{"a":{"must":"one_or_more"}}, "values":[1,2]}
        right={"values":[1,2], "checks":{"a":{"must":"one_or_more"}}}
        self.assertEqual(source_digest(left),source_digest(right))
        self.assertNotEqual(source_digest(left),source_digest({
            "values":[2,1],"checks":{"a":{"must":"one_or_more"}}}))
        with self.assertRaisesRegex(ValueError,"cannot digest"):
            source_digest({"nonfinite":float("nan")})

    def test_source_id_catalog_injective_with_long_semantic_aliases(self):
        doc={"apache_version_from_process":True,
             "session_cookie_secure":True}
        src={"apache_version_from_process":"apache-source-var-1",
             "session_cookie_secure":"apache-source-var-2"}
        self.assertEqual(require_author_binding_catalog(
            doc,src,label="derived source"),src)
        with self.assertRaisesRegex(ValueError,"reused"):
            require_author_binding_catalog(doc,{
                "apache_version_from_process":"apache-source-var-1",
                "session_cookie_secure":"apache-source-var-1"},label="derived source")

    def test_missing_binding_and_nonmeaningful_short_alias_rejected(self):
        authored={"windows_dns_answer":True}
        with self.assertRaisesRegex(ValueError,"incomplete"):
            require_author_binding_catalog(
                authored,{},label="OVAL Test")
        with self.assertRaisesRegex(ValueError,"unreviewed C source alias"):
            require_author_binding_catalog(
                {"1234":True},{"1234":"source:test:1"},label="OVAL Test")

    def test_typed_provenance_preserves_kind_and_type_behind_identity(self):
        author={"local_apache_command":True}
        recorded={"local_apache_command":{
            "source_id":"source-command-1","datatype":"string","kind":"local"}}
        self.assertEqual(require_author_binding_catalog(
            author,recorded,label="typed derived value",source_id_field="source_id"),
            {"local_apache_command":"source-command-1"})
        changed=deepcopy(recorded)
        del changed["local_apache_command"]["source_id"]
        with self.assertRaisesRegex(ValueError,"identity missing"):
            require_author_binding_catalog(
                author,changed,label="typed derived value",source_id_field="source_id")

    def test_source_proof_does_not_accept_modified_author_or_fake_hex(self):
        author={"checks":{"selinux_status":{"must":"present"}}}
        self.assertTrue(require_pinned_authoring(author,source_digest(author)))
        changed=deepcopy(author);changed["checks"]["selinux_status"]["must"]="missing"
        with self.assertRaisesRegex(ValueError,"source proof requires"):
            require_pinned_authoring(changed,source_digest(author))
        with self.assertRaises(ValueError):
            require_pinned_authoring(author,"abc")

    def test_source_digest_is_not_authoritative_signature(self):
        # A checksum detects accidental drift from a supplied baseline; it
        # does not prove who approved the baseline or identify the publisher.
        self.assertEqual(len(source_digest({"source":"original OVAL"})),64)
        self.assertNotEqual(source_digest({"source":"original OVAL"}),
                            source_digest({"source":"edited OVAL"}))

if __name__=="__main__":
    unittest.main()
