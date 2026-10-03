"""Versioned native mappings; 0.2.0 additions never enter the 0.1.0 catalog."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def mapping_path(capability, version="0.2.0", root=ROOT):
    if not isinstance(capability, str) or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", capability):
        raise ValueError(f"Invalid capability identifier: {capability!r}")
    if version not in {"0.1.0", "0.2.0"}:
        raise ValueError(f"Unsupported capability specification version: {version}")
    baseline = root / "schema/v0.1.0/capability-mappings" / (capability + ".json")
    draft = root / "schema/v0.2.0/capability-mappings" / (capability + ".json")
    if draft.is_file() and baseline.is_file():
        raise ValueError(f"Draft capability must not shadow the stable mapping: {capability}")
    if version == "0.2.0" and draft.is_file():
        return draft
    if baseline.is_file():
        return baseline
    raise ValueError(f"Unknown capability for {version}: {capability}")


def load_mapping(capability, version="0.2.0", root=ROOT):
    path = mapping_path(capability, version, root)
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if mapping.get("capability") != capability:
        raise ValueError(f"Capability mapping identity differs: {capability}")
    if path.parent.parent.name == "v0.2.0" and mapping.get("specification_version") != "0.2.0":
        raise ValueError(f"Draft mapping requires explicit specification version: {capability}")
    return mapping


def draft_capabilities(root=ROOT):
    return frozenset(p.stem for p in (root / "schema/v0.2.0/capability-mappings").glob("*.json"))


def mappings(version="0.2.0", root=ROOT):
    if version not in {"0.1.0", "0.2.0"}:
        raise ValueError(f"Unsupported capability specification version: {version}")
    names = {p.stem for p in (root / "schema/v0.1.0/capability-mappings").glob("*.json")}
    if version == "0.2.0":
        names.update(draft_capabilities(root))
    return [load_mapping(name, version, root) for name in sorted(names)]
