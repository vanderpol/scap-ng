"""Verify the paired YAML boundary sources and their independent receipts."""
from hashlib import sha256
from pathlib import PurePosixPath, PureWindowsPath
import unittest
import xml.etree.ElementTree as ET

from conformance.tools.runner import CONFORMANCE, load, validator

CORPUS = CONFORMANCE / "oval-self-assertion"
BOUNDARIES = CORPUS / "yaml-boundaries"
OVAL = "{http://oval.mitre.org/XMLSchema/oval-definitions-5}"
INDEPENDENT = "{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}"
PREFIX = "oval:org.scapng.conformance"


class YamlBoundaryCases(unittest.TestCase):
    def setUp(self):
        self.expected = load(BOUNDARIES / "expected.json")

    def test_source_and_native_documents_share_independent_authoring_cases(self):
        validated = load(BOUNDARIES / "validation.json")
        converted = load(BOUNDARIES / "converter.json")
        self.assertEqual(converted["schema_pin"], load(CONFORMANCE / "manifest.json")["schema_commit"])
        self.assertEqual(converted["source_pin"], "187a01d389d40c6f2bff171f92d48c40dd98d351")
        converted_by_test = {row["source_test"]: row for row in converted["definitions"]}
        self.assertEqual(len(converted_by_test), 2 * len(self.expected["cases"]))
        schema = validator()

        for index, (platform, paths) in enumerate(self.expected["platforms"].items()):
            source_path = BOUNDARIES / paths["xml"]
            relative = source_path.relative_to(CONFORMANCE.parent).as_posix()
            receipt = validated[relative]
            self.assertEqual(receipt["sha256"], sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual((receipt["xsd"], receipt["schematron"]), ("pass", "pass"))
            source = ET.parse(source_path)
            nodes = {node.attrib["id"]: node for node in source.getroot().iter() if "id" in node.attrib}
            native = load(BOUNDARIES / paths["native"])
            schema.validate(native)
            authored = native["assessment"]["tests"]

            self.assertEqual(set(authored), {f"{key}-test" for key in self.expected["cases"]})
            for name, case in self.expected["cases"].items():
                number = case["source_ids"][index]
                test_id = f"{PREFIX}:tst:{number}"
                object_id = f"{PREFIX}:obj:{number}"
                state_id = f"{PREFIX}:ste:{number}"
                definition_id = f"{PREFIX}:def:{number}"
                self.assertEqual(nodes[definition_id].find(f"{OVAL}criteria/{OVAL}criterion").get("test_ref"), test_id)
                self.assertEqual(nodes[definition_id].find(f"{OVAL}metadata/{OVAL}affected").get("family"), platform)
                self.assertEqual(nodes[test_id].get("check_existence"), "at_least_one_exists")
                self.assertEqual(nodes[test_id].find(INDEPENDENT + "object").get("object_ref"), object_id)
                self.assertEqual(nodes[test_id].find(INDEPENDENT + "state").get("state_ref"), state_id)
                native_test = authored[f"{name}-test"]
                object_ = native_test["object"]
                path_cls = PurePosixPath if platform == "unix" else PureWindowsPath
                selected = str(path_cls(paths["fixture_root"]) / case["destination"])
                self.assertEqual(nodes[object_id].findtext(INDEPENDENT + "filepath"), selected)
                self.assertEqual(object_["full_path"]["equals"], selected)
                self.assertEqual(nodes[object_id].findtext(INDEPENDENT + "yamlpath"), self.expected["yamlpath"])
                self.assertEqual(object_["yamlpath"]["equals"], self.expected["yamlpath"])
                field = nodes[state_id].find(f"{INDEPENDENT}value/{OVAL}field")
                self.assertEqual((field.get("name"), field.text), ("my^camel^case^^^key", "amber"))
                native_field = native_test["require"]["fields"]["value"]["record"]["fields"]
                self.assertEqual(native_field, {"myCamelCase^Key": {"equals": "amber"}})
                conversion = converted_by_test[test_id]
                self.assertEqual(conversion["definition"], definition_id)
                self.assertEqual(conversion["structural"], "schema-valid")
                self.assertTrue(conversion["authored_test_equivalent"])
                self.assertEqual(set(conversion["native_tests"].values()), {test_id})

    def test_real_unix_collection_and_native_consumer_receipts_are_separate(self):
        observed = load(BOUNDARIES / "openscap-unix.json")
        source = CONFORMANCE / observed["source"]
        self.assertEqual(observed["source_sha256"], sha256(source.read_bytes()).hexdigest())
        statuses = self.expected["outcomes_by_source_collection_flag"]
        self.assertEqual(statuses, {
            "does not exist": "false", "error": "error", "not collected": "unknown",
            "not applicable": "not applicable",
        })
        self.assertEqual(observed["observations"].keys(), self.expected["cases"].keys())
        for name, record in observed["observations"].items():
            source_case = self.expected["cases"][name]
            fixture = CORPUS / source_case["source_fixture"]
            self.assertEqual(record["fixture_sha256"], sha256(fixture.read_bytes()).hexdigest())
            number = source_case["source_ids"][0]
            self.assertEqual(record["definition"], f"{PREFIX}:def:{number}")
            if "complete_expectation" in source_case:
                self.assertEqual(record["definition_outcome"], source_case["complete_expectation"])
            self.assertEqual(record["definition_outcome"], statuses[record["object_flag"]])
            self.assertEqual(record["test_outcome"], record["definition_outcome"])
            self.assertEqual(record["fixture_mode"], "0000" if name == "unreadable" else "0600")

        studio = load(BOUNDARIES / "studio.json")
        ri = load(BOUNDARIES / "ri-hold.json")
        self.assertEqual(ri["schema_pin"], studio["schema_pin"])
        self.assertEqual(ri["platforms"].keys(), self.expected["platforms"].keys())
        self.assertEqual(studio["counts"]["ok"], len(self.expected["platforms"]))
        self.assertEqual(studio["counts"]["undoRoundTrips"], len(self.expected["platforms"]))
        self.assertEqual(studio["counts"]["failed"], 0)
        for platform, row in ri["platforms"].items():
            authored = BOUNDARIES / self.expected["platforms"][platform]["native"]
            self.assertEqual(sha256(authored.read_bytes()).hexdigest(), row["assessment_sha256"])
            self.assertEqual(row["assessment_sha256"], studio["assessment_sha256"][platform])
            self.assertEqual(row["tests"].keys(), load(authored)["assessment"]["tests"].keys())
            for name, diagnostic in row["tests"].items():
                self.assertEqual(diagnostic, {"exit_code": 2, "observation": {"diagnostic": {
                    "code": "selected_test_feature_held", "pointer": f"/assessment/tests/{name}",
                }}})


if __name__ == "__main__":
    unittest.main()
