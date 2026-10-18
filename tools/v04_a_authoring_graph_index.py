#!/usr/bin/env python3
"""#232/#239: independent YAML/JSON parsing into a stable *research* 0.4-A graph.

This produces a canonical parsed-authoring graph fingerprint, NOT a compiled,
validated, signed or executable .scapng package. Neither source format silently
changes a Benchmark's source assessment specification version.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import PurePosixPath
import zipfile

from test_v04_review_reference_graph import scan

KINDS = frozenset({"assessment", "rule", "benchmark", "applicability"})


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def read_authoring_archive(path, fmt):
    """Read only the requested source format: JSON uses json, never PyYAML."""
    if fmt not in ("json", "yaml"):
        raise ValueError("source format must be json or yaml")
    docs = {}
    with zipfile.ZipFile(path) as zf:
        if zf.testzip() is not None:
            raise ValueError("archive member CRC mismatch")
        for name in sorted(zf.namelist()):
            if not (name.startswith("authoring/") and name.endswith("." + fmt)):
                continue
            components = PurePosixPath(name).parts
            if ".." in components or name.startswith("/"):
                raise ValueError("unsafe authoring member name")
            if name in docs:
                raise ValueError(f"duplicate ZIP member: {name}")
            raw = zf.read(name)
            if len(raw) > 5_000_000:
                raise ValueError(f"oversized authoring document: {name}")
            try:
                if fmt == "json":
                    # JSON source must not rely on a YAML parser.
                    def unique_object_pairs(pairs):
                        obj = {}
                        for key, value in pairs:
                            if key in obj:
                                raise ValueError(f"duplicate JSON key {key!r}")
                            obj[key] = value
                        return obj
                    doc = json.loads(raw, object_pairs_hook=unique_object_pairs,
                                     parse_constant=lambda x: (_ for _ in ()).throw(
                                         ValueError(f"invalid JSON constant {x}")))
                else:
                    # Never use YAML as an alternative loader for JSON input.
                    import yaml
                    class UniqueSafeLoader(yaml.SafeLoader):
                        pass
                    def unique_mapping(loader, node):
                        items = {}
                        for k, v in node.value:
                            key = loader.construct_object(k, deep=True)
                            if not isinstance(key, str):
                                raise ValueError("nonstring/implicitly coerced YAML key")
                            if key in items:
                                raise ValueError(f"duplicate YAML key {key!r}")
                            items[key] = loader.construct_object(v, deep=True)
                        return items
                    UniqueSafeLoader.add_constructor(
                        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
                    doc = yaml.load(raw, Loader=UniqueSafeLoader)
                # JSON canonicalization enforces the same JSON-compatible
                # scalar model for both loaders; no silent datetime coercion.
                canonical_json(doc)
            except (ValueError, TypeError, UnicodeError) as error:
                raise ValueError(f"{name}: cannot parse unambiguously: {error}") from error
            if not isinstance(doc, dict) or len(doc) != 1:
                raise ValueError(f"{name}: expected exactly one native document root")
            docs[name] = doc
    if not docs:
        raise ValueError("no authoring documents in source archive")
    return docs


def graph_index(documents):
    """Fingerprint logical identities and parsed source, independent of filename."""
    if not isinstance(documents, dict) or not documents:
        raise ValueError("empty authoring graph")
    nodes = {}
    for filename, doc in documents.items():
        if not isinstance(doc, dict) or len(doc) != 1:
            raise ValueError(f"{filename}: expected single-root native document")
        kind, payload = next(iter(doc.items()))
        if kind not in KINDS or not isinstance(payload, dict):
            raise ValueError(f"{filename}: unsupported document kind")
        ident = payload.get("id")
        if not isinstance(ident, str) or not ident:
            raise ValueError(f"{filename}: missing logical {kind} id")
        key = (kind, ident)
        if key in nodes:
            raise ValueError(f"{filename}: duplicate logical identity {kind}/{ident}")
        nodes[key] = {
            "kind": kind,
            "id": ident,
            "sha256": sha256(canonical_json(doc)).hexdigest(),
        }

    counts, problems = scan(documents)
    if problems:
        raise ValueError(f"unresolved authoring graph: {problems[:8]!r}")

    records = [nodes[k] for k in sorted(nodes)]
    graph_digest = sha256(canonical_json(records)).hexdigest()
    # This is a *parsed-source equivalence* index, not an executable IR.
    return {
        "format": "scap-ng-a-parsed-authoring-index/0.1",
        "stage": "parsed_source_only_not_compiled",
        "graph_sha256": graph_digest,
        "nodes": records,
        "counts": counts,
        "limitations": [
            "static Rule/Assessment references only",
            "source assessment specifications and schema versions are not rewritten",
            "no capability execution or OVAL semantics proof",
            "no compiled scanner package or signing",
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", required=True)
    p.add_argument("--yaml-archive")
    p.add_argument("--index-json")
    args = p.parse_args()
    json_graph = graph_index(read_authoring_archive(args.json_archive, "json"))
    report = {
        "status": "SOURCE_GRAPH_VALIDATED_NOT_COMPILED",
        "json_sha256": json_graph["graph_sha256"],
        "counts": json_graph["counts"],
        "nodes": len(json_graph["nodes"]),
    }
    if args.yaml_archive:
        yaml_graph = graph_index(read_authoring_archive(args.yaml_archive, "yaml"))
        if yaml_graph["graph_sha256"] != json_graph["graph_sha256"]:
            j = {(x["kind"], x["id"]): x["sha256"] for x in json_graph["nodes"]}
            y = {(x["kind"], x["id"]): x["sha256"] for x in yaml_graph["nodes"]}
            difference = [str(key) for key in sorted(set(j) | set(y)) if j.get(key) != y.get(key)]
            raise ValueError(f"YAML/JSON parsed authoring graph differs: {difference[:12]}")
        report["yaml_sha256"] = yaml_graph["graph_sha256"]
        report["formats_equivalent"] = True
    if args.index_json:
        from pathlib import Path
        Path(args.index_json).write_bytes(json.dumps(json_graph, sort_keys=True, indent=2,
                                                     ensure_ascii=False).encode("utf-8") + b"\n")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
