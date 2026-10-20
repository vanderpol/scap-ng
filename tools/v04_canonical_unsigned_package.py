#!/usr/bin/env python3
"""SCAP-NG 0.4.0 deterministic, UNSIGNED native-schema source packages (#232).

Stage between validated canonical source IR and *future* executable compiler.
Produces six independent Benchmark-scoped ZIPs with manifests that validate
against schema/v0.4.0/package-manifest.schema.json. These contain source AST,
NOT executable scanner instructions; do not name them .scapng.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

from v04_a_authoring_graph_index import canonical_json, graph_index
from v04_a_benchmark_choice_version_closure import inspect_edges, _folder
from v04_canonical_source_ir import compile_pair, decode_and_verify, _schema_validators, validate_docs

STAGE = "validated-unsigned-source-package-not-executable/0.1"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
EXPECTED_SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
MANIFEST_MEMBER = "META-INF/manifest.json"
SOURCE_FORMAT = "canonical-authoring-json-no-execution"


def _package_member(kind, ident):
    if kind not in ("benchmark", "rule", "assessment", "applicability"):
        raise ValueError("unsupported native source kind")
    if not isinstance(ident, str) or not ident:
        raise ValueError("missing native source identity")
    digest = sha256((kind + "\0" + ident).encode("utf-8")).hexdigest()
    return f"documents/{kind}/{digest}.json"


def _write_member(zf, name, data):
    info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=8)


def _manifest_schema():
    from jsonschema import Draft202012Validator
    path = Path(__file__).resolve().parents[1] / "schema/v0.4.0/package-manifest.schema.json"
    return Draft202012Validator(json.loads(path.read_text(encoding="utf-8")))


def partition_documents(documents):
    """Include local documents and complete shared library; omit other private STIGs.

    Full shared library is intentionally retained, even if some contents are
    unreferenced, until strict per-Benchmark dependency pruning is proven.
    """
    all_graph = graph_index(documents)
    overall_edges = inspect_edges(documents)
    if overall_edges["incompatible_edge_count"]:
        raise ValueError("incompatible 0.4.0 Benchmark Assessment specifications")
    benchmarks = {}
    for path, doc in documents.items():
        if "benchmark" in doc:
            folder = _folder(path)
            if folder in benchmarks:
                raise ValueError("duplicate Benchmark namespace: " + folder)
            benchmarks[folder] = path
    if not benchmarks:
        raise ValueError("no Benchmark source files")
    result = {}
    for folder, benchmark_path in sorted(benchmarks.items()):
        subset = {
            path: doc for path, doc in documents.items()
            if _folder(path) in (folder, "shared")
        }
        scoped = inspect_edges(subset)
        if scoped["incompatible_edge_count"] or len(scoped["benchmarks"]) != 1:
            raise ValueError("unclosed Benchmark Assessment choices: " + folder)
        bench = documents[benchmark_path]["benchmark"]
        if bench["assessment_specifications"] != [EXPECTED_SPEC]:
            raise ValueError("unexpected Benchmark specification: " + folder)
        rule_ids = {doc["rule"]["id"] for doc in subset.values() if "rule" in doc}
        benchmark_rules = bench.get("rules")
        if not isinstance(benchmark_rules, list) or set(benchmark_rules) != rule_ids or len(benchmark_rules) != len(rule_ids):
            raise ValueError("Benchmark Rule list does not equal packaged Rules: " + folder)
        graph_index(subset)
        result[folder] = subset
    if all_graph["counts"]["documents"] != len(documents):
        raise ValueError("graph lost source documents")
    return result


def build_package(documents, *, validate_schema=True):
    if not isinstance(documents, dict):
        raise ValueError("package requires source documents")
    graph = graph_index(documents)
    edges = inspect_edges(documents)
    if edges["incompatible_edge_count"]:
        raise ValueError("incompatible Benchmark Assessment specification/Rule choices")
    if len(edges["benchmarks"]) != 1:
        raise ValueError("package requires exactly one complete Benchmark")
    if validate_schema:
        validate_docs(documents, _schema_validators(Path(__file__).resolve().parents[1] / "schema/v0.4.0"))
    rows, contents = {}, {}
    kinds = {"benchmark": "benchmark", "rule": "rule", "assessment": "assessment", "applicability": "applicability_catalog"}
    benchmark = next(d["benchmark"] for d in documents.values() if "benchmark" in d)
    if benchmark.get("assessment_specifications") != [EXPECTED_SPEC]:
        raise ValueError("package expects canonical 0.4.0 Assessment declaration")
    for path, doc in sorted(documents.items()):
        kind, body = next(iter(doc.items()))
        ident = body["id"]
        name = _package_member(kind, ident)
        if name in contents:
            raise ValueError("duplicate document member " + name)
        raw = canonical_json(doc)
        contents[name] = raw
        rows[f"{kind}:{ident}"] = {
            "type": kinds[kind], "version": body.get("version"),
            "path": name, "sha256": sha256(raw).hexdigest(), "size": len(raw),
        }
    entrypoint = _package_member("benchmark", benchmark["id"])
    manifest = {
        "format": "scap-ng-package-manifest",
        "format_version": "0.4.0",
        "benchmark_id": benchmark["id"],
        "benchmark_version": benchmark["version"],
        "entrypoint": entrypoint,
        "objects": rows,
        "integrity": {"algorithm": "sha-256", "unexpected_members": "reject"},
        "build_provenance": {
            "stage": STAGE,
            "source_format": SOURCE_FORMAT,
            "scope": "complete-benchmark-plus-all-shared-assessments",
            "source_graph_sha256": graph["graph_sha256"],
            "rule_choice_links": edges["counts"]["choice_links"],
            "source_documents": len(documents),
            "executable_compiler_complete": False,
            "scanner_evaluation_verified": False,
            "publisher_signature_verified": False,
        },
        "signature": {"format": None, "path": None, "certificate_path": None, "trust": None},
    }
    _manifest_schema().validate(manifest)
    contents[MANIFEST_MEMBER] = canonical_json(manifest)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as zf:
        for name, raw in sorted(contents.items()):
            _write_member(zf, name, raw)
    return out.getvalue(), manifest


def _strict_json(raw):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("duplicate JSON key: " + k)
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("non-finite JSON: " + x)))


def verify_package(raw, *, validate_schema=True):
    """Independently decode, hash-check, reconstruct and revalidate full graph."""
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        if zf.testzip() is not None:
            raise ValueError("corrupt ZIP CRC")
        names = zf.namelist()
        if len(names) != len(set(names)) or MANIFEST_MEMBER not in names:
            raise ValueError("duplicate members or missing manifest")
        if any(x != str(PurePosixPath(x)) or ".." in PurePosixPath(x).parts or "\\" in x for x in names):
            raise ValueError("unsafe package member name")
        manifest_raw = zf.read(MANIFEST_MEMBER)
        manifest = _strict_json(manifest_raw)
        if canonical_json(manifest) != manifest_raw:
            raise ValueError("noncanonical manifest serialization")
        _manifest_schema().validate(manifest)
        prov = manifest["build_provenance"]
        if (prov.get("stage") != STAGE or prov.get("source_format") != SOURCE_FORMAT
                or prov.get("executable_compiler_complete") is not False
                or prov.get("scanner_evaluation_verified") is not False
                or prov.get("publisher_signature_verified") is not False):
            raise ValueError("unknown or falsely executable source package")
        if any(value is not None for value in manifest["signature"].values()):
            raise ValueError("source package may not advertise a signature")
        expected = {MANIFEST_MEMBER}
        docs = {}
        for key, row in manifest["objects"].items():
            kind, sep, ident = key.partition(":")
            if not sep or row["type"] != {"benchmark":"benchmark","rule":"rule","assessment":"assessment","applicability":"applicability_catalog"}.get(kind):
                raise ValueError("member kind mismatch")
            member = _package_member(kind, ident)
            if member != row["path"] or member in expected:
                raise ValueError("duplicate or changed member identity")
            expected.add(member)
            if member not in names:
                raise ValueError("missing package member: " + member)
            content = zf.read(member)
            if len(content) != row["size"] or sha256(content).hexdigest() != row["sha256"]:
                raise ValueError("member digest mismatch: " + member)
            doc = _strict_json(content)
            if canonical_json(doc) != content or list(doc) != [kind] or doc[kind]["id"] != ident:
                raise ValueError("document or identity mismatch")
            if row["version"] != doc[kind].get("version"):
                raise ValueError("document version mismatch")
            docs[f"authoring/{manifest['benchmark_id']}/{member}"] = doc
        if expected != set(names):
            raise ValueError("extra unlisted member(s)")
    bench = next((v["benchmark"] for v in docs.values() if "benchmark" in v), None)
    if bench is None or bench["id"] != manifest["benchmark_id"] or manifest["entrypoint"] != _package_member("benchmark", bench["id"]):
        raise ValueError("incorrect Benchmark entrypoint")
    if bench["version"] != manifest["benchmark_version"]:
        raise ValueError("wrong Benchmark version")
    graph = graph_index(docs)
    edges = inspect_edges(docs)
    if edges["incompatible_edge_count"] or len(edges["benchmarks"]) != 1:
        raise ValueError("broken packaged Assessment choice closure")
    if (graph["graph_sha256"] != prov["source_graph_sha256"]
            or len(docs) != prov["source_documents"]
            or edges["counts"]["choice_links"] != prov["rule_choice_links"]):
        raise ValueError("manifest graph/count mismatches")
    if validate_schema:
        validate_docs(docs, _schema_validators(Path(__file__).resolve().parents[1] / "schema/v0.4.0"))
    return {"status": "VALIDATED_UNSIGNED_SOURCE_PACKAGE_NOT_EXECUTABLE",
            "benchmark": bench["id"], "documents": len(docs),
            "rule_choice_links": edges["counts"]["choice_links"],
            "source_graph_sha256": graph["graph_sha256"],
            "scanner_evaluated": False, "signature_verified": False}


def package_pair(json_zip, yaml_zip, *, validate_schema=True):
    ir_bytes, preflight = compile_pair(json_zip, yaml_zip, validate_schema=validate_schema)
    if preflight["version_conflicting_choice_links"]:
        raise ValueError("unresolved Benchmark version conflict")
    docs = decode_and_verify(_strict_json(ir_bytes))
    folders = partition_documents(docs)
    packages, reports = {}, {}
    for folder, subset in sorted(folders.items()):
        packed, _ = build_package(subset, validate_schema=validate_schema)
        independently_verified = verify_package(packed, validate_schema=validate_schema)
        packages[folder] = packed
        reports[folder] = {**independently_verified, "sha256": sha256(packed).hexdigest(),
                           "bytes": len(packed)}
    return packages, {"status": "SIX_BENCHMARK_UNSIGNED_SOURCE_PACKAGES_NOT_EXECUTABLE",
                      "source_ir_sha256": sha256(ir_bytes).hexdigest(),
                      "benchmarks": reports, "native_compiler_complete": False,
                      "signed": False, "scanner_parity": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", type=Path, required=True)
    p.add_argument("--yaml-archive", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--assert-six", action="store_true")
    args = p.parse_args()
    packages, report = package_pair(args.json_archive, args.yaml_archive)
    if args.assert_six and len(packages) != 6:
        raise ValueError(f"expected six Benchmark packages; found {len(packages)}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, raw in sorted(packages.items()):
        (args.out_dir / (name + ".source-preview.zip")).write_bytes(raw)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
