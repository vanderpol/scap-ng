#!/usr/bin/env python3
"""Generate a small, clean, semantically exact SCAP-NG 003 RHEL 9 review slice.

Only source paths fully understood by this checkpoint are emitted. Legacy
lineage is written separately under evidence/.
"""

from __future__ import annotations
import hashlib, json, re, shutil, tempfile, urllib.request, zipfile
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

SOURCE_URL = (
    "https://raw.githubusercontent.com/niwc-atlantic/scap-content-library/main/Current/"
    "U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip"
)
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/iterations/003/source/split-policy-assessment/rhel9-review-slice"
EVIDENCE = ROOT / "research/iterations/003/evidence/rhel9-review-slice"
XCCDF = "http://checklists.nist.gov/xccdf/1.2"
NS = {"x": XCCDF}

def local(tag): return tag.rsplit("}", 1)[-1]
def text(node):
    if node is None: return None
    s = " ".join("".join(node.itertext()).split())
    return s or None
def safe_id(s): return re.sub(r"[^A-Za-z0-9_.-]+", "-", s.strip()).strip("-")
def semantic_id(value, fallback):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    stop = {"the","a","an","is","are","must","be","of","to","for","with","and"}
    words = [w for w in slug.split("-") if w and w not in stop]
    return "-".join(words[:10]) or fallback
def node_title(node):
    return ((node.get("comment") or "").strip() or None) if node is not None else None
