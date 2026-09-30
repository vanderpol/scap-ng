#!/usr/bin/env python3
"""Audit pinned upstream OVAL XSD contracts, including non-XSD prose semantics.

Usage:
 python tools/scap_ng_roundtrip_v003/audit_oval_xsd_defaults.py \
   --schemas oval-language/oval-schemas --out work/oval-xsd-default-audit
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, re
from pathlib import Path
from lxml import etree as ET

XSD = "http://www.w3.org/2001/XMLSchema"
SCH = "http://purl.oclc.org/dsdl/schematron"
DEFAULT_TERMS = re.compile(
    r"\bdefault(?:s|ed)?\b|\bif\b.{0,80}\b(?:absent|omitted|not provided|not present|not specified)\b|"
    r"\bwhen\b.{0,80}\b(?:absent|omitted|not specified)\b|\bno value\b|"
    r"\bdoes not exist\b|\bnot collected\b|\bnon.exist\b|\bmissing\b",
    re.I | re.S,
)
SEMANTIC_TERMS = re.compile(
    r"\b(?:existence|check_existence|var_check|entity_check|operator|"
    r"item_creation|recurs|flag|error|unknown|datatype|mask|"
    r"variable|cartesian|restriction|collection|not evaluated|status)\b", re.I
)
def local(node): return ET.QName(node).localname
def location(path, node): return {"file":path.name,"line":node.sourceline}
def txt(node):
    return " ".join(" ".join(node.itertext()).split())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    paths=sorted(args.schemas.glob("*.xsd"))
    if len(paths)<45: raise SystemExit(f"Expected upstream complete OVAL 5.12.3 schema set, found {len(paths)}")
    defaults=[]; fixed=[]; inherited=[]; attribute_groups=[]; optional=[]; annotations=[]; rules=[]
    source_hashes={}
    # Resolve references to named global types/groups only; do not infer inherited defaults.
    named_declarations=collections.defaultdict(list)
    references=[]
    errors=[]
    for path in paths:
        try: root=ET.parse(str(path)).getroot()
        except ET.XMLSyntaxError as exc:
            errors.append({"file":path.name,"error":str(exc)})
            continue
        source_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        target=root.get("targetNamespace","")
        for child in root:
            if not isinstance(child.tag,str):
                continue
            kind=local(child)
            if kind in ("complexType","simpleType","attributeGroup","group") and child.get("name"):
                named_declarations[(target,kind,child.get("name"))].append(location(path,child))
        for node in root.iter():
            # lxml includes comments and processing instructions in iter().
            # They have non-string .tag values and are not XML schema nodes.
            if not isinstance(node.tag, str):
                continue
            tag=local(node)
            if tag in ("attribute","element") and node.get("default") is not None:
                defaults.append({**location(path,node),"kind":tag,"name":node.get("name") or node.get("ref"),
                     "default":node.get("default"),"targetNamespace":target})
            if tag in ("attribute","element") and node.get("fixed") is not None:
                fixed.append({**location(path,node),"kind":tag,
                    "name":node.get("name") or node.get("ref"),
                    "fixed":node.get("fixed"),"targetNamespace":target})
            if tag in ("extension","restriction") and node.get("base"):
                references.append((path,node,"type",node.get("base")))
            if tag in ("attributeGroup","group") and node.get("ref"):
                references.append((path,node,tag,node.get("ref")))
            if tag=="attributeGroup":
                attribute_groups.append({**location(path,node),"name":node.get("name"),
                    "ref":node.get("ref"),"targetNamespace":target,
                    "status":"unresolved" if node.get("ref") else "declaration"})
            if tag in ("extension","restriction") and node.get("base"):
                inherited.append({**location(path,node),"base":node.get("base")})
            if tag=="element" and node.get("minOccurs")=="0":
                optional.append({**location(path,node),"name":node.get("name") or node.get("ref"),
                    "maxOccurs":node.get("maxOccurs")})
            if tag in ("documentation","evaluation_documentation"):
                value=txt(node)
                if DEFAULT_TERMS.search(value) or SEMANTIC_TERMS.search(value):
                    annotations.append({**location(path,node),"kind":tag,"text":value[:2600],
                        "default_language":bool(DEFAULT_TERMS.search(value))})
            if tag in ("assert","report") and node.tag.startswith("{"+SCH+"}"):
                rules.append({**location(path,node),"kind":tag,"test":node.get("test"),"text":txt(node)[:1000]})
    resolved_references=[]
    for path,node,kind,qname in references:
        if ":" in qname:
            prefix,name=qname.split(":",1)
            uri=node.nsmap.get(prefix)
        else:
            name=qname
            uri=node.nsmap.get(None,"")
        candidates=(
            ("complexType","simpleType") if kind=="type" else (kind,)
        )
        matches=[(candidate,source) for candidate in candidates
                 for source in named_declarations.get((uri,candidate,name),[])]
        if uri==XSD and kind=="type":
            status="builtin_xsd"
        elif not uri:
            status="unresolved_namespace"
        elif len(matches)==1:
            status="resolved_global"
        elif len(matches)>1:
            status="ambiguous_global"
        else:
            status="unresolved_global"
        resolved_references.append({
            **location(path,node),"kind":kind,"reference":qname,
            "expanded_name":f"{{{uri}}}{name}" if uri else None,
            "status":status,
            "candidates":[{"kind":candidate,**source} for candidate,source in matches],
        })
    args.out.mkdir(parents=True,exist_ok=True)
    def save(name, data):
        (args.out/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    save("explicit-defaults.json",defaults)
    save("fixed-values.json",fixed)
    save("attribute-group-links.json",attribute_groups)
    save("source-sha256.json",source_hashes)
    save("named-reference-resolution.json",resolved_references)
    save("type-inheritance.json",inherited)
    save("optional-elements.json",optional)
    save("semantic-documentation.json",annotations)
    save("schematron-assertions.json",rules)
    save("parse-errors.json",errors)
    summary={"upstream_xsd_files":len(paths),"parse_errors":len(errors),
       "explicit_defaults":len(defaults),"fixed_values":len(fixed),
       "attribute_group_references":sum(bool(x["ref"]) for x in attribute_groups),
       "attribute_group_declarations":sum(bool(x["name"]) for x in attribute_groups),
       "inheritance_relations":len(inherited),
       "named_reference_resolution":dict(sorted(collections.Counter(
           row["status"] for row in resolved_references).items())),
       "optional_elements":len(optional),"semantic_annotation_passages":len(annotations),
       "implicit_or_default_documentation_passages":sum(x["default_language"] for x in annotations),
       "embedded_schematron_assertions":len(rules),
       "default_field_names":dict(collections.Counter(x["name"] for x in defaults).most_common())}
    save("summary.json",summary)
    print(json.dumps({k:v for k,v in summary.items() if k!="default_field_names"},indent=2))
    # Human-readable index: no claim of proof where type inheritance or prose is unresolved.
    lines=["# OVAL 5.12.3 XSD default and semantic-language audit",
           "", "Source: pinned upstream `OVAL-Community/OVAL@v5.12.3`.",
           "Status: complete schema-file inventory; each candidate needs type-closure and execution review.",
           "", "## Inventory", ""]
    lines += [f"- **{k}**: {v}" for k,v in summary.items() if k!="default_field_names"]
    lines += ["", "## All explicit defaults", "",
      "| Source | Line | Attribute/element | Default |","| --- | ---: | --- | --- |"]
    for x in defaults:
        lines.append("| `%s` | %d | `%s` | `%s` |"%(x["file"],x["line"],x["name"],str(x["default"]).replace("|","/")))
    lines += ["", "## Fixed-value declarations and attribute-group references", "",
      "See `fixed-values.json` and `attribute-group-links.json` for source-anchored",
      "details. These are inventory entries, NOT proof that type inheritance",
      "or referenced group composition has been resolved.",
      "The `named-reference-resolution.json` inventory distinguishes local",
      "global declarations, built-in XSD types, ambiguous and missing links.",
      "It does not yet compute effective inherited defaults.",
      "", "## Implicit behavioral defaults and existence checks", "",
      "Review all entries in `semantic-documentation.json`, including the",
      "embedded ExistenceEnumeration evaluation tables and records whose prose",
      "spans several XML lines. Counting only XSD `default=` is not sufficient.",
      "","### Mandatory semantic review cases","",
      "1. Test `check_existence` defaults `at_least_one_exists`;",
      "   this is separate from required `check` and Test `state_operator`.",
      "2. State EntityStateSimple/ComplexBaseType `check_existence` also",
      "   defaults `at_least_one_exists`, but it checks entity presence.",
      "3. State `entity_check` defaults `all` and combines repeated entity results.",
      "4. `var_check` has **no XSD default**; docs specify effective `all`",
      "   when `var_ref` is present and `var_check` omitted.",
      "5. For a variable with no values: Object use produces nonexistence,",
      "   State use produces error. Error/not-collected statuses affect truth.",
      "6. When a State entity has multiple item values and the variable also",
      "   has multiple values: use `var_check` per item, then `entity_check`.",
      "7. `none_exist` Test plus States violates embedded Schematron.",
      "8. External-variable possible_restriction operator defaults AND;",
      "   alternatives are OR-linked to possible_value restrictions.",
      "9. Optional `behaviors` parent absence may differ from empty attributes;",
      "   defaults are conditional on type and collector applicability.",
      "10. Masks, item creation, result/status flags, and directives defaults",
      "    must be separated into runtime, results, provenance, and migration.",
      "","## Remaining required review","",
      "- Resolve effective inherited attributes through complexTypes and attributeGroups.",
      "- Inspect every documentation passage and embedded evaluation table.",
      "- Build independent executable result truth tables and invalid fixtures.",
      "- Compare verified resolved defaults, not only explicit XML attributes.",
      "- Classify unsupported publisher extensions independently of standard OVAL.",
      ""]
    (args.out/"README.md").write_text("\n".join(lines),encoding="utf-8")
    if errors: raise SystemExit("XSD parse errors encountered")

if __name__=="__main__": main()
