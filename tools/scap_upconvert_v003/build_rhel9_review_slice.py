#!/usr/bin/env python3
"""Build the first clean SCAP-NG 003 RHEL 9 review slice from authoritative SCAP 1.4.

This script consumes the published ZIP directly, emits only semantics that can
be normalized cleanly, and records legacy lineage separately under evidence/.
"""

from __future__ import annotations
import hashlib, json, re, tempfile, urllib.request, zipfile
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

def local(tag): return tag.rsplit("}",1)[-1]
def text(node):
    if node is None: return None
    s=" ".join("".join(node.itertext()).split())
    return s or None
def safe_id(s):
    return re.sub(r"[^A-Za-z0-9_.-]+","-",s.strip()).strip("-")
def sha256(data): return hashlib.sha256(data).hexdigest()
def write_yaml(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(obj,sort_keys=False,allow_unicode=True,width=100),encoding="utf-8")
def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def find_component(files, needle):
    ms=[p for p in files if needle in p.name.lower() and p.suffix.lower()==".xml"]
    if not ms: raise RuntimeError(f"No {needle} XML component found")
    ms.sort(key=lambda p:(len(p.name),p.name))
    return ms[0]
def native_rule_id(rule):
    version=text(rule.find("x:version",NS))
    if version: return safe_id(version)
    return safe_id((text(rule.find("x:title",NS)) or "rule").lower())[:80]
def check_kind(check):
    selector=(check.get("selector") or "").strip().lower()
    system=(check.get("system") or "").lower()
    inline=text(check.find("x:check-content",NS))
    if selector=="manual" or "ocil" in system or inline: return "manual"
    return "automated"

def records(root):
    out=[]
    for group in root.findall(".//x:Group",NS):
        for rule in group.findall("x:Rule",NS):
            checks=rule.findall("x:check",NS)
            out.append({
                "element":rule,
                "source_rule_id":rule.get("id"),
                "id":native_rule_id(rule),
                "title":text(rule.find("x:title",NS)),
                "severity":rule.get("severity"),
                "role":rule.get("role"),
                "weight":rule.get("weight"),
                "checks":checks,
                "has_automated":any(check_kind(c)=="automated" for c in checks),
                "has_manual":any(check_kind(c)=="manual" for c in checks),
                "has_rule_platform":bool(rule.findall("x:platform",NS)),
                "has_requires":bool(rule.findall("x:requires",NS)),
                "has_conflicts":bool(rule.findall("x:conflicts",NS)),
            })
    return out

def choose(rs):
    chosen=[]
    def add(r,why):
        if r and r["source_rule_id"] not in {x[0]["source_rule_id"] for x in chosen}: chosen.append((r,why))
    add(next((r for r in rs if r["has_automated"] and r["has_manual"]),None),"selectable automated/manual checks")
    add(next((r for r in rs if r["has_rule_platform"] and r["has_automated"]),None),"rule applicability")
    add(next((r for r in rs if r["has_automated"] and not r["has_manual"] and not r["has_rule_platform"]),None),"simple automated rule")
    add(next((r for r in rs if r["has_requires"] or r["has_conflicts"]),None),"rule dependency semantics")
    return chosen[:5]

def find_by_id(root,item_id,suffix):
    for n in root.iter():
        if n.get("id")==item_id and local(n.tag).endswith(suffix): return n
    return None

def simple_oval_assessment(oroot,definition_id,assessment_id):
    definition=find_by_id(oroot,definition_id,"definition")
    if definition is None:
        for n in oroot.iter():
            if local(n.tag)=="definition" and n.get("id")==definition_id: definition=n; break
    if definition is None: return None,"referenced automated definition was not found"
    criteria=next((c for c in definition if local(c.tag)=="criteria"),None)
    if criteria is None: return None,"definition has no criteria"
    children=[c for c in criteria if local(c.tag) in ("criterion","criteria","extend_definition")]
    if len(children)!=1 or local(children[0].tag)!="criterion": return None,"first implementation supports exactly one criterion"
    test_ref=children[0].get("test_ref")
    test=next((n for n in oroot.iter() if n.get("id")==test_ref and local(n.tag).endswith("_test")),None)
    if test is None: return None,"criterion test was not found"
    test_name=local(test.tag)
    ns_uri=test.tag.split("}",1)[0].strip("{")
    family=ns_uri.split("#")[-1].split("/")[-1]
    capability=f"{family}.{test_name[:-5] if test_name.endswith('_test') else test_name}"
    obj_ref=None; state_refs=[]
    for child in test:
        if local(child.tag)=="object": obj_ref=child.get("object_ref")
        elif local(child.tag)=="state" and child.get("state_ref"): state_refs.append(child.get("state_ref"))
    obj=find_by_id(oroot,obj_ref,"_object") if obj_ref else None
    if obj is None: return None,"object was not found"
    query={}
    for child in obj:
        name=local(child.tag)
        if name in ("behaviors","set","filter"): return None,f"object uses unsupported {name} semantics"
        if child.get("var_ref"): return None,"object uses a variable reference"
        value=text(child)
        if value is not None:
            query[name]={"value":value,"operation":child.get("operation")} if child.get("operation") else value
    expected=[]
    for ref in state_refs:
        state=find_by_id(oroot,ref,"_state")
        if state is None: return None,"state was not found"
        for child in state:
            if child.get("var_ref"): return None,"state uses a variable reference"
            item={"field":local(child.tag),"operation":child.get("operation") or "equals","value":text(child)}
            if child.get("entity_check"): item["entity_check"]=child.get("entity_check")
            expected.append(item)
    return {"assessment":{
        "id":assessment_id,"mode":"automated",
        "collect":{"capability":capability,"query":query},
        "evaluate":{"existence":test.get("check_existence") or "at_least_one_exists","check":test.get("check") or "all","expected":expected}
    }},None

