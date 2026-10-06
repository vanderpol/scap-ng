"""Versioned native mappings; each schema version resolves only its local catalog."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def mapping_path(capability, version="0.2.0", root=ROOT):
    if not isinstance(capability, str) or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", capability):
        raise ValueError(f"Invalid capability identifier: {capability!r}")
    if version not in {"0.1.0", "0.2.0", "0.3.0"}:
        raise ValueError(f"Unsupported capability specification version: {version}")
    baseline_root = (
        root / f"schema/v{version}/capability-mappings/supported"
        if version in {"0.2.0", "0.3.0"}
        else root / "schema/v0.1.0/capability-mappings"
    )
    baseline = baseline_root / (capability + ".json")
    draft = root / f"schema/v{version}/capability-mappings/experimental" / (capability + ".json")
    if draft.is_file() and baseline.is_file():
        raise ValueError(f"Draft capability must not shadow the stable mapping: {capability}")
    if version in {"0.2.0", "0.3.0"} and draft.is_file():
        return draft
    if baseline.is_file():
        return baseline
    raise ValueError(f"Unknown capability for {version}: {capability}")


def load_mapping(capability, version="0.2.0", root=ROOT):
    path = mapping_path(capability, version, root)
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if mapping.get("capability") != capability:
        raise ValueError(f"Capability mapping identity differs: {capability}")
    experimental_root = root / f"schema/v{version}/capability-mappings/experimental"
    if path.is_relative_to(experimental_root) and mapping.get("specification_version") != version:
        raise ValueError(f"Experimental mapping requires explicit specification version: {capability}")
    return mapping


def draft_capabilities(root=ROOT, version="0.2.0"):
    if version not in {"0.2.0", "0.3.0"}:
        return frozenset()
    return frozenset(
        p.stem
        for p in (root / f"schema/v{version}/capability-mappings/experimental").glob("*.json")
    )


def mappings(version="0.2.0", root=ROOT):
    if version not in {"0.1.0", "0.2.0", "0.3.0"}:
        raise ValueError(f"Unsupported capability specification version: {version}")
    mapping_root = (
        root / f"schema/v{version}/capability-mappings/supported"
        if version in {"0.2.0", "0.3.0"}
        else root / "schema/v0.1.0/capability-mappings"
    )
    names = {p.stem for p in mapping_root.glob("*.json")}
    if version in {"0.2.0", "0.3.0"}:
        names.update(draft_capabilities(root, version))
    return [load_mapping(name, version, root) for name in sorted(names)]