def sha256(data): return hashlib.sha256(data).hexdigest()
def write_yaml(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    class Dumper(yaml.SafeDumper):
        def ignore_aliases(self, data): return True
    path.write_text(yaml.dump(obj, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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

def native_rule_id(rule):
    version = text(rule.find("x:version", NS))
    return safe_id(version) if version else safe_id(text(rule.find("x:title", NS)) or "rule")

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
            out.append({
                "element": rule, "source_rule_id": rule.get("id"), "id": native_rule_id(rule),
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

def policy_content(rule):
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
        value = text(ref)
        if href and not any(term in href.lower() for term in ("xccdf", "oval", "ocil", "cpe.mitre.org/language")):
            item["url"] = href
        if value: item["text"] = value
        if item: references.append(item)
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

def lower_definition(oroot, definition_id, assessment_id):
    """Lower Boolean definition logic while requiring every leaf test to be exact."""
    definition = next(
        (n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == definition_id),
        None,
    )
    if definition is None:
        return None, "definition_not_found"

    assessment_title = node_title(definition)
    checks = {}
    test_to_check = {}
    used_check_ids = set()
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

        obj_ref = None
        state_refs = []
        for child in test:
            if local(child.tag) == "object":
                obj_ref = child.get("object_ref")
            elif local(child.tag) == "state" and child.get("state_ref"):
                state_refs.append(child.get("state_ref"))

        obj = find_by_id(oroot, obj_ref, "_object")
        if obj is None:
            return None, "object_not_found"

        query = {}
        for child in obj:
            name = local(child.tag)
            if name in ("behaviors", "set", "filter"):
                return None, f"object_{name}_not_yet_lowered"
            if child.get("var_ref"):
                return None, "object_variable_not_yet_lowered"
            value = text(child)
            if value is not None:
                query[name] = (
                    {"operation": child.get("operation"), "value": value}
                    if child.get("operation") else value
                )

        states = []
        state_titles = []
        for ref in state_refs:
            state = find_by_id(oroot, ref, "_state")
            if state is None:
                return None, "state_not_found"
            if node_title(state):
                state_titles.append(node_title(state))
            conditions = []
            for child in state:
                if child.get("var_ref"):
                    return None, "state_variable_not_yet_lowered"
                item = {
                    "field": local(child.tag),
                    "operation": child.get("operation") or "equals",
                    "value": text(child),
                }
                if child.get("entity_check"):
                    item["entity_check"] = child.get("entity_check")
                if child.get("datatype"):
                    item["datatype"] = child.get("datatype")
                conditions.append(item)
            if conditions:
                states.append(conditions[0] if len(conditions) == 1 else {"all": conditions})

        check_id = unique_check_id(test_title, capability)
        test_to_check[test_ref] = check_id

        assertion = {
            "title": " / ".join(state_titles) if state_titles else None,
            "existence": test.get("check_existence") or "at_least_one_exists",
            "check": test.get("check") or "all",
            "state": None,
        }
        if states:
            state_operator = (test.get("state_operator") or "AND").upper()
            if len(states) == 1:
                assertion["state"] = states[0]
            elif state_operator == "AND":
                assertion["state"] = {"all": states}
            elif state_operator == "OR":
                assertion["state"] = {"any": states}
            else:
                return None, f"unsupported_state_operator:{state_operator}"

        checks[check_id] = {
            "title": test_title,
            "collect": {
                "title": node_title(obj),
                "capability": capability,
                "select": query,
            },
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
            if (child.get("negate") or "false").lower() == "true":
                term = {"not": term}
            terms.append(term)

        if not terms:
            return None, "empty_criteria"
        if len(terms) == 1:
            expr = terms[0]
        elif operator == "AND":
            expr = {"all": terms}
        elif operator == "OR":
            expr = {"any": terms}
        else:
            return None, f"unsupported_criteria_operator:{operator}"

        if (node.get("negate") or "false").lower() == "true":
            expr = {"not": expr}
        return expr, None

    root_criteria = next((n for n in definition if local(n.tag) == "criteria"), None)
    if root_criteria is None:
        return None, "missing_criteria"

    active_definitions.add(definition_id)
    expression, error = lower_criteria(root_criteria)
    active_definitions.remove(definition_id)
    if error:
        return None, error

    return {"assessment": {
        "id": assessment_id,
        "title": assessment_title,
        "mode": "automated",
        "checks": checks,
        "evaluate": expression,
    }}, None

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
    haystack = " ".join(filter(None, [
        rec.get("title"),
        text(rec["element"].find("x:description", NS)),
        text(rec["element"].find("x:fixtext", NS)),
    ])).lower()
    topics = [
        ("ssh", "SSH", ("ssh", "sshd", "secure shell")),
        ("password-policy", "Password Policy", ("password", "pam", "pwquality", "login.defs")),
        ("auditing", "Auditing", ("audit", "audisp", "journald", "log")),
        ("account-management", "Account Management", ("account", "user", "group", "uid", "gid")),
        ("services", "Services", ("service", "systemd", "daemon", "target")),
        ("filesystem", "Filesystem and Permissions", ("file", "directory", "permission", "owner", "mount")),
        ("networking", "Networking", ("network", "firewall", "ipv4", "ipv6", "tcp", "udp")),
        ("cryptography", "Cryptography", ("crypto", "fips", "cipher", "certificate", "key")),
    ]
    for gid, title, needles in topics:
        if any(n in haystack for n in needles):
            return gid, title
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

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.rmtree(EVIDENCE, ignore_errors=True)
    OUT.mkdir(parents=True); EVIDENCE.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as t:
        td = Path(t); zp = td / "source.zip"
        urllib.request.urlretrieve(SOURCE_URL, zp); package_bytes = zp.read_bytes()
        with zipfile.ZipFile(zp) as zf: zf.extractall(td / "pkg")
        files = [p for p in (td / "pkg").rglob("*") if p.is_file()]
        xr, oroot, xsrc, osrc = load_source_components(files)
        rs = records(xr)

        # First accepted slice: three Rules for which this checkpoint can
        # preserve every check-selection and automated-assessment semantic it emits.
        selected = [r for r in rs if fully_lowerable(r, oroot)][:3]
        if len(selected) < 3:
            from collections import Counter
            reasons = Counter(lowerability_reason(r, oroot) for r in rs)
            summary = ", ".join(f"{k}={v}" for k, v in reasons.most_common(12))
            fix_systems = Counter(
                (fix.get("system") or "<none>")
                for r in rs
                for fix in r["element"].findall("x:fix", NS)
            )
            fix_summary = ", ".join(f"{k}={v}" for k, v in fix_systems.most_common(8))
            raise RuntimeError(
                f"Only {len(selected)} fully lowerable Rules found; refusing partial review slice. "
                f"Top rejection reasons: {summary}. Source remediation systems: {fix_summary}"
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
        version_node = xr.find("x:version", NS)
        benchmark_doc = {
            "benchmark": {
                "id": "rhel9-stig-review-slice",
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
                "front_matter": localized_texts(xr, "front-matter"),
                "rear_matter": localized_texts(xr, "rear-matter"),
                "references": benchmark_references(xr),
                "text_blocks": benchmark_text_blocks(xr),
                "platform": {
                    "id": "rhel.9",
                    "title": "Red Hat Enterprise Linux 9",
                    "identifiers": [
                        {
                            "scheme": "cpe",
                            "version": "2.3",
                            "value": "cpe:2.3:o:redhat:enterprise_linux:9:*:*:*:*:*:*:*",
                        }
                    ],
                    "assessment": None,
                },
                "scoring": benchmark_scoring(xr),
                "parameters": [],
                "groups": groups,
                "profiles": profiles,
                "rules": deepcopy(selected_ids),
            }
        }
        write_yaml(OUT / "benchmark.yaml", benchmark_doc)

        evidence = []
        diagnostics = [
            {
                "area": "benchmark.metadata",
                "status": "requires_review",
                "reason": "benchmark metadata element is not yet normalized",
                "detail": item,
            }
            for item in unsupported_metadata
        ]
        for rec in selected:
            rid = rec["id"]; rule = rec["element"]
            content_fields = policy_content(rule)
            policy = {"policy": {
                "id": rid,
                "title": rec["title"],
                "severity": rec["severity"],
                "role": rec["role"],
                "weight": float(rec["weight"]) if rec["weight"] is not None else None,
                "discussion": content_fields.get("discussion"),
                "rationale": content_fields.get("rationale"),
                "documentable": content_fields.get("documentable"),
                "false_positives": content_fields.get("false_positives"),
                "false_negatives": content_fields.get("false_negatives"),
                "mitigations": content_fields.get("mitigations"),
                "potential_impacts": content_fields.get("potential_impacts"),
                "responsibility": content_fields.get("responsibility"),
                "warnings": content_fields.get("warnings", []),
                "identifiers": content_fields.get("identifiers", []),
                "references": content_fields.get("references", []),
                "requires": [],
                "conflicts": [],
                "applicability": [],
                "parameters": {},
                "remediation": content_fields.get("remediation"),
                "checks": {},
                "default_check": None,
            }}

            checks = {}
            definition_to_assessment = {}
            for c in rec["checks"]:
                selector = (c.get("selector") or "").strip() or "default"
                if check_kind(c) == "manual":
                    aid = f"{rid}.manual"
                    procedure = text(c.find("x:check-content", NS))
                    write_yaml(OUT / "assessments/manual" / f"{rid}.manual.assessment.yaml",
                               {"assessment": {
                                   "id": aid,
                                   "title": f"Manual assessment for {rid}",
                                   "mode": "manual",
                                   "procedure": procedure,
                                   "inputs": [],
                                   "evidence": [],
                               }})
                    checks[selector] = aid
                    continue

                ref = c.find("x:check-content-ref", NS)
                definition_id = ref.get("name")
                aid = definition_to_assessment.get(definition_id)
                if aid is None:
                    aid = f"{rid}.automated"
                    assessment, error = lower_definition(oroot, definition_id, aid)
                    if assessment is None:
                        raise RuntimeError(f"{rid}: automated lowering regressed: {error}")
                    write_yaml(OUT / "assessments/automated" / f"{rid}.automated.assessment.yaml", assessment)
                    definition_to_assessment[definition_id] = aid
                checks[selector] = aid

            policy["policy"]["checks"] = checks
            if "default" in checks: policy["policy"]["default_check"] = "default"
            elif len(checks) == 1: policy["policy"]["default_check"] = next(iter(checks))
            else: raise RuntimeError(f"{rid}: no source default check could be preserved")
            write_yaml(OUT / "policy" / f"{rid}.policy.yaml", policy)

            evidence.append({
                "native_rule_id": rid,
                "source_rule_id": rec["source_rule_id"],
                "source_checks": [{
                    "selector": c.get("selector"),
                    "system": c.get("system"),
                    "reference": (c.find("x:check-content-ref", NS).get("name")
                                  if c.find("x:check-content-ref", NS) is not None else None),
                    "href": (c.find("x:check-content-ref", NS).get("href")
                             if c.find("x:check-content-ref", NS) is not None else None),
                } for c in rec["checks"]],
            })

        write_json(EVIDENCE / "source-package.json", {
            "source_url": SOURCE_URL, "zip_sha256": sha256(package_bytes),
            "archive_files": sorted(str(p.relative_to(td / "pkg")) for p in files),
            "benchmark_component": xsrc, "assessment_component": osrc,
        })
        write_json(EVIDENCE / "rule-mapping.json", {"rules": evidence})
        write_json(EVIDENCE / "grouping.json", {"groups": grouping_evidence})
        write_json(EVIDENCE / "diagnostics.json", {"diagnostics": diagnostics})
        print("accepted native rules:", ", ".join(selected_ids))

if __name__ == "__main__":
    main()
