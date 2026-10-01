#!/usr/bin/env python3
"""Compile current SCAP-NG YAML authoring trees into deterministic .scapng bundles.

This experimental compiler consumes freshly generated current-design source.
It resolves Rule Assessment paths to logical Assessment IDs, emits a canonical
manifest, and can optionally sign the exact manifest bytes with a generated
self-signed X.509 test certificate using detached CMS/PKCS#7.

A self-signed certificate is for experimentation only and establishes no
publisher trust.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "scapng"


def deterministic_zip_add(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data)


def generate_test_certificate():
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "SCAP-NG Experimental Test Signer")]
    )
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(days=7))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    return key, cert


def sign_manifest(manifest_bytes: bytes):
    key, cert = generate_test_certificate()
    signature = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(manifest_bytes)
        .add_signer(cert, key, hashes.SHA256())
        .sign(
            serialization.Encoding.DER,
            [
                pkcs7.PKCS7Options.DetachedSignature,
                pkcs7.PKCS7Options.Binary,
            ],
        )
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    return signature, cert_pem


def verify_cms_signature(manifest_bytes: bytes, signature: bytes, cert_pem: bytes) -> None:
    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError("openssl is required for CMS verification in this experiment")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        manifest = root / "manifest.json"
        sig = root / "signature.p7s"
        cert = root / "signer.pem"
        manifest.write_bytes(manifest_bytes)
        sig.write_bytes(signature)
        cert.write_bytes(cert_pem)
        command = [
            openssl,
            "cms",
            "-verify",
            "-binary",
            "-inform",
            "DER",
            "-in",
            str(sig),
            "-content",
            str(manifest),
            "-CAfile",
            str(cert),
            "-purpose",
            "any",
            "-out",
            os.devnull,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(
                "CMS verification failed: "
                + (result.stderr.strip() or result.stdout.strip())
            )


def _lexical_abs(path: Path) -> Path:
    return Path(os.path.abspath(os.path.normpath(str(path))))


def _relative_member_path(path: Path, root: Path) -> str:
    rel = os.path.relpath(str(_lexical_abs(path)), str(_lexical_abs(root)))
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        raise ValueError(f"{path}: path escapes corpus root {root}")
    return Path(rel).as_posix()


def resolve_assessment(source_root: Path, rule_path: Path, ref: str) -> tuple[Path, dict]:
    target = _lexical_abs(rule_path.parent / ref)
    source_root = _lexical_abs(source_root)
    try:
        _relative_member_path(target, source_root)
    except ValueError as exc:
        raise ValueError(f"{rule_path}: Assessment reference escapes corpus root: {ref}") from exc
    if not target.is_file():
        raise ValueError(f"{rule_path}: unresolved Assessment reference: {ref}")
    doc = load_yaml(target)
    assessment = doc.get("assessment")
    if not isinstance(assessment, dict) or not assessment.get("id"):
        raise ValueError(f"{target}: missing Assessment id")
    return target, doc


def compile_benchmark(source_root: Path, benchmark_dir: Path):
    benchmark_path = benchmark_dir / "benchmark.yaml"
    benchmark_doc = load_yaml(benchmark_path)
    benchmark = benchmark_doc.get("benchmark")
    if not isinstance(benchmark, dict) or not benchmark.get("id"):
        raise ValueError(f"{benchmark_path}: missing Benchmark id")

    members: dict[str, bytes] = {}
    object_index: dict[str, dict] = {}
    assessment_docs: dict[str, tuple[Path, dict]] = {}

    def add_object(object_id: str, kind: str, member: str, obj: dict, source_path: Path):
        if object_id in object_index:
            prior = object_index[object_id]["source"]
            raise ValueError(
                f"duplicate logical object id {object_id}: {prior} vs {source_path}"
            )
        data = canonical_json(obj)
        members[member] = data
        object_index[object_id] = {
            "type": kind,
            "path": member,
            "source": _relative_member_path(source_path, source_root),
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        }

    compiled_benchmark = json.loads(json.dumps(benchmark_doc))
    applicability_path = benchmark_dir / "applicability.yaml"
    if applicability_path.exists():
        applicability_doc = load_yaml(applicability_path)
        app_root = applicability_doc.get("applicability") or {}
        conditions = []
        for row in app_root.get("conditions", []) or []:
            if not isinstance(row, dict) or not isinstance(row.get("assessment"), str):
                conditions.append(row)
                continue
            target, assessment_doc = resolve_assessment(
                source_root, applicability_path, row["assessment"]
            )
            aid = assessment_doc["assessment"]["id"]
            assessment_docs[aid] = (target, assessment_doc)
            updated = json.loads(json.dumps(row))
            updated["assessment"] = aid
            conditions.append(updated)
        compiled_applicability = {
            "applicability": {
                **{k: v for k, v in app_root.items() if k != "conditions"},
                "conditions": conditions,
            }
        }
        app_id = app_root.get("id") or f"{benchmark['id']}.applicability"
        add_object(
            app_id,
            "applicability_catalog",
            "objects/applicability.json",
            compiled_applicability,
            applicability_path,
        )
        compiled_benchmark["benchmark"]["applicability_catalog"] = app_id

    for rule_path in sorted((benchmark_dir / "rules").glob("*.yaml")):
        doc = load_yaml(rule_path)
        rule = doc.get("rule")
        if not isinstance(rule, dict) or not rule.get("id"):
            raise ValueError(f"{rule_path}: missing Rule id")
        compiled = json.loads(json.dumps(doc))
        choices = compiled["rule"].get("assessment_choices") or {}
        for selector, choice in choices.items():
            if not isinstance(choice, dict) or not isinstance(choice.get("assessment"), str):
                continue
            target, assessment_doc = resolve_assessment(
                source_root, rule_path, choice["assessment"]
            )
            aid = assessment_doc["assessment"]["id"]
            assessment_docs[aid] = (target, assessment_doc)
            choice["assessment"] = aid
        rid = rule["id"]
        add_object(
            rid,
            "rule",
            f"objects/rules/{safe_name(rid)}.json",
            compiled,
            rule_path,
        )

    for aid, (source_path, doc) in sorted(assessment_docs.items()):
        add_object(
            aid,
            "assessment",
            f"objects/assessments/{safe_name(aid)}.json",
            doc,
            source_path,
        )

    add_object(
        benchmark["id"],
        "benchmark",
        "objects/benchmark.json",
        compiled_benchmark,
        benchmark_path,
    )

    return benchmark, members, object_index


def write_bundle(
    output: Path,
    benchmark: dict,
    members: dict[str, bytes],
    object_index: dict[str, dict],
    *,
    sign_self_signed: bool,
    provenance: dict,
):
    manifest = {
        "format": "scap-ng-package-manifest",
        "format_version": "0.0.3-experimental",
        "benchmark_id": benchmark["id"],
        "benchmark_version": benchmark.get("version"),
        "entrypoint": benchmark["id"],
        "objects": {
            oid: {
                "type": row["type"],
                "path": row["path"],
                "sha256": row["sha256"],
                "size": row["size"],
                "source": row["source"],
            }
            for oid, row in sorted(object_index.items())
        },
        "integrity": {
            "algorithm": "sha-256",
            "unexpected_members": "reject",
        },
        "build_provenance": provenance,
        "signature": {
            "format": "cms-detached-der" if sign_self_signed else None,
            "path": "META-INF/signature.p7s" if sign_self_signed else None,
            "certificate_path": "META-INF/signer-test.pem" if sign_self_signed else None,
            "trust": "self-signed-experimental-no-publisher-trust"
            if sign_self_signed
            else None,
        },
    }
    manifest_bytes = canonical_json(manifest)
    signature = cert_pem = None
    if sign_self_signed:
        signature, cert_pem = sign_manifest(manifest_bytes)
        verify_cms_signature(manifest_bytes, signature, cert_pem)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zf:
        deterministic_zip_add(zf, "META-INF/manifest.json", manifest_bytes)
        if signature is not None:
            deterministic_zip_add(zf, "META-INF/signature.p7s", signature)
            deterministic_zip_add(zf, "META-INF/signer-test.pem", cert_pem)
        for name, data in sorted(members.items()):
            deterministic_zip_add(zf, name, data)

    return {
        "benchmark_id": benchmark["id"],
        "file": output.name,
        "bytes": output.stat().st_size,
        "object_count": len(object_index),
        "member_count": len(members) + 1 + (2 if sign_self_signed else 0),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "signed": sign_self_signed,
        "signing_trust": "self-signed-experimental-no-publisher-trust"
        if sign_self_signed
        else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--metrics", type=Path, required=True)
    ap.add_argument("--sign-self-signed-test-cert", action="store_true")
    ap.add_argument("--source-revision")
    ap.add_argument("--scap-ng-revision")
    args = ap.parse_args()

    source_root = _lexical_abs(args.corpus_root)
    benchmark_dirs = sorted(
        p.parent
        for p in source_root.rglob("benchmark.yaml")
        if (p.parent / "rules").is_dir() and (p.parent / "assessments").is_dir()
    )
    if not benchmark_dirs:
        raise SystemExit("No current-design Benchmark trees found")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics = []
    for benchmark_dir in benchmark_dirs:
        benchmark, members, object_index = compile_benchmark(source_root, benchmark_dir)
        filename = f"{safe_name(benchmark['id'])}.scapng"
        metrics.append(
            write_bundle(
                args.output_dir / filename,
                benchmark,
                members,
                object_index,
                sign_self_signed=args.sign_self_signed_test_cert,
                provenance={
                    "authoring_source_root": source_root.name,
                    "niwc_source_revision": args.source_revision,
                    "scap_ng_revision": args.scap_ng_revision,
                    "generated_fresh_for_this_run": True,
                },
            )
        )

    summary = {
        "format": "scap-ng-content-compiler-experiment-0.1",
        "bundles": len(metrics),
        "total_bytes": sum(x["bytes"] for x in metrics),
        "signed_bundles": sum(1 for x in metrics if x["signed"]),
        "signing_trust": (
            "self-signed-experimental-no-publisher-trust"
            if args.sign_self_signed_test_cert
            else None
        ),
        "packages": metrics,
    }
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "packages"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
