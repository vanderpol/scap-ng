#!/usr/bin/env python3
"""Generate a small, clean, semantically exact SCAP-NG 003 RHEL 9 review slice.

Only source paths fully understood by this checkpoint are emitted. Legacy
lineage is written separately under evidence/.
"""

from __future__ import annotations
import hashlib, json, os, re, shutil, tempfile, urllib.request, zipfile
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

SOURCE_URL = (
    "https://raw.githubusercontent.com/niwc-atlantic/scap-content-library/main/Current/"
    "U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip"
)
ROOT = Path(__file__).resolve().parents[2]

_DEPRECATED_TEST_TYPES = None
_OVAL_DEFINITION_ELEMENTS = None

def oval_definition_elements():
    """Return concrete top-level OVAL Definition element QNames from 5.12.3 XSDs.

    This provides a schema-derived vocabulary boundary. Publisher/custom
    extensions SHALL be diagnosed explicitly instead of being silently treated
    as standard OVAL merely because their local name ends in _test/_object/_state.
    """
    global _OVAL_DEFINITION_ELEMENTS
    if _OVAL_DEFINITION_ELEMENTS is not None:
        return _OVAL_DEFINITION_ELEMENTS

    schema_override = os.environ.get("SCAP_NG_OVAL_SCHEMA_ROOT")
    schema_root = (
        Path(schema_override)
        if schema_override
        else ROOT / "third_party" / "scap-1.4-schemas" / "oval_5.12.3"
    )
    elements = set()
    for path in sorted(schema_root.glob("*-definitions-schema.xsd")):
        try:
            xroot = ET.parse(path).getroot()
        except Exception:
            continue
        target = xroot.get("targetNamespace") or ""
        for child in list(xroot):
            if local(child.tag) != "element" or not child.get("name"):
                continue
            name = child.get("name")
            if name.endswith(("_test", "_object", "_state")):
                elements.add((target, name))

    _OVAL_DEFINITION_ELEMENTS = frozenset(elements)
    return _OVAL_DEFINITION_ELEMENTS

def deprecated_test_types():
    """Return effective deprecated OVAL test QNames from bundled 5.12.3 schemas.

    Explicit support overrides may reinstate schema-deprecated tests. Everything
    else carrying oval:deprecated_info is rejected from native SCAP-NG.
    """
    global _DEPRECATED_TEST_TYPES
    if _DEPRECATED_TEST_TYPES is not None:
        return _DEPRECATED_TEST_TYPES

    schema_root = ROOT / "third_party" / "scap-1.4-schemas" / "oval_5.12.3"
    deprecated = set()
    for path in sorted(schema_root.rglob("*.xsd")):
        try:
            xroot = ET.parse(path).getroot()
        except Exception:
            continue
        target = xroot.get("targetNamespace") or ""
        for child in list(xroot):
            if local(child.tag) != "element" or not child.get("name"):
                continue
            name = child.get("name")
            if not name.endswith("_test"):
                continue
            if any(local(node.tag) == "deprecated_info" for node in child.iter()):
                deprecated.add((target, name))

    override_path = ROOT / "research" / "iterations" / "001" / "oval-test-support-overrides.json"
    if override_path.exists():
        try:
            doc = json.loads(override_path.read_text(encoding="utf-8"))
            for row in doc.get("overrides", []):
                if row.get("effective_status") != "supported_reinstated":
                    continue
                qualified = row.get("qualified_name") or ""
                namespace, sep, name = qualified.rpartition("#")
                if sep:
                    deprecated.discard((namespace, name))
        except Exception:
            pass

    _DEPRECATED_TEST_TYPES = frozenset(deprecated)
    return _DEPRECATED_TEST_TYPES

FULL_MODE = os.environ.get("SCAP_NG_V003_MODE", "slice").lower() == "full"
BUILD_NAME = "rhel9-full" if FULL_MODE else "rhel9-review-slice"
OUT = ROOT / "research/iterations/003/source/split-rule-assessment" / BUILD_NAME
LEGACY_OUT = ROOT / "research/iterations/003/source/split-policy-assessment" / BUILD_NAME
EVIDENCE = ROOT / "research/iterations/003/evidence" / BUILD_NAME
PACKAGE_OUT = ROOT / "research/iterations/003/packages"
PACKAGE_NAME = f"{BUILD_NAME}.scap-ng.zip"
XCCDF = "http://checklists.nist.gov/xccdf/1.2"
NS = {"x": XCCDF}

def local(tag): return tag.rsplit("}", 1)[-1]
def text(node):
    if node is None: return None
    s = " ".join("".join(node.itertext()).split())
    return s or None

def oval_value_text(node):
    """Return OVAL simple-content text without whitespace normalization."""
    if node is None:
        return None
    value = "".join(node.itertext())
    return value
def safe_id(s): return re.sub(r"[^A-Za-z0-9_.-]+", "-", s.strip()).strip("-")
def semantic_id(value, fallback):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    stop = {"the","a","an","is","are","must","be","of","to","for","with","and"}
    words = [w for w in slug.split("-") if w and w not in stop]
    return "-".join(words[:10]) or fallback
def node_title(node):
    return ((node.get("comment") or "").strip() or None) if node is not None else None

# Preserve the OVAL Definition metadata title as optional Assessment descriptive metadata.
def oval_definition_title(definition):
    if definition is None:
        return None
    metadata = next((n for n in definition if local(n.tag) == "metadata"), None)
    if metadata is None:
        return None
    title_node = next((n for n in metadata if local(n.tag) == "title"), None)
    return text(title_node)
