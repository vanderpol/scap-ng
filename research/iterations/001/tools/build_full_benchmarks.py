#!/usr/bin/env python3
"""Rebuild iteration 001 full-benchmark .scapng bundles from committed YAML source."""
from __future__ import annotations
import argparse, base64, hashlib, json, zipfile
from pathlib import Path
import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

SPEC = "0.1-prototype"
# RFC 8032 public test vector key. NEVER a production trust key.
TEST_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def provenance(package_type: str):
    return {"scap_ng": SPEC, "prototype": True, "source": {
        "classification": "illustrative", "iteration": "001",
        "policy_origin": "DISA-style fields, illustrative only",
        "automation_origin": "SCAP-NG research prototype" if package_type == "automated" else None,
        "official_content": False}}


def combined_members(platform_dir: Path, package_type: str):
    doc = load(platform_dir / "source" / ("automated-benchmark.yaml" if package_type == "automated" else "policy-only-benchmark.yaml"))
    members = {
        "benchmark.json": {"scap_ng": SPEC, "prototype": True, "benchmark": doc["benchmark"]},
        "profile.json": {"scap_ng": SPEC, "prototype": True, "profile": doc["profile"]},
    }
    for rule in doc["rules"]:
        members[f"rules/{rule['id']}.json"] = {"scap_ng": SPEC, "prototype": True, "model": "combined-rule", "rule": rule}
    members["provenance/source.json"] = provenance(package_type)
    return members, doc["benchmark"]


def split_members(platform_dir: Path, package_type: str):
    policy = load(platform_dir / "source" / "policy.yaml")
    automation = load(platform_dir / "source" / "automation.yaml")
    benchmark = policy["benchmark"] if package_type == "policy-only" else automation["benchmark"]
    members = {
        "benchmark.json": {"scap_ng": SPEC, "prototype": True, "benchmark": benchmark},
        "profile.json": {"scap_ng": SPEC, "prototype": True, "profile": policy["profile"]},
    }
    for rule in policy["rules"]:
        members[f"policy/rules/{rule['id']}.json"] = {"scap_ng": SPEC, "prototype": True, "model": "split-policy-assessment-binding", "rule": rule}
    if package_type == "automated":
        for assessment in automation["assessments"]:
            members[f"assessments/{assessment['id']}.json"] = {"scap_ng": SPEC, "prototype": True, "model": "split-policy-assessment-binding", "assessment": assessment}
        members["bindings.json"] = {"scap_ng": SPEC, "prototype": True, "model": "split-policy-assessment-binding", "bindings": automation["bindings"]}
    members["provenance/source.json"] = provenance(package_type)
    return members, benchmark


def write_bundle(output: Path, model: str, package_type: str, members: dict, benchmark: dict):
    mb = {name: canonical(obj) for name, obj in members.items()}
    manifest = {
        "spec": SPEC, "prototype": True,
        "package": {"id": benchmark["id"], "version": benchmark["version"], "type": package_type, "source_model": model},
        "entrypoint": "benchmark.json",
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "media_type": "application/scap-ng+json"}
                  for name, data in sorted(mb.items())],
        "integrity": {"algorithm": "sha-256", "unexpected_members": "reject"},
        "signature": {"path": "META-INF/signature.prototype.json", "format": "prototype-ed25519"},
    }
    manifest_bytes = canonical(manifest)
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    signature = {
        "prototype": True,
        "warning": "Uses the public RFC 8032 test key. Demonstrates package mechanics only; no publisher trust.",
        "algorithm": "Ed25519", "signed_object": "META-INF/manifest.json exact bytes",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "public_key_raw_base64": base64.b64encode(pub).decode(),
        "signature_base64": base64.b64encode(key.sign(manifest_bytes)).decode(),
    }
    sig_bytes = canonical(signature)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        def add(name, data):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
        add("META-INF/manifest.json", manifest_bytes)
        add("META-INF/signature.prototype.json", sig_bytes)
        for name, data in sorted(mb.items()): add(name, data)
    (output.parent / f"{output.name}.manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    (output.parent / f"{output.name}.signature.prototype.json").write_text(json.dumps(signature, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("research/iterations/001/prototypes/full-benchmarks"))
    args = ap.parse_args()
    for model in ("combined-rule", "split-policy-assessment-binding"):
        for platform in ("windows", "linux"):
            d = args.root / model / platform
            for package_type in ("policy-only", "automated"):
                if model == "combined-rule": members, benchmark = combined_members(d, package_type)
                else: members, benchmark = split_members(d, package_type)
                out = d / "dist" / f"demo-{platform}-001-{model}-{package_type}.scapng"
                write_bundle(out, model, package_type, members, benchmark)
                print(out)
    return 0

if __name__ == "__main__": raise SystemExit(main())
