#!/usr/bin/env python3
"""Build iteration 001 SCAP-NG prototype bundles from individual authoring files.

Combined-rule Windows prototypes support shared rule bases plus STIG-specific
overlays. Overlays are a source/build concept only: published packages contain
fully resolved self-contained rule documents.

Split-model assessments may also be shared across benchmarks and are resolved
into each published package.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import zipfile

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SPEC = "0.1-prototype"
TEST_SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
MODELS = ("combined-rule", "split-policy-assessment-binding")
BENCHMARKS = ("windows-client", "windows-server", "linux")


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def canonical(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def load_rule_dir(path: Path) -> dict[str, dict]:
    rules = {}
    if not path.exists():
        return rules
    for file in sorted(path.glob("*.yaml")):
        doc = load(file)
        rule = doc["rule"]
        if rule["id"] in rules:
            raise ValueError(f"duplicate rule id {rule['id']} in {path}")
        rules[rule["id"]] = doc
    return rules


def validate_rules(benchmark: dict, rules: dict[str, dict]) -> None:
    expected = list(benchmark["rules"])
    actual = list(rules)
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing or extra:
        raise ValueError(
            f"rule closure mismatch for {benchmark['id']}: "
            f"missing={missing}, extra={extra}"
        )


def policy_documents(benchmark_dir: Path):
    policy = benchmark_dir / "source" / "policy"
    benchmark_doc = load(policy / "benchmark.yaml")
    profile_doc = load(policy / "profile.yaml")
    provenance_doc = load(policy / "provenance.yaml")
    rules = load_rule_dir(policy / "rules")
    validate_rules(benchmark_doc["benchmark"], rules)
    return benchmark_doc, profile_doc, provenance_doc, rules


def assessment_index(model_root: Path, benchmark_dir: Path) -> dict[str, dict]:
    files = []
    shared = model_root / "shared-assessments"
    if shared.exists():
        files.extend(sorted(shared.rglob("*.yaml")))
    local = benchmark_dir / "source" / "automation" / "assessments"
    if local.exists():
        files.extend(sorted(local.glob("*.yaml")))

    index = {}
    for file in files:
        doc = load(file)
        assessment = doc["assessment"]
        aid = assessment["id"]
        if aid in index and index[aid] != doc:
            raise ValueError(f"conflicting assessment definitions for {aid}")
        index[aid] = doc
    return index


def shared_rule_index(model_root: Path) -> dict[str, dict]:
    index = {}
    shared = model_root / "shared-rules"
    if not shared.exists():
        return index
    for file in sorted(shared.rglob("*.yaml")):
        doc = load(file)
        item = doc["shared_rule"]
        sid = item["id"]
        if sid in index and index[sid] != doc:
            raise ValueError(f"conflicting shared rule definitions for {sid}")
        index[sid] = doc
    return index


def policy_part(rule: dict) -> dict:
    return {k: copy.deepcopy(v) for k, v in rule.items() if k != "assessment"}


def validate_resolved_policy(
    benchmark_id: str,
    resolved: dict[str, dict],
    policy_rules: dict[str, dict],
) -> None:
    for rule_id, doc in resolved.items():
        expected = policy_rules[rule_id]["rule"]
        actual = policy_part(doc["rule"])
        if actual != expected:
            raise ValueError(
                f"resolved combined rule policy mismatch for {benchmark_id} / "
                f"{rule_id}\nexpected={expected!r}\nactual={actual!r}"
            )


def resolve_combined_overlays(
    model_root: Path,
    benchmark_dir: Path,
) -> dict[str, dict]:
    shared = shared_rule_index(model_root)
    overlay_dir = benchmark_dir / "source" / "automated" / "overlays"
    resolved = {}

    if not overlay_dir.exists():
        return resolved

    for file in sorted(overlay_dir.glob("*.yaml")):
        doc = load(file)
        overlay = doc["overlay"]
        sid = overlay["extends"]
        if sid not in shared:
            raise ValueError(f"{file}: unknown shared rule {sid}")

        shared_doc = shared[sid]["shared_rule"]
        requested_version = overlay.get("version")
        if requested_version != shared_doc["version"]:
            raise ValueError(
                f"{file}: requested shared rule {sid}@{requested_version}, "
                f"available version is {shared_doc['version']}"
            )

        rule = copy.deepcopy(shared_doc["rule"])
        for key, value in overlay.get("rule", {}).items():
            rule[key] = copy.deepcopy(value)

        params = overlay.get("assessment_parameters")
        if params is not None:
            if "assessment" not in rule:
                raise ValueError(f"{file}: parameters supplied to rule without assessment")
            rule["assessment"]["parameters"] = copy.deepcopy(params)

        rule_id = rule.get("id")
        if not rule_id:
            raise ValueError(f"{file}: resolved overlay has no rule id")
        if rule_id in resolved:
            raise ValueError(f"{file}: duplicate resolved rule id {rule_id}")

        resolved[rule_id] = {
            "scap_ng": SPEC,
            "prototype": True,
            "model": "combined-rule",
            "resolved_from": {
                "shared_rule": sid,
                "shared_rule_version": shared_doc["version"],
                "overlay": file.name,
            },
            "rule": rule,
        }

    return resolved


def combined_members(model_root: Path, benchmark_dir: Path, package_type: str):
    benchmark_doc, profile_doc, provenance_doc, policy_rules = policy_documents(
        benchmark_dir
    )

    if package_type == "policy-only":
        rules = policy_rules
    else:
        rules = load_rule_dir(benchmark_dir / "source" / "automated" / "rules")
        overlays = resolve_combined_overlays(model_root, benchmark_dir)
        duplicate = sorted(set(rules) & set(overlays))
        if duplicate:
            raise ValueError(f"local and overlay rules collide: {duplicate}")
        rules.update(overlays)
        validate_rules(benchmark_doc["benchmark"], rules)
        validate_resolved_policy(
            benchmark_doc["benchmark"]["id"], rules, policy_rules
        )

    members = {
        "benchmark.json": benchmark_doc,
        "profile.json": profile_doc,
        "provenance/source.json": provenance_doc,
    }
    for rule_id, doc in rules.items():
        members[f"rules/{rule_id}.json"] = doc
    return members, benchmark_doc["benchmark"]


def split_members(model_root: Path, benchmark_dir: Path, package_type: str):
    benchmark_doc, profile_doc, provenance_doc, rules = policy_documents(benchmark_dir)
    members = {
        "benchmark.json": benchmark_doc,
        "profile.json": profile_doc,
        "provenance/source.json": provenance_doc,
    }
    for rule_id, doc in rules.items():
        members[f"policy/rules/{rule_id}.json"] = doc

    if package_type == "automated":
        binding_doc = load(benchmark_dir / "source" / "automation" / "bindings.yaml")
        bindings = binding_doc["bindings"]
        rule_ids = set(rules)
        bound_rules = set()
        index = assessment_index(model_root, benchmark_dir)
        referenced = set()

        for binding in bindings:
            rule_id = binding["rule"]
            assessment_id = binding["assessment"]
            if rule_id not in rule_ids:
                raise ValueError(f"binding references unknown rule {rule_id}")
            if rule_id in bound_rules:
                raise ValueError(f"multiple bindings for rule {rule_id}")
            if assessment_id not in index:
                raise ValueError(f"binding references unknown assessment {assessment_id}")
            bound_rules.add(rule_id)
            referenced.add(assessment_id)

        members["bindings.json"] = binding_doc
        for assessment_id in sorted(referenced):
            members[f"assessments/{assessment_id}.json"] = index[assessment_id]

    return members, benchmark_doc["benchmark"]


def package_id(benchmark: dict, model: str, package_type: str) -> str:
    return f"{benchmark['id']}.{model}.{package_type}"


def write_bundle(
    output: Path,
    model: str,
    package_type: str,
    members: dict,
    benchmark: dict,
) -> dict:
    member_bytes = {name: canonical(obj) for name, obj in members.items()}
    manifest = {
        "spec": SPEC,
        "prototype": True,
        "package": {
            "id": package_id(benchmark, model, package_type),
            "benchmark_id": benchmark["id"],
            "benchmark_version": benchmark["version"],
            "type": package_type,
            "source_model": model,
        },
        "entrypoint": "benchmark.json",
        "files": [
            {
                "path": name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
                "media_type": "application/scap-ng+json",
            }
            for name, data in sorted(member_bytes.items())
        ],
        "integrity": {
            "algorithm": "sha-256",
            "unexpected_members": "reject",
        },
        "signature": {
            "path": "META-INF/signature.prototype.json",
            "format": "prototype-ed25519",
        },
    }
    manifest_bytes = canonical(manifest)

    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    public_key = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    signature = {
        "prototype": True,
        "warning": (
            "Uses the public RFC 8032 test key. Demonstrates package mechanics "
            "only; no publisher trust."
        ),
        "algorithm": "Ed25519",
        "signed_object": "META-INF/manifest.json exact bytes",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "public_key_raw_base64": base64.b64encode(public_key).decode(),
        "signature_base64": base64.b64encode(key.sign(manifest_bytes)).decode(),
    }
    signature_bytes = canonical(signature)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:

        def add(name: str, data: bytes) -> None:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

        add("META-INF/manifest.json", manifest_bytes)
        add("META-INF/signature.prototype.json", signature_bytes)
        for name, data in sorted(member_bytes.items()):
            add(name, data)

    (output.parent / f"{output.name}.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output.parent / f"{output.name}.signature.prototype.json").write_text(
        json.dumps(signature, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    return {
        "model": model,
        "benchmark": output.parent.parent.name,
        "type": package_type,
        "file": output.name,
        "bytes": output.stat().st_size,
        "members": len(manifest["files"]) + 2,
        "manifest_sha256": signature["manifest_sha256"],
        "package_id": manifest["package"]["id"],
        "benchmark_id": benchmark["id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("research/iterations/001/prototypes/full-benchmarks"),
    )
    args = parser.parse_args()

    metrics = []
    for model in MODELS:
        model_root = args.root / model
        for benchmark_name in BENCHMARKS:
            benchmark_dir = model_root / benchmark_name
            if not benchmark_dir.exists():
                raise FileNotFoundError(benchmark_dir)

            for package_type in ("policy-only", "automated"):
                if model == "combined-rule":
                    members, benchmark = combined_members(
                        model_root, benchmark_dir, package_type
                    )
                else:
                    members, benchmark = split_members(
                        model_root, benchmark_dir, package_type
                    )

                filename = (
                    f"demo-{benchmark_name}-001-{model}-{package_type}.scapng"
                )
                output = benchmark_dir / "dist" / filename
                metrics.append(
                    write_bundle(output, model, package_type, members, benchmark)
                )
                print(output)

    (args.root / "package-metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