def sha256(data): return hashlib.sha256(data).hexdigest()
def write_yaml(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    class Dumper(yaml.SafeDumper):
        def ignore_aliases(self, data): return True
    path.write_text(yaml.dump(obj, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

DIAGNOSTIC_LEVELS = ("info", "warn", "error", "fatal")

def add_diagnostic(diagnostics, severity, code, message, **context):
    if severity not in DIAGNOSTIC_LEVELS:
        raise ValueError(f"invalid diagnostic severity: {severity}")
    item = {
        "severity": severity,
        "code": code,
        "message": message,
    }
    item.update({k: v for k, v in context.items() if v is not None})
    diagnostics.append(item)

def diagnostic_summary(diagnostics):
    counts = {level: 0 for level in DIAGNOSTIC_LEVELS}
    for item in diagnostics:
        counts[item["severity"]] += 1
    return {
        "counts": counts,
        "total": sum(counts.values()),
        "highest_severity": next(
            (level for level in reversed(DIAGNOSTIC_LEVELS) if counts[level]),
            None,
        ),
    }

def oval_descriptive_metadata_diagnostics(oroot, definition_id, rule_id, assessment_id, diagnostics):
    definition = next(
        (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == definition_id),
        None,
    )
    if definition is None:
        return

    seen_tests = set()
    seen_objects = set()
    seen_states = set()
    seen_variables = set()

    def warn_missing(kind, node, field, code):
        if node is not None and not node_title(node):
            add_diagnostic(
                diagnostics,
                "warn",
                code,
                f"OVAL {kind} comment is absent; {field} is emitted as null.",
                rule_id=rule_id,
                assessment_id=assessment_id,
                source_id=node.get("id"),
                field=field,
            )

    def visit_criteria(node):
        for child in node:
            kind = local(child.tag)
            if kind == "criterion":
                test_ref = child.get("test_ref")
                if not test_ref or test_ref in seen_tests:
                    continue
                seen_tests.add(test_ref)
                test = find_by_id(oroot, test_ref, "_test")
                warn_missing("Test", test, "test_title", "OVAL_TEST_COMMENT_MISSING")
                if test is None:
                    continue
                for part in test:
                    part_kind = local(part.tag)
                    if part_kind == "object":
                        obj_ref = part.get("object_ref")
                        if obj_ref and obj_ref not in seen_objects:
                            seen_objects.add(obj_ref)
                            obj = find_by_id(oroot, obj_ref, "_object")
                            warn_missing("Object", obj, "object_title", "OVAL_OBJECT_COMMENT_MISSING")
                    elif part_kind == "state":
                        state_ref = part.get("state_ref")
                        if state_ref and state_ref not in seen_states:
                            seen_states.add(state_ref)
                            state = find_by_id(oroot, state_ref, "_state")
                            warn_missing("State", state, "state_title", "OVAL_STATE_COMMENT_MISSING")
            elif kind == "criteria":
                visit_criteria(child)
            elif kind == "extend_definition":
                ref = child.get("definition_ref")
                target = next(
                    (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == ref),
                    None,
                )
                if target is not None:
                    nested = next((n for n in target if local(n.tag) == "criteria"), None)
                    if nested is not None:
                        visit_criteria(nested)

    criteria = next((n for n in definition if local(n.tag) == "criteria"), None)
    if criteria is not None:
        visit_criteria(criteria)

    # Variables can be referenced by object/state entities. Flag only variables
    # actually referenced by the converted definition closure.
    referenced_ids = seen_objects | seen_states
    for source_id in list(referenced_ids):
        node = next((n for n in oroot.iter() if n.get("id") == source_id), None)
        if node is None:
            continue
        for descendant in node.iter():
            var_ref = descendant.get("var_ref")
            if var_ref and var_ref not in seen_variables:
                seen_variables.add(var_ref)
                variable = next(
                    (n for n in oroot.iter() if n.get("id") == var_ref and local(n.tag).endswith("_variable")),
                    None,
                )
                warn_missing("Variable", variable, "variable_title", "OVAL_VARIABLE_COMMENT_MISSING")

def canonical_json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def build_experimental_package(source_root, package_path):
    """Build an iteration-003 package demonstrating logical-ID resolution.

    This is intentionally an experimental package shape. It compiles YAML
    authoring files to canonical JSON-like members and replaces source-path
    applicability bindings with logical Assessment IDs.
    """
    benchmark_source = load_yaml(source_root / "benchmark.yaml")
    applicability_source = load_yaml(source_root / "applicability.yaml")

    benchmark = deepcopy(benchmark_source)
    benchmark_id = benchmark["benchmark"]["id"]
    applicability_catalog_id = f"{benchmark_id}.applicability"

    # Scanner-facing Benchmark references the logical catalog identity, not a path.
    benchmark["benchmark"]["applicability_catalog"] = applicability_catalog_id

    applicability = {
        "applicability_catalog": {
            "id": applicability_catalog_id,
            "conditions": [],
        }
    }

    members = {}
    objects = {}

    def add_object(object_id, object_type, package_member, obj):
        if object_id in objects:
            raise RuntimeError(f"duplicate package object id: {object_id}")
        data = canonical_json_bytes(obj)
        members[package_member] = data
        objects[object_id] = {
            "type": object_type,
            "path": package_member,
            "sha256": sha256(data),
        }

    add_object(
        benchmark_id,
        "benchmark",
        "benchmark.json",
        benchmark,
    )

    # Resolve authoring applicability paths to logical Assessment IDs.
    for entry in applicability_source.get("applicability", []):
        source_path = source_root / entry["assessment"]
        assessment_doc = load_yaml(source_path)
        assessment_id = assessment_doc["assessment"]["id"]
        applicability["applicability_catalog"]["conditions"].append({
            "id": entry["id"],
            "assessment": assessment_id,
        })

    add_object(
        applicability_catalog_id,
        "applicability_catalog",
        "applicability.json",
        applicability,
    )

    for rule_path in sorted((source_root / "rules").glob("*.yaml")):
        rule_doc = load_yaml(rule_path)
        rule_id = rule_doc["rule"]["id"]
        add_object(rule_id, "rule", f"rules/{rule_id}.rule.json", rule_doc)

    assessment_paths = sorted((source_root / "assessments").rglob("*.yaml"))
    for assessment_path in assessment_paths:
        assessment_doc = load_yaml(assessment_path)
        assessment_id = assessment_doc["assessment"]["id"]
        rel_group = assessment_path.parent.name
        add_object(
            assessment_id,
            "assessment",
            f"assessments/{rel_group}/{assessment_id}.json",
            assessment_doc,
        )

    # Validate that every Benchmark Rule ID resolves exactly once in the index.
    benchmark_rules = benchmark["benchmark"].get("rules", [])
    missing_rules = [
        rid for rid in benchmark_rules
        if rid not in objects or objects[rid]["type"] != "rule"
    ]
    if missing_rules:
        raise RuntimeError(f"package index cannot resolve Benchmark Rules: {missing_rules}")

    # One package manifest is both the logical-object resolver and integrity map.
    # Avoid a separate index that would duplicate path/digest information.
    manifest_objects = {}
    for object_id, record in sorted(objects.items()):
        package_member = record["path"]
        data = members[package_member]
        manifest_objects[object_id] = {
            "type": record["type"],
            "path": package_member,
            "sha256": record["sha256"],
            "size": len(data),
        }

    manifest = {
        "format": "scap-ng-package-manifest",
        "format_version": "0.0.3-experimental",
        "benchmark": benchmark_id,
        "objects": manifest_objects,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    members["manifest.json"] = manifest_bytes

    package_path.parent.mkdir(parents=True, exist_ok=True)
    if package_path.exists():
        package_path.unlink()
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name)
            # Fixed timestamp makes the package reproducible for identical content.
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)

    # Write a review copy beside the package so manifest diffs are visible.
    write_json(package_path.parent / f"{BUILD_NAME}.manifest.json", manifest)
    stale_index = package_path.parent / f"{BUILD_NAME}.index.json"
    if stale_index.exists():
        stale_index.unlink()

    return {
        "package": str(package_path.relative_to(ROOT)),
        "sha256": sha256(package_path.read_bytes()),
        "member_count": len(members),
        "object_count": len(objects),
        "rule_count": sum(1 for x in objects.values() if x["type"] == "rule"),
        "assessment_count": sum(1 for x in objects.values() if x["type"] == "assessment"),
    }

def evidence_tree(node):
    return {
        "element": local(node.tag),
        "attributes": dict(node.attrib),
        "text": text(node),
        "children": [evidence_tree(child) for child in list(node)],
    }

def load_source_components(files):
    benchmark = oval = None
    benchmark_source = oval_source = None
    parsed = []
    for p in files:
        if p.suffix.lower() != ".xml": continue
        try: root = ET.parse(p).getroot()
        except ET.ParseError: continue
        parsed.append((p, root))
        if local(root.tag) == "Benchmark" and benchmark is None:
            benchmark, benchmark_source = root, p.name
        if local(root.tag) == "oval_definitions" and oval is None:
            oval, oval_source = root, p.name
    if benchmark is None or oval is None:
        for p, root in parsed:
            for node in root.iter():
                n = local(node.tag)
                if benchmark is None and n == "Benchmark":
                    benchmark, benchmark_source = node, f"{p.name}#Benchmark"
                elif oval is None and n == "oval_definitions":
                    oval, oval_source = node, f"{p.name}#oval_definitions"
                if benchmark is not None and oval is not None: break
            if benchmark is not None and oval is not None: break
    if benchmark is None or oval is None:
        raise RuntimeError("Required Benchmark/OVAL component not found")
    return benchmark, oval, benchmark_source, oval_source

def collect_oval_bundle(files):
    bundle = ET.Element("assessment-bundle")
    seen = set()
    for p in files:
        if p.suffix.lower() != ".xml":
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        candidates = [root] if local(root.tag) == "oval_definitions" else [
            node for node in root.iter() if local(node.tag) == "oval_definitions"
        ]
        for node in candidates:
            key = ET.tostring(node, encoding="unicode")
            digest = hashlib.sha256(key.encode()).hexdigest()
            if digest not in seen:
                bundle.append(deepcopy(node))
                seen.add(digest)
    return bundle

def oval_generator_metadata(oroot):
    generators = []
    for root in list(oroot):
        if local(root.tag) != "oval_definitions":
            continue
        generator = next((n for n in root if local(n.tag) == "generator"), None)
        if generator is None:
            continue
        item = {}
        schema_versions = []
        for child in generator:
            name = local(child.tag)
            value = text(child)
            if name == "schema_version":
                schema_versions.append({
                    "value": value,
                    "namespace": child.get("xmlns") or child.get("{http://www.w3.org/2000/xmlns/}xmlns"),
                })
            elif value is not None:
                item[name] = value
        if schema_versions:
            item["schema_versions"] = schema_versions
        generators.append(item)
    return generators

def source_platform_nodes(files):
    nodes = {}
    for p in files:
        if p.suffix.lower() != ".xml":
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if local(node.tag) == "platform" and node.get("id"):
                nodes[node.get("id")] = node
    return nodes

def native_applicability_id(platform_node):
    title = (text(next((n for n in platform_node if local(n.tag) == "title"), None)) or "").lower()
    mapping = [
        ("gnome", "linux.gnome-installed"),
        ("nfs mounts configured", "linux.nfs-mounted"),
        ("no nfs mounts", "linux.nfs-not-mounted"),
        ("ipv6 enabled", "linux.ipv6-enabled"),
        ("bios boot", "linux.bios-boot"),
        ("uefi boot", "linux.uefi-boot"),
        ("autofs", "linux.autofs-installed"),
        ("postfix", "linux.postfix-installed"),
        ("tftp", "linux.tftp-installed"),
        ("bind", "linux.bind-installed"),
        ("libreswan", "linux.libreswan-installed"),
        ("kernel dumps", "linux.kernel-dumps-enabled"),
        ("not fips", "linux.fips-disabled"),
        ("bare metal", "hardware.bare-metal"),
    ]
    for needle, native in mapping:
        if needle in title:
            return native
    return "applicability." + semantic_id(title, "condition")

def source_platform_definition_id(platform_node):
    logical = next((n for n in platform_node if local(n.tag) == "logical-test"), None)
    if logical is None:
        return None
    children = [n for n in logical if local(n.tag) in ("check-fact-ref", "fact-ref", "logical-test")]
    if len(children) != 1 or local(children[0].tag) != "check-fact-ref":
        return None
    return children[0].get("id-ref")

def lower_source_platform(platform_node, oval_bundle):
    logical = next((n for n in platform_node if local(n.tag) == "logical-test"), None)
    if logical is None:
        return None, None, "platform_missing_logical_test"
    children = [n for n in logical if local(n.tag) in ("check-fact-ref", "fact-ref", "logical-test")]
    if len(children) != 1 or local(children[0].tag) != "check-fact-ref":
        return None, None, "complex_platform_expression_not_yet_lowered"
    definition_id = children[0].get("id-ref")
    if not definition_id:
        return None, None, "platform_check_missing_definition"
    app_id = native_applicability_id(platform_node)
    assessment_id = app_id + ".assessment"
    assessment, error = lower_definition(oval_bundle, definition_id, assessment_id)
    if assessment is None:
        return None, None, error
    negate = (logical.get("negate") or "false").lower() == "true"
    if negate:
        assessment["assessment"]["evaluate"] = {"not": assessment["assessment"]["evaluate"]}
    assessment["assessment"]["assessment_title"] = (
        text(next((n for n in platform_node if local(n.tag) == "title"), None))
        or assessment["assessment"].get("title")
    )
    assessment["assessment"]["purpose"] = "applicability"
    return app_id, assessment, None

def parse_disa_rule_identity(rule):
    source_id = rule.get("id") or ""
    m = re.search(r"_rule_(SV-\d+)(r\d+)_rule$", source_id)
    if not m:
        return None
    return {
        "rule_id": m.group(1),
        "rule_version": m.group(2),
        "stig_id": text(rule.find("x:version", NS)),
    }

def native_rule_identity(rule):
    disa = parse_disa_rule_identity(rule)
    if disa:
        return disa
    source_id = rule.get("id")
    source_version = text(rule.find("x:version", NS))
    return {
        "rule_id": safe_id(source_id) if source_id else safe_id(text(rule.find("x:title", NS)) or "rule"),
        "rule_version": source_version,
        "stig_id": None,
    }

def check_kind(check):
    selector = (check.get("selector") or "").strip().lower()
    system = (check.get("system") or "").lower()
    if selector == "manual" or "ocil" in system or text(check.find("x:check-content", NS)):
        return "manual"
    return "automated"

def records(root):
    out = []
    for group in root.findall(".//x:Group", NS):
        for rule in group.findall("x:Rule", NS):
            checks = rule.findall("x:check", NS)
            identity = native_rule_identity(rule)
            group_source_id = group.get("id") or ""
            group_match = re.search(r"_group_(V-\d+)$", group_source_id)
            out.append({
                "element": rule,
                "source_rule_id": rule.get("id"),
                "source_group_id": group.get("id"),
                "id": identity["rule_id"],
                "version": identity["rule_version"],
                "stig_id": identity["stig_id"],
                "vulnerability_id": group_match.group(1) if group_match else None,
                "title": text(rule.find("x:title", NS)), "severity": rule.get("severity"),
                "role": rule.get("role"), "weight": rule.get("weight"), "checks": checks,
                "platforms": [p.get("idref") for p in rule.findall("x:platform", NS) if p.get("idref")],
                "requires": [x.get("idref") for x in rule.findall("x:requires", NS) if x.get("idref")],
                "conflicts": [x.get("idref") for x in rule.findall("x:conflicts", NS) if x.get("idref")],
            })
    return out

def localized_texts(parent, child_name):
    values = []
    for node in parent.findall(f"x:{child_name}", NS):
        values.append({
            "text": text(node),
            "language": node.get("{http://www.w3.org/XML/1998/namespace}lang"),
        })
    return values

def benchmark_status(root):
    values = []
    for node in root.findall("x:status", NS):
        values.append({
            "value": text(node),
            "date": node.get("date"),
        })
    return values

def benchmark_references(root):
    values = []
    for ref in root.findall("x:reference", NS):
        values.append({
            "text": text(ref),
            "url": ref.get("href"),
        })
    return values

def normalize_front_matter(root):
    values = []
    original = localized_texts(root, "front-matter")
    for item in original:
        value = item["text"]
        if value:
            value = re.sub(
                r"enhanced with OCIL manual questions",
                "enhanced with manual assessment procedures",
                value,
                flags=re.I,
            )
        values.append({"text": value, "language": item["language"]})
    return values, original

def normalize_rear_matter(root):
    values = []
    original = localized_texts(root, "rear-matter")
    for item in original:
        value = item["text"]
        if value:
            value = re.sub(
                r"\s*filename:--:[^\s]+-xccdf\.xml",
                "",
                value,
                flags=re.I,
            )
            value = " ".join(value.split())
        values.append({"text": value, "language": item["language"]})
    return values, original

def benchmark_notices(root):
    values = []
    for node in root.findall("x:notice", NS):
        values.append({
            "id": safe_id(node.get("id") or "notice"),
            "text": text(node),
            "language": node.get("{http://www.w3.org/XML/1998/namespace}lang"),
        })
    return values

def benchmark_text_blocks(root):
    values = []
    for node in root.findall("x:plain-text", NS):
        values.append({
            "id": safe_id(node.get("id") or "text"),
            "text": text(node),
        })
    return values

def benchmark_metadata(root):
    """Normalize common publication metadata without preserving XML namespaces."""
    allowed = {
        "title", "creator", "subject", "description", "publisher",
        "contributor", "date", "type", "format", "identifier",
        "source", "language", "relation", "coverage", "rights",
    }
    values = {}
    unsupported = []
    for metadata in root.findall("x:metadata", NS):
        for child in list(metadata):
            key = local(child.tag)
            value = text(child)
            if key in allowed:
                values.setdefault(key, []).append(value)
            else:
                unsupported.append({
                    "name": key,
                    "value": value,
                })
    return values, unsupported

def benchmark_scoring(root):
    models = []
    for node in root.findall("x:model", NS):
        item = {
            "system": text(node),
            "parameters": {},
        }
        for child in list(node):
            if local(child.tag) == "param":
                name = child.get("name")
                if name:
                    item["parameters"][name] = child.get("value") or text(child)
        models.append(item)
    return models

def normalized_fixes(rule):
    system_map = {
        "urn:xccdf:fix:script:sh": "shell",
        "urn:xccdf:fix:script:ansible": "ansible",
        "urn:xccdf:fix:script:powershell": "powershell",
        "urn:xccdf:fix:script:batch": "batch",
    }
    fixes = []
    for fix in rule.findall("x:fix", NS):
        if list(fix):
            return None, "remediation_substitution_not_yet_lowered"
        source_system = fix.get("system")
        if fix.get("platform"):
            return None, "remediation_platform_not_yet_lowered"
        kind = system_map.get(source_system) if source_system else None
        if source_system and not kind:
            return None, "remediation_system_not_yet_lowered"
        script = text(fix)
        if not script:
            continue
        item = {"content": script}
        if kind:
            item["type"] = kind
        for source_name, native_name in (
            ("reboot", "reboot"),
            ("disruption", "disruption"),
            ("complexity", "complexity"),
            ("strategy", "strategy"),
        ):
            value = fix.get(source_name)
            if value is not None:
                if source_name == "reboot":
                    item[native_name] = value.lower() == "true"
                else:
                    item[native_name] = value
        fixes.append(item)
    return fixes, None

def rule_content(rule):
    out = {}
    raw = rule.find("x:description", NS)
    if raw is not None:
        s = "".join(raw.itertext())
        fields = {
            "VulnDiscussion": "discussion",
            "FalsePositives": "false_positives",
            "FalseNegatives": "false_negatives",
            "Mitigations": "mitigations",
            "PotentialImpacts": "potential_impacts",
            "Responsibility": "responsibility",
        }
        for source_name, native_name in fields.items():
            m = re.search(rf"<{source_name}>(.*?)</{source_name}>", s, flags=re.I | re.S)
            if m:
                value = " ".join(m.group(1).split())
                if value: out[native_name] = value
        m = re.search(r"<Documentable>(.*?)</Documentable>", s, flags=re.I | re.S)
        if m and m.group(1).strip():
            out["documentable"] = m.group(1).strip().lower() == "true"

    rationale = text(rule.find("x:rationale", NS))
    if rationale: out["rationale"] = rationale

    warnings = [text(n) for n in rule.findall("x:warning", NS)]
    warnings = [x for x in warnings if x]
    if warnings: out["warnings"] = warnings

    identifiers = []
    for ident in rule.findall("x:ident", NS):
        value = text(ident)
        system = (ident.get("system") or "").lower()
        if value and "cci" in system:
            identifiers.append({"scheme": "cci", "value": value})
    if identifiers: out["identifiers"] = identifiers

    references = []
    for ref in rule.findall("x:reference", NS):
        item = {}
        href = ref.get("href")
        if href and not any(term in href.lower() for term in ("xccdf", "oval", "ocil", "cpe.mitre.org/language")):
            item["url"] = href

        children = list(ref)
        if children:
            structured = {}
            for child in children:
                name = local(child.tag)
                value = text(child)
                if not value:
                    continue
                if name in structured:
                    if not isinstance(structured[name], list):
                        structured[name] = [structured[name]]
                    structured[name].append(value)
                else:
                    structured[name] = value
            item.update(structured)
        else:
            value = text(ref)
            if value:
                item["text"] = value

        if item:
            references.append(item)
    if references: out["references"] = references

    fixtext_node = rule.find("x:fixtext", NS)
    fixtext = text(fixtext_node)
    fixes, fix_error = normalized_fixes(rule)
    if fix_error:
        raise ValueError(fix_error)
    if fixtext or fixes:
        remediation = {}
        if fixtext: remediation["guidance"] = fixtext
        if fixtext_node is not None:
            for source_name in ("reboot", "disruption", "complexity", "strategy"):
                value = fixtext_node.get(source_name)
                if value is not None:
                    remediation[source_name] = (value.lower() == "true" if source_name == "reboot" else value)
        if fixes: remediation["implementations"] = fixes
        out["remediation"] = remediation
    return out

def find_by_id(root, item_id, suffix):
    if not item_id: return None
    return next((n for n in root.iter() if n.get("id") == item_id and local(n.tag).endswith(suffix)), None)

def oval_semantic_inventory(oroot):
    """Inventory source constructs independently of conversion success.

    This prevents fail-fast lowering from making unsupported source semantics
    appear rarer than they really are.
    """
    counts = {}
    variable_kinds = {}
    for node in oroot.iter():
        name = local(node.tag)
        if name in ("filter", "set", "behaviors"):
            counts[name] = counts.get(name, 0) + 1
        if name.endswith("_variable"):
            variable_kinds[name] = variable_kinds.get(name, 0) + 1
        if name in (
            "arithmetic", "begin", "concat", "count", "end", "escape_regex",
            "literal_component", "merge", "object_component", "regex_capture",
            "split", "substring", "time_difference", "unique",
            "variable_component",
        ):
            counts[name] = counts.get(name, 0) + 1
    return {
        "construct_counts": dict(sorted(counts.items())),
        "variable_kinds": dict(sorted(variable_kinds.items())),
    }

def unsupported_definition_features(oroot, definition_id):
    """Return all structurally unsupported constructs reachable from a Definition.

    Generic variables, sets, filters, and behaviors are native v003 constructs
    and therefore are not errors here. This pass is intentionally independent of
    lowering so diagnostics can enumerate multiple problems instead of masking
    everything behind the first failure.
    """
    findings = []
    seen = set()
    visited_definitions = set()
    visited_variables = set()

    supported_components = {
        "arithmetic", "begin", "concat", "count", "end", "escape_regex",
        "glob_to_regex", "literal_component", "merge", "object_component",
        "regex_capture", "split", "substring", "time_difference", "unique",
        "variable_component",
    }

    def add(feature, source_id=None, detail=None):
        key = (feature, source_id, detail)
        if key in seen:
            return
        seen.add(key)
        item = {"feature": feature}
        if source_id is not None:
            item["source_id"] = source_id
        if detail is not None:
            item["detail"] = detail
        findings.append(item)

    def inspect_variable(var_ref):
        if not var_ref or var_ref in visited_variables:
            return
        visited_variables.add(var_ref)
        variable = next(
            (n for n in oroot.iter() if n.get("id") == var_ref and local(n.tag).endswith("_variable")),
            None,
        )
        if variable is None:
            add("variable_not_found", var_ref)
            return
        kind = local(variable.tag)
        if kind not in ("constant_variable", "local_variable", "external_variable"):
            add("variable_kind", var_ref, kind)
            return
        if kind == "external_variable":
            # possible_value / possible_restriction are input-validation
            # semantics, not OVAL ComponentGroup expressions.
            return
        for descendant in variable.iter():
            name = local(descendant.tag)
            if descendant is variable or name == "value":
                continue
            if name.endswith("_variable"):
                continue
            if name not in supported_components:
                add("variable_component", var_ref, name)
            nested_ref = descendant.get("var_ref")
            if nested_ref:
                inspect_variable(nested_ref)
            # Object-component dependencies are part of the variable graph.
            # Follow them during feature accounting so a standard-looking
            # Definition cannot hide a non-standard Object behind
            # Object -> Variable -> Object chains.
            if name == "object_component" and descendant.get("object_ref"):
                inspect_object(descendant.get("object_ref"))

    def inspect_object(obj_ref):
        obj = find_by_id(oroot, obj_ref, "_object")
        if obj is None:
            add("object_not_found", obj_ref)
            return
        obj_ns = obj.tag.split("}", 1)[0].strip("{") if "}" in obj.tag else ""
        obj_name = local(obj.tag)
        if (obj_ns, obj_name) not in oval_definition_elements():
            add(
                "nonstandard_oval_element",
                obj_ref,
                f"{obj_ns}#{obj_name}",
            )
        for descendant in obj.iter():
            var_ref = descendant.get("var_ref")
            if var_ref:
                inspect_variable(var_ref)
            if local(descendant.tag) == "var_ref" and text(descendant):
                inspect_variable(text(descendant))
            if local(descendant.tag) == "object_reference" and text(descendant):
                inspect_object(text(descendant))
            if local(descendant.tag) == "filter":
                state_ref = descendant.get("state_ref") or text(descendant)
                if not state_ref or find_by_id(oroot, state_ref, "_state") is None:
                    add("filter_state_not_found", obj_ref, state_ref)

    def visit_criteria(node):
        operator = (node.get("operator") or "AND").upper()
        if operator not in ("AND", "OR", "ONE", "XOR"):
            add("criteria_operator", detail=operator)
        for child in node:
            kind = local(child.tag)
            if kind == "criterion":
                test_ref = child.get("test_ref")
                test = next(
                    (n for n in oroot.iter() if n.get("id") == test_ref and local(n.tag).endswith("_test")),
                    None,
                )
                if test is None:
                    add("test_not_found", test_ref)
                    continue
                test_ns = test.tag.split("}", 1)[0].strip("{") if "}" in test.tag else ""
                test_name = local(test.tag)
                if (test_ns, test_name) not in oval_definition_elements():
                    add(
                        "nonstandard_oval_element",
                        test_ref,
                        f"{test_ns}#{test_name}",
                    )
                if (test_ns, test_name) in deprecated_test_types():
                    add(
                        "deprecated_oval_test",
                        test_ref,
                        f"{test_ns}#{test_name}",
                    )
                state_refs = []
                for part in test:
                    part_kind = local(part.tag)
                    if part_kind == "object":
                        inspect_object(part.get("object_ref"))
                    elif part_kind == "state" and part.get("state_ref"):
                        state_refs.append(part.get("state_ref"))
                        state = find_by_id(oroot, part.get("state_ref"), "_state")
                        if state is None:
                            add("state_not_found", part.get("state_ref"))
                        else:
                            state_ns = state.tag.split("}", 1)[0].strip("{") if "}" in state.tag else ""
                            state_name = local(state.tag)
                            if (state_ns, state_name) not in oval_definition_elements():
                                add(
                                    "nonstandard_oval_element",
                                    part.get("state_ref"),
                                    f"{state_ns}#{state_name}",
                                )
                            for descendant in state.iter():
                                var_ref = descendant.get("var_ref")
                                if var_ref:
                                    inspect_variable(var_ref)
                state_operator = (test.get("state_operator") or "AND").upper()
                if len(state_refs) > 1 and state_operator not in ("AND", "OR"):
                    add("state_operator", test_ref, state_operator)
            elif kind == "criteria":
                visit_criteria(child)
            elif kind == "extend_definition":
                visit_definition(child.get("definition_ref"))

    def visit_definition(ref):
        if not ref or ref in visited_definitions:
            return
        visited_definitions.add(ref)
        definition = next(
            (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == ref),
            None,
        )
        if definition is None:
            add("definition_not_found", ref)
            return
        criteria = next((n for n in definition if local(n.tag) == "criteria"), None)
        if criteria is None:
            add("missing_criteria", ref)
            return
        visit_criteria(criteria)

    visit_definition(definition_id)
    return findings

def lower_definition(oroot, definition_id, assessment_id):
    """Lower one OVAL Definition to native SCAP-NG assessment semantics."""
    definition = next(
        (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == definition_id),
        None,
    )
    if definition is None:
        return None, "definition_not_found"

    assessment_title = oval_definition_title(definition)
    assessment_class = definition.get("class") or "miscellaneous"
    checks = {}
    variables = {}
    variable_names = {}
    active_variables = set()
    active_objects = set()
    test_to_check = {}
    used_check_ids = set()
    used_variable_ids = set()
    active_definitions = set()

    def unique_check_id(title, capability):
        base = semantic_id(title, semantic_id(capability, "check"))
        candidate = base
        suffix = 2
        while candidate in used_check_ids:
            candidate = f"{base}-{suffix}"
            suffix += 1
        used_check_ids.add(candidate)
        return candidate

    def unique_variable_id(variable):
        title = node_title(variable)
        kind = local(variable.tag).replace("_variable", "")
        base = semantic_id(title, f"{kind}-value")
        candidate = base
        suffix = 2
        while candidate in used_variable_ids:
            candidate = f"{base}-{suffix}"
            suffix += 1
        used_variable_ids.add(candidate)
        return candidate

    def capability_for_object(obj):
        name = local(obj.tag)
        ns_uri = obj.tag.split("}", 1)[0].strip("{") if "}" in obj.tag else ""
        family = ns_uri.split("#")[-1].split("/")[-1] if ns_uri else "generic"
        object_name = name[:-7] if name.endswith("_object") else name
        return f"{family}.{object_name}"

    def capability_for_state(state):
        name = local(state.tag)
        ns_uri = state.tag.split("}", 1)[0].strip("{") if "}" in state.tag else ""
        family = ns_uri.split("#")[-1].split("/")[-1] if ns_uri else "generic"
        state_name = name[:-6] if name.endswith("_state") else name
        return f"{family}.{state_name}"

    def ensure_variable(var_ref):
        if var_ref in variable_names:
            return variable_names[var_ref], None
        variable = next(
            (n for n in oroot.iter() if n.get("id") == var_ref and local(n.tag).endswith("_variable")),
            None,
        )
        if variable is None:
            return None, f"variable_not_found:{var_ref}"
        if var_ref in active_variables:
            return None, f"variable_cycle:{var_ref}"

        native_id = unique_variable_id(variable)
        variable_names[var_ref] = native_id
        active_variables.add(var_ref)
        kind = local(variable.tag)
        entry = {
            "title": node_title(variable),
            "datatype": variable.get("datatype") or "string",
            "kind": kind.replace("_variable", ""),
        }

        if kind == "constant_variable":
            values = [oval_value_text(child) for child in variable if local(child.tag) == "value"]
            entry["expression"] = {"literal": values[0] if len(values) == 1 else values}
        elif kind == "external_variable":
            input_contract = {
                "required": True,
                "cardinality": "one_or_more",
            }
            alternatives = []
            for child in variable:
                child_kind = local(child.tag)
                if child_kind == "notes":
                    continue
                if child_kind == "possible_value":
                    alternatives.append({
                        "literal": oval_value_text(child),
                        "hint": child.get("hint") or "",
                    })
                elif child_kind == "possible_restriction":
                    conditions = []
                    for restriction in child:
                        if local(restriction.tag) != "restriction":
                            continue
                        conditions.append({
                            "operation": restriction.get("operation"),
                            "value": oval_value_text(restriction),
                        })
                    alternatives.append({
                        "restriction_group": {
                            "operator": (child.get("operator") or "AND").upper(),
                            "hint": child.get("hint") or "",
                            "conditions": conditions,
                        }
                    })
                else:
                    active_variables.remove(var_ref)
                    return None, f"unsupported_external_variable_child:{child_kind}"
            if alternatives:
                input_contract["validation"] = {"alternatives": alternatives}
            entry["input"] = input_contract
        elif kind == "local_variable":
            components = [child for child in variable if local(child.tag) not in ("notes",)]
            if len(components) != 1:
                active_variables.remove(var_ref)
                return None, f"local_variable_component_count:{len(components)}"
            expr, error = lower_component(components[0])
            if error:
                active_variables.remove(var_ref)
                return None, error
            entry["expression"] = expr
        else:
            active_variables.remove(var_ref)
            return None, f"unsupported_variable_kind:{kind}"

        variables[native_id] = entry
        active_variables.remove(var_ref)
        return native_id, None

    def lower_component(node):
        name = local(node.tag)

        if name == "literal_component":
            value = oval_value_text(node)
            if node.get("datatype"):
                return {"literal": {"value": value, "datatype": node.get("datatype")}}, None
            return {"literal": value}, None

        if name == "variable_component":
            var_ref = node.get("var_ref")
            native_id, error = ensure_variable(var_ref)
            if error:
                return None, error
            return {"variable": native_id}, None

        if name == "object_component":
            obj_ref = node.get("object_ref")
            field = node.get("item_field")
            collection, error = lower_object(obj_ref)
            if error:
                return None, error
            result = {
                "object_values": {
                    "collect": collection,
                    "field": field,
                }
            }
            if node.get("record_field"):
                result["object_values"]["record_field"] = node.get("record_field")
            return result, None

        children = [child for child in node if local(child.tag) not in ("notes",)]
        lowered = []
        for child in children:
            item, error = lower_component(child)
            if error:
                return None, error
            lowered.append(item)

        if name == "concat":
            return {"concat": lowered}, None
        if name == "count":
            return {"count": lowered[0] if len(lowered) == 1 else lowered}, None
        if name == "merge":
            return {
                "merge": {
                    "values": lowered[0] if len(lowered) == 1 else lowered,
                    "delimiter": node.get("delimiter") if node.get("delimiter") is not None else "",
                    "sort": (node.get("sort") or "document").lower(),
                    "order": (node.get("order") or "ascending").lower(),
                }
            }, None
        if name == "unique":
            return {"unique": lowered[0] if len(lowered) == 1 else lowered}, None
        if name == "split":
            return {
                "split": {
                    "value": lowered[0] if len(lowered) == 1 else lowered,
                    "delimiter": node.get("delimiter"),
                }
            }, None
        if name == "substring":
            return {
                "substring": {
                    "value": lowered[0] if len(lowered) == 1 else lowered,
                    "start": node.get("substring_start") or node.get("start"),
                    "length": node.get("substring_length") or node.get("length"),
                }
            }, None
        if name == "regex_capture":
            return {
                "regex_capture": {
                    "value": lowered[0] if len(lowered) == 1 else lowered,
                    "pattern": node.get("pattern"),
                }
            }, None
        if name == "escape_regex":
            return {"escape_regex": lowered[0] if len(lowered) == 1 else lowered}, None
        if name == "glob_to_regex":
            return {
                "glob_to_regex": {
                    "value": lowered[0] if len(lowered) == 1 else lowered,
                    "noescape": (node.get("glob_noescape") or "false").lower() == "true",
                }
            }, None
        if name == "arithmetic":
            return {
                "arithmetic": {
                    "operation": (node.get("arithmetic_operation") or node.get("operation") or "").lower(),
                    "operands": lowered,
                }
            }, None
        if name in ("begin", "end"):
            return {
                name: {
                    "value": lowered[0] if len(lowered) == 1 else lowered,
                    "character": node.get("character"),
                }
            }, None
        if name == "time_difference":
            return {
                "time_difference": {
                    "format_1": node.get("format_1"),
                    "format_2": node.get("format_2"),
                    "values": lowered,
                }
            }, None
        return None, f"unsupported_variable_component:{name}"

    def lower_entity_value(node):
        children = [child for child in node if local(child.tag) == "field"]
        if children:
            fields = []
            for child in children:
                var_ref = child.get("var_ref")
                if var_ref:
                    native_id, error = ensure_variable(var_ref)
                    if error:
                        return None, error
                    value = {"variable": native_id}
                else:
                    raw = oval_value_text(child)
                    value = "" if raw is None else raw
                item = {
                    "name": child.get("name"),
                    "value": value,
                }
                for source, target in (
                    ("operation", "operation"),
                    ("datatype", "datatype"),
                    ("var_check", "variable_check"),
                    ("entity_check", "entity_check"),
                    ("mask", "mask"),
                ):
                    if child.get(source) is not None:
                        raw_attr = child.get(source)
                        item[target] = (
                            raw_attr.lower() == "true"
                            if source == "mask"
                            else raw_attr
                        )
                fields.append(item)
            return {"record": fields}, None

        var_ref = node.get("var_ref")
        if not var_ref and local(node.tag) == "var_ref":
            var_ref = text(node)
        if var_ref:
            native_id, error = ensure_variable(var_ref)
            if error:
                return None, error
            return {"variable": native_id}, None
        value = oval_value_text(node)
        return ("" if value is None else value), None

    def lower_state(state_ref):
        state = find_by_id(oroot, state_ref, "_state")
        if state is None:
            return None, None, None, f"state_not_found:{state_ref}"
        conditions = []
        for child in state:
            if local(child.tag) in ("notes",):
                continue
            value, error = lower_entity_value(child)
            if error:
                return None, None, error
            item = {
                "field": local(child.tag),
                "operation": child.get("operation") or "equals",
                "value": value,
            }
            if child.get("entity_check"):
                item["entity_check"] = child.get("entity_check")
            # State entity existence is independent of Test check_existence.
            # Only preserve explicit source values; the semantic comparator
            # resolves documented omission defaults independently.
            if child.get("check_existence") is not None:
                item["entity_existence"] = child.get("check_existence")
            if child.get("var_check"):
                item["variable_check"] = child.get("var_check")
            if child.get("datatype"):
                item["datatype"] = child.get("datatype")
            if child.get("mask"):
                item["mask"] = child.get("mask").lower() == "true"
            nil_value = next(
                (value for key, value in child.attrib.items() if local(key) == "nil"),
                None,
            )
            if nil_value is not None:
                item["nil"] = nil_value.lower() == "true"
            conditions.append(item)
        if not conditions:
            condition = None
        elif len(conditions) == 1:
            condition = conditions[0]
        else:
            state_operator = (state.get("operator") or "AND").upper()
            if state_operator == "AND":
                condition = {"all": conditions}
            elif state_operator == "OR":
                condition = {"any": conditions}
            else:
                return None, node_title(state), capability_for_state(state), f"unsupported_state_operator:{state_operator}"
        return condition, node_title(state), capability_for_state(state), None

    def lower_filter(filter_node):
        state_ref = filter_node.get("state_ref") or text(filter_node)
        if not state_ref:
            return None, "filter_missing_state"
        condition, state_title, state_capability, error = lower_state(state_ref)
        if error:
            return None, error
        item = {
            "action": (filter_node.get("action") or "exclude").lower(),
            "match": condition,
        }
        if state_title:
            item["state_title"] = state_title
        if state_capability:
            item["capability"] = state_capability
        return item, None

    def lower_set(set_node):
        operator = (set_node.get("set_operator") or "UNION").lower()
        members = []
        filters = []
        for child in set_node:
            name = local(child.tag)
            if name == "object_reference":
                collection, error = lower_object(text(child))
                if error:
                    return None, error
                members.append({"collect": collection})
            elif name == "set":
                nested, error = lower_set(child)
                if error:
                    return None, error
                members.append({"set": nested})
            elif name == "filter":
                item, error = lower_filter(child)
                if error:
                    return None, error
                filters.append(item)
            else:
                return None, f"unsupported_set_member:{name}"
        result = {"operator": operator, "members": members}
        if filters:
            result["filters"] = filters
        return result, None

    def lower_object(obj_ref):
        if not obj_ref:
            return None, "object_ref_missing"
        if obj_ref in active_objects:
            return None, f"object_cycle:{obj_ref}"
        obj = find_by_id(oroot, obj_ref, "_object")
        if obj is None:
            return None, f"object_not_found:{obj_ref}"

        active_objects.add(obj_ref)
        result = {
            "object_title": node_title(obj),
            "capability": capability_for_object(obj),
        }
        query = {}
        filters = []
        behaviors = {}
        set_expr = None

        for child in obj:
            name = local(child.tag)
            if name in ("notes",):
                continue
            if name == "behaviors":
                behaviors.update(dict(child.attrib))
                continue
            if name == "filter":
                item, error = lower_filter(child)
                if error:
                    active_objects.remove(obj_ref)
                    return None, error
                filters.append(item)
                continue
            if name == "set":
                if set_expr is not None:
                    active_objects.remove(obj_ref)
                    return None, "multiple_object_sets"
                set_expr, error = lower_set(child)
                if error:
                    active_objects.remove(obj_ref)
                    return None, error
                continue

            value, error = lower_entity_value(child)
            if error:
                active_objects.remove(obj_ref)
                return None, error
            if value is None:
                continue
            item = value
            attrs = {}
            if child.get("operation"):
                attrs["operation"] = child.get("operation")
            if child.get("var_check"):
                attrs["variable_check"] = child.get("var_check")
            if child.get("entity_check"):
                attrs["entity_check"] = child.get("entity_check")
            if child.get("datatype"):
                attrs["datatype"] = child.get("datatype")
            if child.get("mask"):
                attrs["mask"] = child.get("mask").lower() == "true"
            nil_value = next(
                (value for key, value in child.attrib.items() if local(key) == "nil"),
                None,
            )
            if nil_value is not None:
                attrs["nil"] = nil_value.lower() == "true"
            if attrs:
                attrs["value"] = value
                item = attrs
            query[name] = item

        if query:
            result["select"] = query
        if set_expr is not None:
            result["set"] = set_expr
        if filters:
            result["filters"] = filters
        if behaviors:
            result["behaviors"] = behaviors
        active_objects.remove(obj_ref)
        return result, None

    def lower_test(test_ref):
        if test_ref in test_to_check:
            return {"check": test_to_check[test_ref]}, None

        test = next(
            (n for n in oroot.iter() if n.get("id") == test_ref and local(n.tag).endswith("_test")),
            None,
        )
        if test is None:
            return None, "test_not_found"

        test_name = local(test.tag)
        ns_uri = test.tag.split("}", 1)[0].strip("{")
        family = ns_uri.split("#")[-1].split("/")[-1]
        capability = f"{family}.{test_name[:-5] if test_name.endswith('_test') else test_name}"
        test_title = node_title(test)

        # OVAL independent:unknown_test intentionally has no Object and always
        # evaluates to unknown. Preserve that result explicitly instead of
        # inventing collection semantics.
        if test_name == "unknown_test":
            check_id = unique_check_id(test_title, capability)
            test_to_check[test_ref] = check_id
            checks[check_id] = {
                "test_title": test_title,
                "capability": capability,
                "result": "unknown",
            }
            return {"check": check_id}, None

        obj_ref = None
        state_refs = []
        for child in test:
            if local(child.tag) == "object":
                obj_ref = child.get("object_ref")
            elif local(child.tag) == "state" and child.get("state_ref"):
                state_refs.append(child.get("state_ref"))

        collection, error = lower_object(obj_ref)
        if error:
            return None, error
        # Preserve Test, Object, and State capabilities independently. OVAL
        # references can legally preserve distinct component families and a
        # lossless converter must not retag the referenced Object.
        states = []
        for ref in state_refs:
            condition, title, state_capability, error = lower_state(ref)
            if error:
                return None, error
            if condition is not None:
                states.append({
                    "state": condition,
                    "state_title": title,
                    "capability": state_capability,
                })

        check_id = unique_check_id(test_title, capability)
        test_to_check[test_ref] = check_id

        assertion = {
            "existence": test.get("check_existence") or "at_least_one_exists",
            "check": test.get("check") or "all",
            "state": None,
        }
        if states:
            state_operator = (test.get("state_operator") or "AND").upper()
            if state_operator not in ("AND", "OR"):
                return None, f"unsupported_state_operator:{state_operator}"
            if len(states) == 1:
                assertion["state"] = states[0]["state"]
                if states[0].get("state_title"):
                    assertion["state_title"] = states[0]["state_title"]
                if states[0].get("capability"):
                    assertion["state_capability"] = states[0]["capability"]
            else:
                # Preserve Test-level state boundaries separately from the
                # boolean operator inside each State. These are distinct OVAL
                # semantics and cannot be reconstructed from a flattened AST.
                assertion["state_operator"] = state_operator
                assertion["states"] = states

        checks[check_id] = {
            "test_title": test_title,
            "capability": capability,
            "collect": collection,
            "assert": assertion,
        }
        return {"check": check_id}, None

    def lower_criteria(node):
        operator = (node.get("operator") or "AND").upper()
        terms = []
        for child in node:
            kind = local(child.tag)
            if kind == "criterion":
                term, error = lower_test(child.get("test_ref"))
            elif kind == "criteria":
                term, error = lower_criteria(child)
            elif kind == "extend_definition":
                ref = child.get("definition_ref")
                if ref in active_definitions:
                    return None, "definition_cycle"
                target = next(
                    (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == ref),
                    None,
                )
                if target is None:
                    return None, "extended_definition_not_found"
                nested = next((n for n in target if local(n.tag) == "criteria"), None)
                if nested is None:
                    return None, "extended_definition_missing_criteria"
                active_definitions.add(ref)
                term, error = lower_criteria(nested)
                active_definitions.remove(ref)
            else:
                continue
            if error:
                return None, error
            # Nested criteria apply their own node attributes recursively.
            # criterion and extend_definition carry edge attributes here.
            if kind != "criteria":
                if (child.get("negate") or "false").lower() == "true":
                    term = {"not": term}
                if (child.get("applicability_check") or "false").lower() == "true":
                    term = {"applicability_check": term}
            terms.append(term)

        if not terms:
            return None, "empty_criteria"
        if len(terms) == 1:
            expr = terms[0]
        elif operator == "AND":
            expr = {"all": terms}
        elif operator == "OR":
            expr = {"any": terms}
        elif operator == "ONE":
            expr = {"one": terms}
        elif operator == "XOR":
            expr = {"xor": terms}
        else:
            return None, f"unsupported_criteria_operator:{operator}"

        if (node.get("negate") or "false").lower() == "true":
            expr = {"not": expr}
        if (node.get("applicability_check") or "false").lower() == "true":
            expr = {"applicability_check": expr}
        return expr, None

    root_criteria = next((n for n in definition if local(n.tag) == "criteria"), None)
    if root_criteria is None:
        return None, "missing_criteria"

    active_definitions.add(definition_id)
    expression, error = lower_criteria(root_criteria)
    active_definitions.remove(definition_id)
    if error:
        return None, error

    assessment = {
        "id": assessment_id,
        "version": int(definition.get("version")) if (definition.get("version") or "").isdigit() else definition.get("version"),
        "assessment_title": assessment_title,
        "mode": "automated",
        "class": assessment_class,
        "deprecated": (definition.get("deprecated") or "false").lower() in ("true", "1"),
        "purpose": "assessment",
        "checks": checks,
        "evaluate": expression,
    }
    if variables:
        assessment["variables"] = variables
    return {"assessment": assessment}, None

def automated_refs(rec):
    refs = []
    for c in rec["checks"]:
        if check_kind(c) != "automated": continue
        ref = c.find("x:check-content-ref", NS)
        if ref is None or not ref.get("name"): return None
        refs.append(((c.get("selector") or "").strip() or "default", ref.get("name")))
    return refs

def lowerability_reason(rec, oroot):
    rule = rec["element"]
    if rec["platforms"]: return "rule_applicability_not_yet_lowered"
    if rec["requires"]: return "requires_not_yet_lowered"
    if rec["conflicts"]: return "conflicts_not_yet_lowered"
    _, fix_error = normalized_fixes(rule)
    if fix_error: return fix_error
    refs = automated_refs(rec)
    if not refs: return "no_automated_check"
    for _, definition_id in {x for x in refs}:
        assessment, error = lower_definition(oroot, definition_id, "probe")
        if assessment is None: return error
    return None

def fully_lowerable(rec, oroot):
    return lowerability_reason(rec, oroot) is None

def functional_group(rec):
    title = (rec.get("title") or "").lower()
    discussion = (text(rec["element"].find("x:description", NS)) or "").lower()
    remediation = (text(rec["element"].find("x:fixtext", NS)) or "").lower()
    haystack = " ".join((title, discussion, remediation))

    # Prefer specific, recognizable policy domains.  Avoid broad substring
    # matches such as "user" or "log" that create misleading groups.
    topics = [
        ("ssh", "SSH", (r"\bssh\b", r"\bsshd\b", r"secure shell")),
        ("password-policy", "Password Policy", (r"password", r"pwquality", r"login\.defs", r"pam_")),
        ("auditing", "Auditing", (r"\baudit", r"auditd", r"audisp")),
        ("logging", "Logging", (r"journald", r"rsyslog", r"syslog", r"log file")),
        ("graphical-environment", "Graphical Environment", (r"graphical", r"gnome", r"display manager", r"gdm")),
        ("system-lifecycle", "System Lifecycle and Support", (r"vendor-supported", r"supported release", r"end of life")),
        ("login-notices", "Login Notices and Banners", (r"notice and consent banner", r"logon banner", r"login banner")),
        ("account-management", "Account Management", (r"user account", r"account management", r"inactive account", r"root account")),
        ("services", "Services", (r"\bservice\b", r"\bdaemon\b", r"systemd")),
        ("filesystem", "Filesystem and Permissions", (r"file permission", r"directory permission", r"file owner", r"mount point")),
        ("networking", "Networking", (r"firewall", r"ipv4", r"ipv6", r"tcp", r"udp", r"network interface")),
        ("cryptography", "Cryptography", (r"\bfips\b", r"cipher", r"certificate", r"cryptograph", r"private key")),
    ]
    for gid, group_title, patterns in topics:
        if any(re.search(pattern, haystack) for pattern in patterns):
            return gid, group_title
    return "needs-grouping", "Needs Grouping"

def build_groups(selected):
    parents = {
        "automated": {"id": "automated", "title": "Automated", "groups": {}},
        "manual-or-managerial": {
            "id": "manual-or-managerial",
            "title": "Manual or Managerial",
            "groups": {},
        },
    }
    evidence = []
    for rec in selected:
        default = next(
            (c for c in rec["checks"] if not (c.get("selector") or "").strip()),
            rec["checks"][0] if rec["checks"] else None,
        )
        parent_id = "manual-or-managerial" if default is None or check_kind(default) == "manual" else "automated"
        topic_id, topic_title = functional_group(rec)
        subgroup_id = f"{parent_id}.{topic_id}"
        subgroup = parents[parent_id]["groups"].setdefault(
            subgroup_id,
            {"id": subgroup_id, "title": topic_title, "rules": []},
        )
        subgroup["rules"].append(rec["id"])
        evidence.append({
            "rule": rec["id"],
            "assessment_group": parent_id,
            "functional_group": subgroup_id,
            "method": "heuristic",
        })

    output = []
    for parent in parents.values():
        children = list(parent["groups"].values())
        if not children:
            continue
        output.append({
            "id": parent["id"],
            "title": parent["title"],
            "groups": children,
        })
    return output, evidence

def compliance_lowerable(rec, oval_bundle):
    _, fix_error = normalized_fixes(rec["element"])
    if fix_error:
        return False
    refs = automated_refs(rec)
    if not refs:
        return False
    for _, definition_id in {x for x in refs}:
        assessment, _ = lower_definition(oval_bundle, definition_id, "probe")
        if assessment is None:
            return False
    return True

def applicability_lowerable(rec, platform_nodes, oval_bundle):
    if len(rec["platforms"]) != 1:
        return False
    node = platform_nodes.get(rec["platforms"][0].lstrip("#"))
    if node is None:
        return False
    _, assessment, error = lower_source_platform(node, oval_bundle)
    return assessment is not None and error is None

def manual_only_lowerable(rec):
    if rec["platforms"] or rec["requires"] or rec["conflicts"]:
        return False
    _, fix_error = normalized_fixes(rec["element"])
    if fix_error:
        return False
    if not rec["checks"]:
        return False
    default = next(
        (c for c in rec["checks"] if not (c.get("selector") or "").strip()),
        rec["checks"][0],
    )
    return check_kind(default) == "manual" and all(check_kind(c) == "manual" for c in rec["checks"])

def benchmark_platform_assessment(platform_id, title, distro_ids):
    conditions = []
    for distro_id in distro_ids:
        conditions.append({
            "field": "id",
            "operation": "equals",
            "value": distro_id,
        })
    return {
        "assessment": {
            "id": platform_id + ".assessment",
            "assessment_title": title,
            "mode": "automated",
            "class": "inventory",
            "purpose": "applicability",
            "checks": {
                "operating-system-identity": {
                    "test_title": title,
                    "collect": {
                        "object_title": "Operating system identity",
                        "capability": "linux.os-release",
                        "select": {},
                    },
                    "assert": {
                        "state_title": title,
                        "existence": "at_least_one_exists",
                        "check": "all",
                        "state": {
                            "all": [
                                {"any": conditions},
                                {
                                    "field": "version_id",
                                    "operation": "pattern match",
                                    "value": r"^9(?:\.|$)",
                                },
                            ]
                        },
                    },
                }
            },
            "evaluate": {"check": "operating-system-identity"},
        }
    }

def benchmark_platform_conditions():
    return [
        (
            "platform.rhel-9",
            "Red Hat Enterprise Linux 9",
            ["rhel"],
            "cpe:/o:redhat:enterprise_linux:9.0",
        ),
        (
            "platform.rocky-9",
            "Rocky Linux 9",
            ["rocky"],
            "cpe:/o:rocky:rocky:9",
        ),
        (
            "platform.almalinux-9",
            "AlmaLinux 9",
            ["almalinux"],
            "cpe:/o:almalinux:almalinux:9",
        ),
    ]

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.rmtree(LEGACY_OUT, ignore_errors=True)
    shutil.rmtree(EVIDENCE, ignore_errors=True)
    OUT.mkdir(parents=True); EVIDENCE.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as t:
        td = Path(t); zp = td / "source.zip"
        urllib.request.urlretrieve(SOURCE_URL, zp); package_bytes = zp.read_bytes()
        with zipfile.ZipFile(zp) as zf: zf.extractall(td / "pkg")
        files = [p for p in (td / "pkg").rglob("*") if p.is_file()]
        xr, oroot, xsrc, osrc = load_source_components(files)
        oval_bundle = collect_oval_bundle(files)
        platform_nodes = source_platform_nodes(files)
        rs = records(xr)

        all_xml_roots = []
        for source_file in files:
            if source_file.suffix.lower() != ".xml":
                continue
            try:
                all_xml_roots.append((source_file.name, ET.parse(source_file).getroot()))
            except ET.ParseError:
                pass

        source_platform_refs = sorted({
            ref.lstrip("#")
            for r in rs
            for ref in r["platforms"]
        })
        source_platform_inventory = []
        for platform_ref in source_platform_refs:
            matches = []
            for source_name, source_root in all_xml_roots:
                for node in source_root.iter():
                    if node.get("id") == platform_ref:
                        item = evidence_tree(node)
                        item["source_file"] = source_name
                        matches.append(item)
            source_platform_inventory.append({
                "source_id": platform_ref,
                "matches": matches,
            })

        applicability_candidates = [
            {
                "rule": r["id"],
                "title": r["title"],
                "platform_refs": r["platforms"],
                "default_check_mode": (
                    check_kind(next(
                        (c for c in r["checks"] if not (c.get("selector") or "").strip()),
                        r["checks"][0] if r["checks"] else None,
                    ))
                    if r["checks"] else None
                ),
            }
            for r in rs if r["platforms"]
        ]
        benchmark_platform_refs = [
            p.get("idref") for p in xr.findall("x:platform", NS) if p.get("idref")
        ]

        manual_default_candidates = [
            {
                "rule": r["id"],
                "title": r["title"],
            }
            for r in rs
            if r["checks"] and check_kind(next(
                (c for c in r["checks"] if not (c.get("selector") or "").strip()),
                r["checks"][0],
            )) == "manual"
        ]

        if FULL_MODE:
            selected = list(rs)
        else:
            # Golden review slice:
            # - three baseline automated Rules;
            # - one Rule with real source Rule-level applicability;
            # - one manual/default Rule.
            baseline = [r for r in rs if fully_lowerable(r, oval_bundle)][:3]
            preferred_applicability = ["RHEL-09-211035", "RHEL-09-271010", "RHEL-09-231065"]
            applicability_rules = []
            for wanted in preferred_applicability:
                candidate = next((r for r in rs if r.get("stig_id") == wanted), None)
                if (
                    candidate
                    and candidate["platforms"]
                    and not candidate["requires"]
                    and not candidate["conflicts"]
                    and compliance_lowerable(candidate, oval_bundle)
                    and applicability_lowerable(candidate, platform_nodes, oval_bundle)
                ):
                    applicability_rules.append(candidate)
                if len(applicability_rules) == 2:
                    break
            if len(applicability_rules) < 2:
                for candidate in rs:
                    if candidate in applicability_rules:
                        continue
                    if (
                        candidate["platforms"]
                        and not candidate["requires"]
                        and not candidate["conflicts"]
                        and compliance_lowerable(candidate, oval_bundle)
                        and applicability_lowerable(candidate, platform_nodes, oval_bundle)
                    ):
                        applicability_rules.append(candidate)
                    if len(applicability_rules) == 2:
                        break
            preferred_manual = ["RHEL-09-251035", "RHEL-09-411095", "RHEL-09-211015"]
            manual_rule = next(
                (r for wanted in preferred_manual for r in rs if r.get("stig_id") == wanted and manual_only_lowerable(r)),
                None,
            )
            if manual_rule is None:
                manual_rule = next((r for r in rs if manual_only_lowerable(r)), None)
    
            selected = []
            for candidate in baseline + applicability_rules + [manual_rule]:
                if candidate and candidate["id"] not in {r["id"] for r in selected}:
                    selected.append(candidate)
    
            if len(selected) < 6 or len(applicability_rules) < 2 or manual_rule is None:
                raise RuntimeError(
                    "Golden slice requirements not satisfied: "
                    f"selected={len(selected)}, applicability={len(applicability_rules)}, manual={bool(manual_rule)}"
                )
    
    
        selected_ids = [r["id"] for r in selected]
        source_to_native = {r["source_rule_id"]: r["id"] for r in rs}

        profiles = []
        for p in xr.findall("x:Profile", NS):
            disabled = []
            for s in p.findall("x:select", NS):
                if (s.get("selected") or "true").lower() == "false":
                    rid = source_to_native.get(s.get("idref"))
                    if rid in selected_ids: disabled.append(rid)
            profile = {"id": safe_id((p.get("id") or "profile").split("_profile_")[-1]),
                       "title": text(p.find("x:title", NS))}
            if disabled: profile["disabled_rules"] = sorted(disabled)
            selectors = {}
            for rr in p.findall("x:refine-rule", NS):
                rid = source_to_native.get(rr.get("idref"))
                selector = rr.get("selector")
                if rid in selected_ids and selector:
                    selectors[rid] = selector
            if selectors: profile["check_selectors"] = selectors
            bindings = {}
            for sv in p.findall("x:set-value", NS):
                target = sv.get("idref")
                value = text(sv)
                if target and value:
                    bindings[safe_id(target.split("_value_")[-1])] = value
            if bindings: profile["parameters"] = bindings
            if p.get("extends"):
                profile["extends"] = safe_id(p.get("extends").split("_profile_")[-1])
            profiles.append(profile)

        groups, grouping_evidence = build_groups(selected)
        metadata, unsupported_metadata = benchmark_metadata(xr)
        front_matter, original_front_matter = normalize_front_matter(xr)
        rear_matter, original_rear_matter = normalize_rear_matter(xr)
        version_node = xr.find("x:version", NS)
        benchmark_doc = {
            "benchmark": {
                "id": "rhel9-stig-full" if FULL_MODE else "rhel9-stig-review-slice",
                "use_case": "compliance",
                "title": localized_texts(xr, "title"),
                "description": localized_texts(xr, "description"),
                "language": xr.get("{http://www.w3.org/XML/1998/namespace}lang"),
                "status": benchmark_status(xr),
                "version": {
                    "value": text(version_node),
                    "time": version_node.get("time") if version_node is not None else None,
                    "update": version_node.get("update") if version_node is not None else None,
                },
                "metadata": metadata,
                "notices": benchmark_notices(xr),
                "front_matter": front_matter,
                "rear_matter": rear_matter,
                "references": benchmark_references(xr),
                "text_blocks": benchmark_text_blocks(xr),
                "platform": {
                    "id": "enterprise-linux.9",
                    "title": "Enterprise Linux 9 family",
                    "identifiers": [
                        {
                            "scheme": "cpe",
                            "binding": "uri",
                            "value": value,
                        }
                        for value in benchmark_platform_refs
                    ],
                    "applicability": {
                        "operator": "any",
                        "conditions": [
                            "platform.rhel-9",
                            "platform.rocky-9",
                            "platform.almalinux-9",
                        ],
                    },
                },
                "scoring": benchmark_scoring(xr),
                "applicability_catalog": "applicability.yaml",
                "parameters": [],
                "groups": groups,
                "profiles": profiles,
                "rules": deepcopy(selected_ids),
            }
        }
        write_yaml(OUT / "benchmark.yaml", benchmark_doc)

        applicability_registry = {}
        applicability_assessments_written = set()

        for app_id, app_title, distro_ids, cpe_value in benchmark_platform_conditions():
            assessment = benchmark_platform_assessment(app_id, app_title, distro_ids)
            applicability_registry[app_id] = assessment["assessment"]["id"]
            write_yaml(
                OUT / "assessments/applicability" / f"{assessment['assessment']['id']}.yaml",
                assessment,
            )
            applicability_assessments_written.add(assessment["assessment"]["id"])

        evidence = []
        diagnostics = []
        for item in unsupported_metadata:
            add_diagnostic(
                diagnostics,
                "warn",
                "BENCHMARK_METADATA_NOT_NORMALIZED",
                "Benchmark metadata element is preserved in evidence but is not yet normalized into native SCAP-NG fields.",
                area="benchmark.metadata",
                detail=item,
            )
        for rec in selected:
            rid = rec["id"]; rule = rec["element"]
            content_fields = rule_content(rule)
            publisher_extension = {
                "documentable": content_fields.get("documentable"),
                "false_positives": content_fields.get("false_positives"),
                "false_negatives": content_fields.get("false_negatives"),
                "mitigations": content_fields.get("mitigations"),
                "potential_impacts": content_fields.get("potential_impacts"),
                "responsibility": content_fields.get("responsibility"),
            }
            rule_identifiers = list(content_fields.get("identifiers", []))
            if rec.get("stig_id"):
                rule_identifiers.append({"scheme": "disa-stig-id", "value": rec["stig_id"]})
            if rec.get("vulnerability_id"):
                rule_identifiers.append({"scheme": "disa-vulnerability-id", "value": rec["vulnerability_id"]})

            normalized_remediation, remediation_error = normalized_fixes(rule)
            if FULL_MODE and remediation_error:
                add_diagnostic(
                    diagnostics, "error", "RULE_REMEDIATION_NOT_LOWERABLE",
                    "Source remediation could not be represented faithfully; remediation was not emitted.",
                    rule_id=rid, detail=remediation_error,
                )

            rule_doc = {"rule": {
                "id": rid,
                "version": rec.get("version"),
                "title": rec["title"],
                "severity": rec["severity"],
                "role": rec["role"],
                "weight": float(rec["weight"]) if rec["weight"] is not None else None,
                "discussion": content_fields.get("discussion"),
                "rationale": content_fields.get("rationale"),
                "extensions": {
                    "disa_stig": publisher_extension,
                },
                "warnings": content_fields.get("warnings", []),
                "identifiers": rule_identifiers,
                "references": content_fields.get("references", []),
                "requires": [
                    source_to_native.get(value, value)
                    for value in rec["requires"]
                ],
                "conflicts": [
                    source_to_native.get(value, value)
                    for value in rec["conflicts"]
                ],
                "applicability": [],
                "parameters": {},
                "remediation": (
                    None if (FULL_MODE and remediation_error)
                    else content_fields.get("remediation")
                ),
                "checks": {},
                "default_check": None,
            }}

            unresolved_requires = [
                value for value in rule_doc["rule"]["requires"]
                if value not in selected_ids
            ]
            unresolved_conflicts = [
                value for value in rule_doc["rule"]["conflicts"]
                if value not in selected_ids
            ]
            if FULL_MODE and unresolved_requires:
                add_diagnostic(
                    diagnostics, "error", "RULE_REQUIRES_TARGET_UNRESOLVED",
                    "One or more Rule dependency targets could not be resolved to Benchmark Rule identities.",
                    rule_id=rid, detail=unresolved_requires,
                )
            if FULL_MODE and unresolved_conflicts:
                add_diagnostic(
                    diagnostics, "error", "RULE_CONFLICT_TARGET_UNRESOLVED",
                    "One or more Rule conflict targets could not be resolved to Benchmark Rule identities.",
                    rule_id=rid, detail=unresolved_conflicts,
                )

            if rec["platforms"]:
                if len(rec["platforms"]) != 1:
                    if FULL_MODE:
                        add_diagnostic(
                            diagnostics, "error", "RULE_APPLICABILITY_MULTIPLE_PREDICATES_UNSUPPORTED",
                            "Rule has multiple source applicability predicates; current v003 lowering requires explicit design support.",
                            rule_id=rid,
                        )
                        rec_platform_error = True
                    else:
                        raise RuntimeError(f"{rid}: multiple Rule applicability predicates not yet supported")
                else:
                    rec_platform_error = False
                if rec_platform_error:
                    platform_node = None
                else:
                    source_platform_id = rec["platforms"][0].lstrip("#")
                    platform_node = platform_nodes.get(source_platform_id)
                    if platform_node is None:
                        if FULL_MODE:
                            add_diagnostic(
                                diagnostics, "error", "RULE_APPLICABILITY_SOURCE_NOT_FOUND",
                                "Source applicability predicate could not be resolved.",
                                rule_id=rid, source_id=source_platform_id,
                            )
                            rec_platform_error = True
                        else:
                            raise RuntimeError(f"{rid}: source platform predicate not found")
                if not rec_platform_error:
                    app_id, app_assessment, app_error = lower_source_platform(platform_node, oval_bundle)
                    if app_error:
                        if FULL_MODE:
                            add_diagnostic(
                                diagnostics, "error", "RULE_APPLICABILITY_LOWERING_UNSUPPORTED",
                                "Rule applicability could not be represented faithfully by the current v003 lowerer.",
                                rule_id=rid, detail=app_error,
                            )
                            rec_platform_error = True
                        else:
                            raise RuntimeError(f"{rid}: applicability lowering failed: {app_error}")
                if not rec_platform_error:
                    app_definition_id = source_platform_definition_id(platform_node)
                else:
                    app_definition_id = None
                if app_definition_id:
                    oval_descriptive_metadata_diagnostics(
                        oval_bundle,
                        app_definition_id,
                        rid,
                        app_assessment["assessment"]["id"],
                        diagnostics,
                    )
                if not rec_platform_error:
                    rule_doc["rule"]["applicability"] = [app_id]
                    app_assessment_id = app_assessment["assessment"]["id"]
                    applicability_registry[app_id] = app_assessment_id
                else:
                    app_assessment_id = None
                if app_assessment_id and app_assessment_id not in applicability_assessments_written:
                    write_yaml(
                        OUT / "assessments/applicability" / f"{app_assessment_id}.yaml",
                        app_assessment,
                    )
                    applicability_assessments_written.add(app_assessment_id)

            checks = {}
            definition_to_assessment = {}
            definition_failures = {}
            for c in rec["checks"]:
                selector = (c.get("selector") or "").strip() or "default"
                if check_kind(c) == "manual":
                    aid = f"{rid}.manual"
                    procedure = text(c.find("x:check-content", NS))
                    write_yaml(OUT / "assessments/manual" / f"{rid}.manual.assessment.yaml",
                               {"assessment": {
                                   "id": aid,
                                   "version": 1,
                                   "assessment_title": None,
                                   "mode": "manual",
                                   "class": "compliance",
                                   "purpose": "assessment",
                                   "procedure": procedure,
                                   "inputs": [],
                                   "evidence": [],
                               }})
                    checks[selector] = aid
                    continue

                ref = c.find("x:check-content-ref", NS)
                definition_id = ref.get("name")
                aid = definition_to_assessment.get(definition_id)
                if definition_id in definition_failures:
                    aid = None
                elif aid is None:
                    aid = f"{rid}.automated"
                    unsupported = unsupported_definition_features(oval_bundle, definition_id)
                    if unsupported:
                        definition_failures[definition_id] = unsupported
                        if FULL_MODE:
                            add_diagnostic(
                                diagnostics, "error", "AUTOMATED_ASSESSMENT_UNSUPPORTED_FEATURES",
                                "Automated source Assessment was not emitted because the source uses one or more constructs not yet supported by the current v003 lowerer.",
                                rule_id=rid,
                                assessment_id=aid,
                                source_id=definition_id,
                                unsupported_features=unsupported,
                            )
                            aid = None
                        else:
                            raise RuntimeError(
                                f"{rid}: automated lowering requires unsupported features: {unsupported}"
                            )
                    else:
                        assessment, error = lower_definition(oval_bundle, definition_id, aid)
                        if assessment is None:
                            definition_failures[definition_id] = [{"feature": "lowering_error", "detail": error}]
                            if FULL_MODE:
                                add_diagnostic(
                                    diagnostics, "error", "AUTOMATED_ASSESSMENT_NOT_LOWERABLE",
                                    "Automated source Assessment was not emitted because it cannot be represented faithfully.",
                                    rule_id=rid, assessment_id=aid, source_id=definition_id, detail=error,
                                )
                                aid = None
                            else:
                                raise RuntimeError(f"{rid}: automated lowering regressed: {error}")
                        else:
                            oval_descriptive_metadata_diagnostics(
                                oval_bundle, definition_id, rid, aid, diagnostics
                            )
                            write_yaml(OUT / "assessments/automated" / f"{rid}.automated.assessment.yaml", assessment)
                            definition_to_assessment[definition_id] = aid
                if aid is not None:
                    checks[selector] = aid

            rule_doc["rule"]["checks"] = checks
            if "default" in checks:
                rule_doc["rule"]["default_check"] = "default"
            elif len(checks) == 1:
                rule_doc["rule"]["default_check"] = next(iter(checks))
            elif FULL_MODE and not checks:
                add_diagnostic(
                    diagnostics, "error", "RULE_HAS_NO_EMITTABLE_ASSESSMENT",
                    "No Assessment could be emitted for this Rule.",
                    rule_id=rid,
                )
                rule_doc["rule"]["default_check"] = None
            elif FULL_MODE:
                add_diagnostic(
                    diagnostics, "error", "RULE_DEFAULT_CHECK_NOT_PRESERVED",
                    "Multiple remaining Assessment selections exist but the source default could not be preserved.",
                    rule_id=rid,
                )
                rule_doc["rule"]["default_check"] = None
            else:
                raise RuntimeError(f"{rid}: no source default check could be preserved")
            write_yaml(OUT / "rules" / f"{rid}.rule.yaml", rule_doc)

            evidence.append({
                "publisher_extension": {
                    "disa_stig": publisher_extension,
                },
                "native_rule_id": rid,
                "native_rule_version": rec.get("version"),
                "source_rule_id": rec["source_rule_id"],
                "source_group_id": rec.get("source_group_id"),
                "source_xccdf_version": text(rec["element"].find("x:version", NS)),
                "source_checks": [{
                    "selector": c.get("selector"),
                    "system": c.get("system"),
                    "reference": (c.find("x:check-content-ref", NS).get("name")
                                  if c.find("x:check-content-ref", NS) is not None else None),
                    "href": (c.find("x:check-content-ref", NS).get("href")
                             if c.find("x:check-content-ref", NS) is not None else None),
                } for c in rec["checks"]],
            })

        write_yaml(
            OUT / "applicability.yaml",
            {
                "applicability": [
                    {
                        "id": app_id,
                        "assessment": f"assessments/applicability/{assessment_id}.yaml",
                    }
                    for app_id, assessment_id in sorted(applicability_registry.items())
                ]
            },
        )

        write_json(
            EVIDENCE / "legacy-publication-prose.json",
            {
                "front_matter": original_front_matter,
                "rear_matter": original_rear_matter,
            },
        )

        write_json(EVIDENCE / "source-package.json", {
            "source_url": SOURCE_URL, "zip_sha256": sha256(package_bytes),
            "archive_files": sorted(str(p.relative_to(td / "pkg")) for p in files),
            "benchmark_component": xsrc, "assessment_component": osrc,
        })
        write_json(EVIDENCE / "oval-generator-metadata.json", {
            "generators": oval_generator_metadata(oval_bundle),
        })
        write_json(EVIDENCE / "rule-mapping.json", {"rules": evidence})
        write_json(EVIDENCE / "grouping.json", {"groups": grouping_evidence})
        write_json(
            EVIDENCE / "benchmark-platform-mapping.json",
            {
                "conditions": [
                    {
                        "id": app_id,
                        "title": app_title,
                        "cpe": cpe_value,
                        "assessment": app_id + ".assessment",
                    }
                    for app_id, app_title, distro_ids, cpe_value in benchmark_platform_conditions()
                ]
            },
        )
        write_json(EVIDENCE / "applicability-candidates.json", {"rules": applicability_candidates})
        write_json(EVIDENCE / "source-platform-inventory.json", {"platforms": source_platform_inventory})
        write_json(EVIDENCE / "benchmark-platform-source.json", {"platform_refs": benchmark_platform_refs})
        write_json(EVIDENCE / "manual-default-candidates.json", {"rules": manual_default_candidates})
        source_semantic_inventory = oval_semantic_inventory(oval_bundle)
        write_json(EVIDENCE / "source-semantic-inventory.json", source_semantic_inventory)
        summary = diagnostic_summary(diagnostics)
        write_json(EVIDENCE / "diagnostics.json", {
            "summary": summary,
            "source_semantic_inventory": source_semantic_inventory,
            "diagnostics": diagnostics,
        })
        package_summary = build_experimental_package(
            OUT,
            PACKAGE_OUT / PACKAGE_NAME,
        )
        write_json(EVIDENCE / "package-summary.json", package_summary)
        print("accepted native rules:", ", ".join(selected_ids))
        print(
            "package:",
            package_summary["package"],
            "objects=" + str(package_summary["object_count"]),
            "sha256=" + package_summary["sha256"],
        )
        print(
            "diagnostics:",
            " ".join(f"{level.upper()}={summary['counts'][level]}" for level in DIAGNOSTIC_LEVELS),
        )

if __name__ == "__main__":
    main()
