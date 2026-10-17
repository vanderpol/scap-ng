#!/usr/bin/env python3
"""Research #235: verify DISA/NAVWAR source OVAL ID namespaces by element type.

Original source graph/XML fixture test, NOT full six-STIG attribution census.
Publisher-neutral SCAP-NG IDs and repository maintainer are not provenance.
"""
from __future__ import annotations
from collections import Counter
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PREFIX={
    "DISA":"oval:mil.disa.stig.",
    "NIWC/NAVWAR":"oval:navy.navwar.niwcatlantic.",
}
KINDS=("def","tst","obj","ste","var")
ID_RE=re.compile(r"^oval:[^:]+:(def|tst|obj|ste|var):[0-9]+$")

def classify(value):
    if not isinstance(value,str) or not ID_RE.fullmatch(value):
        return None,None
    kind=ID_RE.fullmatch(value).group(1)
    for origin,prefix in PREFIX.items():
        if value.startswith(prefix):
            return origin,kind
    return "OTHER",kind

def report(root):
    graph=json.loads((root/"research/assessment-simplification/evidence/rhel_9/SV-257889/graph.json").read_text())
    xml=ET.parse(root/"research/iterations/003/evidence/roundtrip-source-oval/U_RHEL_10_SV-281037-oval.xml")
    graph_ids={value for closure in graph["closures"] for value in closure["ids"]}
    xml_ids={el.attrib["id"] for el in xml.iter() if "id" in el.attrib}
    results={}
    for label,ids in (("RHEL9 DISA source graph",graph_ids),
                      ("RHEL10 NAVWAR source XML",xml_ids)):
        counts=Counter()
        examples={}
        for item in sorted(ids):
            namespace,kind=classify(item)
            if namespace is None:continue
            counts[(namespace,kind)]+=1
            examples.setdefault(namespace,{}).setdefault(kind,item)
        results[label]={
            "by_namespace_type":{f"{ns}:{kind}":n for (ns,kind),n in sorted(counts.items())},
            "examples":examples,
        }
    for kind in KINDS:
        if ("DISA:"+kind) not in results["RHEL9 DISA source graph"]["by_namespace_type"]:
            raise AssertionError("missing DISA "+kind)
        if ("NIWC/NAVWAR:"+kind) not in results["RHEL10 NAVWAR source XML"]["by_namespace_type"]:
            raise AssertionError("missing NAVWAR "+kind)
    return results

def markdown(data):
    dis=data["RHEL9 DISA source graph"]["examples"]["DISA"]
    nw=data["RHEL10 NAVWAR source XML"]["examples"]["NIWC/NAVWAR"]
    lines=[
        "# Source OVAL attribution: DISA vs NIWC/NAVWAR",
        "",
        "**Research correction — 17 October 2026.** These are **original OVAL element IDs**",
        "from the preserved source graph/XML, not rewritten SCAP-NG native authoring IDs.",
        "",
        "| OVAL element | DISA source ID example | NIWC/NAVWAR source ID example |",
        "| --- | --- | --- |",
    ]
    for kind in KINDS:
        lines.append(f"| `{kind}` | `{dis[kind]}` | `{nw[kind]}` |")
    lines.extend([
        "",
        "## Impact on 0.4 language and Item-creation research",
        "",
        "The project owner clarified the lineage of this NIWC enhanced SCAP 1.4 corpus:",
        "DISA's SCAP 1.3 content is imported without modifying its assessment",
        "logic. NIWC adds its own separately identified OVAL content, which may",
        "use SCAP 1.4 / OVAL 5.12.3 additions. **This is a corpus-specific source-lineage",
        "constraint, not a generic claim about every DISA package in the future.**",
        "",
        "- Classify `oval:mil.disa.stig...` and `oval:navy.navwar.niwcatlantic...`",
        "  per original **Definition, Test, Object, State and Variable** identity.",
        "  Root Definition author and referenced element owners may differ; record both.",
        "- A publisher-neutral NG Assessment ID, a benchmark directory, a NIWC",
        "  release ZIP, and a converter-produced native ID do not establish who",
        "  authored its underlying OVAL check.",
        "- Imported SCAP 1.3-era DISA logic should **not** be used to infer that",
        "  modern OVAL authors rejected or accidentally omitted newer",
        "  `item_creation` or related acquisition behaviors.",
        "- For the 201 `all_exist` Tests, the [Item-creation audit](reports/all-exist-item-creation.md)",
        "  measures existing behavior values but **does not classify each Test by original",
        "  OVAL author** because the curated six-STIG native authoring ZIP omits original",
        "  source-OVAL IDs. A source XML/ID join is required before claiming a DISA",
        "  versus NAVWAR statistic for those Tests.",
        "- Keep migration fidelity separately from NG grammar design: we can",
        "  modernize native Item identity/absence handling, but it must be",
        "  differential-proven and cannot be silently substituted into original",
        "  imported DISA or NIWC checks.",
        "- Standard OVAL 5.12.3 feature availability is a different question",
        "  from whether a given SCAP 1.3-origin DISA Assessment used that feature.",
        "",
        "## Verification scope",
        "",
        "DISA preserved graph: `research/assessment-simplification/evidence/rhel_9/SV-257889/graph.json`.",
        "NAVWAR preserved source XML: `research/iterations/003/evidence/roundtrip-source-oval/U_RHEL_10_SV-281037-oval.xml`.",
        "The automated source-ID audit validates both namespaces for all five element types.",
        "This is **not** proof that the entire six-STIG corpus is unchanged from",
        "upstream DISA releases; independent package-to-package byte or semantic",
        "comparison would be needed to prove that claim from artifacts.",
        "",
    ])
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--output")
    a=p.parse_args()
    result=report(Path(a.root))
    if a.output:
        Path(a.output).write_text(markdown(result))
    print(json.dumps(result,indent=2))
