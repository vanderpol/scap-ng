"""Index canonical schema reachability and normative inputs without reading cases."""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from audit_schema_documentation import reachable_schema_locations, walk
from schema_documentation import SchemaStore

# Public file and transport entry points. Bare schema helpers inherit the status
# of the public entry points that reference them. The generated Assessment
# language overlay is reached from assessment.schema.json.
ENTRY_POINTS = {
    "authoring": (
        "applicability", "assessment", "benchmark", "organizational-input",
        "rule", "tailoring",
    ),
    "packaging": ("package-manifest", "result-package-manifest"),
    "results": (
        "assessment-result", "assessment-result-set", "benchmark-result",
        "item-report", "manual-assessment-result", "scan-result",
    ),
}

DECISIONS = {
    "canonical_not": "https://github.com/vanderpol/scap-ng/issues/87#issuecomment-7066443606",
    "object_before_require": "https://github.com/vanderpol/scap-ng/issues/95",
    "variable_state_identity_and_cmdlet_wildcard":
        "https://github.com/vanderpol/scap-ng/issues/87#issuecomment-7078907962",
    "applicability_negation":
        "https://github.com/vanderpol/scap-ng/issues/87#issuecomment-7079517697",
    "esxi_scope": "https://github.com/vanderpol/scap-ng/issues/86",
    "for_each_deferred": "https://github.com/vanderpol/scap-ng/issues/76",
}


def inventory(root, schemas):
    documents = {schema["$id"]: schema for schema in schemas.values()}
    if len(documents) != len(schemas):
        raise ValueError("Duplicate schema identity in the canonical closure")
    store = SchemaStore(documents)
    by_entry = {}
    for kind, names in ENTRY_POINTS.items():
        for name in names:
            path = f"schema/{name}.schema.json"
            uri = schemas[path]["$id"]
            by_entry[name] = (kind, reachable_schema_locations(store, uri))

    resources = {}
    inactive = {}
    for source, schema in schemas.items():
        uri = schema["$id"]
        locations = {uri + "#" + pointer for pointer, *_ in walk(schema)}
        roots = {}
        reached = set()
        for entry, (_, entry_locations) in by_entry.items():
            intersection = locations & entry_locations
            if intersection:
                roots[entry] = len(intersection)
                reached.update(intersection)
        resources[source] = {"declared_nodes": len(locations), "entry_points": roots}
        # Keep pointers for unreachable nodes, including definitions hidden
        # within otherwise reachable overlays, without duplicating the matrix.
        unreachable = sorted(location[len(uri) + 1:] for location in locations - reached)
        if unreachable:
            inactive[source] = unreachable

    authored = by_entry["assessment"][1]
    controls = {"foreach", "for_each", "foreach_binding", "foreach_selector_binding"}
    if any(location.rsplit("/", 1)[-1] in controls for location in authored):
        raise ValueError("Deferred for_each grammar is reachable from active Assessment entry")

    docs = sorted(
        path for directory in ("specification", "docs/contracts", "docs/semantics")
        for path in (root / directory).glob("*.md")
    )
    return {
        "qualification": "Syntactic schema reachability, including validation guards. "
                         "Executable semantics and runtime receipts are separate.",
        "entry_points": {entry: kind for entry, (kind, _) in by_entry.items()},
        "resources": resources,
        "unreachable_schema_nodes": inactive,
        "normative_document_inputs": {
            path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in docs
        },
        "issue_decisions": DECISIONS,
    }
