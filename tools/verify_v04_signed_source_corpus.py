#!/usr/bin/env python3
"""CI source-only CMS proof on current real 0.4 Linux and Windows STIG packages.

Ephemeral test signer only: no keys or signed packages are published.
Refs #232 #239. Does not prove scanner execution or publisher identity.
"""
import argparse
import datetime as dt
from hashlib import sha256
import io
import json
from pathlib import Path
import shutil
import zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from v04_canonical_signed_source_package import (
    MANIFEST_MEMBER, sign_source_package, verify_signed_source_package,
)
from v04_canonical_unsigned_package import verify_package

PLATFORMS = ("rhel_9", "ms_windows_11")


def temporary_signer():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(
        NameOID.COMMON_NAME, "SCAP-NG 0.4 CI source-only ephemeral signer")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(minutes=5))
            .not_valid_after(now + dt.timedelta(hours=2))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.KeyUsage(
                digital_signature=True, content_commitment=True,
                key_encipherment=False, data_encipherment=False,
                key_agreement=False, key_cert_sign=True, crl_sign=True,
                encipher_only=False, decipher_only=False), critical=True)
            .sign(key, hashes.SHA256()))
    return (
        key.private_bytes(serialization.Encoding.PEM,
                          serialization.PrivateFormat.PKCS8,
                          serialization.NoEncryption()),
        cert.public_bytes(serialization.Encoding.PEM),
    )


def modified_manifest(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        members = {name: zf.read(name) for name in zf.namelist()}
    members[MANIFEST_MEMBER] += b" "
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as zf:
        for name, content in sorted(members.items()):
            zf.writestr(name, content)
    return out.getvalue()


def run(directory):
    if not shutil.which("openssl"):
        raise ValueError("OpenSSL independent CMS verification is mandatory")
    files = sorted(directory.glob("*.source-preview.zip"))
    if len(files) != 6:
        raise ValueError(f"expected six canonical packages, got {len(files)}")
    by_name = {p.name.removesuffix(".source-preview.zip"): p for p in files}
    if not set(PLATFORMS).issubset(by_name):
        raise ValueError("representative Windows/Linux packages are missing")
    key, cert = temporary_signer()
    _, wrong_cert = temporary_signer()
    cases = []
    for platform in PLATFORMS:
        original = by_name[platform].read_bytes()
        baseline = verify_package(original, validate_schema=True)
        signed = sign_source_package(original, key, cert, validate_schema=True)
        verified = verify_signed_source_package(
            signed, trusted_certificate_pem=cert, validate_schema=True)
        if any(verified[k] != baseline[k] for k in (
                "documents", "rule_choice_links", "source_graph_sha256")):
            raise AssertionError("source graph changed when signed")
        if not verified["signature_verified"] or verified["scanner_evaluated"]:
            raise AssertionError("incorrect signature/executable status")
        try:
            verify_signed_source_package(
                signed, trusted_certificate_pem=wrong_cert,
                validate_schema=False)
        except ValueError as error:
            if "external trust failed" not in str(error):
                raise
        else:
            raise AssertionError("independently untrusted signer accepted")
        try:
            verify_signed_source_package(
                modified_manifest(signed), trusted_certificate_pem=cert,
                validate_schema=False)
        except ValueError as error:
            if "noncanonical signed manifest" not in str(error):
                raise
        else:
            raise AssertionError("modified signed manifest accepted")
        cases.append({
            "platform": platform,
            "unsigned_sha256": sha256(original).hexdigest(),
            "source_graph_sha256": verified["source_graph_sha256"],
            "documents": verified["documents"],
            "rule_choice_links": verified["rule_choice_links"],
            "full_native_schema_before_and_after_signing": "PASS",
            "cms_explicit_ephemeral_trust": "PASS",
            "wrong_external_trust": "REJECTED",
            "changed_signed_manifest": "REJECTED",
        })
    return {
        "status": "REAL_040_SOURCE_ONLY_CMS_TEST_TRUST_PASS_NOT_EXECUTABLE",
        "original_six_packages": len(files),
        "real_signed_source_packages_verified": len(cases),
        "cases": cases,
        "ephemeral_test_certificate_sha256": sha256(
            x509.load_pem_x509_certificate(cert).public_bytes(
                serialization.Encoding.DER)).hexdigest(),
        "publisher_trust_proven": False,
        "private_keys_or_signed_test_packages_published": False,
        "executable_compiler_complete": False,
        "scanner_semantics_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-package-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report = run(args.source_package_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k:v for k,v in report.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
