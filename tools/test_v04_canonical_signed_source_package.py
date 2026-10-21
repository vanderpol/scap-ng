#!/usr/bin/env python3
"""0.4.0 source-only CMS positive and negative trust boundary tests (#232)."""
from copy import deepcopy
import datetime as dt
from hashlib import sha256
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
import zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_canonical_source_ir import sample
from v04_canonical_unsigned_package import build_package, MANIFEST_MEMBER
from v04_canonical_signed_source_package import (
    SIGNATURE, CERTIFICATE, EXTERNAL_TRUST, SIGNED_STAGE,
    sign_source_package, verify_signed_source_package,
)


def certificate(common_name):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(days=1))
            .not_valid_after(now + dt.timedelta(days=2))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.KeyUsage(
                digital_signature=True, content_commitment=True,
                key_encipherment=False, data_encipherment=False,
                key_agreement=False, key_cert_sign=True, crl_sign=True,
                encipher_only=False, decipher_only=False), critical=True)
            .sign(key, hashes.SHA256()))
    pemkey = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption())
    return pemkey, cert.public_bytes(serialization.Encoding.PEM)


def modified(raw, edits):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        members = {name: zf.read(name) for name in zf.namelist()}
    edits(members)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as zf:
        for name, value in sorted(members.items()):
            zf.writestr(name, value)
    return out.getvalue()


@unittest.skipUnless(shutil.which("openssl"), "OpenSSL CLI required for real CMS validation")
class SignedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key, cls.cert = certificate("0.4 signed source fixture")
        cls.other_key, cls.other_cert = certificate("not the trusted signer")
        docs = sample()
        docs["authoring/demo/benchmark.demo.json"]["benchmark"]["rules"] = ["r1"]
        docs["authoring/demo/benchmark.demo.json"]["benchmark"]["version"] = {"value": "1"}
        cls.unsigned, _ = build_package(docs, validate_schema=False)
        cls.signed = sign_source_package(
            cls.unsigned, cls.key, cls.cert, validate_schema=False)

    def test_explicit_external_trust_passes_full_unsigned_graph_verifier(self):
        status = verify_signed_source_package(
            self.signed, trusted_certificate_pem=self.cert,
            validate_schema=False)
        self.assertEqual(status["status"],
                         "VALIDATED_CMS_SIGNED_SOURCE_PACKAGE_NOT_EXECUTABLE")
        self.assertTrue(status["signature_verified"])
        self.assertFalse(status["scanner_evaluated"])
        self.assertEqual(status["documents"], 3)
        self.assertEqual(status["rule_choice_links"], 1)
        expected = sha256(x509.load_pem_x509_certificate(
            self.cert).public_bytes(serialization.Encoding.DER)).hexdigest()
        self.assertEqual(status["certificate_sha256"], expected)
        with zipfile.ZipFile(io.BytesIO(self.signed)) as zf:
            manifest = json.loads(zf.read(MANIFEST_MEMBER))
            self.assertEqual(manifest["build_provenance"]["stage"], SIGNED_STAGE)
            self.assertEqual(manifest["signature"]["trust"], EXTERNAL_TRUST)
            self.assertFalse(manifest["build_provenance"]["executable_compiler_complete"])
            self.assertFalse(manifest["build_provenance"]["publisher_signature_verified"])

    def test_no_trust_or_wrong_trust_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit trusted"):
            verify_signed_source_package(self.signed, trusted_certificate_pem=b"",
                                         validate_schema=False)
        with self.assertRaisesRegex(ValueError, "external trust failed"):
            verify_signed_source_package(self.signed,
                                         trusted_certificate_pem=self.other_cert,
                                         validate_schema=False)

    def test_wrong_signing_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            sign_source_package(self.unsigned, self.other_key, self.cert,
                                validate_schema=False)

    def test_unsigned_not_accepted_as_signed(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            verify_signed_source_package(self.unsigned,
                                         trusted_certificate_pem=self.cert,
                                         validate_schema=False)

    def test_manifest_and_signature_tamper_rejected(self):
        def damage_manifest(members):
            manifest = json.loads(members[MANIFEST_MEMBER])
            manifest["benchmark_version"] = "tampered"
            members[MANIFEST_MEMBER] = json.dumps(
                manifest,sort_keys=True,separators=(",",":")).encode()
        bad = modified(self.signed, damage_manifest)
        with self.assertRaisesRegex(ValueError, "CMS validation"):
            verify_signed_source_package(bad, trusted_certificate_pem=self.cert,
                                         validate_schema=False)
        def damage_signature(members):
            payload = bytearray(members[SIGNATURE])
            payload[len(payload)//2] ^= 0x10
            members[SIGNATURE] = bytes(payload)
        bad = modified(self.signed, damage_signature)
        with self.assertRaisesRegex(ValueError, "CMS validation"):
            verify_signed_source_package(bad, trusted_certificate_pem=self.cert,
                                         validate_schema=False)

    def test_source_digest_and_extra_member_rejected_after_valid_signature(self):
        def damage_document(members):
            target = next(x for x in members if x.startswith("documents/assessment/"))
            members[target] += b" "
        bad = modified(self.signed, damage_document)
        with self.assertRaisesRegex(ValueError, "member digest"):
            verify_signed_source_package(bad, trusted_certificate_pem=self.cert,
                                         validate_schema=False)
        bad = modified(self.signed, lambda members:members.update({"surprise":b"unexpected"}))
        with self.assertRaisesRegex(ValueError, "extra unlisted"):
            verify_signed_source_package(bad, trusted_certificate_pem=self.cert,
                                         validate_schema=False)


if __name__ == "__main__":
    unittest.main()
