#!/usr/bin/env python3
"""Audit RHEL 9 source XCCDF semantics against iteration-003 NG source.

This is intentionally independent of the v003 converter's platform-title
mapping so converter heuristic defects are visible here rather than repeated.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import yaml

PLATFORM_MAP = {
    "xccdf_mil.disa.stig_platform_LinuxBIND": "linux.bind-installed",
    "xccdf_mil.disa.stig_platform_LinuxNFSMounts": "linux.nfs-mounted",
    "xccdf_mil.disa.stig_platform_LinuxIPv6enabled": "linux.ipv6-enabled",
    "xccdf_mil.disa.stig_platform_LinuxLibreswan": "linux.libreswan-installed",
    "xccdf_mil.disa.stig_platform_LinuxBIOS": "linux.bios-boot",
    "xccdf_mil.disa.stig_platform_LinuxGnome": "linux.gnome-installed",
    "xccdf_navy.navwar.niwcatlantic.scc_platform_LinuxGnome": "linux.gnome-installed",
    "xccdf_mil.disa.stig_platform_LinuxNoNFSMounts": "linux.nfs-not-mounted",
    "xccdf_mil.disa.stig_platform_LinuxTFTP": "linux.tftp-installed",
    "xccdf_mil.disa.stig_platform_LinuxUEFI": "linux.uefi-boot",
    "xccdf_mil.disa.stig_platform_RHEL_9_NotFIPS": "linux.fips-disabled",
    "xccdf_mil.disa.stig_platform_LinuxKernelDumps": "linux.kernel-dumps-enabled",
    "xccdf_mil.disa.stig_platform_LinuxPostfix": "linux.postfix-installed",
    "xccdf_mil.disa.stig_platform_LinuxAutofs": "linux.autofs-installed",
    "xccdf_navy.navwar.niwcatlantic.scc_platform_isNotVirtualMachine2": "hardware.bare-metal",
}

CPE_TO_NG = {
    "cpe:/o:redhat:enterprise_linux:9.0": "platform.rhel-9",
    "cpe:/o:rocky:rocky:9": "platform.rocky-9",
    "cpe:/o:almalinux:almalinux:9": "platform.almalinux-9",
}

RULE_RE = re.compile(r"_rule_(SV-\d+)(r\d+)_rule$")
PROFILE_PREFIX = "xccdf_mil.disa.stig_profile_"

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def rule_identity(source_id: str):
    m = RULE_RE.search(source_id or "")
    if not m:
        raise ValueError(f"unrecognized DISA Rule id: {source_id}")
    return m.group(1), m.group(2)

def profile_id(source_id: str):
    return source_id[len(PROFILE_PREFIX):] if source_id.startswith(PROFILE_PREFIX) else source_id

def norm_text(value):
    if value is None:
        return None
    value=" ".join(str(value).split())
    return value or None

def disa_tag(description, tag):
    if not description:
        return None
    m=re.search(rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>",description,re.S|re.I)
    return norm_text(m.group(1)) if m else None

def tree_children(node,name):
    return [x for x in node.get("children",[]) if x.get("name")==name]

def tree_text(node):
    if node is None:
        return None
    parts=[]
    if node.get("text"):
        parts.append(node["text"])
    for child in node.get("children",[]):
        v=tree_text(child)
        if v: parts.append(v)
    return norm_text(" ".join(parts))

def tree_localized(node,name):
    out=[]
    for x in tree_children(node,name):
        out.append({
            "text":tree_text(x),
            "language":(x.get("attributes") or {}).get("lang"),
        })
    return out

def source_benchmark_metadata(tree):
    out={}
    for md in tree_children(tree,"metadata"):
        for x in md.get("children",[]):
            key=x.get("name")
            value=tree_text(x)
            if value is not None:
                out.setdefault(key,[]).append(value)
    return out

def normalize_front(items):
    out=[]
    for item in items:
        value=item.get("text")
        if value:
            value=re.sub(r"enhanced with OCIL manual questions",
                         "enhanced with manual assessment procedures",value,flags=re.I)
        out.append({"text":value,"language":item.get("language")})
    return out

def normalize_rear(items):
    out=[]
    for item in items:
        value=item.get("text")
        if value:
            value=re.sub(r"\s*filename:--:[^\s]+-xccdf\.xml","",value,flags=re.I)
            value=norm_text(value)
        out.append({"text":value,"language":item.get("language")})
    return out

def native_rules(root: Path):
    out={}
    for p in sorted((root/"rules").glob("*.yaml")):
        doc=load_yaml(p)["rule"]
        out[doc["id"]]=doc
    return out

def native_manual_assessments(root: Path):
    out={}
    manual_dir=root/"assessments"/"manual"
    if not manual_dir.exists():
        return out
    for p in sorted(manual_dir.glob("*.yaml")):
        doc=load_yaml(p)["assessment"]
        out[doc["id"]]=doc
    return out

def expected_profile_disabled(source: dict, resolved_profile: dict):
    rules=source["rules"]
    selected={rule_identity(r["id"])[0]: bool(r.get("selected_default",True)) for r in rules}
    groups={g["id"]:g for g in source["groups"]}
    for action in resolved_profile.get("effective_actions",[]):
        if action.get("kind")!="select":
            continue
        value=str(action.get("attributes",{}).get("selected","true")).lower() in {"1","true"}
        for target in action.get("targets",[]):
            if target["kind"]=="rule":
                rid,_=rule_identity(target["id"])
                selected[rid]=value
            elif target["kind"]=="group":
                # RHEL9 source groups are checked below to be inert one-rule wrappers.
                group=groups[target["id"]]
                for srid in group.get("members",{}).get("rules",[]):
                    rid,_=rule_identity(srid)
                    selected[rid]=value
    return sorted(k for k,v in selected.items() if not v)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_ir",type=Path)
    ap.add_argument("ng_root",type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()

    src=json.loads(a.source_ir.read_text(encoding="utf-8"))
    bench=load_yaml(a.ng_root/"benchmark.yaml")["benchmark"]
    nr=native_rules(a.ng_root)
    manual_assessments=native_manual_assessments(a.ng_root)
    app=load_yaml(a.ng_root/"applicability.yaml").get("applicability",[])
    app_ids={x["id"] for x in app}

    issues=[]
    stats={}

    def issue(kind, **kw):
        issues.append({"kind":kind,**kw})

    # Benchmark descriptive/publication metadata. These fields do not change
    # assessment truth, but they are part of the benchmark information contract.
    sb=src["benchmark"]
    stree=sb.get("source_tree") or {}
    if bench.get("title") != tree_localized(stree,"title"):
        issue("benchmark_title_mismatch",source=tree_localized(stree,"title"),ng=bench.get("title"))
    if bench.get("description") != tree_localized(stree,"description"):
        issue("benchmark_description_mismatch",source=tree_localized(stree,"description"),ng=bench.get("description"))
    source_lang=(stree.get("attributes") or {}).get("lang")
    if bench.get("language") != source_lang:
        issue("benchmark_language_mismatch",source=source_lang,ng=bench.get("language"))

    source_status=[]
    for x in tree_children(stree,"status"):
        source_status.append({"value":tree_text(x),"date":(x.get("attributes") or {}).get("date")})
    if bench.get("status") != source_status:
        issue("benchmark_status_mismatch",source=source_status,ng=bench.get("status"))

    source_version_nodes=tree_children(stree,"version")
    if source_version_nodes:
        sv=source_version_nodes[0]
        expected_version={
            "value":tree_text(sv),
            "time":(sv.get("attributes") or {}).get("time"),
            "update":(sv.get("attributes") or {}).get("update"),
        }
        if bench.get("version") != expected_version:
            issue("benchmark_version_mismatch",source=expected_version,ng=bench.get("version"))

    source_refs=[]
    for x in tree_children(stree,"reference"):
        source_refs.append({"text":tree_text(x),"url":(x.get("attributes") or {}).get("href")})
    if bench.get("references") != source_refs:
        issue("benchmark_reference_mismatch",source=source_refs,ng=bench.get("references"))

    source_notices=[]
    for x in tree_children(stree,"notice"):
        attrs=x.get("attributes") or {}
        source_notices.append({
            "id":re.sub(r"[^A-Za-z0-9_.-]+","-",attrs.get("id") or "notice").strip("-"),
            "text":tree_text(x),
            "language":attrs.get("lang"),
        })
    if bench.get("notices") != source_notices:
        issue("benchmark_notice_mismatch",source=source_notices,ng=bench.get("notices"))

    expected_front=normalize_front(tree_localized(stree,"front-matter"))
    if bench.get("front_matter") != expected_front:
        issue("benchmark_front_matter_mismatch",source_normalized=expected_front,ng=bench.get("front_matter"))

    expected_rear=normalize_rear(tree_localized(stree,"rear-matter"))
    if bench.get("rear_matter") != expected_rear:
        issue("benchmark_rear_matter_mismatch",source_normalized=expected_rear,ng=bench.get("rear_matter"))

    source_blocks=[]
    for x in tree_children(stree,"plain-text"):
        attrs=x.get("attributes") or {}
        source_blocks.append({
            "id":re.sub(r"[^A-Za-z0-9_.-]+","-",attrs.get("id") or "text").strip("-"),
            "text":tree_text(x),
        })
    if bench.get("text_blocks") != source_blocks:
        issue("benchmark_text_blocks_mismatch",source=source_blocks,ng=bench.get("text_blocks"))

    expected_metadata=source_benchmark_metadata(stree)
    # Empty namespace-specific metadata is ignored exactly as the converter does.
    if bench.get("metadata") != expected_metadata:
        issue("benchmark_metadata_mismatch",source=expected_metadata,ng=bench.get("metadata"))

    source_models=[]
    for x in tree_children(stree,"model"):
        params={}
        for pnode in tree_children(x,"param"):
            attrs=pnode.get("attributes") or {}
            if attrs.get("name"):
                params[attrs["name"]]=attrs.get("value") or tree_text(pnode)
        source_models.append({"system":tree_text(x),"parameters":params})
    if bench.get("scoring",[]) != source_models:
        issue("benchmark_scoring_mismatch",source=source_models,ng=bench.get("scoring",[]))

    # Rule identity + core policy surface.
    source_groups={g["id"]:g for g in src["groups"]}
    expected_rules={}
    for r in src["rules"]:
        rid,rev=rule_identity(r["id"])
        expected_rules[rid]=(rev,r)

    stats["source_rules"]=len(expected_rules)
    stats["ng_rules"]=len(nr)
    if set(expected_rules)!=set(nr):
        issue("rule_set_mismatch",
              missing=sorted(set(expected_rules)-set(nr)),
              extra=sorted(set(nr)-set(expected_rules)))

    platform_rule_count=0
    for rid,(rev,sr) in expected_rules.items():
        ng=nr.get(rid)
        if ng is None: continue
        for field,sv,nv in (
            ("version",rev,ng.get("version")),
            ("title",sr.get("title"),ng.get("title")),
            ("severity",sr.get("severity"),ng.get("severity")),
            ("role",sr.get("role"),ng.get("role")),
        ):
            if sv!=nv:
                issue("rule_field_mismatch",rule=rid,field=field,source=sv,ng=nv)
        sw=sr.get("weight")
        nw=ng.get("weight")
        if sw is not None and nw is not None and float(sw)!=float(nw):
            issue("rule_field_mismatch",rule=rid,field="weight",source=sw,ng=nw)

        # Descriptive/publisher metadata used by reports and authoring tools.
        expected_discussion=disa_tag(sr.get("description"),"VulnDiscussion")
        if norm_text(ng.get("discussion"))!=expected_discussion:
            issue("rule_discussion_mismatch",rule=rid,
                  source=expected_discussion,ng=norm_text(ng.get("discussion")))

        source_doc=disa_tag(sr.get("description"),"Documentable")
        expected_doc=None if source_doc is None else source_doc.lower() in {"1","true","yes"}
        actual_doc=((ng.get("extensions") or {}).get("disa_stig") or {}).get("documentable")
        if actual_doc!=expected_doc:
            issue("rule_documentable_mismatch",rule=rid,source=expected_doc,ng=actual_doc)

        source_ccis=sorted(i.get("value") for i in sr.get("idents",[])
                           if i.get("system")=="http://cyber.mil/cci")
        ng_ccis=sorted(i.get("value") for i in ng.get("identifiers",[])
                       if i.get("scheme")=="cci")
        if source_ccis!=ng_ccis:
            issue("rule_cci_mismatch",rule=rid,source=source_ccis,ng=ng_ccis)

        group_path=sr.get("group_path") or []
        source_vuln=None
        if group_path:
            m=re.search(r"_group_(V-\\d+)$",group_path[-1])
            source_vuln=m.group(1) if m else None
        ng_vulns=[i.get("value") for i in ng.get("identifiers",[])
                  if i.get("scheme")=="disa-vulnerability-id"]
        if source_vuln is not None and ng_vulns!=[source_vuln]:
            issue("rule_vulnerability_id_mismatch",rule=rid,source=source_vuln,ng=ng_vulns)

        source_srg=None
        if group_path:
            group=source_groups.get(group_path[-1])
            if group:
                title=norm_text(group.get("title"))
                if title and re.fullmatch(r"SRG-[A-Za-z0-9-]+",title):
                    source_srg=title
        ng_srgs=[i.get("value") for i in ng.get("identifiers",[])
                 if i.get("scheme")=="disa-srg-id"]
        if source_srg is not None and ng_srgs!=[source_srg]:
            issue("rule_srg_id_mismatch",rule=rid,source=source_srg,ng=ng_srgs)

        source_fix_nodes=[x for x in sr.get("fixes",[]) if x.get("kind")=="fix"]
        for fx in source_fix_nodes:
            if norm_text(fx.get("text")) or fx.get("system") or fx.get("platform"):
                issue("nonempty_source_fix_not_preserved",rule=rid,source=fx)
        fixtexts=[x.get("text") for x in sr.get("fixes",[]) if x.get("kind")=="fixtext"]
        expected_guidance=norm_text(fixtexts[0]) if fixtexts else None
        actual_guidance=norm_text((ng.get("remediation") or {}).get("guidance"))
        if expected_guidance!=actual_guidance:
            issue("rule_remediation_mismatch",rule=rid,
                  source=expected_guidance,ng=actual_guidance)

        # RHEL9 has one normalized DPMS reference per Rule. Compare its semantic
        # text content rather than the legacy XML wrapper.
        src_refs=sorted(norm_text(x.get("text")) for x in sr.get("references",[]))
        ng_refs=[]
        for ref in ng.get("references",[]):
            ng_refs.append(norm_text(" ".join(str(ref.get(k) or "") for k in
                ("title","publisher","type","subject","identifier"))))
        if src_refs!=sorted(ng_refs):
            issue("rule_reference_mismatch",rule=rid,source=src_refs,ng=sorted(ng_refs))

        # Manual procedure fidelity. RHEL9 embeds the NIWC manual procedure
        # directly in the selector="manual" XCCDF check-content, so compare
        # that source text to the native manual Assessment rather than relying
        # on the legacy OCIL serialization.
        source_manual=[
            chk for chk in sr.get("checks",[])
            if (chk.get("selector") or "")=="manual"
        ]
        if len(source_manual)!=1:
            issue("manual_check_count_mismatch",rule=rid,count=len(source_manual))
        else:
            expected_procedure=norm_text(source_manual[0].get("inline_content"))
            manual_id=(ng.get("checks") or {}).get("manual")
            ma=manual_assessments.get(manual_id)
            if ma is None:
                issue("missing_manual_assessment",rule=rid,assessment=manual_id)
            else:
                actual_procedure=norm_text(ma.get("procedure"))
                if expected_procedure!=actual_procedure:
                    issue("manual_procedure_mismatch",rule=rid,
                          source=expected_procedure,ng=actual_procedure)
                if ma.get("mode")!="manual":
                    issue("manual_assessment_mode_mismatch",rule=rid,ng=ma.get("mode"))
                if ma.get("class")!="compliance":
                    issue("manual_assessment_class_mismatch",rule=rid,ng=ma.get("class"))

        # This source has no requires/conflicts, but compare generically.
        if sr.get("requires") != ng.get("requires",[]):
            issue("rule_requires_mismatch",rule=rid,source=sr.get("requires"),ng=ng.get("requires"))
        if sr.get("conflicts") != ng.get("conflicts",[]):
            issue("rule_conflicts_mismatch",rule=rid,source=sr.get("conflicts"),ng=ng.get("conflicts"))

        # Check-selector surface. Selector identity is policy semantics;
        # assessment behavior is validated separately by OVAL round-trip.
        expected_selectors={c.get("selector") or "default" for c in sr.get("checks",[])}
        ng_selectors=set((ng.get("checks") or {}).keys())
        if expected_selectors!=ng_selectors:
            issue("rule_check_selector_mismatch",rule=rid,
                  source=sorted(expected_selectors),ng=sorted(ng_selectors))
        if "default" in expected_selectors and ng.get("default_check")!="default":
            issue("rule_default_check_mismatch",rule=rid,
                  source="default",ng=ng.get("default_check"))
        if {"default","automated"} <= expected_selectors:
            checks=ng.get("checks") or {}
            if checks.get("default")!=checks.get("automated"):
                issue("default_automated_binding_mismatch",rule=rid,
                      default=checks.get("default"),automated=checks.get("automated"))
        if {"default","manual"} <= expected_selectors and "automated" not in expected_selectors:
            checks=ng.get("checks") or {}
            if checks.get("default")!=checks.get("manual"):
                issue("default_manual_binding_mismatch",rule=rid,
                      default=checks.get("default"),manual=checks.get("manual"))

        # Explicit Rule platform replaces inherited Benchmark platform in XCCDF.
        source_platforms=sr.get("platforms") or []
        if source_platforms:
            platform_rule_count+=1
            try:
                expected_app=sorted(PLATFORM_MAP[x.lstrip("#")] for x in source_platforms)
            except KeyError as exc:
                issue("unmapped_source_platform",rule=rid,platform=str(exc))
                expected_app=[]
            actual=sorted(ng.get("applicability") or [])
            if expected_app!=actual:
                issue("rule_applicability_mismatch",rule=rid,
                      source_platforms=source_platforms,
                      expected_ng=expected_app,ng=actual)
        elif ng.get("applicability"):
            issue("unexpected_rule_applicability",rule=rid,ng=ng.get("applicability"))

    stats["source_rules_with_explicit_platform"]=platform_rule_count
    stats["native_manual_assessments"]=len(manual_assessments)

    # Source Groups are intentionally normalized away only if semantically inert.
    non_inert=[]
    for g in src["groups"]:
        members=g.get("members",{})
        group_title=norm_text(g.get("title"))
        group_desc=norm_text(g.get("description"))
        title_normalized=(
            group_title is None or bool(re.fullmatch(r"SRG-[A-Za-z0-9-]+",group_title))
        )
        description_normalized=group_desc in (None,"<GroupDescription></GroupDescription>")
        inert=(
            len(members.get("rules",[]))==1 and
            not members.get("groups") and not members.get("values") and
            g.get("selected") is None and g.get("selected_default",True) and
            not g.get("requires") and not g.get("conflicts") and
            not g.get("platforms") and not g.get("extends") and
            not g.get("abstract") and not g.get("hidden") and
            not g.get("prohibit_changes") and g.get("weight") is None and
            title_normalized and description_normalized
        )
        if not inert:
            non_inert.append(g["id"])
    stats["source_groups"]=len(src["groups"])
    stats["source_non_inert_groups"]=len(non_inert)
    if non_inert:
        issue("source_group_semantics_not_preserved_by_regrouping",groups=non_inert)

    # Profiles: compare final selection outcome, independent of source's verbose
    # explicit select list representation.
    ng_profiles={p["id"]:p for p in bench.get("profiles",[])}
    source_profiles={profile_id(p["id"]):p for p in src["profiles"]}
    resolved={profile_id(p["id"]):p for p in src["resolved_profiles"]}
    if set(resolved)!=set(ng_profiles):
        issue("profile_set_mismatch",
              missing=sorted(set(resolved)-set(ng_profiles)),
              extra=sorted(set(ng_profiles)-set(resolved)))
    for pid,sp in resolved.items():
        np=ng_profiles.get(pid)
        if not np: continue
        source_profile=source_profiles.get(pid) or {}
        if norm_text(np.get("title"))!=norm_text(source_profile.get("title")):
            issue("profile_title_mismatch",profile=pid,source=source_profile.get("title"),ng=np.get("title"))
        profile_desc=norm_text(source_profile.get("description"))
        if profile_desc not in (None,"<ProfileDescription></ProfileDescription>"):
            issue("profile_description_not_preserved",profile=pid,source=profile_desc)
        expected_disabled=expected_profile_disabled(src,sp)
        actual_disabled=sorted(np.get("disabled_rules") or [])
        if expected_disabled!=actual_disabled:
            issue("profile_selection_mismatch",profile=pid,
                  expected_disabled=expected_disabled,ng_disabled=actual_disabled)

    # RHEL9 source contains no Values; NG should not invent policy parameters.
    stats["source_values"]=len(src["values"])
    if src["values"]==[] and bench.get("parameters"):
        issue("unexpected_ng_parameters",parameters=bench.get("parameters"))

    # Benchmark rule membership.
    if set(bench.get("rules",[]))!=set(expected_rules):
        issue("benchmark_rule_membership_mismatch",
              missing=sorted(set(expected_rules)-set(bench.get("rules",[]))),
              extra=sorted(set(bench.get("rules",[]))-set(expected_rules)))

    # Benchmark target CPEs are represented by NG top-level applicability.
    source_cpes=set(src["benchmark"].get("platforms") or [])
    expected_top={CPE_TO_NG[x] for x in source_cpes if x in CPE_TO_NG}
    ng_top=set((bench.get("platform") or {}).get("applicability",{}).get("conditions",[]) or [])
    if expected_top != ng_top:
        issue("benchmark_platform_mismatch",
              source=sorted(source_cpes),expected_ng=sorted(expected_top),ng=sorted(ng_top))

    # Every independently expected native applicability condition must exist.
    expected_condition_ids=set(PLATFORM_MAP.values()) | expected_top
    missing_conditions=sorted(expected_condition_ids-app_ids)
    if missing_conditions:
        issue("missing_applicability_conditions",missing=missing_conditions)

    stats["profiles"]=len(resolved)
    stats["applicability_conditions"]=len(app_ids)
    result={
        "format":"scap-ng-rhel9-benchmark-fidelity-audit-0.1",
        "pass":not issues,
        "stats":stats,
        "issue_count":len(issues),
        "issues":issues,
    }
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(text,encoding="utf-8")
    print(text,end="")
    raise SystemExit(0 if result["pass"] else 1)

if __name__=="__main__":
    main()
