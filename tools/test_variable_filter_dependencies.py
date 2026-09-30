#!/usr/bin/env python3
"""Synthetic conversion regressions; not scanner runtime conformance evidence."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from lxml import etree, isoschematron
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scap_upconvert_v003.build_rhel9_review_slice as converter
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from scap_ng_roundtrip_v003.audit_test_object_state_types import audit_set_references
import oval_semantic_ir as ir

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
UNIX = OD + "#unix"
INDEPENDENT = OD + "#independent"
COMMON = "http://oval.mitre.org/XMLSchema/oval-common-5"
DID = "oval:dependency:def:1"


def source():
    return ET.fromstring(f"""<oval_definitions xmlns="{OD}" xmlns:u="{UNIX}">
      <generator xmlns:c="{COMMON}"><c:schema_version>5.12.3</c:schema_version>
        <c:timestamp>2026-09-30T18:00:00Z</c:timestamp></generator>
      <definitions><definition id="{DID}" version="1" class="compliance">
        <metadata><title>Dependency test</title><description>Synthetic</description></metadata>
        <criteria><criterion test_ref="oval:dependency:tst:1"/></criteria>
      </definition></definitions>
      <tests><u:file_test id="oval:dependency:tst:1" version="1" check="all"
        comment="Synthetic file collection">
        <u:object object_ref="oval:dependency:obj:1"/>
      </u:file_test></tests>
      <objects><u:file_object id="oval:dependency:obj:1" version="1">
        <u:path>/tmp</u:path><u:filename var_ref="oval:dependency:var:1"/>
      </u:file_object></objects><states/><variables/>
    </oval_definitions>""")


def variable(root, number, expression):
    node = ET.SubElement(root.find(f"{{{OD}}}variables"), f"{{{OD}}}local_variable",
                         id=f"oval:dependency:var:{number}", version="1",
                         datatype="string", comment=f"Value {number}")
    node.append(expression)
    return node


def component(name, **attrs):
    return ET.Element(f"{{{OD}}}{name}", attrs)


def literal(value="demo"):
    node = component("literal_component")
    node.text = value
    return node


def add_filter(root, variable_ref):
    obj = root.find(f".//{{{UNIX}}}file_object")
    filename = obj.find(f"{{{UNIX}}}filename")
    filename.attrib.clear()
    filename.text = "demo"
    ET.SubElement(obj, f"{{{OD}}}filter").text = "oval:dependency:ste:1"
    state = ET.SubElement(root.find(f"{{{OD}}}states"), f"{{{UNIX}}}file_state",
                          id="oval:dependency:ste:1", version="1")
    ET.SubElement(state, f"{{{UNIX}}}filename", var_ref=variable_ref)


def set_source(depth, target_namespace=UNIX, target_name="file_object", missing=False):
    root = source()
    objects = root.find(f"{{{OD}}}objects")
    owner = objects[0]
    owner.clear()
    owner.attrib.update(id="oval:dependency:obj:1", version="1")
    node = owner
    for _ in range(depth):
        node = ET.SubElement(node, f"{{{OD}}}set")
    ET.SubElement(node, f"{{{OD}}}object_reference").text = "oval:dependency:obj:2"
    if not missing:
        leaf = ET.SubElement(objects, f"{{{target_namespace}}}{target_name}",
                             id="oval:dependency:obj:2", version="1")
        ET.SubElement(leaf, f"{{{target_namespace}}}path").text = "/tmp"
        ET.SubElement(leaf, f"{{{target_namespace}}}filename").text = "demo"
        if target_name == "fileextendedattribute_object":
            ET.SubElement(leaf, f"{{{target_namespace}}}attribute_name").text = "user.demo"
    return root


class DependencyTests(unittest.TestCase):
    def roundtrip(self, root):
        self.assertEqual(converter.unsupported_definition_features(root, DID), [])
        native, error = converter.lower_definition(root, DID, "dependency-assessment")
        self.assertIsNone(error, error)
        regenerated, regenerated_id = build(native)
        with tempfile.TemporaryDirectory() as td:
            before, after = Path(td) / "source.xml", Path(td) / "reverse.xml"
            ET.ElementTree(root).write(before, encoding="utf-8")
            regenerated.write(after, encoding="utf-8")
            result = compare(before, after, DID, regenerated_id, root_only=True)
        self.assertTrue(result["equal"], result)
        return native

    def test_deep_variable_chains_preserve_semantics_and_shared_values(self):
        for depth in (4, 10, 32):
            with self.subTest(depth=depth):
                root = source()
                for n in range(1, depth):
                    variable(root, n, component("variable_component",
                                               var_ref=f"oval:dependency:var:{n+1}"))
                variable(root, depth, literal())
                # A second consumer of the same value must reuse a completed node.
                path = root.find(f".//{{{UNIX}}}file_object/{{{UNIX}}}path")
                path.set("var_ref", "oval:dependency:var:1")
                path.text = None
                native = self.roundtrip(root)
                self.assertEqual(len(native["assessment"]["variables"]), depth)

    def test_nested_functions_beyond_three_levels(self):
        root = source()
        expr = literal()
        for _ in range(32):
            parent = component("begin", character="x")
            parent.append(expr)
            expr = parent
        variable(root, 1, expr)
        self.roundtrip(root)

    def test_filter_dependencies_roundtrip(self):
        root = source()
        add_filter(root, "oval:dependency:var:1")
        for n in range(1, 10):
            variable(root, n, component("variable_component",
                                       var_ref=f"oval:dependency:var:{n+1}"))
        variable(root, 10, literal())
        self.roundtrip(root)

    def test_missing_variable_behind_filter_is_accounted(self):
        root = source()
        add_filter(root, "oval:dependency:var:99")
        findings = converter.unsupported_definition_features(root, DID)
        self.assertIn({"feature": "variable_not_found",
                       "source_id": "oval:dependency:var:99"}, findings)

    def test_extension_behind_filter_variable_object_component_is_accounted(self):
        root = source()
        add_filter(root, "oval:dependency:var:1")
        variable(root, 1, component("object_component", object_ref="oval:dependency:obj:2",
                                    item_field="value"))
        ET.SubElement(root.find(f"{{{OD}}}objects"),
                      "{urn:synthetic:publisher}custom_object",
                      id="oval:dependency:obj:2", version="1")
        findings = converter.unsupported_definition_features(root, DID)
        self.assertIn({"feature": "nonstandard_oval_element",
                       "source_id": "oval:dependency:obj:2",
                       "detail": "urn:synthetic:publisher#custom_object"}, findings)

    def test_direct_and_indirect_variable_cycles_do_not_emit_native(self):
        for cycle_length in (1, 2, 10):
            root = source()
            for n in range(1, cycle_length + 1):
                variable(root, n, component("variable_component",
                         var_ref=f"oval:dependency:var:{n % cycle_length + 1}"))
            self.assertEqual(converter.unsupported_definition_features(root, DID), [])
            native, error = converter.lower_definition(root, DID, "cycle")
            self.assertIsNone(native)
            self.assertTrue(error.startswith("variable_cycle:"), error)

    def test_cycle_through_object_filter_state_and_variable_is_blocked(self):
        root = source()
        add_filter(root, "oval:dependency:var:1")
        variable(root, 1, component("object_component",
                                    object_ref="oval:dependency:obj:1", item_field="filename"))
        self.assertEqual(converter.unsupported_definition_features(root, DID), [])
        native, error = converter.lower_definition(root, DID, "mixed-cycle")
        self.assertIsNone(native)
        self.assertTrue(error.startswith("object_cycle:"), error)

    def test_cyclic_object_sets_do_not_recurse_in_feature_accounting(self):
        root = set_source(4)
        other = root.find(f"{{{OD}}}objects")[1]
        other.clear()
        other.attrib.update(id="oval:dependency:obj:2", version="1")
        nested = ET.SubElement(other, f"{{{OD}}}set")
        ET.SubElement(nested, f"{{{OD}}}object_reference").text = "oval:dependency:obj:1"
        self.assertEqual(converter.unsupported_definition_features(root, DID), [])
        native, error = converter.lower_definition(root, DID, "set-cycle")
        self.assertIsNone(native)
        self.assertTrue(error.startswith("object_cycle:"), error)

    def test_deep_feature_accounting_uses_worklist(self):
        root = source()
        for n in range(1, 1200):
            variable(root, n, component("variable_component",
                                       var_ref=f"oval:dependency:var:{n+1}"))
        variable(root, 1200, literal())
        self.assertEqual(converter.unsupported_definition_features(root, DID), [])
        native, error = converter.lower_definition(root, DID, "deep")
        self.assertIsNone(native)
        self.assertEqual(error, "conversion_resource_limit:python_recursion")

    def test_static_object_set_cycle_reports_cycle(self):
        root = source()
        objects = root.find(f"{{{OD}}}objects")
        objects.clear()
        for number, target in ((1, 2), (2, 1)):
            obj = ET.SubElement(objects, f"{{{INDEPENDENT}}}variable_object",
                id=f"oval:dependency:obj:{number}", version="1")
            nested = ET.SubElement(obj, f"{{{OD}}}set")
            ET.SubElement(nested, f"{{{OD}}}object_reference").text = f"oval:dependency:obj:{target}"
        variable(root, 1, component("object_component",
                                    object_ref="oval:dependency:obj:1", item_field="value"))
        nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
        kinds = {key: "variable" if ":var:" in key else "object" for key in nodes}
        result = ir.resolve_static_variables(nodes, kinds)
        self.assertEqual(result["oval:dependency:var:1"]["status"], "cycle")
        self.assertIn("object_cycle", result["oval:dependency:var:1"]["reason"])

    def test_nested_set_roundtrip(self):
        for depth in (4, 10, 32):
            with self.subTest(depth=depth):
                self.roundtrip(set_source(depth))

    def test_valid_deep_sources_validate_against_pinned_xsd(self):
        schema_dir = Path(__file__).resolve().parents[1] / "third_party/scap-1.4-schemas/oval_5.12.3"
        schema = etree.XMLSchema(etree.fromstring(f"""
          <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:import namespace="{OD}" schemaLocation="{schema_dir}/oval-definitions-schema.xsd"/>
            <xs:import namespace="{UNIX}" schemaLocation="{schema_dir}/unix-definitions-schema.xsd"/>
          </xs:schema>"""))
        root = source()
        for n in range(1, 32):
            variable(root, n, component("variable_component",
                                       var_ref=f"oval:dependency:var:{n+1}"))
        variable(root, 32, literal())
        for candidate in (root, set_source(32)):
            for section in list(candidate):
                if section.tag in (f"{{{OD}}}states", f"{{{OD}}}variables") and not len(section):
                    candidate.remove(section)
            with self.subTest(kind="variables" if candidate is root else "sets"):
                schema.assertValid(etree.fromstring(ET.tostring(candidate)))

    def test_nested_set_types_checked_at_every_depth(self):
        for depth in (1, 3, 4, 32):
            for namespace, name in ((UNIX, "fileextendedattribute_object"),
                                    (OD + "#windows", "file_object")):
                with self.subTest(depth=depth, namespace=namespace):
                    root = etree.fromstring(ET.tostring(set_source(depth, namespace, name)))
                    result = audit_set_references(root)
                    self.assertEqual(result["set_object_refs"], 1)
                    self.assertEqual(result["mismatches"][0]["set_depth"], depth)
            valid = etree.fromstring(ET.tostring(set_source(depth)))
            self.assertEqual(audit_set_references(valid)["mismatches"], [])
            missing = etree.fromstring(ET.tostring(set_source(depth, missing=True)))
            self.assertEqual(audit_set_references(missing)["missing_targets"][0]["set_depth"],
                             depth)

    def test_deep_set_schematron_coverage_gap(self):
        """An XSD-valid mismatch is missed by this upstream pattern at depth 4."""
        schema_dir = Path(__file__).resolve().parents[1] / "third_party/scap-1.4-schemas/oval_5.12.3"
        xsd = etree.XMLSchema(etree.fromstring(f"""
          <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:import namespace="{OD}" schemaLocation="{schema_dir}/oval-definitions-schema.xsd"/>
            <xs:import namespace="{UNIX}" schemaLocation="{schema_dir}/unix-definitions-schema.xsd"/>
          </xs:schema>"""))
        sch = "http://purl.oclc.org/dsdl/schematron"
        definition_schema = etree.parse(str(schema_dir / "oval-definitions-schema.xsd"))
        pattern = definition_schema.find(f".//{{{sch}}}pattern[@id='oval-def_setobjref']")
        focused = etree.Element(f"{{{sch}}}schema", nsmap={"sch": sch}, queryBinding="xslt")
        etree.SubElement(focused, f"{{{sch}}}ns", prefix="oval-def", uri=OD)
        focused.append(deepcopy(pattern))
        validator = isoschematron.Schematron(focused, store_report=True)
        for depth in (1, 3, 4, 32):
            root = set_source(depth, target_name="fileextendedattribute_object")
            for section in list(root):
                if section.tag in (f"{{{OD}}}states", f"{{{OD}}}variables"):
                    root.remove(section)
            document = etree.fromstring(ET.tostring(root))
            xsd.assertValid(document)
            self.assertEqual(validator.validate(document), depth > 3)
            self.assertEqual(audit_set_references(document)["mismatches"][0]["set_depth"],
                             depth)

    def test_concat_limit_is_checked_before_product_allocation(self):
        root = source()
        expr = component("concat")
        for n in (2, 3):
            expr.append(component("variable_component", var_ref=f"oval:dependency:var:{n}"))
            constant = ET.SubElement(root.find(f"{{{OD}}}variables"),
                f"{{{OD}}}constant_variable", id=f"oval:dependency:var:{n}",
                version="1", datatype="string", comment="Operand")
            for value in range(20):
                ET.SubElement(constant, f"{{{OD}}}value").text = str(value)
        variable(root, 1, expr)
        nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
        kinds = {key: "variable" for key in nodes if ":var:" in key}
        with patch.object(ir.itertools, "product",
                          side_effect=AssertionError("Product must not be allocated")):
            result = ir.resolve_static_variables(nodes, kinds, max_values=100)
        self.assertEqual(result["oval:dependency:var:1"]["status"], "bounded")
        self.assertEqual(result["oval:dependency:var:1"]["candidate_values"], 400)
        self.assertNotIn("values", result["oval:dependency:var:1"])
        # Static evaluation bounds must not truncate or replace the native AST.
        native = self.roundtrip(root)
        self.assertIn("concat", str(native["assessment"]["variables"]))


if __name__ == "__main__":
    unittest.main()
