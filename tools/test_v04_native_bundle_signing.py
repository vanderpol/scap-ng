#!/usr/bin/env python3
"""Native .scapng CMS authentication and compiled-graph regression (#232)."""
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_canonical_signed_source_package import certificate, modified
from test_v04_native_bundle_compiler import fixture
from v04_a_authoring_graph_index import canonical_json
from v04_canonical_signed_source_package import CERTIFICATE, SIGNATURE
from v04_native_bundle_compiler import MANIFEST_MEMBER, build_bundle, verify_bundle
from v04_native_bundle_signing import (
    SIGNED_STAGE, sign_compiled_bundle, verify_signed_compiled_bundle,
)


@unittest.skipUnless(shutil.which("openssl"), "OpenSSL CLI required for CMS verification")
class SignedCompiledBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key, cls.certificate = certificate("0.4 compiled fixture signer")
        cls.wrong_key, cls.wrong_certificate = certificate("other publisher")
        cls.unsigned, _ = build_bundle(fixture(), validate_schema=False)
        cls.signed = sign_compiled_bundle(
            cls.unsigned, cls.private_key, cls.certificate,
            validate_schema=False)

    def verify(self, raw, trusted=None):
        return verify_signed_compiled_bundle(
            raw, trusted_certificate_pem=(self.certificate if trusted is None else trusted),
            validate_schema=False)

    def test_signed_compiled_programs_pass_external_trust_and_full_graph(self):
        result = self.verify(self.signed)
        self.assertEqual(result["status"],
                         "VALIDATED_CMS_SIGNED_NATIVE_040_CONTENT_NOT_SCANNER_TESTED")
        self.assertTrue(result["signature_verified"])
        self.assertFalse(result["scanner_evaluated"])
        self.assertEqual((result["documents"], result["programs"], result["tests"]),
                         (3, 1, 1))
        with zipfile.ZipFile(io.BytesIO(self.signed)) as archive:
            manifest = json.loads(archive.read(MANIFEST_MEMBER))
            self.assertEqual(manifest["build_provenance"]["stage"], SIGNED_STAGE)
            self.assertFalse(manifest["build_provenance"]["publisher_signature_verified"])
            self.assertTrue(archive.read(SIGNATURE))
            self.assertEqual(archive.read(CERTIFICATE), self.certificate)
        with self.assertRaisesRegex(ValueError, "supported compiled"):
            verify_bundle(self.signed, validate_schema=False)

    def test_no_trust_and_wrong_trust_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit trusted"):
            self.verify(self.signed, trusted=b"")
        with self.assertRaisesRegex(ValueError, "external trust failed"):
            self.verify(self.signed, trusted=self.wrong_certificate)

    def test_wrong_key_and_unsigned_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            sign_compiled_bundle(self.unsigned, self.wrong_key, self.certificate,
                                 validate_schema=False)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.verify(self.unsigned)
        with self.assertRaisesRegex(ValueError, "supported compiled"):
            sign_compiled_bundle(self.signed, self.private_key, self.certificate,
                                 validate_schema=False)

    def test_manifest_signature_and_signer_certificate_tampering_rejected(self):
        def alter_manifest(members):
            manifest = json.loads(members[MANIFEST_MEMBER])
            manifest["benchmark_version"] = "altered"
            members[MANIFEST_MEMBER] = canonical_json(manifest)
        with self.assertRaisesRegex(ValueError, "CMS validation"):
            self.verify(modified(self.signed, alter_manifest))

        def corrupt_signature(members):
            data = bytearray(members[SIGNATURE])
            data[len(data) // 2] ^= 0x01
            members[SIGNATURE] = bytes(data)
        with self.assertRaisesRegex(ValueError, "CMS validation"):
            self.verify(modified(self.signed, corrupt_signature))

        with self.assertRaisesRegex(ValueError, "CMS validation|advertised signing"):
            self.verify(modified(self.signed, lambda m: m.update({
                CERTIFICATE: self.wrong_certificate,
            })))

    def test_modified_document_program_and_unlisted_members_rejected(self):
        def corrupt_document(members):
            path = next(p for p in members if p.startswith("assessments/"))
            members[path] += b" "
        with self.assertRaisesRegex(ValueError, "compiled document digest mismatch"):
            self.verify(modified(self.signed, corrupt_document))

        def corrupt_program(members):
            path = next(p for p in members if p.startswith("programs/"))
            members[path] += b" "
        with self.assertRaisesRegex(ValueError, "compiled program digest mismatch"):
            self.verify(modified(self.signed, corrupt_program))

        with self.assertRaisesRegex(ValueError, "extra or unlisted"):
            self.verify(modified(self.signed, lambda m: m.update({"surprise": b"extra"})))


if __name__ == "__main__":
    unittest.main()
