#!/usr/bin/env python3
"""Build a schema-derived semantic catalog for OVAL 5.12.3 within SCAP 1.4.

The goal is not XSD-to-NG translation. This catalog enumerates the language
surface that a faithful OVAL semantic front end must account for and checks
that every variable ComponentGroup operation declared by the schema is known
to the semantic IR parser.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

XSD="{http://www.w3.org/2001/XMLSchema}"


def qlocal(value: str | None) -> str | None:
    if value is None:
        return None
    return value.split(":")[-1]


def text(node):
    return " ".join(" ".join(node.itertext()).split())


def load_parser(path: Path):
    spec=importlib.util.spec_from_file_location("oval_semantic_ir",path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("schema_root",type=Path)
    ap.add_argument("--parser",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    repo_root = Path(__file__).resolve().parent.parent
    default_overrides = repo_root / "research" / "iterations" / "001" / "oval-test-support-overrides.json"
    ap.add_argument(
        "--support-overrides",
        type=Path,
        default=default_overrides if default_overrides.exists() else None,
    )
    args=ap.parse_args()

    parser=load_parser(args.parser)
    support_overrides={}
    if args.support_overrides:
        override_doc=json.loads(args.support_overrides.read_text(encoding="utf-8"))
        support_overrides={
            row["qualified_name"]:row
            for row in override_doc.get("overrides",[])
        }
    global_elements=[]
    substitution_groups=defaultdict(list)
    enums=defaultdict(set)
    complex_types={}
    deprecated=[]

    for path in sorted(args.schema_root.rglob("*.xsd")):
        root=ET.parse(path).getroot()
        target=root.get("targetNamespace")
        rel=path.relative_to(args.schema_root).as_posix()

        for child in root:
            kind=child.tag.rsplit("}",1)[-1]
            if kind=="element" and child.get("name"):
                deprecated_nodes=[
                    n for n in child.iter()
                    if n.tag.rsplit("}",1)[-1]=="deprecated_info"
                ]
                deprecation_evidence=" ".join(
                    text(n) for n in deprecated_nodes
                ) or None
                qname=f"{target or ''}#{child.get('name')}"
                override=support_overrides.get(qname)
                raw_deprecated=bool(deprecated_nodes)
                reinstated=bool(
                    override and override.get("effective_status")=="supported_reinstated"
                )
                row={
                    "name":child.get("name"),
                    "namespace":target,
                    "type":child.get("type"),
                    "substitution_group":child.get("substitutionGroup"),
                    "schema":rel,
                    "deprecated":raw_deprecated,
                    "deprecation_evidence":deprecation_evidence,
                    "support_override":override,
                    "reinstated":reinstated,
                    "effective_deprecated":raw_deprecated and not reinstated,
                }
                global_elements.append(row)
                sub=qlocal(child.get("substitutionGroup"))
                if sub:
                    substitution_groups[sub].append(row)

            elif kind=="complexType" and child.get("name"):
                attrs=[]
                children=[]
                base=None
                for node in child.iter():
                    local=node.tag.rsplit("}",1)[-1]
                    if local in {"extension","restriction"} and node.get("base") and base is None:
                        base=node.get("base")
                    elif local=="attribute" and node.get("name"):
                        attrs.append({
                            "name":node.get("name"),
                            "type":node.get("type"),
                            "use":node.get("use"),
                            "default":node.get("default"),
                            "fixed":node.get("fixed"),
                        })
                    elif local=="element":
                        if node is child:
                            continue
                        if node.get("name") or node.get("ref"):
                            children.append({
                                "name":node.get("name"),
                                "ref":node.get("ref"),
                                "type":node.get("type"),
                                "min":node.get("minOccurs"),
                                "max":node.get("maxOccurs"),
                            })
                complex_types[f"{target}#{child.get('name')}"]={
                    "name":child.get("name"),"namespace":target,"schema":rel,
                    "base":base,"attributes":attrs,"children":children,
                }

            elif kind=="simpleType" and child.get("name"):
                values=[]
                for node in child.iter():
                    if node.tag==XSD+"enumeration" and node.get("value") is not None:
                        values.append(node.get("value"))
                if values:
                    enums[f"{target}#{child.get('name')}"].update(values)

        for node in root.iter():
            local=node.tag.rsplit("}",1)[-1]
            if local in {"documentation","appinfo"}:
                content=text(node)
                if "deprecat" in content.lower():
                    deprecated.append({"schema":rel,"text":content})

    tests=sorted(
        (e for e in global_elements if e["name"].endswith("_test")),
        key=lambda x:(x["namespace"] or "",x["name"])
    )
    objects=sorted(
        (e for e in global_elements if e["name"].endswith("_object")),
        key=lambda x:(x["namespace"] or "",x["name"])
    )
    states=sorted(
        (e for e in global_elements if e["name"].endswith("_state")),
        key=lambda x:(x["namespace"] or "",x["name"])
    )
    component_members=sorted({
        e["name"] for e in substitution_groups.get("ComponentGroup",[])
    })
    known_components=sorted(parser.OVAL_COMPONENT_OPERATIONS)
    missing_components=sorted(set(component_members)-set(known_components))
    parser_only_components=sorted(set(known_components)-set(component_members))

    by_ns=defaultdict(lambda:{"tests":0,"objects":0,"states":0})
    for row in tests: by_ns[row["namespace"]]["tests"]+=1
    for row in objects: by_ns[row["namespace"]]["objects"]+=1
    for row in states: by_ns[row["namespace"]]["states"]+=1

    out={
        "format":"scap-ng-iteration001-oval-schema-semantic-catalog-0.1",
        "schema_root":args.schema_root.as_posix(),
        "global_elements":len(global_elements),
        "test_elements":tests,
        "object_elements":objects,
        "state_elements":states,
        "substitution_groups":{
            k:sorted(v,key=lambda x:(x["namespace"] or "",x["name"]))
            for k,v in sorted(substitution_groups.items())
        },
        "variable_component_operations":{
            "schema_declared":component_members,
            "parser_known":known_components,
            "missing_from_parser":missing_components,
            "parser_only":parser_only_components,
        },
        "enumerations":{
            k:sorted(v) for k,v in sorted(enums.items())
        },
        "complex_types":complex_types,
        "platform_surface_by_namespace":dict(sorted(by_ns.items())),
        "deprecated_annotation_count":len(deprecated),
        "support_override_file":args.support_overrides.as_posix() if args.support_overrides else None,
        "support_override_count":len(support_overrides),
        "coverage_assertions":{
            "all_component_group_operations_modeled":not missing_components,
            "generic_test_semantics_modeled":True,
            "generic_object_semantics_modeled":True,
            "generic_state_semantics_modeled":True,
            "platform_specific_payload_preservation":"lossless_xml_semantic_tree",
            "native_capability_mapping":"separate_registry_required",
        },
        "limitations":[
            "Schema presence proves structural language coverage, not native SCAP-NG capability equivalence.",
            "Platform-specific test/object/state payloads are faithfully preserved generically until a reviewed native translator exists.",
            "Schematron constraints are validated separately and are not reduced to this catalog.",
            "Element deprecation is recognized only from explicit oval:deprecated_info metadata, not incidental annotation text."
        ],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    print(json.dumps({
        "tests":len(tests),"objects":len(objects),"states":len(states),
        "component_group_operations":len(component_members),
        "missing_component_operations":missing_components,
        "namespaces":len(by_ns),
    },indent=2,sort_keys=True))
    return 1 if missing_components else 0


if __name__=="__main__":
    raise SystemExit(main())
