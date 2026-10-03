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

PACKAGE_MANIFEST_SCHEMA = Path(__file__).resolve().parents[1] / "schema/v0.1.0/package-manifest.schema.json"

import yaml
import jsonschema
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


def readable_member_name(source_path: Path, logical_id: str, kind: str) -> str:
    """Return a stable, human-readable package member name.

    Preserve familiar SCAP-NG authoring structure inside compiled bundles. Only
    shorten an individual filename when needed to satisfy the package's 160
    character member-path ceiling.
    """
    source_path = Path(source_path)
    suffix = ".json"

    if kind == "benchmark":
        return "benchmark.json"
    if kind == "applicability_catalog":
        return "applicability.json"

    parts = list(source_path.parts)
    if kind == "rule":
        base = safe_name(source_path.stem)
        member = f"rules/{base}{suffix}"
    elif kind == "assessment":
        rel_parts = None
        # Preserve everything below the nearest authoring 'assessments' directory,
        # including automated/manual/applicability categorization.
        for i in range(len(parts) - 1, -1, -1):
            if parts[i] == "assessments":
                rel_parts = parts[i + 1 :]
                break
        if not rel_parts:
            rel_parts = [source_path.name]
        clean = [safe_name(p) for p in rel_parts[:-1]]
        clean.append(safe_name(Path(rel_parts[-1]).stem) + suffix)
        member = Path("assessments", *clean).as_posix()
    else:
        member = f"{safe_name(kind)}/{safe_name(source_path.stem)}{suffix}"

    if len(member) <= 160:
        return member

    # Targeted fallback for pathological source names: keep the directory and a
    # readable prefix, adding a short digest solely to avoid extraction failures.
    p = Path(member)
    digest = hashlib.sha256(logical_id.encode("utf-8")).hexdigest()[:10]
    prefix_budget = max(12, 159 - len(p.parent.as_posix()) - len(digest) - len(suffix) - 2)
    stem = safe_name(p.stem)[:prefix_budget].rstrip("._-") or safe_name(kind)
    shortened = (p.parent / f"{stem}-{digest}{suffix}").as_posix()
    if len(shortened) > 160:
        raise ValueError(f"unable to produce readable package path <=160 characters: {member}")
    return shortened


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


def validate_draft_expression_assessments(assessments):
    """Validate the explicit 0.2.0 slice after dependency binding, not 0.1.0."""
    from validate_native_json_schemas import build_validators, document_errors
    from assessment_expression import AssessmentExpressionEvaluator
    from reported_elements import source_errors
    validators = None
    for aid, assessment in assessments.items():
        if assessment.get("specification", {}).get("version") != "0.2.0":
            continue
        if validators is None:
            validators = build_validators(Path(__file__).resolve().parents[1] / "schema/v0.2.0")
        errors = list(document_errors(validators["assessment.schema.json"], {"assessment": assessment}))
        if errors:
            raise ValueError(f"{aid}: invalid 0.2.0 Assessment: {errors[0].message}")
        reporting_errors = source_errors(assessment)
        if reporting_errors:
            raise ValueError(f"{aid}: invalid reported_elements: {reporting_errors[0]}")
        graph = {}
        def collect(identity):
            if identity in graph:
                return
            node = assessments[identity]
            graph[identity] = node
            for dependency in node.get("dependencies", {}).values():
                collect(dependency["expected_id"])
        collect(aid)
        AssessmentExpressionEvaluator(graph)


