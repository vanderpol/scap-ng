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

def find_by_id(root, item_id, suffix):
    if not item_id: return None
    return next((n for n in root.iter() if n.get("id") == item_id and local(n.tag).endswith(suffix)), None)

def lower_simple_definition(oroot, definition_id, assessment_id):
    definition = next((n for n in oroot.iter() if local(n.tag) == "definition" and n.get("id") == definition_id), None)
    if definition is None: return None, "definition_not_found"
    criteria = next((c for c in definition if local(c.tag) == "criteria"), None)
    if criteria is None: return None, "missing_criteria"
    children = [c for c in criteria if local(c.tag) in ("criterion", "criteria", "extend_definition")]
    if len(children) != 1 or local(children[0].tag) != "criterion":
        return None, "complex_criteria"
    if (criteria.get("negate") or "false").lower() == "true" or (children[0].get("negate") or "false").lower() == "true":
        return None, "negated_criteria"
    test_ref = children[0].get("test_ref")
    test = next((n for n in oroot.iter() if n.get("id") == test_ref and local(n.tag).endswith("_test")), None)
    if test is None: return None, "test_not_found"
    test_name = local(test.tag)
    ns_uri = test.tag.split("}", 1)[0].strip("{")
    family = ns_uri.split("#")[-1].split("/")[-1]
    capability = f"{family}.{test_name[:-5] if test_name.endswith('_test') else test_name}"
    obj_ref = None; state_refs = []
    for child in test:
        if local(child.tag) == "object": obj_ref = child.get("object_ref")
        elif local(child.tag) == "state" and child.get("state_ref"): state_refs.append(child.get("state_ref"))
    obj = find_by_id(oroot, obj_ref, "_object")
    if obj is None: return None, "object_not_found"
    query = {}
    for child in obj:
        name = local(child.tag)
        if name in ("behaviors", "set", "filter"): return None, f"object_{name}_not_yet_lowered"
        if child.get("var_ref"): return None, "object_variable_not_yet_lowered"
        value = text(child)
        if value is not None:
            query[name] = ({ "operation": child.get("operation"), "value": value }
                           if child.get("operation") else value)
    expected = []
    for ref in state_refs:
        state = find_by_id(oroot, ref, "_state")
        if state is None: return None, "state_not_found"
        for child in state:
            if child.get("var_ref"): return None, "state_variable_not_yet_lowered"
            item = {"field": local(child.tag), "operation": child.get("operation") or "equals", "value": text(child)}
            if child.get("entity_check"): item["entity_check"] = child.get("entity_check")
            if child.get("datatype"): item["datatype"] = child.get("datatype")
            expected.append(item)
    return {"assessment": {
        "id": assessment_id,
        "mode": "automated",
        "collect": {"capability": capability, "select": query},
        "assert": {
            "existence": test.get("check_existence") or "at_least_one_exists",
            "check": test.get("check") or "all",
            **({"state": expected} if expected else {}),
        },
    }}, None

def automated_refs(rec):
    refs = []
    for c in rec["checks"]:
        if check_kind(c) != "automated": continue
        ref = c.find("x:check-content-ref", NS)
        if ref is None or not ref.get("name"): return None
        refs.append(((c.get("selector") or "").strip() or "default", ref.get("name")))
    return refs

def fully_lowerable(rec, oroot):
    if rec["platforms"] or rec["requires"] or rec["conflicts"]: return False
    refs = automated_refs(rec)
    if not refs: return False
    for _, definition_id in {x for x in refs}:
        assessment, _ = lower_simple_definition(oroot, definition_id, "probe")
        if assessment is None: return False
    return True

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
            raise RuntimeError(f"Only {len(selected)} fully lowerable Rules found; refusing partial review slice")

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
            profiles.append(profile)

        write_yaml(OUT / "benchmark.yaml", {"benchmark": {
            "id": "rhel9-stig-review-slice",
            "title": "Red Hat Enterprise Linux 9 STIG — SCAP-NG 003 review slice",
            "version": text(xr.find("x:version", NS)),
            "platform": "rhel.9",
            "profiles": profiles,
            "rules": deepcopy(selected_ids),
        }})

        evidence = []; diagnostics = []
        for rec in selected:
            rid = rec["id"]; rule = rec["element"]
            policy = {"policy": {"id": rid, "title": rec["title"], "severity": rec["severity"]}}
            if rec["role"]: policy["policy"]["role"] = rec["role"]
            if rec["weight"]: policy["policy"]["weight"] = float(rec["weight"])

            checks = {}
            definition_to_assessment = {}
            for c in rec["checks"]:
                selector = (c.get("selector") or "").strip() or "default"
                if check_kind(c) == "manual":
                    aid = f"{rid}.manual"
                    procedure = text(c.find("x:check-content", NS))
                    write_yaml(OUT / "assessments/manual" / f"{rid}.manual.assessment.yaml",
                               {"assessment": {"id": aid, "mode": "manual", "procedure": procedure}})
                    checks[selector] = aid
                    continue

                ref = c.find("x:check-content-ref", NS)
                definition_id = ref.get("name")
                aid = definition_to_assessment.get(definition_id)
                if aid is None:
                    aid = f"{rid}.automated"
                    assessment, error = lower_simple_definition(oroot, definition_id, aid)
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
        write_json(EVIDENCE / "diagnostics.json", {"diagnostics": diagnostics})
        print("accepted native rules:", ", ".join(selected_ids))

if __name__ == "__main__":
    main()
