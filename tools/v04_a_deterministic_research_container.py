#!/usr/bin/env python3
"""#232/#239: deterministic UNSIGNED 0.4-A research content graph archive.

NOT a normative .scapng bundle. Runs only after independently parsing input,
resolving every Rule choice, and constructing an unapproved isolated
Benchmark-spec declaration preview. No compiled capability IR or scanner.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import io
import json
from pathlib import PurePosixPath
import zipfile

from v04_a_authoring_graph_index import canonical_json, graph_index, read_authoring_archive
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_a_benchmark_spec_migration_preview import build_preview

STAGE = "research-only-0.4-a-deterministic-authoring-container/0.1"
MAGIC = "UNSIGNED_NOT_EXECUTABLE_NOT_APPROVED"
TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _logical_source(path):
    name = str(PurePosixPath(path))
    if not name.startswith("authoring/") or ".." in PurePosixPath(name).parts:
        raise ValueError(f"unsafe or unknown source path: {path}")
    for ext in (".json", ".yaml", ".yml"):
        if name.endswith(ext):
            return name[:-len(ext)]
    raise ValueError(f"unrecognized source extension: {path}")


def _artifact_name(kind, identity):
    # Content location is independent of source filenames and cannot traverse.
    digest = sha256(identity.encode("utf-8")).hexdigest()
    return f"documents/{kind}/{digest}.json"


def _zip_entry(archive, path, data):
    info = zipfile.ZipInfo(filename=path, date_time=TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=8)


def create_research_container(documents):
    report, staged = build_preview(documents)
    if report["candidate_incompatible_edges"] != 0 or not report["preservation_proved"]:
        raise ValueError("unresolved Rule contract or source-preservation failure")
    graph = graph_index(staged)
    items, payloads = [], {}
    for path, doc in staged.items():
        kind, body = next(iter(doc.items()))
        identity = body["id"]
        archive_path = _artifact_name(kind, identity)
        content = canonical_json(doc)
        if archive_path in payloads:
            raise ValueError("hash collision or duplicate logical identity: " + archive_path)
        payloads[archive_path] = content
        items.append({
            "kind": kind, "id": identity, "member": archive_path,
            "logical_source": _logical_source(path),
            "sha256": sha256(content).hexdigest(), "size": len(content),
        })
    items.sort(key=lambda x: (x["kind"], x["id"]))
    manifest = {
        "stage": STAGE,
        "build_status": MAGIC,
        "authoring_spec_approval": False,
        "migration_policy_approval": False,
        "source_graph_sha256": report["source_graph_sha256"],
        "staged_graph_sha256": graph["graph_sha256"],
        "documents": items,
        "counts": graph["counts"],
        "required_owner_decisions": [
            "final 0.4-A grammar scope and vocabulary",
            "Benchmark specification declaration policy",
        ],
        "no_source_mutation": True,
        "not_verified": [
            "native executable 0.4 compiler semantics", "manifest signature",
            "OVAL/scanner evaluation parity", "publisher trust",
        ],
    }
    contents = {"manifest.json": canonical_json(manifest)}
    contents.update(payloads)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for path in sorted(contents):
            _zip_entry(archive, path, contents[path])
    return stream.getvalue(), manifest


def verify_research_container(raw):
    """Independently read every archive member, rederive source/graph references."""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError("corrupted research container")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP member names")
        if "manifest.json" not in names:
            raise ValueError("missing research manifest")
        # Manifest flags, graph hashes, and provenance must be unambiguous.
        # Reject duplicate keys at every nesting level and non-JSON constants.
        manifest_bytes = archive.read("manifest.json")
        def unique_manifest_pairs(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError(f"duplicate research manifest key {key!r}")
                obj[key] = value
            return obj
        manifest = json.loads(
            manifest_bytes,
            object_pairs_hook=unique_manifest_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"invalid research manifest JSON constant {token}")),
        )
        if canonical_json(manifest) != manifest_bytes:
            raise ValueError("noncanonical research manifest")
        if (manifest.get("stage") != STAGE or manifest.get("build_status") != MAGIC
                or manifest.get("authoring_spec_approval") is not False
                or manifest.get("migration_policy_approval") is not False):
            raise ValueError("not an unapproved 0.4-A research container")
        docs = {}
        expected_names = {"manifest.json"}
        for record in manifest["documents"]:
            kind, ident, member = record["kind"], record["id"], record["member"]
            if member != _artifact_name(kind, ident) or member in expected_names:
                raise ValueError("untrusted member name / identity collision")
            expected_names.add(member)
            if member not in names:
                raise ValueError("missing manifest-named document member")
            body = archive.read(member)
            if sha256(body).hexdigest() != record["sha256"] or len(body) != record["size"]:
                raise ValueError("member digest or size mismatch")
            document = json.loads(body)
            if canonical_json(document) != body:
                raise ValueError("noncanonical member content")
            if list(document) != [kind] or document[kind].get("id") != ident:
                raise ValueError("document identity mismatch")
            logical = record["logical_source"]
            if _logical_source(logical + ".json") != logical:
                raise ValueError("invalid authoring source logical path")
            path = logical + ".json"
            if path in docs:
                raise ValueError("duplicate logical source path")
            docs[path] = document
        if set(names) != expected_names:
            raise ValueError("unexpected extra research container member")
    graph = graph_index(docs)
    edges = inspect_edges(docs)
    if edges["incompatible_edge_count"]:
        raise ValueError("broken per-Benchmark version declaration closure")
    if (graph["graph_sha256"] != manifest["staged_graph_sha256"]
            or graph["counts"] != manifest["counts"]):
        raise ValueError("staged graph mismatch or forged totals")
    if manifest["no_source_mutation"] is not True:
        raise ValueError("invalid source preservation declaration")
    return {
        "status": "UNSIGNED_RESEARCH_CONTAINER_VERIFIED_NOT_EXECUTABLE",
        "member_count": len(docs), "graph_sha256": graph["graph_sha256"],
        "choice_links": edges["counts"]["choice_links"],
        "signatures_verified": False,
        "native_compiler_completed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", required=True)
    p.add_argument("--yaml-archive")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    from pathlib import Path
    raw, manifest = create_research_container(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        other, other_manifest = create_research_container(
            read_authoring_archive(args.yaml_archive, "yaml"))
        if other != raw or other_manifest != manifest:
            raise ValueError("independent YAML and JSON package bytes differ")
    verified = verify_research_container(raw)
    Path(args.out).write_bytes(raw)
    print(json.dumps({
        **verified, "output": args.out, "archive_bytes": len(raw),
        "archive_sha256": sha256(raw).hexdigest(),
        "source_graph_sha256": manifest["source_graph_sha256"],
        "format_parity": "PASS" if args.yaml_archive else "NOT_CHECKED",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
