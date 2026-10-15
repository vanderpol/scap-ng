#!/usr/bin/env python3
"""Pinned Joval comparison: archived original OVAL single to published NG v0.4 r2.
Feature demos not present in the converter output are explicitly separated.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
CASES={
"SV-257889":("rhel_9","RHEL 9","ObjectComponent + filters; separate proven foreach prototype"),
"SV-258179":("rhel_9","RHEL 9","extend_definition and shared Assessment"),
"SV-258236":("rhel_9","RHEL 9","multi-Test source fidelity"),
"SV-278001":("ms_windows_server_2025","Windows Server 2025","constant Variable to literal arrays; role evaluation"),
"SV-278028":("ms_windows_server_2025","Windows Server 2025","Set filters + dynamic PowerShell command Variables"),
"SV-278138":("ms_windows_server_2025","Windows Server 2025","exclude filters and Windows permissions"),
"SV-259345":("ms_windows_server_dns","Windows Server DNS","runtime Variables, multi-stage DNS checks"),
"SV-259350":("ms_windows_server_dns","Windows Server DNS","shared DNS Assessment"),
"SV-214228":("apache_server_2-4_unix_server","Apache 2.4 UNIX","regex_capture and Apache discovery Variables"),
"SV-214268":("apache_server_2-4_unix_server","Apache 2.4 UNIX","complex configuration checks"),
}
def hashbytes(d):return hashlib.sha256(d).hexdigest()
def has(root,tag):return [e for e in root.iter() if e.tag.split("}")[-1]==tag]
def code(s,lang="yaml"):return chr(96)*3+lang+"\n"+s.rstrip()+"\n"+chr(96)*3
def excerpt(xml,tag,limit=1400):
    root=ET.fromstring(xml);hits=has(root,tag)
    if not hits:return "No source element of this name."
    e=ET.fromstring(ET.tostring(hits[0]));ET.indent(e)
    txt=ET.tostring(e,encoding="unicode")
    if len(txt)>limit:txt=txt[:limit]+"\n<!-- excerpt truncated; open entire original OVAL XML -->"
    return code(txt,"xml")
def build(yzip,jzip,outdir):
    outdir.mkdir(exist_ok=True,parents=True)
    files={};log={}
    with zipfile.ZipFile(yzip) as y, zipfile.ZipFile(jzip) as j:
        index={}
        for path in y.namelist():
            if "/assessments/" not in path or not path.endswith(".yaml"):continue
            if path.split("/")[-2]=="manual":continue
            doc=yaml.safe_load(y.read(path))
            if isinstance(doc,dict) and isinstance(doc.get("assessment"),dict):
                logical=doc["assessment"].get("id")
                if logical in index:raise ValueError("Duplicate Assessment ID "+str(logical))
                index[logical]=path
        lines=[
"# Original OVAL single vs. SCAP-NG v0.4 — Joval showcase",
"",
"**Peer review packet, October 16, 2026. Not a normative specification or scanner.**",
"",
"This packet pairs ten archived NIWC/DISA OVAL single XML sources with their",
"actual **published** SCAP-NG v0.4 r2 YAML and equivalent JSON Assessments.",
"Each pair includes its Rule. Shared Assessments are resolved by the Rule's",
"logical Assessment ID; no file-name-based guessing.",
"",
"The archived original XML sources are held in the GitHub research evidence",
"tree; we do not claim their bytes match every original source in the",
"published 0.3 authoring release. All target NG documents are copied unchanged",
"from the verified v0.4 r2 meeting prerelease.",
"",
"## Inspect these pairs",
"",
"| Rule | STIG | Feature to examine |",
"| --- | --- | --- |",
]
        for rule,(benchmark,title,focus) in CASES.items():
            source=ROOT/"research/assessment-simplification/evidence"/benchmark/rule/"source-oval.xml"
            if not source.exists():raise ValueError("Missing original OVAL XML: "+str(source))
            original=source.read_bytes()
            root=ET.fromstring(original)
            if root.tag.split("}")[-1]!="oval_definitions":raise ValueError("Invalid root")
            if not any(rule.split("-")[-1] in x.attrib.get("id","") for x in has(root,"definition")):
                raise ValueError("Source OVAL definition not linked to rule "+rule)
            rpath="authoring/"+benchmark+"/rules/"+rule+".rule.yaml"
            if rpath not in y.namelist():raise ValueError("Rule missing from r2 "+rule)
            rule_doc=yaml.safe_load(y.read(rpath))["rule"]
            logical=rule_doc["assessment_choices"]["automated"]["assessment"]
            apath=index.get(logical)
            if not apath:raise ValueError("No Assessment for "+rule+" -> "+logical)
            jp=apath[:-5]+".json"
            if jp not in j.namelist():raise ValueError("JSON mirror missing "+jp)
            ng_y=y.read(apath);ng_j=j.read(jp)
            a=yaml.safe_load(ng_y)
            if a!=json.loads(ng_j):raise ValueError("Mirror mismatch "+rule)
            if a["assessment"]["specification"]["version"]!="0.4.0":raise ValueError("Not 0.4 "+rule)
            base="pairs/"+rule+"/"
            files[base+"01-original-oval-single.xml"]=original
            files[base+"02-ng-v04.assessment.yaml"]=ng_y
            files[base+"03-ng-v04.assessment.json"]=ng_j
            files[base+"04-rule.yaml"]=y.read(rpath)
            log[rule]={"benchmark":title,"focus":focus,"assessment_id":logical,
                       "archived_source_path":str(source.relative_to(ROOT)),
                       "ng_yaml_source_path":apath,"ng_json_source_path":jp,
                       "oval_sha256":hashbytes(original),"ng_yaml_sha256":hashbytes(ng_y),
                       "ng_json_sha256":hashbytes(ng_j),
                       "oval_definitions":len(has(root,"definition")),
                       "ng_tests":len(a["assessment"].get("tests") or {})}
            lines.append("| "+rule+" | "+title+" | "+focus+" |")
            if rule=="SV-257889" and (not has(root,"object_component") or not has(root,"filter")):
                raise ValueError("Missing verified RHEL foreach OVAL precursor")
            if rule=="SV-278001":
                if not any(len(has(v,"value"))>1 for v in has(root,"constant_variable")):
                    raise ValueError("Missing source literal-collection Variable")
                if "matches_regex:" not in ng_y.decode():raise ValueError("Missing NG literal comparison")
            if rule=="SV-278028" and (not has(root,"filter") or "filters:" not in ng_y.decode()):
                raise ValueError("Expected matched source/NG filter is missing")
            if rule=="SV-278138" and "exclude:" not in ng_y.decode():
                raise ValueError("Expected exclusion filter is missing")
            if rule=="SV-214228" and "regex_capture:" not in ng_y.decode():
                raise ValueError("Missing native derived runtime Variable")
            print("PAIRED",rule,logical,flush=True)
        lines+=["",
"## 1. Real static Variable folding (SV-278001)",
"",
"OVAL requires a named multi-valued constant Variable; the matching",
"SCAP-NG State carries literal array values and explicit value_match.",
"",
"**OVAL single excerpt:**",
"",
excerpt(files["pairs/SV-278001/01-original-oval-single.xml"],"constant_variable"),
"",
"**Converted NG literal array from the same Rule:**",
"",
]
        a=yaml.safe_load(files["pairs/SV-278001/02-ng-v04.assessment.yaml"])["assessment"]
        chosen=next(t for t in a["tests"].values() if "matches_regex" in str(t.get("states")))
        lines += [code(yaml.safe_dump({"states":chosen["states"]},sort_keys=False,width=105)),"",
"## 2. OVAL Set/filter expressions become readable NG filters",
"",
"SV-278028 pairs original OVAL filter XML with the NG include predicate.",
"SV-278138 additionally shows exclusion and multi-field conditions.",
"",
"**Original OVAL example from SV-278028:**",
"",
excerpt(files["pairs/SV-278028/01-original-oval-single.xml"],"filter"),
"",
"**Converted NG filtered Object from SV-278028 (representative):**",
"",
]
        b=yaml.safe_load(files["pairs/SV-278028/02-ng-v04.assessment.yaml"])["assessment"]
        filtered=next(t["object"] for t in b["tests"].values() if "set" in t.get("object",{}))
        short={"set":filtered["set"]}
        ngtext=yaml.safe_dump(short,sort_keys=False,width=105)
        if len(ngtext)>3400:ngtext=ngtext[:3400]+"\n# excerpt truncated: see complete paired Assessment"
        lines += [code(ngtext),"",
"## 3. Foreach removes one-use ObjectComponent projection",
"",
"RHEL9 SV-257889 OVAL uses filtered password Objects, ObjectComponent(home_dir),",
"one-use local Variables and downstream file collection. The *published*",
"NG r2 converter still emits the faithful graph, not foreach.",
"The additional-proof folder contains the accepted 0.3 foreach authoring",
"fixture and its separately verified original-source lowering proof.",
"Do not claim that the default v0.4 source converter emitted this shortcut.",
"",
"## 4. If/then/else is available as native authoring, NOT blanket auto-conversion",
"",
"SV-278001 faithfully retains OR/AND criteria in actual NG evaluate.",
"The extra authored conditional fragment below uses REAL SV-278001 Tests",
"and VALID v0.4 evaluate grammar, but is deliberately marked",
"**NOT six-state-equivalent to the pinned OVAL source**. Converting arbitrary",
"OR(AND(G,A),AND(NOT G,B)) into if/else changes outcomes for some",
"error/unknown/not_applicable combinations.",
"",
]
        actual=a["evaluate"]
        lines.extend(["**Source-preserving current NG evaluation:**", "",
             code(yaml.safe_dump({"evaluate":actual},sort_keys=False)),""])
        guard="system-windows-domain-controller-test"
        dc="default-domain-controller-permissions-hkey-local-machine-system-registry-key-test"
        member="default-non-domain-controller-permissions-hkey-local-machine-system-registry-test"
        if not {guard,dc,member} <= set(a["tests"]):raise ValueError("Real role Test IDs missing")
        conditional={"if":{"test":guard},"then":{"test":dc},"else":{"test":member}}
        expression=json.loads((ROOT/"schema/v0.4.0/expression.schema.json").read_text())
        Draft202012Validator(expression).validate(conditional)
        frag=code(yaml.safe_dump({"evaluate":conditional},sort_keys=False))
        files["additional-proof/if-then-else-NOT-source-equivalent.example.yaml"]=(
            "# Real Test IDs and valid v0.4 expression grammar only.\n"
            "# NOT equivalent to SV-278001 original OVAL for all six-state outcomes.\n"+
            yaml.safe_dump({"evaluate":conditional},sort_keys=False)).encode()
        lines.extend(["**Valid native grammar illustration, not faithful OVAL rewrite:**","",frag,"",
"## 5. Dynamic Variables stay meaningful",
"",
"DNS SV-259345 and Apache SV-214228 show Object-derived Variables,",
"command concat, and regex_capture. These are real runtime dataflow;",
"the converter does not flatten their inputs or omit provenance.",
"",
"## 6. Shared content reduces duplication",
"",
"RHEL9 SV-258179 is linked through a logical shared Assessment ID; the",
"Rule, original OVAL single, and full shared NG Assessment are all included.",
"",
"## 7. New Test/State language and authoring-format parity",
"",
"The 0.4 examples use collected_items_require for collected Item",
"cardinality, state_fields_require when scalar fields share a condition,",
"and per-field require for exceptions. Native nested Windows records",
"still have separate record/record-field requirements.",
"YAML/JSON mirrors parse to identical Assessments; independent JSON",
"reference-resolution compilation is not yet guaranteed.",
"",
"## 8. Other reviewed SCAP-NG changes",
"",
"First-class Organizational Input, author-facing manual Assessments,",
"bounded/reported/redacted evidence and readable results are represented",
"by separate project fixtures, not presented as derived from these OVAL",
"singles. See additional-proof directory and 0.3 example docs.",
"",
"**Important limits:** A scanner does not exist, no runtime equivalence",
"is claimed, 0.4 grammar candidates are not ratified, opt-in foreach",
"source modernization is not in r2 default conversion, and if/else",
"is not a blanket OVAL rewrite.",
"",
"Discussion: https://github.com/vanderpol/scap-ng/issues/227",
"Release: https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r2",
])
        supplementary=[
("foreach-source-backed-review.md","research/assessment-simplification/foreach-07/REVIEW.md"),
("foreach-production-proof.md","research/assessment-simplification/foreach-07/PRODUCTION-PROOF.md"),
("foreach-accepted-v03-fixture.assessment.yaml","tests/foreach-0.3.0/content/foreach-home-files.assessment.yaml"),
("conditional-source-shape-and-six-state-warning.md","research/assessment-simplification/conditional-10/README.md"),
("organizational-input.example.yaml","research/iterations/003/examples/organizational-input/site.organizational-input.yaml"),
("conditional-0.2-historical-fixture.assessment.yaml","board/review-content/0.2.0/content/conditional-evaluation.assessment.yaml"),
("synthetic-explainable-assessment-result.json","specification/examples/0.3.0/results/assessment-result.json"),
]
        for dest,src in supplementary:
            p=ROOT/src
            if not p.exists():raise ValueError("Proof fixture absent "+src)
            files["additional-proof/"+dest]=p.read_bytes()
        files["SHOWCASE-START-HERE.md"]=("\n".join(lines)+"\n").encode()
        man={"status":"pre-alpha source-backed comparison, separate conditional/foreach proof limitations",
             "release":"v0.4.0-joval-meeting-preview-20261015-r2","pairs":log}
        files["MANIFEST.json"]=(json.dumps(man,indent=2,sort_keys=True)+"\n").encode()
        name=outdir/"scap-ng-v04-oval-single-to-ng-showcase.zip"
        with zipfile.ZipFile(name,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as zout:
            for key,val in sorted(files.items()):zout.writestr(key,val)
        with zipfile.ZipFile(name) as z:
            if z.testzip() is not None:raise ValueError("Broken ZIP")
            if len(z.namelist())!=len(files):raise ValueError("File count")
        (outdir/"SHOWCASE-START-HERE.md").write_bytes(files["SHOWCASE-START-HERE.md"])
        (outdir/"MANIFEST.json").write_bytes(files["MANIFEST.json"])
        print("SHOWCASE_PASS",json.dumps({"pairs":len(log),"files":len(files),
             "sha256":hashbytes(name.read_bytes()),"size":name.stat().st_size}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--yaml",type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    build(a.yaml,a.json,a.out)
