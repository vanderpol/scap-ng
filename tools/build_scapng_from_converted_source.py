#!/usr/bin/env python3
"""Build deterministic signed prototype .scapng packages from converted source layouts."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import zipfile

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SPEC="0.1-prototype"
TEST_SEED=bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+","_",value).strip("_") or "scapng"


def canonical(obj) -> bytes:
    return json.dumps(
        obj,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode("utf-8")


def policy_only_combined_rule(doc: dict) -> dict:
    out=json.loads(json.dumps(doc))
    rule=out.get("rule",{})
    rule.pop("assessment",None)
    return out


def combined_members(root: Path, package_type: str):
    members={
        "benchmark.json":load(root/"benchmark.yaml"),
        "processing.json":load(root/"processing.yaml"),
        "profiles.json":load(root/"profiles.yaml"),
        "platforms.json":load(root/"platforms.yaml"),
        "groups.json":load(root/"groups.yaml"),
        "values.json":load(root/"values.yaml"),
    }
    applicability_path=root/"applicability.yaml"
    if applicability_path.exists():
        applicability=load(applicability_path)
        if (
            package_type!="policy-only"
            and applicability.get("migration",{}).get("status")=="unsupported"
        ):
            raise ValueError("unsupported applicability assessment cannot enter automated package")
        members["applicability.json"]=applicability
    for path in sorted((root/"rules").glob("*.yaml")):
        doc=load(path)
        if package_type=="policy-only":
            doc=policy_only_combined_rule(doc)
        elif doc.get("rule",{}).get("migration",{}).get("status")=="unsupported":
            raise ValueError(f"{path}: unsupported rule cannot enter automated package")
        members[f"rules/{path.stem}.json"]=doc
    return members


def split_members(root: Path, package_type: str):
    members={
        "benchmark.json":load(root/"benchmark.yaml"),
        "processing.json":load(root/"processing.yaml"),
        "profiles.json":load(root/"profiles.yaml"),
        "platforms.json":load(root/"platforms.yaml"),
        "groups.json":load(root/"groups.yaml"),
        "values.json":load(root/"values.yaml"),
    }
    applicability_path=root/"applicability.yaml"
    if applicability_path.exists():
        applicability=load(applicability_path)
        if applicability.get("migration",{}).get("status")=="unsupported":
            raise ValueError("unsupported applicability assessment cannot enter package")
        members["applicability.json"]=applicability

    rule_ids=set()
    for path in sorted((root/"policy"/"rules").glob("*.yaml")):
        doc=load(path)
        rid=doc.get("rule",{}).get("id")
        if rid:
            rule_ids.add(rid)
        members[f"policy/rules/{path.stem}.json"]=doc

    if package_type=="policy-only":
        return members

    bindings=load(root/"automation"/"bindings.yaml")
    assessment_files={
        p.stem:p for p in sorted((root/"automation"/"assessments").glob("*.yaml"))
    }
    seen_rules=set()
    referenced=set()
    for binding in bindings.get("bindings",[]):
        rid=binding.get("rule")
        aid=binding.get("assessment")
        if rid not in rule_ids:
            raise ValueError(f"binding references unknown rule: {rid}")
        if rid in seen_rules:
            raise ValueError(f"duplicate binding for rule: {rid}")
        seen_rules.add(rid)
        safe_aid="".join(
            c if c.isalnum() or c in "._-" else "_" for c in aid
        ).strip("_")
        if safe_aid not in assessment_files:
            raise ValueError(f"binding references missing assessment: {aid}")
        seen_rules.add(rid)
        referenced.add(safe_aid)

    members["bindings.json"]=bindings
    for safe_aid in sorted(referenced):
        doc=load(assessment_files[safe_aid])
        migration=doc.get("assessment",{}).get("migration",{})
        if migration.get("status")=="unsupported":
            raise ValueError(
                f"{assessment_files[safe_aid]}: unsupported assessment cannot enter package"
            )
        members[f"assessments/{safe_aid}.json"]=doc
    return members


def write_bundle(output: Path,model: str,package_type: str,members: dict,benchmark: dict):
    member_bytes={name:canonical(obj) for name,obj in members.items()}
    bid=benchmark["benchmark"]["id"]
    bver=benchmark["benchmark"].get("version")
    manifest={
        "spec":SPEC,
        "prototype":True,
        "package":{
            "id":f"{bid}.{model}.{package_type}",
            "benchmark_id":bid,
            "benchmark_version":bver,
            "type":package_type,
            "source_model":model,
        },
        "entrypoint":"benchmark.json",
        "files":[
            {
                "path":name,
                "sha256":hashlib.sha256(data).hexdigest(),
                "size":len(data),
                "media_type":"application/scap-ng+json",
            }
            for name,data in sorted(member_bytes.items())
        ],
        "integrity":{"algorithm":"sha-256","unexpected_members":"reject"},
        "signature":{
            "path":"META-INF/signature.prototype.json",
            "format":"prototype-ed25519",
        },
    }
    manifest_bytes=canonical(manifest)
    key=Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    public_key=key.public_key().public_bytes(
        serialization.Encoding.Raw,serialization.PublicFormat.Raw
    )
    signature={
        "prototype":True,
        "warning":"Uses the public RFC 8032 test key; no publisher trust is implied.",
        "algorithm":"Ed25519",
        "signed_object":"META-INF/manifest.json exact bytes",
        "manifest_sha256":hashlib.sha256(manifest_bytes).hexdigest(),
        "public_key_raw_base64":base64.b64encode(public_key).decode(),
        "signature_base64":base64.b64encode(key.sign(manifest_bytes)).decode(),
    }
    signature_bytes=canonical(signature)

    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        def add(name,data):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,data)
        add("META-INF/manifest.json",manifest_bytes)
        add("META-INF/signature.prototype.json",signature_bytes)
        for name,data in sorted(member_bytes.items()):
            add(name,data)

    return {
        "model":model,
        "type":package_type,
        "file":output.name,
        "bytes":output.stat().st_size,
        "member_count":len(member_bytes)+2,
        "manifest_sha256":signature["manifest_sha256"],
        "package_id":manifest["package"]["id"],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("conversion_dir",type=Path)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--artifact-prefix")
    ap.add_argument("--skip-automated-if-blocked",action="store_true")
    args=ap.parse_args()

    root=args.conversion_dir
    out=args.output_dir
    metrics=[]
    conversion_summary={}
    summary_path=root/"conversion-summary.json"
    if summary_path.exists():
        conversion_summary=json.loads(summary_path.read_text(encoding="utf-8"))
    blocked_rules=int(conversion_summary.get("blocked_rules",0) or 0)

    for model in ("combined-rule","split-policy-assessment-binding"):
        source=root/model
        benchmark=load(source/"benchmark.yaml")
        prefix=args.artifact_prefix or safe_name(benchmark["benchmark"]["id"])
        for package_type in ("policy-only","automated"):
            if (
                package_type=="automated"
                and blocked_rules
                and args.skip_automated_if_blocked
            ):
                metrics.append({
                    "model":model,
                    "type":package_type,
                    "status":"skipped",
                    "reason":"source_remediation_blockers",
                    "blocked_rules":blocked_rules,
                })
                continue
            members=(
                combined_members(source,package_type)
                if model=="combined-rule"
                else split_members(source,package_type)
            )
            filename=f"{prefix}-{model}-{package_type}.scapng"
            row=write_bundle(out/filename,model,package_type,members,benchmark)
            row["status"]="built"
            metrics.append(row)

    out.mkdir(parents=True,exist_ok=True)
    (out/"package-metrics.json").write_text(
        json.dumps(metrics,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(metrics,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
