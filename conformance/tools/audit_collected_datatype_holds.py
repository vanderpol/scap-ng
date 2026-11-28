#!/usr/bin/env python3
"""Account for unresolved collected-field types using the pinned source and native mappings."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from qualify_merge_fixture import INDEPENDENT, OVAL, require_equal
from runner import CONFORMANCE, ROOT, load

AUDIT = CONFORMANCE / "qualification/upstream-converter-audit.json"
RECEIPT = CONFORMANCE / "qualification/collected-datatype-holds.json"
OVAL_CENSUS = CONFORMANCE / "oval-source-coverage.json"
XSD = "{http://www.w3.org/2001/XMLSchema}"
XSD_PATH = "oval-schemas/independent-system-characteristics-schema.xsd"
ITEM_CAPABILITIES = {"environmentvariable58": "independent.environmentvariable",
                     "shellcommand": "independent.shellcommand"}


def native_values(expression):
    if "values" in expression:
        return expression["values"]
    if "concat" in expression:
        operand, = [node for node in expression["concat"] if "values" in node]
        return operand["values"]
    raise ValueError(f"Expected a collected projection in {expression!r}")


def source_projection(nodes, variable):
    projection, = variable.iter(OVAL + "object_component")
    ref = projection.attrib["object_ref"]
    obj = nodes[ref]
    source_kind = obj.tag.removeprefix(INDEPENDENT).removesuffix("_object")
    return ref, source_kind, projection.attrib["item_field"]


def audit(self_assertion, oval, converted):
    conversion = load(AUDIT)
    source_pins = load(OVAL_CENSUS)["pins"]
    xsd_path = oval / XSD_PATH
    xsd = ET.parse(xsd_path).getroot()
    traces = {sha256(path.read_bytes()).hexdigest(): path for path in converted.glob("*/*/source-trace.json")}
    holds = []
    for row in conversion["holds"]:
        if row["parity_diagnostic"] != "native collected-field datatype is unresolved":
            continue
        raw = (self_assertion / row["source_path"]).read_bytes()
        require_equal(sha256(raw).hexdigest(), row["source_sha256"], "source XML bytes")
        nodes = {node.attrib["id"]: node for node in ET.fromstring(raw).iter() if "id" in node.attrib}
        trace_path = traces[row["source_trace_sha256"]]
        trace = load(trace_path)
        require_equal(trace["source_commit"], source_pins["self_assertion"], "source trace commit")
        require_equal(trace["definition_id"], row["definition_id"], "source trace Definition")
        require_equal(trace["source_sha256"], row["source_sha256"], "source trace XML bytes")
        json_path = trace_path.with_name("assessment.json")
        require_equal(sha256(json_path.read_bytes()).hexdigest(), row["assessment_json_sha256"], "native JSON bytes")
        variables = load(json_path)["assessment"]["variables"]
        details = []
        for identity in trace["native_identities"]:
            if identity["kind"] != "variable":
                continue
            source_id = identity["source_id"]
            source_variable = nodes[source_id]
            original_type = source_variable.attrib["datatype"]
            ref, source_kind, field = source_projection(nodes, source_variable)
            native_capability = ITEM_CAPABILITIES[source_kind]
            item, = [element for element in xsd.findall(XSD + "element")
                     if element.get("name") == source_kind + "_item"]
            field_element, = [element for element in item.iter(XSD + "element") if element.get("name") == field]
            require_equal(field_element.attrib["type"], "oval-sc:EntityItemAnySimpleType", source_id)
            evidence = trace["source_nodes"][source_id]
            original_token, = evidence["original_datatype_tokens"]
            require_equal((original_token["path"], original_token["token"]), ([], original_type), source_id)
            require_equal(evidence["references"], [{"attribute": "object_ref", "id": ref}], source_id)
            native = variables[identity["native_id"]]
            require_equal(set(native), {"kind", "expression"}, source_id)
            projection = native_values(native["expression"])
            require_equal((projection["object"]["capability"], projection["field"]),
                          (native_capability, field), source_id)
            mapping = load(ROOT / "schema/capability-mappings/supported" / f"{native_capability}.json")
            types = mapping["native"]["field_datatypes"][field]
            if len(types) <= 1:
                raise ValueError(f"{native_capability}.{field} is no longer polymorphic")
            details.append({
                "source_variable": source_id,
                "source_datatype": original_type,
                "source_object": ref,
                "xsd_item_field": f"{source_kind}_item.{field}",
                "xsd_item_field_type": field_element.attrib["type"],
                "native_variable": identity["native_id"],
                "native_capability": native_capability,
                "native_field": field,
                "native_datatypes": types,
            })
        holds.append({"definition_id": row["definition_id"], "source_path": row["source_path"],
                      "source_sha256": row["source_sha256"], "native_assessment_sha256": row["assessment_json_sha256"],
                      "projections": details})

    return {
        "format": "scap-ng-collected-datatype-holds-1",
        "oval_schema_commit": source_pins["oval_5_12_3"], "oval_schema_path": XSD_PATH,
        "oval_schema_sha256": sha256(xsd_path.read_bytes()).hexdigest(),
        "schema_commit": conversion["schema_pin"], "converter_revision": conversion["tools_revision"],
        "holds": holds, "status": "unqualified",
        "basis": "An OVAL local Variable token is preserved as provenance. The source Item field and native mapping both permit multiple types. Exact collector evidence and any required compatibility mapping are still needed.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-assertion", type=Path, required=True)
    parser.add_argument("--oval", type=Path, required=True)
    parser.add_argument("--converted-definitions", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit(args.self_assertion, args.oval, args.converted_definitions)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check and RECEIPT.read_text(encoding="utf-8") != rendered:
        raise SystemExit("collected datatype hold receipt differs from the source audit")
    print(rendered, end="")
