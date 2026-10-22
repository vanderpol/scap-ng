#!/usr/bin/env python3
"""Detached-CMS publisher-signature boundary for compiled 0.4.0 `.scapng`.

Signing changes neither the compiled Test instructions nor their source graph.
Verification requires a caller-provided trust anchor, checks the detached CMS
signature, then re-runs the entire *unsigned* native compiler verifier.
Neither operation proves live scanner conformance or Board acceptance.

The generated six-STIG preview bundles are deliberately unsigned until a real
publisher chooses a signing identity and trust policy. Refs #232 #229.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7

from v04_a_authoring_graph_index import canonical_json
from v04_canonical_signed_source_package import (
    CERTIFICATE, EXTERNAL_TRUST, SIGNATURE, _archive, _check_cms,
    _read_members, _validate_signing_certificate,
)
from v04_canonical_unsigned_package import _manifest_schema, _strict_json
from v04_native_bundle_compiler import (
    FORMAT_VERSION, MANIFEST_MEMBER, STAGE, verify_bundle,
)


SIGNED_STAGE = "compiled-native-0.4.0-cms-signed-not-scanner-validated/0.1"
SIGNATURE_DECLARATION = {
    "format": "cms-detached-der",
    "path": SIGNATURE,
    "certificate_path": CERTIFICATE,
    "trust": EXTERNAL_TRUST,
}
UNSIGNED_DECLARATION = {
    "format": None, "path": None,
    "certificate_path": None, "trust": None,
}


def sign_compiled_bundle(unsigned, private_key_pem, signer_certificate_pem,
                         *, validate_schema=True):
    """Sign a fully verified compiled bundle; do not infer publisher trust."""
    verify_bundle(unsigned, validate_schema=validate_schema)
    members = _read_members(unsigned)
    manifest = _strict_json(members[MANIFEST_MEMBER])
    key = serialization.load_pem_private_key(private_key_pem, password=None)
    certificate = x509.load_pem_x509_certificate(signer_certificate_pem)
    _validate_signing_certificate(key, certificate)
    manifest["build_provenance"]["stage"] = SIGNED_STAGE
    manifest["signature"] = deepcopy(SIGNATURE_DECLARATION)
    _manifest_schema().validate(manifest)
    signed_manifest = canonical_json(manifest)
    signature = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(signed_manifest)
        .add_signer(certificate, key, hashes.SHA256())
        .sign(serialization.Encoding.DER, [
            pkcs7.PKCS7Options.DetachedSignature,
            pkcs7.PKCS7Options.Binary,
        ])
    )
    members[MANIFEST_MEMBER] = signed_manifest
    members[SIGNATURE] = signature
    members[CERTIFICATE] = certificate.public_bytes(serialization.Encoding.PEM)
    return _archive(members)


def verify_signed_compiled_bundle(raw, *, trusted_certificate_pem,
                                   validate_schema=True):
    """Verify explicit external CMS trust and the full native compiled graph."""
    if not trusted_certificate_pem:
        raise ValueError("explicit trusted certificate is mandatory")
    members = _read_members(raw)
    if not all(x in members for x in (MANIFEST_MEMBER, SIGNATURE, CERTIFICATE)):
        raise ValueError("incomplete compiled package signature members")
    manifest_bytes = members[MANIFEST_MEMBER]
    manifest = _strict_json(manifest_bytes)
    if manifest_bytes != canonical_json(manifest):
        raise ValueError("noncanonical signed manifest")
    _manifest_schema().validate(manifest)
    if (manifest["format_version"] != FORMAT_VERSION or
            manifest["signature"] != SIGNATURE_DECLARATION):
        raise ValueError("unsupported compiled signature contract")
    provenance = manifest.get("build_provenance")
    if (not isinstance(provenance, dict) or
            provenance.get("stage") != SIGNED_STAGE or
            provenance.get("scanner_evaluation_verified") is not False or
            provenance.get("publisher_signature_verified") is not False):
        raise ValueError("signed package makes unsupported runtime/trust claims")
    _check_cms(manifest_bytes, members[SIGNATURE], members[CERTIFICATE],
               trusted_certificate_pem)

    signer_certificate_data = members[CERTIFICATE]
    unsigned_manifest = deepcopy(manifest)
    unsigned_manifest["build_provenance"]["stage"] = STAGE
    unsigned_manifest["signature"] = deepcopy(UNSIGNED_DECLARATION)
    members.pop(SIGNATURE)
    members.pop(CERTIFICATE)
    members[MANIFEST_MEMBER] = canonical_json(unsigned_manifest)
    decoded = verify_bundle(_archive(members), validate_schema=validate_schema)
    signer = x509.load_pem_x509_certificate(signer_certificate_data)
    return {
        **decoded,
        "status": "VALIDATED_CMS_SIGNED_NATIVE_040_CONTENT_NOT_SCANNER_TESTED",
        "signature_verified": True,
        "trust_source": "explicit-caller-provided-certificate",
        "signer_certificate_sha256": sha256(
            signer.public_bytes(serialization.Encoding.DER)).hexdigest(),
        "scanner_evaluated": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="action", required=True)
    sign = subcommands.add_parser("sign", help="sign a verified compiled .scapng")
    sign.add_argument("--input", type=Path, required=True)
    sign.add_argument("--private-key", type=Path, required=True)
    sign.add_argument("--signer-certificate", type=Path, required=True)
    sign.add_argument("--output", type=Path, required=True)
    verify = subcommands.add_parser("verify", help="verify CMS and compiled graph")
    verify.add_argument("--input", type=Path, required=True)
    verify.add_argument("--trusted-certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "sign":
        if args.input.resolve() == args.output.resolve():
            parser.error("signing output must not overwrite the unsigned input")
        signed = sign_compiled_bundle(args.input.read_bytes(),
                                      args.private_key.read_bytes(),
                                      args.signer_certificate.read_bytes())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(signed)
        print(f"Wrote CMS-signed compiled package to {args.output}; "
              "not scanner validated or publisher-trusted until independently verified")
    else:
        report = verify_signed_compiled_bundle(
            args.input.read_bytes(),
            trusted_certificate_pem=args.trusted_certificate.read_bytes())
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
