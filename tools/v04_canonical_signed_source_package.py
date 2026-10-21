#!/usr/bin/env python3
"""Detached-CMS signing boundary for validated 0.4.0 SOURCE-ONLY packages.

This module deliberately does not compile executable .scapng instructions.
No internal signer certificate is trusted by default: verification requires an
explicit caller-supplied trusted certificate. Ref #232.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7

from v04_a_authoring_graph_index import canonical_json
from v04_canonical_unsigned_package import (
    FIXED_TIME, MANIFEST_MEMBER, PROVENANCE_KEYS, SOURCE_FORMAT, STAGE,
    _manifest_schema, _strict_json, _write_member, verify_package,
)

SIGNED_STAGE = "validated-signed-source-package-not-executable/0.1"
SIGNATURE = "META-INF/signature.p7s"
CERTIFICATE = "META-INF/signer.pem"
EXTERNAL_TRUST = "explicit-trusted-certificate-required"


def _read_members(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate package members")
        if zf.testzip() is not None:
            raise ValueError("damaged package member")
        return {name: zf.read(name) for name in names}


def _archive(members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as zf:
        for name, data in sorted(members.items()):
            _write_member(zf, name, data)
    return stream.getvalue()


def _validate_signing_certificate(key, cert):
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    public = cert.public_key()
    if not isinstance(public, (rsa.RSAPublicKey, ec.EllipticCurvePublicKey)):
        raise ValueError("unsupported signing certificate key")
    if (public.public_bytes(serialization.Encoding.DER,
                            serialization.PublicFormat.SubjectPublicKeyInfo) !=
            key.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo)):
        raise ValueError("signing key does not match certificate")
    try:
        usage = cert.extensions.get_extension_for_class(x509.KeyUsage).value
    except x509.ExtensionNotFound:
        usage = None
    if usage is not None and not usage.digital_signature:
        raise ValueError("certificate does not permit digital signatures")


def sign_source_package(unsigned, private_key_pem, signer_certificate_pem, *, validate_schema=True):
    """Convert independently validated unsigned SOURCE ZIP to signed SOURCE ZIP.

    Signing DOES NOT assert a trusted publisher until an external caller checks
    the detached CMS signature against an independently trusted certificate.
    """
    verify_package(unsigned, validate_schema=validate_schema)
    members = _read_members(unsigned)
    manifest = _strict_json(members[MANIFEST_MEMBER])
    key = serialization.load_pem_private_key(private_key_pem, password=None)
    cert = x509.load_pem_x509_certificate(signer_certificate_pem)
    _validate_signing_certificate(key, cert)
    manifest["build_provenance"]["stage"] = SIGNED_STAGE
    manifest["signature"] = {
        "format": "cms-detached-der",
        "path": SIGNATURE,
        "certificate_path": CERTIFICATE,
        "trust": EXTERNAL_TRUST,
    }
    _manifest_schema().validate(manifest)
    signed_manifest = canonical_json(manifest)
    detached = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(signed_manifest)
        .add_signer(cert, key, hashes.SHA256())
        .sign(serialization.Encoding.DER, [
            pkcs7.PKCS7Options.DetachedSignature,
            pkcs7.PKCS7Options.Binary,
        ])
    )
    members[MANIFEST_MEMBER] = signed_manifest
    members[SIGNATURE] = detached
    members[CERTIFICATE] = cert.public_bytes(serialization.Encoding.PEM)
    return _archive(members)


def _check_cms(manifest_bytes, detached, expected_cert, trusted_cert):
    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError("OpenSSL required for independent detached CMS verification")
    with tempfile.TemporaryDirectory(prefix="scapng-v04-cms-") as td:
        base = Path(td)
        paths = {
            "manifest": base / "manifest.json",
            "signature": base / "signature.der",
            "signer": base / "signer.pem",
            "trusted": base / "trusted.pem",
            "verified_signers": base / "verified-signers.pem",
        }
        for key, data in (("manifest", manifest_bytes), ("signature", detached),
                          ("signer", expected_cert), ("trusted", trusted_cert)):
            paths[key].write_bytes(data)
        cmd = [
            openssl, "cms", "-verify", "-binary", "-inform", "DER",
            "-in", str(paths["signature"]),
            "-content", str(paths["manifest"]),
            "-CAfile", str(paths["trusted"]), "-purpose", "any",
            "-signer", str(paths["verified_signers"]),
            "-out", os.devnull,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode:
            raise ValueError("detached CMS validation or external trust failed: " +
                             (result.stderr.strip() or result.stdout.strip())[:400])
        # A valid chain alone does not prove that the manifest's advertised
        # signer certificate was the one that signed the CMS.
        actual = x509.load_pem_x509_certificate(paths["verified_signers"].read_bytes())
        advertised = x509.load_pem_x509_certificate(expected_cert)
        if actual.fingerprint(hashes.SHA256()) != advertised.fingerprint(hashes.SHA256()):
            raise ValueError("advertised signing certificate differs from CMS signer")


def verify_signed_source_package(raw, *, trusted_certificate_pem, validate_schema=True):
    """Verify CMS *and* full native source closure, never scanner execution."""
    if not trusted_certificate_pem:
        raise ValueError("explicit trusted certificate is mandatory")
    members = _read_members(raw)
    if not all(name in members for name in (MANIFEST_MEMBER, SIGNATURE, CERTIFICATE)):
        raise ValueError("incomplete source package signature members")
    manifest_raw = members[MANIFEST_MEMBER]
    manifest = _strict_json(manifest_raw)
    if manifest_raw != canonical_json(manifest):
        raise ValueError("noncanonical signed manifest")
    _manifest_schema().validate(manifest)
    if manifest["signature"] != {
        "format": "cms-detached-der", "path": SIGNATURE,
        "certificate_path": CERTIFICATE, "trust": EXTERNAL_TRUST,
    }:
        raise ValueError("unsupported or untrusted signing contract")
    if manifest["format_version"] != "0.4.0":
        raise ValueError("signed source package must declare format_version 0.4.0")
    provenance = manifest["build_provenance"]
    if (not isinstance(provenance, dict) or set(provenance) != PROVENANCE_KEYS
            or provenance["stage"] != SIGNED_STAGE
            or provenance["source_format"] != SOURCE_FORMAT
            or provenance["executable_compiler_complete"] is not False
            or provenance["scanner_evaluation_verified"] is not False
            or provenance["publisher_signature_verified"] is not False):
        raise ValueError("signed package makes unsupported runtime/trust claims")
    _check_cms(manifest_raw, members[SIGNATURE], members[CERTIFICATE],
               trusted_certificate_pem)
    unsigned = deepcopy(manifest)
    unsigned["build_provenance"]["stage"] = STAGE
    unsigned["signature"] = {
        "format": None, "path": None,
        "certificate_path": None, "trust": None,
    }
    members.pop(SIGNATURE)
    members.pop(CERTIFICATE)
    members[MANIFEST_MEMBER] = canonical_json(unsigned)
    decoded = verify_package(_archive(members), validate_schema=validate_schema)
    return {
        **decoded,
        "status": "VALIDATED_CMS_SIGNED_SOURCE_PACKAGE_NOT_EXECUTABLE",
        "signature_verified": True,
        "trust_source": "explicit-caller-provided-certificate",
        "certificate_sha256": sha256(
            x509.load_pem_x509_certificate(trusted_certificate_pem).public_bytes(
                serialization.Encoding.DER)).hexdigest(),
        "scanner_evaluated": False,
    }
