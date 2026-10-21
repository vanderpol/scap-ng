#!/usr/bin/env python3
"""Source-invertible flat-Object authoring and hybrid YAML six-STIG preview.

Only generic Object select/collect wrappers are moved; capability-defined
native selectors and acquisition parameters, Set, Filter and all predicate
semantics are preserved. NOT independent scanner parity.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import yaml

RESERVED = frozenset({"filters", "set", "capability", "object", "object_title",
                      "traversal", "for_each", "foreach", "behaviors"})


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode()).hexdigest()


def load_catalog(directory: Path):
    catalog = {}
    paths = sorted(directory.glob("*.json"))
    if len(paths) != 100:
        raise ValueError(f"Expected 100 supported mappings, found {len(paths)}")
    for path in paths:
        mapping = json.loads(path.read_text(encoding="utf-8"))
        cap, native = mapping["capability"], mapping["native"]
        selectors = set(native.get("selector_map", {}).values())
        parameters = set(native.get("collection_parameters", {}))
        conflicting = (selectors & parameters) | ((selectors | parameters) & RESERVED)
        if conflicting:
            raise ValueError(f"{cap}: selector/parameter/control collision {sorted(conflicting)}")
        catalog[cap] = {"selectors": selectors, "parameters": parameters}
    return catalog


def resolve_object(obj, cap, catalog, route, edits):
    """Move verified legacy Object wrapper keys into native Object field slots."""
    effective = obj.get("capability", cap)
    if effective not in catalog:
        if "select" in obj or "collect" in obj:
            raise ValueError(f"{route}: cannot classify Object capability {effective!r}")
        return effective
    fields = catalog[effective]
    extracted = {}
    for wrapper, category in (("select", "selectors"), ("collect", "parameters")):
        if wrapper not in obj:
            continue
        value = obj[wrapper]
        if not isinstance(value, dict) or not value:
            raise ValueError(f"{route}: nonmapping/empty Object {wrapper}")
        # A native windows.cmdlet parameter named 'select' is under
        # legacy collect, not the generic Object select container.
        if wrapper == "select" and not fields["selectors"]:
            raise ValueError(f"{route}: ambiguous or unsupported generic select")
        unknown = set(value) - fields[category]
        if unknown:
            raise ValueError(f"{route}: {effective} {wrapper}: unrecognized {sorted(unknown)}")
        extracted[wrapper] = deepcopy(value)
    if not extracted:
        return effective
    introduced = {key for val in extracted.values() for key in val}
    existing = set(obj) - set(extracted)
    collisions = existing & introduced
    if ("select" in extracted and "collect" in extracted
            and (set(extracted["select"]) & set(extracted["collect"]))):
        collisions |= set(extracted["select"]) & set(extracted["collect"])
    if collisions:
        raise ValueError(f"{route}: field name collision {sorted(collisions)}")
    before = digest(obj)
    for wrapper, value in extracted.items():
        obj.pop(wrapper)
        obj.update(value)
    edits.append({"path": list(route), "capability": effective,
                  "old_wrappers": extracted,
                  "after": digest(obj), "before": before})
    return effective


def flatten_document(document, catalog):
    source, doc = deepcopy(document), deepcopy(document)
    changes = []

    def walk(node, cap=None, route=()):
        if isinstance(node, list):
            for i, child in enumerate(node):
                walk(child, cap, route + (i,))
        elif isinstance(node, dict):
            cap = node.get("capability", cap)
            for key, value in node.items():
                if key == "object" and isinstance(value, dict):
                    effective = resolve_object(value, cap, catalog, route + (key,), changes)
                    walk(value, effective, route + (key,))
                elif key in ("objects", "shared_objects") and isinstance(value, dict):
                    for obj_name, obj in value.items():
                        if isinstance(obj, dict):
                            effective = resolve_object(obj, obj.get("capability"), catalog,
                                                       route + (key, obj_name), changes)
                            walk(obj, effective, route + (key, obj_name))
                else:
                    walk(value, cap, route + (key,))
    walk(doc)
    proof = {"before": digest(source), "after": digest(doc), "edits": changes}
    if restore_document(doc, proof) != source:
        raise ValueError("Source reconstruction failed")
    return doc, proof


def restore_document(document, proof):
    if digest(document) != proof["after"]:
        raise ValueError("Flat Object graph modified after conversion")
    restored = deepcopy(document)
    for edit in reversed(proof["edits"]):
        node = restored
        for key in edit["path"]:
            node = node[key]
        if digest(node) != edit["after"]:
            raise ValueError(f"Object modified at {edit['path']}")
        for wrapper, value in edit["old_wrappers"].items():
            for field in value:
                if field not in node or node[field] != value[field]:
                    raise ValueError(f"Cannot reconstruct selector/parameter {field}")
                node.pop(field)
            node[wrapper] = deepcopy(value)
        if digest(node) != edit["before"]:
            raise ValueError(f"Cannot reconstruct original Object at {edit['path']}")
    if digest(restored) != proof["before"]:
        raise ValueError("Cannot reconstruct original document")
    return restored


class FlowMap(dict):
    pass


class HybridDumper(yaml.SafeDumper):
    pass


def represent_flow(dumper, value):
    return dumper.represent_mapping("tag:yaml.org,2002:map", value.items(),
                                    flow_style=True)


HybridDumper.add_representer(FlowMap, represent_flow)


def hybridize(node, key=None):
    if isinstance(node, list):
        return [hybridize(v) for v in node]
    if not isinstance(node, dict):
        return node
    items = list(node.items())
    if "fields" in node and "field_requirement" in node:
        items.sort(key=lambda entry: 0 if entry[0] == "field_requirement" else 1)
    if key == "require" and "field_requirement" in node:
        items.sort(key=lambda entry: 0 if entry[0] == "items" else 1 if entry[0] == "field_requirement" else 2)
    mapped = {k: hybridize(v, k) for k, v in items}
    comparator = (len(node) == 1 and next(iter(node), "") in {
        "equals", "not_equal", "case_insensitive_equals", "case_insensitive_not_equal",
        "matches_regex", "pattern_match", "version_equals", "version_greater_than",
        "version_greater_than_or_equal", "greater_than", "greater_than_or_equal",
        "less_than", "less_than_or_equal", "bitwise_and", "bitwise_or",
    } and not isinstance(next(iter(node.values())), (list, dict)))
    simple_fields = key == "fields" and bool(mapped) and all(
        isinstance(v, FlowMap) for v in mapped.values())
    simple_object = key == "object" and bool(mapped) and all(
        isinstance(v, FlowMap) for v in mapped.values())
    if comparator or simple_fields or simple_object:
        approx = len(json.dumps(mapped, ensure_ascii=False))
        limit = 140 if simple_fields else 180 if simple_object else 90
        if approx <= limit:
            return FlowMap(mapped)
    return mapped


def dump_hybrid(document):
    source = yaml.dump(hybridize(document), Dumper=HybridDumper,
                       sort_keys=False, allow_unicode=True, width=160)
    if yaml.safe_load(source) != document:
        raise ValueError("Hybrid YAML differs from its parsed JSON structure")
    return source


def write_zip(path, members):
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
        for name, data in sorted(members.items()):
            info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            zf.writestr(info, data.encode("utf-8"))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-json", type=Path, required=True)
    cli.add_argument("--candidate-json", type=Path, required=True)
    cli.add_argument("--candidate-yaml", type=Path, required=True)
    cli.add_argument("--proof", type=Path, required=True)
    cli.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] /
                     "schema/v0.4.0/capability-mappings/supported")
    args = cli.parse_args()
    from v04_a_authoring_graph_index import read_authoring_archive
    catalog = load_catalog(args.catalog)
    docs = read_authoring_archive(args.source_json, "json")
    per_cap, per_wrapper, results, inverse = Counter(), Counter(), {}, {}
    for name, source in sorted(docs.items()):
        candidate, proof = flatten_document(source, catalog)
        results[name] = candidate
        if proof["edits"]:
            inverse[name] = proof
        for edit in proof["edits"]:
            per_cap[edit["capability"]] += 1
            per_wrapper.update(edit["old_wrappers"].keys())
    json_members = {name: json.dumps(doc, ensure_ascii=False, sort_keys=True,
                                     indent=2) + "\n" for name, doc in results.items()}
    yaml_members = {name.removesuffix(".json") + ".yaml": dump_hybrid(doc)
                    for name, doc in results.items()}
    write_zip(args.candidate_json, json_members)
    write_zip(args.candidate_yaml, yaml_members)
    report = {"status": "FLAT_OBJECT_SOURCE_INVERSE_PASS_NO_NATIVE_SCANNER_PARITY",
              "documents": len(results), "changed_documents": len(inverse),
              "changed_objects": sum(per_cap.values()),
              "wrapper_types": dict(sorted(per_wrapper.items())),
              "capabilities": dict(sorted(per_cap.items())),
              "catalog_size": len(catalog),
              "source_zip_sha256": sha256(args.source_json.read_bytes()).hexdigest(),
              "candidate_json_sha256": sha256(args.candidate_json.read_bytes()).hexdigest(),
              "candidate_yaml_sha256": sha256(args.candidate_yaml.read_bytes()).hexdigest(),
              "source_inverse": inverse,
              "native_schema_promoted": False, "scanner_parity_proven": False}
    args.proof.parent.mkdir(parents=True, exist_ok=True)
    args.proof.write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                    sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "source_inverse"}, indent=2))


if __name__ == "__main__":
    main()