def main():
    OUT.mkdir(parents=True,exist_ok=True); EVIDENCE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        td=Path(t); zp=td/"source.zip"; urllib.request.urlretrieve(SOURCE_URL,zp); data=zp.read_bytes()
        with zipfile.ZipFile(zp) as zf: zf.extractall(td/"pkg")
        files=[p for p in (td/"pkg").rglob("*") if p.is_file()]
        xp=find_component(files,"xccdf"); op=find_component(files,"oval")
        xr=ET.parse(xp).getroot(); oroot=ET.parse(op).getroot()
        rs=records(xr); selected=choose(rs)
        source_to_native={r["source_rule_id"]:r["id"] for r in rs}
        profiles=[]
        for p in xr.findall("x:Profile",NS):
            disabled=[]
            for s in p.findall("x:select",NS):
                if (s.get("selected") or "true").lower()=="false":
                    rid=source_to_native.get(s.get("idref"))
                    if rid: disabled.append(rid)
            obj={"id":safe_id((p.get("id") or "profile").split("_profile_")[-1]),"title":text(p.find("x:title",NS))}
            if disabled: obj["disabled_rules"]=sorted(disabled)
            profiles.append(obj)
        ids=[r["id"] for r,_ in selected]
        write_yaml(OUT/"benchmark.yaml",{"benchmark":{
            "id":"rhel9-stig-review-slice",
            "title":"Red Hat Enterprise Linux 9 STIG — SCAP-NG 003 review slice",
            "version":text(xr.find("x:version",NS)),
            "platform":"rhel.9",
            "scope":{"kind":"conversion-review-slice","rules":ids},
            "profiles":profiles,"rules":ids
        }})
        apps=[]; ev=[]; diags=[]
        for rec,why in selected:
            rule=rec["element"]; rid=rec["id"]
            policy={"policy":{"id":rid,"title":rec["title"],"severity":rec["severity"]}}
            if rec["role"]: policy["policy"]["role"]=rec["role"]
            if rec["weight"]: policy["policy"]["weight"]=float(rec["weight"])
            checks={}
            manuals=[c for c in rec["checks"] if check_kind(c)=="manual"]
            autos=[c for c in rec["checks"] if check_kind(c)=="automated"]
            if manuals:
                proc=text(manuals[0].find("x:check-content",NS))
                aid=f"{rid}.manual"
                write_yaml(OUT/"assessments/manual"/f"{rid}.manual.assessment.yaml",{"assessment":{"id":aid,"mode":"manual","procedure":proc}})
                checks["manual"]=aid
            for i,c in enumerate(autos):
                ref=c.find("x:check-content-ref",NS); did=ref.get("name") if ref is not None else None
                selector=(c.get("selector") or "default").strip() or "default"
                aid=f"{rid}.automated" if i==0 else f"{rid}.automated-{i+1}"
                assessment,error=simple_oval_assessment(oroot,did,aid) if did else (None,"automated check has no content reference")
                if assessment:
                    write_yaml(OUT/"assessments/automated"/f"{aid}.assessment.yaml",assessment)
                    checks[selector]=aid
                    if selector=="default": checks.setdefault("automated",aid)
                else:
                    diags.append({"rule":rid,"area":"automated-assessment","status":"requires_review","reason":error})
            policy["policy"]["checks"]=checks
            for preferred in ("default","automated","manual"):
                if preferred in checks: policy["policy"]["default_check"]=preferred; break
            platforms=[p.get("idref") for p in rule.findall("x:platform",NS) if p.get("idref")]
            if platforms:
                app_id=f"{rid}.applicable"
                policy["policy"]["applicability"]=[app_id]
                apps.append({"id":app_id,"assessment":f"{app_id}.assessment"})
                diags.append({"rule":rid,"area":"applicability-assessment","status":"requires_review","reason":"source platform predicate requires semantic lowering before native assessment emission"})
            write_yaml(OUT/"policy"/f"{rid}.policy.yaml",policy)
            ev.append({"native_rule_id":rid,"selection_reason":why,"source_rule_id":rec["source_rule_id"],
                "source_check_refs":[{
                    "selector":c.get("selector"),"system":c.get("system"),
                    "href":(c.find("x:check-content-ref",NS).get("href") if c.find("x:check-content-ref",NS) is not None else None),
                    "name":(c.find("x:check-content-ref",NS).get("name") if c.find("x:check-content-ref",NS) is not None else None)
                } for c in rec["checks"]],"source_platform_refs":platforms})
        if apps: write_yaml(OUT/"applicability.yaml",{"applicability":apps})
        write_json(EVIDENCE/"source-package.json",{"source_url":SOURCE_URL,"zip_sha256":sha256(data),
            "archive_files":sorted(str(p.relative_to(td/"pkg")) for p in files),
            "selected_xccdf_component":xp.name,"selected_oval_component":op.name})
        write_json(EVIDENCE/"rule-mapping.json",{"rules":ev})
        write_json(EVIDENCE/"diagnostics.json",{"diagnostics":diags})
        print(f"emitted {len(selected)} representative policies; diagnostics: {len(diags)}")

if __name__=="__main__":
    main()
