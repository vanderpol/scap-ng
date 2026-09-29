#!/usr/bin/env python3
"""Fail-closed audit of the raw RHEL9 XCCDF XML surface.

This does not normalize the XML. Every observed element path and attribute path
must be explicitly classified. Selected structural/provenance-only constructs
also have corpus-specific invariants checked here.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from lxml import etree as E

X="http://checklists.nist.gov/xccdf/1.2"

# Every raw source element path observed in the pinned RHEL9 benchmark must be
# listed here. A new source construct therefore fails the audit instead of being
# silently omitted by a transform/comparator.
CLASSIFIED_PATHS={
"/Benchmark":"native+provenance",
"/Benchmark/status":"native",
"/Benchmark/title":"native",
"/Benchmark/description":"native",
"/Benchmark/notice":"native",
"/Benchmark/front-matter":"native-normalized",
"/Benchmark/metadata":"native",
"/Benchmark/metadata/creator":"native",
"/Benchmark/metadata/publisher":"native",
"/Benchmark/metadata/contributor":"native",
"/Benchmark/metadata/source":"native",
"/Benchmark/plain-text":"native",
"/Benchmark/platform":"native-applicability",
"/Benchmark/reference":"native",
"/Benchmark/reference/publisher":"native",
"/Benchmark/reference/source":"native",
"/Benchmark/rear-matter":"native-normalized",
"/Benchmark/version":"native",
"/Benchmark/Profile":"native-profile",
"/Benchmark/Profile/title":"native",
"/Benchmark/Profile/description":"approved-empty-wrapper",
"/Benchmark/Profile/select":"native-effective-selection",
"/Benchmark/Group":"normalized-wrapper",
"/Benchmark/Group/title":"promoted-rule-identifier",
"/Benchmark/Group/description":"approved-empty-wrapper",
"/Benchmark/Group/Rule":"native-rule",
"/Benchmark/Group/Rule/version":"native-rule-identifier",
"/Benchmark/Group/Rule/title":"native",
"/Benchmark/Group/Rule/description":"native-structured-extension",
"/Benchmark/Group/Rule/reference":"native",
"/Benchmark/Group/Rule/reference/title":"native",
"/Benchmark/Group/Rule/reference/publisher":"native",
"/Benchmark/Group/Rule/reference/type":"native",
"/Benchmark/Group/Rule/reference/subject":"native",
"/Benchmark/Group/Rule/reference/identifier":"native",
"/Benchmark/Group/Rule/ident":"native",
"/Benchmark/Group/Rule/fixtext":"native-remediation-guidance",
"/Benchmark/Group/Rule/fix":"approved-empty-fix-anchor",
"/Benchmark/Group/Rule/check":"native-check-selector",
"/Benchmark/Group/Rule/check/check-content-ref":"provenance+assessment-binding",
"/Benchmark/Group/Rule/check/check-content":"native-manual-procedure",
"/Benchmark/Group/Rule/platform":"native-applicability",
"/Benchmark/platform-specification":"native-applicability+provenance",
"/Benchmark/platform-specification/platform":"native-applicability+provenance",
"/Benchmark/platform-specification/platform/title":"native-applicability-title",
"/Benchmark/platform-specification/platform/logical-test":"native-applicability-expression",
"/Benchmark/platform-specification/platform/logical-test/check-fact-ref":"provenance+assessment-binding",
}

CLASSIFIED_ATTRS={
"/Benchmark@id":"normalized-id+provenance",
"/Benchmark@lang":"native",
"/Benchmark@style":"legacy-serialization",
"/Benchmark/status@date":"native",
"/Benchmark/notice@id":"native",
"/Benchmark/notice@lang":"native",
"/Benchmark/front-matter@lang":"native",
"/Benchmark/plain-text@id":"native",
"/Benchmark/platform@idref":"native-applicability",
"/Benchmark/reference@href":"native",
"/Benchmark/rear-matter@lang":"native",
"/Benchmark/Profile@id":"normalized-id+provenance",
"/Benchmark/Profile/select@idref":"native-effective-selection",
"/Benchmark/Profile/select@selected":"native-effective-selection",
"/Benchmark/Group@id":"promoted-vulnerability-id+provenance",
"/Benchmark/Group/Rule@id":"normalized-id+provenance",
"/Benchmark/Group/Rule@severity":"native",
"/Benchmark/Group/Rule@weight":"native",
"/Benchmark/Group/Rule/ident@system":"native-identifier-scheme",
"/Benchmark/Group/Rule/fixtext@fixref":"approved-empty-fix-anchor",
"/Benchmark/Group/Rule/fix@id":"approved-empty-fix-anchor",
"/Benchmark/Group/Rule/check@selector":"native-check-selector",
"/Benchmark/Group/Rule/check@system":"native-check-mode",
"/Benchmark/Group/Rule/check/check-content-ref@href":"provenance",
"/Benchmark/Group/Rule/check/check-content-ref@name":"provenance+assessment-binding",
"/Benchmark/Group/Rule/platform@idref":"native-applicability",
"/Benchmark/platform-specification/platform@id":"native-applicability+provenance",
"/Benchmark/platform-specification/platform/logical-test@negate":"native-applicability-expression",
"/Benchmark/platform-specification/platform/logical-test@operator":"native-applicability-expression",
"/Benchmark/platform-specification/platform/logical-test/check-fact-ref@href":"provenance",
"/Benchmark/platform-specification/platform/logical-test/check-fact-ref@id-ref":"provenance+assessment-binding",
"/Benchmark/platform-specification/platform/logical-test/check-fact-ref@system":"native-check-mode",
}

RULE_RE=re.compile(r"_rule_(SV-\d+)(r\d+)_rule$")

def local(tag):
    return E.QName(tag).localname if isinstance(tag,str) else ""

def text(e):
    if e is None:return None
    s=" ".join("".join(e.itertext()).split())
    return s or None

def walk(root):
    paths=Counter(); attrs=Counter()
    def rec(e,parent=""):
        p=f"{parent}/{local(e.tag)}"
        paths[p]+=1
        for raw in e.attrib:
            attrs[f"{p}@{E.QName(raw).localname}"]+=1
        for c in e:
            if isinstance(c.tag,str):rec(c,p)
    rec(root)
    return paths,attrs

def issue(issues,kind,**kw):
    issues.append({"kind":kind,**kw})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_xccdf",type=Path)
    ap.add_argument("--rule-mapping",type=Path,required=True)
    ap.add_argument("--platform-inventory",type=Path,required=True)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()

    root=E.parse(str(a.source_xccdf)).getroot()
    paths,attrs=walk(root)
    issues=[]

    unknown_paths=sorted(set(paths)-set(CLASSIFIED_PATHS))
    unknown_attrs=sorted(set(attrs)-set(CLASSIFIED_ATTRS))
    if unknown_paths:issue(issues,"unaccounted_element_paths",paths=unknown_paths)
    if unknown_attrs:issue(issues,"unaccounted_attribute_paths",paths=unknown_attrs)

    # Group normalization is allowed only for the exact one-Rule wrapper form.
    for g in root.findall(f"{{{X}}}Group"):
        rules=g.findall(f"{{{X}}}Rule")
        groups=g.findall(f"{{{X}}}Group")
        if len(rules)!=1 or groups:
            issue(issues,"nontrivial_group_wrapper",id=g.get("id"),
                  rule_count=len(rules),nested_group_count=len(groups))
        title=text(g.find(f"{{{X}}}title"))
        if not title or not re.fullmatch(r"SRG-[A-Za-z0-9-]+",title):
            issue(issues,"group_title_not_srg",id=g.get("id"),title=title)
        desc=text(g.find(f"{{{X}}}description"))
        if desc not in (None,"<GroupDescription></GroupDescription>"):
            issue(issues,"nonempty_group_description",id=g.get("id"),description=desc)

    # Profile descriptions are normalized away only because this corpus uses
    # empty publisher wrappers. Any real profile prose becomes an error.
    for p in root.findall(f"{{{X}}}Profile"):
        desc=text(p.find(f"{{{X}}}description"))
        if desc not in (None,"<ProfileDescription></ProfileDescription>"):
            issue(issues,"nonempty_profile_description",id=p.get("id"),description=desc)

    # Empty <fix> nodes are linkage anchors for fixtext, not implementations.
    # Require exact sibling linkage before allowing that normalization.
    for rule in root.findall(f"{{{X}}}Group/{{{X}}}Rule"):
        fixes=rule.findall(f"{{{X}}}fix")
        fixtexts=rule.findall(f"{{{X}}}fixtext")
        fix_by_id={f.get("id"):f for f in fixes}
        for f in fixes:
            if list(f) or text(f) is not None or set(f.attrib)!={"id"}:
                issue(issues,"nonempty_or_semantic_fix",rule=rule.get("id"),
                      attributes=dict(f.attrib),text=text(f),child_count=len(f))
        for ft in fixtexts:
            ref=ft.get("fixref")
            if not ref or ref not in fix_by_id:
                issue(issues,"dangling_fixtext_fixref",rule=rule.get("id"),fixref=ref)

    # Every raw check-content-ref tuple must survive verbatim in provenance.
    mapping=json.loads(a.rule_mapping.read_text(encoding="utf-8"))
    by_rule={x["native_rule_id"]:x for x in mapping.get("rules",[])}
    for rule in root.findall(f"{{{X}}}Group/{{{X}}}Rule"):
        m=RULE_RE.search(rule.get("id") or "")
        if not m:
            issue(issues,"unrecognized_source_rule_id",id=rule.get("id"));continue
        rid=m.group(1)
        observed=[]
        for chk in rule.findall(f"{{{X}}}check"):
            ref=chk.find(f"{{{X}}}check-content-ref")
            if ref is None:continue
            observed.append({
                "selector":chk.get("selector") or "",
                "system":chk.get("system"),
                "href":ref.get("href"),
                "reference":ref.get("name"),
            })
        expected=(by_rule.get(rid) or {}).get("source_checks")
        if expected!=observed:
            issue(issues,"check_reference_provenance_mismatch",rule=rid,
                  source=observed,evidence=expected)

    # The complete source platform-specification tree is retained in provenance.
    # Applicability assessment behavior is checked separately by OVAL round-trip.
    inv=json.loads(a.platform_inventory.read_text(encoding="utf-8"))
    evidenced={x.get("source_id") for x in inv.get("platforms",[])}
    observed={p.get("id") for p in root.xpath(
        "./*[local-name()='platform-specification']/*[local-name()='platform']")}
    if observed!=evidenced:
        issue(issues,"platform_provenance_set_mismatch",
              source=sorted(observed),evidence=sorted(evidenced))

    result={
        "format":"scap-ng-xccdf-raw-surface-audit-0.1",
        "pass":not issues,
        "issue_count":len(issues),
        "issues":issues,
        "source_surface":{
            "element_path_count":len(paths),
            "attribute_path_count":len(attrs),
            "element_instance_count":sum(paths.values()),
            "attribute_instance_count":sum(attrs.values()),
        },
        "classification":{
            "element_paths":{k:CLASSIFIED_PATHS[k] for k in sorted(paths) if k in CLASSIFIED_PATHS},
            "attribute_paths":{k:CLASSIFIED_ATTRS[k] for k in sorted(attrs) if k in CLASSIFIED_ATTRS},
        },
    }
    out=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(out,encoding="utf-8")
    print(out,end="")
    raise SystemExit(0 if result["pass"] else 1)

if __name__=="__main__":main()
