#!/usr/bin/env python3
"""Build and verify a version-pinned SCAP-NG *source toolchain* archive.

This is distinct from compiling a .scapng content bundle. It snapshots the
entire committed source tree so historical tools, tests, specification,
schemas, and developer guidance cannot be accidentally omitted. Nothing in
the archive proves runtime/scanner conformance or release acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile


FORMAT = "scap-ng-source-toolchain/1"
DATE = (1980, 1, 1, 0, 0, 0)
VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\Z")
MANIFEST_NAME = "TOOLCHAIN-MANIFEST.json"
COMMON_REQUIRED = (
    "README.md",
    "MAINTAINING.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "specification/README.md",
    "specification/core/conformance.md",
    "specification/migration/oval-5.12.3-to-ng.md",
    "tools/HUMAN-RUNNABLE-SCRIPTS.md",
    "tools/oval_semantic_ir.py",
    "tools/scap_upconvert_v003/convert_full_review.py",
    "tools/scap_ng_content_compiler.py",
)
CURRENT_REQUIRED = (
    "docs/developer/README.md",
    "docs/developer/CONVERTER-COMPILER-RUNBOOK.md",
    "docs/releases/TOOLCHAIN-RELEASES.md",
    "tools/scap_converter_core.py",
    "tools/v04_source_verified_object_presence.py",
    "tools/v04_source_verified_multitest_presence.py",
    "tools/v04_source_verified_multitest_states.py",
    "tools/v04_source_verified_constant_variable_matrix.py",
    "tools/convert_v04_oval_constant_variable_matrix.py",
    "tools/test_scap_converter_core.py",
    "tools/test_scap_converter_core_object_presence.py",
    "tools/test_scap_converter_core_multitest.py",
    "tools/test_scap_converter_core_multistate.py",
    "tools/test_scap_converter_core_singleton_presence.py",
    "tools/test_v04_public_cli_smoke.py",
    "tools/test_scap_converter_core_constant_matrix.py",
    "tools/test_v04_source_verified_constant_datatypes.py",
    "tools/convert_v04_oval_variable_datatype_suite.py",
    "tools/test_scap_converter_core_variable.py",
    "tools/test_scap_converter_core_family.py",
    "tools/audit_scap_converter_core_coverage.py",
    "tools/test_audit_scap_converter_core_coverage.py",
    "tools/v04_native_bundle_compiler.py",
)


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _archive_entries(repo: Path, ref: str) -> tuple[str, dict[str, tuple[bytes, int]]]:
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    archive = _git(repo, "archive", "--format=zip", commit)
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        entries = {}
        for name in source.namelist():
            if name.endswith("/"):
                continue
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or not path.parts:
                raise ValueError(f"unsafe git archive entry: {name}")
            if name in entries:
                raise ValueError(f"duplicate git archive entry: {name}")
            original_attr = source.getinfo(name).external_attr
            # zipfile replaces zero external_attr when writing; normalize it
            # in the manifest first so verification describes the actual ZIP.
            attr = original_attr or (0o100644 << 16)
            entries[name] = (source.read(name), attr)
    return commit, entries


def _check_required(entries: dict[str, tuple[bytes, int]], version: str, *, current: bool) -> None:
    required = list(COMMON_REQUIRED) + [f"schema/v{version}/README.md"]
    if current:
        required += CURRENT_REQUIRED
    missing = [path for path in required if path not in entries]
    if missing:
        raise ValueError("source snapshot lacks required release inputs: " + ", ".join(missing))
    prefixes = ("tools/", "tests/", "schema/", "specification/")
    if current:
        prefixes += ("docs/",)
    for prefix in prefixes:
        if not any(path.startswith(prefix) for path in entries):
            raise ValueError(f"source snapshot lacks {prefix}")


def build(repo: Path, out: Path, version: str, *, ref: str = "HEAD", current: bool = True,
          require_tag: bool = False) -> tuple[Path, dict]:
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"invalid SCAP-NG version: {version!r}")
    if require_tag:
        if current and ref != "v" + version:
            raise ValueError("release toolchains must use the exact vX.Y.Z tag")
        if not current and not ref.startswith("v" + version + "-"):
            raise ValueError("historical snapshots require a vX.Y.Z-* tag")
        # An identically named branch is not an immutable release tag.
        _git(repo, "show-ref", "--verify", "--quiet", "refs/tags/" + ref)
    commit, entries = _archive_entries(repo, ref)
    _check_required(entries, version, current=current)
    root = f"scap-ng-{version}-toolchain/"
    records = [
        {"path": path, "sha256": hashlib.sha256(data).hexdigest(),
         "bytes": len(data), "unix_mode_attributes": mode}
        for path, (data, mode) in sorted(entries.items())
    ]
    manifest = {
        "format": FORMAT,
        "version": version,
        "source_commit": commit,
        "source_ref": ref,
        "source_scope": "all committed files at source_commit",
        "validation_level": "source_snapshot_only; no scanner or OVAL semantic parity claim",
        "normative_specification": "specification/",
        "schema": f"schema/v{version}/",
        "developer_guides": "docs/developer/" if current else None,
        "operator_guide": "tools/HUMAN-RUNNABLE-SCRIPTS.md",
        "snapshot_kind": "current_release_candidate" if current else "historical_tag_source_reconstruction",
        "entrypoints": {
            **({"current_0_4_oval_converter_proven_leaf_subset": "tools/scap_converter_core.py",
                "current_native_0_4_compiler": "tools/v04_native_bundle_compiler.py"}
               if current else {}),
            "historical_0_3_conversion_engine": "tools/scap_upconvert_v003/convert_full_review.py",
            "version_independent_oval_ir": "tools/oval_semantic_ir.py",
        },
        "known_gaps": ([
            "The shared 0.3-derived 0.4 importer currently proves only two leaf shapes, not full OVAL conversion.",
            "This source snapshot is not an approved interoperable release or a conformance result.",
            "Publisher identity/trust, runtime semantic parity and dependency locking require separate gates.",
        ] if current else [
            "Historical tag source is preserved unchanged; modern developer guides were not present at this tag.",
            "This is a reconstructed source archive, not a replacement for historical published assets.",
            "Historical runtime dependencies, authoring/build outputs and scanner parity require separate verification.",
        ]),
        "files": records,
    }
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"scap-ng-{version}-toolchain-{commit[:12]}.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9, allowZip64=True) as dest:
        for path, (data, mode) in sorted(entries.items()):
            info = zipfile.ZipInfo(root + path, date_time=DATE)
            info.external_attr = mode
            info.compress_type = zipfile.ZIP_DEFLATED
            dest.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        info = zipfile.ZipInfo(root + MANIFEST_NAME, date_time=DATE)
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        dest.writestr(info, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    verify(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (out / "SHA256SUMS.txt").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    return target, manifest


def verify(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as zf:
        names = [name for name in zf.namelist() if not name.endswith("/")]
        roots = {name.split("/", 1)[0] for name in names}
        if len(roots) != 1:
            raise ValueError("toolchain archive has multiple roots")
        root = next(iter(roots)) + "/"
        manifest = json.loads(zf.read(root + MANIFEST_NAME))
        if manifest.get("format") != FORMAT:
            raise ValueError("unknown toolchain manifest format")
        version = manifest["version"]
        if not VERSION_RE.fullmatch(version) or root != f"scap-ng-{version}-toolchain/":
            raise ValueError("toolchain root/version mismatch")
        records = manifest["files"]
        expected = [root + record["path"] for record in records] + [root + MANIFEST_NAME]
        if len(expected) != len(set(expected)) or sorted(names) != sorted(expected):
            raise ValueError("toolchain file inventory differs from manifest")
        for record in records:
            path = record["path"]
            p = PurePosixPath(path)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError(f"unsafe toolchain path: {path}")
            data = zf.read(root + path)
            mode = zf.getinfo(root + path).external_attr
            if (len(data) != record["bytes"] or mode != record["unix_mode_attributes"]
                    or hashlib.sha256(data).hexdigest() != record["sha256"]):
                raise ValueError(f"toolchain member digest mismatch: {path}")
        return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--version")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--require-tag", action="store_true")
    ap.add_argument("--historical", action="store_true",
                    help="Reconstruct exact source from an older descriptive vX.Y.Z-* tag; do not require modern 0.4 guides")
    ap.add_argument("--verify", type=Path, help="Verify an existing toolchain ZIP without a Git checkout")
    args = ap.parse_args()
    if args.verify:
        if args.version or args.output_dir or args.require_tag or args.historical:
            ap.error("--verify is independent of build options")
        checked = verify(args.verify)
        print(json.dumps({"archive": str(args.verify), "source_commit": checked["source_commit"],
                          "files": len(checked["files"]), "verification": "pass"}))
        return
    if not args.version or not args.output_dir:
        ap.error("--version and --output-dir are required for building")
    target, manifest = build(args.repo, args.output_dir, args.version,
                             ref=args.ref, current=not args.historical,
                             require_tag=args.require_tag)
    print(json.dumps({"archive": str(target), "source_commit": manifest["source_commit"],
                      "files": len(manifest["files"]), "validation": manifest["validation_level"]}))


if __name__ == "__main__":
    main()