def compile_benchmark(source_root: Path, benchmark_dir: Path):
    benchmark_path = benchmark_dir / "benchmark.yaml"
    benchmark_doc = load_yaml(benchmark_path)
    benchmark = benchmark_doc.get("benchmark")
    if not isinstance(benchmark, dict) or not benchmark.get("id"):
        raise ValueError(f"{benchmark_path}: missing Benchmark id")

    members: dict[str, bytes] = {}
    object_index: dict[str, dict] = {}
    assessment_docs: dict[str, tuple[Path, dict]] = {}

    def remember_assessment(aid, source_path, doc):
        previous = assessment_docs.get(aid)
        if previous is not None and previous[0] != source_path:
            raise ValueError(f"duplicate Assessment identity {aid}: {previous[0]} vs {source_path}")
        if previous is not None:
            return  # Preserve an already compiled shared dependency.
        assessment_docs[aid] = (source_path, doc)

    def add_object(object_id: str, kind: str, member: str, obj: dict, source_path: Path):
        if object_id in object_index:
            prior = object_index[object_id]["source"]
            raise ValueError(
                f"duplicate logical object id {object_id}: {prior} vs {source_path}"
            )
        if member in members:
            raise ValueError(
                f"duplicate package member path {member}: logical object {object_id}"
            )
        data = canonical_json(obj)
        members[member] = data
        payload = obj.get(kind) if isinstance(obj.get(kind), dict) else None
        if payload is None:
            root_key = {
                "applicability_catalog": "applicability",
            }.get(kind, kind)
            payload = obj.get(root_key) if isinstance(obj.get(root_key), dict) else {}
        object_index[object_id] = {
            "type": kind,
            "version": payload.get("version"),
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
        source_conditions = app_root.get("conditions") or {}
        if isinstance(source_conditions, dict):
            conditions = {}
            for condition_id, row in source_conditions.items():
                if not isinstance(row, dict):
                    conditions[condition_id] = row
                    continue
                updated = json.loads(json.dumps(row))
                ref = updated.get("assessment")
                if isinstance(ref, str):
                    target, assessment_doc = resolve_assessment(
                        source_root, applicability_path, ref
                    )
                    aid = assessment_doc["assessment"]["id"]
                    remember_assessment(aid, target, assessment_doc)
                    updated["assessment"] = aid
                conditions[condition_id] = updated
        elif isinstance(source_conditions, list):
            conditions = []
            for row in source_conditions:
                if not isinstance(row, dict) or not isinstance(row.get("assessment"), str):
                    conditions.append(row)
                    continue
                target, assessment_doc = resolve_assessment(
                    source_root, applicability_path, row["assessment"]
                )
                aid = assessment_doc["assessment"]["id"]
                remember_assessment(aid, target, assessment_doc)
                updated = json.loads(json.dumps(row))
                updated["assessment"] = aid
                conditions.append(updated)
        else:
            raise ValueError(f"{applicability_path}: conditions must be mapping or list")
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
            readable_member_name(applicability_path, app_id, "applicability_catalog"),
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
            remember_assessment(aid, target, assessment_doc)
            choice["assessment"] = aid
        rid = rule["id"]
        add_object(
            rid,
            "rule",
            readable_member_name(rule_path, rid, "rule"),
            compiled,
            rule_path,
        )

    # Resolve every declared edge, including unused/unselected branches, before
    # packaging. A dependency is an immutable manifest object, never a source path.
    active, finished = set(), set()
    def close_dependencies(aid):
        if aid in active:
            raise ValueError(f"Assessment dependency cycle: {aid}")
        if aid in finished:
            return
        if len(active) >= 200:
            raise ValueError("Assessment dependency depth budget exceeded")
        active.add(aid)
        source_path, doc = assessment_docs[aid]
        compiled_doc = json.loads(json.dumps(doc))
        for alias, dependency in compiled_doc["assessment"].get("dependencies", {}).items():
            if not isinstance(dependency, dict) or not isinstance(dependency.get("assessment"), str):
                raise ValueError(f"{aid}: invalid Assessment dependency {alias}")
            target_path, target_doc = resolve_assessment(source_root, source_path, dependency["assessment"])
            # Resolve symlinks too; lexical containment alone is insufficient.
            if not target_path.resolve().is_relative_to(source_root.resolve()):
                raise ValueError(f"{aid}: dependency escapes corpus root: {alias}")
            target = target_doc["assessment"]
            for key, actual in (("expected_id", target["id"]), ("expected_version", target.get("version")), ("purpose", target.get("purpose"))):
                if dependency.get(key) is not None and dependency[key] != actual:
                    raise ValueError(f"{aid}: dependency {alias} {key} mismatch")
            remember_assessment(target["id"], target_path, target_doc)
            close_dependencies(target["id"])
            dependency.update(assessment=target["id"], expected_id=target["id"], expected_version=target.get("version"))
        assessment_docs[aid] = (source_path, compiled_doc)
        active.remove(aid)
        finished.add(aid)

    for aid in list(assessment_docs):
        close_dependencies(aid)

    validate_draft_expression_assessments({
        aid: doc["assessment"] for aid, (_, doc) in assessment_docs.items()
    })

    for aid, (source_path, doc) in sorted(assessment_docs.items()):
        add_object(
            aid,
            "assessment",
            readable_member_name(source_path, aid, "assessment"),
            doc,
            source_path,
        )

    add_object(
        benchmark["id"],
        "benchmark",
        readable_member_name(benchmark_path, benchmark["id"], "benchmark"),
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
                "version": row.get("version"),
                "path": row["path"],
                "sha256": row["sha256"],
                "size": row["size"],
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

    verification = verify_bundle(output, verify_signature=sign_self_signed)
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
        "verified_object_graph": verification["objects"],
    }


def verify_bundle(package: Path, *, verify_signature: bool = False) -> dict:
    """Verify archive profile, manifest integrity and logical package references."""
    with zipfile.ZipFile(package, "r") as zf:
        infos = zf.infolist()
        names = [x.filename for x in infos]
        if len(names) != len(set(names)):
            raise ValueError(f"{package}: duplicate ZIP member names")
        if zf.comment:
            raise ValueError(f"{package}: ZIP archive comment is not permitted")
        for info in infos:
            name = info.filename
            p = Path(name)
            if (
                name.startswith("/")
                or "\\" in name
                or any(part in {"", ".", ".."} for part in p.parts)
                or (p.parts and re.match(r"^[A-Za-z]:$", p.parts[0]))
            ):
                raise ValueError(f"{package}: unsafe ZIP member path {name!r}")
            if info.date_time != (1980, 1, 1, 0, 0, 0):
                raise ValueError(f"{package}: non-deterministic timestamp on {name}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise ValueError(f"{package}: unsupported compression method on {name}")
            if info.extra:
                raise ValueError(f"{package}: ZIP extra fields are not permitted on {name}")
            if info.comment:
                raise ValueError(f"{package}: ZIP member comments are not permitted on {name}")
            if len(name) > 160:
                raise ValueError(f"{package}: ZIP member path too long ({len(name)}): {name}")

        try:
            manifest_bytes = zf.read("META-INF/manifest.json")
        except KeyError as exc:
            raise ValueError(f"{package}: missing META-INF/manifest.json") from exc
        manifest = json.loads(manifest_bytes)
        schema = json.loads(PACKAGE_MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(manifest)
        objects = manifest.get("objects")
        if not isinstance(objects, dict):
            raise ValueError(f"{package}: manifest objects must be a mapping")

        expected = {"META-INF/manifest.json"}
        sig = manifest.get("signature") or {}
        for key in ("path", "certificate_path"):
            value = sig.get(key)
            if isinstance(value, str):
                expected.add(value)

        physical_paths = set()
        for object_id, row in objects.items():
            if not isinstance(row, dict):
                raise ValueError(f"{package}: invalid manifest object record {object_id}")
            path = row.get("path")
            if not isinstance(path, str):
                raise ValueError(f"{package}: object {object_id} missing path")
            if path in physical_paths:
                raise ValueError(f"{package}: multiple logical objects share member path {path}")

            kind = row.get("type")
            if kind == "benchmark" and path != "benchmark.json":
                raise ValueError(f"{package}: Benchmark must use readable path benchmark.json, got {path}")
            if kind == "applicability_catalog" and path != "applicability.json":
                raise ValueError(f"{package}: applicability catalog must use readable path applicability.json, got {path}")
            if kind == "rule" and not path.startswith("rules/"):
                raise ValueError(f"{package}: Rule {object_id} must be under rules/, got {path}")
            if kind == "assessment" and not path.startswith("assessments/"):
                raise ValueError(f"{package}: Assessment {object_id} must be under assessments/, got {path}")
            if kind in {"rule", "assessment"} and re.fullmatch(r"[0-9a-f]{16}\\.json", Path(path).name):
                raise ValueError(f"{package}: opaque hash-only member name is not permitted: {path}")

            physical_paths.add(path)
            expected.add(path)
            try:
                data = zf.read(path)
            except KeyError as exc:
                raise ValueError(f"{package}: missing member {path} for {object_id}") from exc
            if len(data) != row.get("size"):
                raise ValueError(f"{package}: size mismatch for {object_id}")
            if hashlib.sha256(data).hexdigest() != row.get("sha256"):
                raise ValueError(f"{package}: digest mismatch for {object_id}")

        if (manifest.get("integrity") or {}).get("unexpected_members") == "reject":
            unexpected = sorted(set(names) - expected)
            if unexpected:
                raise ValueError(f"{package}: unexpected ZIP members: {unexpected}")

        entrypoint = manifest.get("entrypoint")
        entry = objects.get(entrypoint)
        if not isinstance(entry, dict) or entry.get("type") != "benchmark":
            raise ValueError(f"{package}: entrypoint does not resolve to Benchmark")
        benchmark_doc = json.loads(zf.read(entry["path"]))
        benchmark = benchmark_doc.get("benchmark") or {}

        for rid in benchmark.get("rules") or []:
            row = objects.get(rid)
            if not isinstance(row, dict) or row.get("type") != "rule":
                raise ValueError(f"{package}: Benchmark Rule {rid} does not resolve through manifest")

        app_id = benchmark.get("applicability_catalog")
        if app_id is not None:
            app_row = objects.get(app_id)
            if not isinstance(app_row, dict) or app_row.get("type") != "applicability_catalog":
                raise ValueError(f"{package}: applicability catalog {app_id} does not resolve")
            app_doc = json.loads(zf.read(app_row["path"]))
            conditions = (app_doc.get("applicability") or {}).get("conditions") or {}
            rows = conditions.values() if isinstance(conditions, dict) else conditions
            for condition in rows:
                if not isinstance(condition, dict):
                    continue
                aid = condition.get("assessment")
                if aid is None:
                    continue
                target = objects.get(aid)
                if not isinstance(target, dict) or target.get("type") != "assessment":
                    raise ValueError(
                        f"{package}: applicability Assessment {aid} does not resolve"
                    )

        for object_id, row in objects.items():
            if row.get("type") != "rule":
                continue
            rule_doc = json.loads(zf.read(row["path"]))
            rule = rule_doc.get("rule") or {}
            for selector, choice in (rule.get("assessment_choices") or {}).items():
                if not isinstance(choice, dict):
                    continue
                aid = choice.get("assessment")
                if aid is None:
                    continue
                target = objects.get(aid)
                if not isinstance(target, dict) or target.get("type") != "assessment":
                    raise ValueError(
                        f"{package}: Rule {object_id} choice {selector} Assessment "
                        f"{aid} does not resolve"
                    )

        assessments = {}
        for identity, row in objects.items():
            if row["type"] == "assessment":
                assessments[identity] = json.loads(zf.read(row["path"]))["assessment"]
        active, finished = set(), set()
        def verify_dependencies(identity):
            if identity in active:
                raise ValueError(f"{package}: Assessment dependency cycle: {identity}")
            if identity in finished:
                return
            if len(active) >= 200:
                raise ValueError(f"{package}: Assessment dependency depth budget exceeded")
            active.add(identity)
            for alias, dependency in assessments[identity].get("dependencies", {}).items():
                target_id = dependency.get("assessment")
                target = assessments.get(target_id)
                if target is None:
                    raise ValueError(f"{package}: Assessment {identity} dependency {alias} does not resolve")
                if dependency.get("expected_id") != target_id or dependency.get("expected_version") != target.get("version"):
                    raise ValueError(f"{package}: Assessment {identity} dependency {alias} identity/version mismatch")
                if dependency.get("purpose") is not None and dependency["purpose"] != target.get("purpose"):
                    raise ValueError(f"{package}: Assessment {identity} dependency {alias} purpose mismatch")
                verify_dependencies(target_id)
            active.remove(identity)
            finished.add(identity)
        for identity in assessments:
            verify_dependencies(identity)

        validate_draft_expression_assessments(assessments)

        if verify_signature and sig.get("format") == "cms-detached-der":
            verify_cms_signature(
                manifest_bytes,
                zf.read(sig["path"]),
                zf.read(sig["certificate_path"]),
            )

    return {
        "benchmark_id": entrypoint,
        "objects": len(objects),
        "members": len(names),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
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
