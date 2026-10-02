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
from scap_upconvert_v003.conversion_budget import ConversionBudget, ConversionBudgetExceeded, ConversionBudgetTracker
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


def literal(value="demo", datatype=None):
    attrs = {"datatype": datatype} if datatype is not None else {}
    node = component("literal_component", **attrs)
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
    def test_collected_bundle_preserves_dependency_accounting_and_lowering(self):
        root = source()
        variable(root, 1, literal())
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.xml"
            ET.ElementTree(root).write(path)
            bundle = converter.collect_oval_bundle([path])
        self.assertEqual(converter.unsupported_definition_features(bundle, DID), [])
        native, error = converter.lower_definition(bundle, DID, "bundle-assessment")
        self.assertIsNone(error, error)
        self.assertIsNotNone(native)
        add_filter(bundle[0], "oval:dependency:var:99")
        findings = converter.unsupported_definition_features(bundle, DID)
        self.assertIn({"feature": "variable_not_found",
                       "source_id": "oval:dependency:var:99"}, findings)

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

    def test_external_variable_constraints_roundtrip(self):
        root = source()
        variables = root.find(f"{{{OD}}}variables")
        external = ET.SubElement(
            variables,
            f"{{{OD}}}external_variable",
            id="oval:dependency:var:1",
            version="1",
            datatype="string",
            comment="Organization supplied threshold",
        )
        value = ET.SubElement(external, f"{{{OD}}}possible_value", hint="Preferred")
        value.text = "10"
        group = ET.SubElement(
            external,
            f"{{{OD}}}possible_restriction",
            hint="Approved range",
        )
        low = ET.SubElement(group, f"{{{OD}}}restriction", operation="pattern match")
        low.text = "^[0-9]+$"
        high = ET.SubElement(group, f"{{{OD}}}restriction", operation="not equal")
        high.text = "0"

        native = self.roundtrip(root)
        variable_entry = next(iter(native["assessment"]["variables"].values()))
        validation = variable_entry["input"]["validation"]["alternatives"]
        self.assertEqual(validation[0], {"literal": "10", "hint": "Preferred"})
        self.assertEqual(
            validation[1]["restriction_group"],
            {
                "operator": "AND",
                "hint": "Approved range",
                "conditions": [
                    {"operation": "pattern match", "value": "^[0-9]+$"},
                    {"operation": "not equal", "value": "0"},
                ],
            },
        )

    def test_external_variable_explicit_or_restrictions_roundtrip(self):
        root = source()
        variables = root.find(f"{{{OD}}}variables")
        external = ET.SubElement(
            variables,
            f"{{{OD}}}external_variable",
            id="oval:dependency:var:1",
            version="1",
            datatype="string",
            comment="Allowed environment",
        )
        group = ET.SubElement(
            external,
            f"{{{OD}}}possible_restriction",
            operator="OR",
            hint="Approved names",
        )
        for value in ("prod.*", "stage.*"):
            restriction = ET.SubElement(
                group,
                f"{{{OD}}}restriction",
                operation="pattern match",
            )
            restriction.text = value

        native = self.roundtrip(root)
        variable_entry = next(iter(native["assessment"]["variables"].values()))
        group = variable_entry["input"]["validation"]["alternatives"][0]["restriction_group"]
        self.assertEqual(group["operator"], "OR")
        self.assertEqual(group["hint"], "Approved names")
        self.assertEqual(
            [row["value"] for row in group["conditions"]],
            ["prod.*", "stage.*"],
        )

    def test_multivalue_constant_variable_roundtrip(self):
        root = source()
        constant = ET.SubElement(
            root.find(f"{{{OD}}}variables"),
            f"{{{OD}}}constant_variable",
            id="oval:dependency:var:1",
            version="1",
            datatype="string",
            comment="Multiple values",
        )
        for value in ("alpha", "beta", "gamma"):
            ET.SubElement(constant, f"{{{OD}}}value").text = value
        native = self.roundtrip(root)
        entry = next(iter(native["assessment"]["variables"].values()))
        self.assertEqual(
            entry["expression"]["literal"],
            ["alpha", "beta", "gamma"],
        )

    def test_literal_component_explicit_datatype_roundtrip(self):
        root = source()
        node = variable(root, 1, literal("5", "int"))
        node.set("datatype", "int")
        filename = root.find(f".//{{{UNIX}}}file_object/{{{UNIX}}}filename")
        filename.set("datatype", "int")
        native = self.roundtrip(root)
        entry = next(iter(native["assessment"]["variables"].values()))
        self.assertEqual(entry["datatype"], "int")
        self.assertEqual(
            entry["expression"]["literal"],
            {"value": "5", "datatype": "int"},
        )

    def test_mixed_nested_function_roundtrip(self):
        root = source()
        escaped = component("escape_regex")
        escaped.append(literal("x.y"))
        prefixed = component("begin", character="/")
        prefixed.append(literal("tmp"))
        expression = component("concat")
        expression.extend([prefixed, escaped])
        variable(root, 1, expression)
        native = self.roundtrip(root)
        rendered = str(next(iter(native["assessment"]["variables"].values()))["expression"])
        self.assertIn("concat", rendered)
        self.assertIn("begin", rendered)
        self.assertIn("escape_regex", rendered)

    def test_object_component_record_field_roundtrip(self):
        root = source()
        objects = root.find(f"{{{OD}}}objects")
        extra = ET.SubElement(
            objects,
            f"{{{UNIX}}}file_object",
            id="oval:dependency:obj:2",
            version="1",
        )
        ET.SubElement(extra, f"{{{UNIX}}}path").text = "/tmp"
        ET.SubElement(extra, f"{{{UNIX}}}filename").text = "demo"

        expr = component(
            "object_component",
            object_ref="oval:dependency:obj:2",
            item_field="record_entity",
            record_field="member",
        )
        variable(root, 1, expr)

        native = self.roundtrip(root)
        entry = next(iter(native["assessment"]["variables"].values()))
        values = entry["expression"]["object_values"]
        self.assertEqual(values["field"], "record_entity")
        self.assertEqual(values["record_field"], "member")

    def test_object_var_check_multivalue_roundtrip(self):
        for var_check in ("all", "at least one", "none satisfy", "only one"):
            with self.subTest(var_check=var_check):
                root = source()
                filename = root.find(f".//{{{UNIX}}}file_object/{{{UNIX}}}filename")
                filename.set("var_check", var_check)
                constant = ET.SubElement(
                    root.find(f"{{{OD}}}variables"),
                    f"{{{OD}}}constant_variable",
                    id="oval:dependency:var:1",
                    version="1",
                    datatype="string",
                    comment="Multiple selector values",
                )
                for value in ("demo", "other"):
                    ET.SubElement(constant, f"{{{OD}}}value").text = value
                native = self.roundtrip(root)
                check = next(iter(native["assessment"]["checks"].values()))
                selector = check["collect"]["select"]["filename"]
                self.assertEqual(selector["variable_check"], var_check)

    def test_variable_dependent_object_inside_set_roundtrip(self):
        root = set_source(4)
        leaf = root.find(f".//{{{UNIX}}}file_object[@id='oval:dependency:obj:2']")
        filename = leaf.find(f"{{{UNIX}}}filename")
        filename.text = None
        filename.set("var_ref", "oval:dependency:var:1")
        filename.set("var_check", "at least one")
        variable(root, 1, literal("demo"))
        native = self.roundtrip(root)
        self.assertEqual(len(native["assessment"]["variables"]), 1)
        check = next(iter(native["assessment"]["checks"].values()))
        self.assertIsNotNone(check["collect"]["set"])

    def test_filter_dependencies_roundtrip(self):
        root = source()
        add_filter(root, "oval:dependency:var:1")
        for n in range(1, 10):
            variable(root, n, component("variable_component",
                                       var_ref=f"oval:dependency:var:{n+1}"))
        variable(root, 10, literal())
        self.roundtrip(root)

    def test_var_ref_datatype_mismatch_is_diagnosed(self):
        root = source()
        variable(
            root,
            1,
            literal("5"),
        ).set("datatype", "int")
        findings = converter.unsupported_definition_features(root, DID)
        row = next(x for x in findings if x["feature"] == "var_ref_datatype_mismatch")
        self.assertEqual(row["source_id"], "oval:dependency:obj:1")
        self.assertIn("filename:string", row["detail"])
        self.assertIn("oval:dependency:var:1:int", row["detail"])

    def test_var_check_without_reference_is_diagnosed(self):
        root = source()
        filename = root.find(f".//{{{UNIX}}}file_object/{{{UNIX}}}filename")
        filename.attrib.clear()
        filename.set("var_check", "all")
        filename.text = "demo"
        findings = converter.unsupported_definition_features(root, DID)
        self.assertIn(
            {
                "feature": "var_check_without_var_ref",
                "source_id": "oval:dependency:obj:1",
                "detail": "filename",
            },
            findings,
        )

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

    def test_feature_accounting_dependency_node_budget_is_explicit(self):
        root = source()
        for n in range(1, 20):
            variable(root, n, component("variable_component",
                                       var_ref=f"oval:dependency:var:{n+1}"))
        variable(root, 20, literal())
        rows = converter.unsupported_definition_features(
            root, DID, budget=ConversionBudget(dependency_nodes=6)
        )
        limit = next(row for row in rows if row["feature"] == "conversion_resource_limit")
        self.assertIn("dependency_nodes", limit["detail"])
        self.assertIn("limit=6", limit["detail"])
        self.assertIn("observed=7", limit["detail"])

    def test_feature_accounting_dependency_edge_budget_is_explicit(self):
        root = source()
        variable(root, 1, literal())
        rows = converter.unsupported_definition_features(
            root, DID, budget=ConversionBudget(dependency_edges=1)
        )
        limit = next(row for row in rows if row["feature"] == "conversion_resource_limit")
        self.assertIn("dependency_edges", limit["detail"])

    def test_feature_accounting_expression_depth_budget_is_explicit(self):
        root = source()
        criteria = root.find(f"{{{OD}}}definitions/{{{OD}}}definition/{{{OD}}}criteria")
        criterion = list(criteria)[0]
        criteria.remove(criterion)
        current = criteria
        for _ in range(6):
            current = ET.SubElement(current, f"{{{OD}}}criteria", operator="AND")
        current.append(criterion)
        rows = converter.unsupported_definition_features(
            root, DID, budget=ConversionBudget(expression_depth=4)
        )
        limit = next(row for row in rows if row["feature"] == "conversion_resource_limit")
        self.assertIn("expression_depth", limit["detail"])

    def test_budget_tracker_distinguishes_value_and_time_resources(self):
        tracker = ConversionBudgetTracker(ConversionBudget(generated_values=2))
        with self.assertRaisesRegex(ConversionBudgetExceeded, "generated_values"):
            tracker.note_generated_values(3)

        ticks = iter((0.0, 0.010))
        timed = ConversionBudgetTracker(
            ConversionBudget(elapsed_ms=5), clock=lambda: next(ticks)
        )
        with self.assertRaisesRegex(ConversionBudgetExceeded, "elapsed_ms"):
            timed.check_elapsed()

    def test_static_variable_budget_generated_values_preflights_concat(self):
        root = source()
        expr = component("concat")
        for n in (2, 3):
            expr.append(component("variable_component", var_ref=f"oval:dependency:var:{n}"))
            constant = ET.SubElement(
                root.find(f"{{{OD}}}variables"),
                f"{{{OD}}}constant_variable",
                id=f"oval:dependency:var:{n}",
                version="1",
                datatype="string",
                comment="Operand",
            )
            for value in range(4):
                ET.SubElement(constant, f"{{{OD}}}value").text = str(value)
        variable(root, 1, expr)
        nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
        kinds = {key: "variable" for key in nodes if ":var:" in key}
        with patch.object(
            ir.itertools,
            "product",
            side_effect=AssertionError("product must not be allocated after budget breach"),
        ):
            result = ir.resolve_static_variables(
                nodes,
                kinds,
                budget=ConversionBudget(generated_values=8),
            )
        row = result["oval:dependency:var:1"]
        self.assertEqual(row["status"], "resource_limit")
        self.assertIn("generated_values", row["reason"])
        self.assertEqual(row["candidate_values"], 16)

    def test_static_variable_budget_value_bytes_drops_partial_values(self):
        root = source()
        variable(root, 1, literal("0123456789"))
        nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
        kinds = {key: "variable" for key in nodes if ":var:" in key}
        result = ir.resolve_static_variables(
            nodes,
            kinds,
            budget=ConversionBudget(value_bytes=4),
        )
        row = result["oval:dependency:var:1"]
        self.assertEqual(row["status"], "resource_limit")
        self.assertIn("value_bytes", row["reason"])
        self.assertNotIn("values", row)

    def test_lowering_budget_preflights_recursive_set_depth(self):
        root = set_source(10)
        native, error = converter.lower_definition(
            root,
            DID,
            "budgeted-set",
            budget=ConversionBudget(expression_depth=4),
        )
        self.assertIsNone(native)
        self.assertIn("conversion_resource_limit:expression_depth", error)

    def test_lowering_output_budget_returns_no_partial_assessment(self):
        root = source()
        variable(root, 1, literal("demo"))
        native, error = converter.lower_definition(
            root,
            DID,
            "budgeted-output",
            budget=ConversionBudget(output_nodes=5),
        )
        self.assertIsNone(native)
        self.assertIn("conversion_resource_limit:output_nodes", error)

    def test_output_node_counter_is_structure_based(self):
        tracker = ConversionBudgetTracker(ConversionBudget(output_nodes=4))
        tracker.note_output_nodes(4)
        with self.assertRaisesRegex(ConversionBudgetExceeded, "output_nodes"):
            tracker.note_output_nodes(5)

    def test_wide_shared_variable_dag_preserves_shared_dependency(self):
        root = source()
        expr = component("concat")
        for number in range(2, 26):
            expr.append(component("variable_component", var_ref=f"oval:dependency:var:{number}"))
            variable(
                root,
                number,
                component("variable_component", var_ref="oval:dependency:var:100"),
            )
        variable(root, 1, expr)
        variable(root, 100, literal("shared"))

        rows = converter.unsupported_definition_features(
            root,
            DID,
            budget=ConversionBudget(dependency_nodes=30, dependency_edges=60),
        )
        self.assertFalse(
            [row for row in rows if row["feature"] == "conversion_resource_limit"],
            rows,
        )
        native, error = converter.lower_definition(root, DID, "wide-shared-dag")
        self.assertIsNone(error)
        self.assertIsNotNone(native)

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
            <xs:import namespace="{OD}" schemaLocation="{(schema_dir / 'oval-definitions-schema.xsd').as_uri()}"/>
            <xs:import namespace="{UNIX}" schemaLocation="{(schema_dir / 'unix-definitions-schema.xsd').as_uri()}"/>
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
            <xs:import namespace="{OD}" schemaLocation="{(schema_dir / 'oval-definitions-schema.xsd').as_uri()}"/>
            <xs:import namespace="{UNIX}" schemaLocation="{(schema_dir / 'unix-definitions-schema.xsd').as_uri()}"/>
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

    def test_candidate_recursive_set_schematron_covers_all_depths_and_namespaces(self):
        """Candidate upstream rule covers recursive depth and qualified type identity."""
        sch = "http://purl.oclc.org/dsdl/schematron"
        focused = etree.Element(
            f"{{{sch}}}schema", nsmap={"sch": sch}, queryBinding="xslt"
        )
        etree.SubElement(focused, f"{{{sch}}}ns", prefix="oval-def", uri=OD)
        pattern = etree.SubElement(
            focused, f"{{{sch}}}pattern", id="oval-def_setobjref_recursive_candidate"
        )
        rule = etree.SubElement(
            pattern,
            f"{{{sch}}}rule",
            context=(
                "oval-def:oval_definitions/oval-def:objects/*/"
                "oval-def:set//oval-def:object_reference"
            ),
        )
        assertion = etree.SubElement(
            rule,
            f"{{{sch}}}assert",
            test=(
                "local-name(ancestor::*[parent::oval-def:objects][1]) = "
                "local-name(ancestor::oval-def:oval_definitions/"
                "oval-def:objects/*[@id=current()]) and "
                "namespace-uri(ancestor::*[parent::oval-def:objects][1]) = "
                "namespace-uri(ancestor::oval-def:oval_definitions/"
                "oval-def:objects/*[@id=current()])"
            ),
        )
        assertion.text = (
            "Each object referenced by the set must be of the same qualified "
            "type as the parent object"
        )
        validator = isoschematron.Schematron(focused, store_report=True)

        for depth in (1, 3, 4, 32):
            with self.subTest(depth=depth, case="valid"):
                valid = etree.fromstring(ET.tostring(set_source(depth)))
                self.assertTrue(validator.validate(valid))

            with self.subTest(depth=depth, case="same_namespace_mismatch"):
                mismatch = etree.fromstring(ET.tostring(
                    set_source(depth, target_name="fileextendedattribute_object")
                ))
                self.assertFalse(validator.validate(mismatch))

            with self.subTest(depth=depth, case="same_local_name_other_namespace"):
                mismatch = etree.fromstring(ET.tostring(
                    set_source(depth, OD + "#windows", "file_object")
                ))
                self.assertFalse(validator.validate(mismatch))

    def test_static_function_semantics_matrix(self):
        def evaluate(expr):
            root = source()
            variable(root, 1, expr)
            nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
            kinds = {key: "variable" for key in nodes if ":var:" in key}
            return ir.resolve_static_variables(nodes, kinds)["oval:dependency:var:1"]

        def unary(name, value, **attrs):
            node = component(name, **attrs)
            node.append(literal(value))
            return node

        arithmetic = component("arithmetic", arithmetic_operation="add")
        arithmetic.extend([literal("2", "int"), literal("3", "int")])
        self.assertEqual(evaluate(arithmetic)["values"], ["5"])

        escaped = evaluate(unary("escape_regex", "a.b*"))
        self.assertEqual(escaped["values"], [r"a\.b\*"])

        globbed = evaluate(unary("glob_to_regex", "*.txt"))
        self.assertEqual(globbed["values"], [r"^(?=[^\.])[^/]*\.txt$"])

        merged = component("merge", delimiter=",", sort="lexical", order="ascending")
        merged.extend([literal("b"), literal("a")])
        self.assertEqual(evaluate(merged)["values"], ["a,b"])

        capture = unary("regex_capture", "prefix id=42 suffix", pattern=r"id=([0-9]+)")
        self.assertEqual(evaluate(capture)["values"], ["42"])

        no_capture = unary("regex_capture", "no id here", pattern=r"id=([0-9]+)")
        self.assertEqual(evaluate(no_capture)["values"], [""])

        split = unary("split", "a,,b", delimiter=",")
        self.assertEqual(evaluate(split)["values"], ["a", "", "b"])

        substring = unary(
            "substring", "abcdef", substring_start="2", substring_length="3"
        )
        self.assertEqual(evaluate(substring)["values"], ["bcd"])

        difference = component(
            "time_difference", format_1="year_month_day", format_2="year_month_day"
        )
        difference.extend([literal("2024-01-02"), literal("2024-01-01")])
        self.assertEqual(evaluate(difference)["values"], ["86400"])

        unique = component("unique")
        unique.extend([literal("a"), literal("a"), literal("b")])
        self.assertEqual(evaluate(unique)["values"], ["a", "b"])

        count = component("count")
        count.extend([literal("a"), literal("b"), literal("c")])
        root = source()
        variable_node = variable(root, 1, count)
        variable_node.set("datatype", "int")
        nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
        kinds = {key: "variable" for key in nodes if ":var:" in key}
        result = ir.resolve_static_variables(nodes, kinds)["oval:dependency:var:1"]
        self.assertEqual(result["values"], ["3"])
        self.assertEqual(result["datatype"], "int")

        self.assertEqual(
            evaluate(unary("begin", "value", character="/"))["values"],
            ["/value"],
        )
        self.assertEqual(
            evaluate(unary("end", "value", character="/"))["values"],
            ["value/"],
        )

    def test_static_function_error_semantics(self):
        def evaluate(expr):
            root = source()
            variable(root, 1, expr)
            nodes = {n.get("id"): n for n in root.iter() if n.get("id")}
            kinds = {key: "variable" for key in nodes if ":var:" in key}
            return ir.resolve_static_variables(nodes, kinds)["oval:dependency:var:1"]

        divide = component("arithmetic", arithmetic_operation="divide")
        divide.extend([literal("1", "int"), literal("0", "int")])
        result = evaluate(divide)
        self.assertEqual(result["status"], "static_evaluation_error")
        self.assertEqual(result["reason"], "arithmetic_input_or_operation_error")

        bad_substring = component(
            "substring", substring_start="99", substring_length="2"
        )
        bad_substring.append(literal("abc"))
        result = evaluate(bad_substring)
        self.assertEqual(result["status"], "static_evaluation_error")
        self.assertEqual(result["reason"], "substring_start_beyond_input_length")

        bad_glob = component("glob_to_regex")
        bad_glob.append(literal("abc\\"))
        result = evaluate(bad_glob)
        self.assertEqual(result["status"], "static_evaluation_error")
        self.assertTrue(result["reason"].startswith("glob_to_regex_invalid_pattern:"))

        bad_merge = component("merge", sort="numeric")
        bad_merge.extend([literal("2"), literal("not-a-number")])
        result = evaluate(bad_merge)
        self.assertEqual(result["status"], "static_evaluation_error")
        self.assertEqual(result["reason"], "merge_numeric_sort_non_numeric_value")

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
