import copy
import unittest
from research_expand_registry_authoring import expand_registry_test, AuthoringError

TEST = {
 "capability": "windows.registry",
 "object": {"select": {
  "hive": {"equals": "local_machine"},
  "key": {"equals": r"SYSTEM\CurrentControlSet\Control\Lsa"},
  "name": {"equals": "RestrictAnonymous"}}},
 "states": [{"expect": {"type": {"equals": "dword"}, "value": {"equals": 1},
   "match": "all", "existence": "one_or_more"}}],
 "reported_elements": "all", "existence": "one_or_more", "match": "all"
}

class RegistryAuthoringExpansionTests(unittest.TestCase):
 def test_exact_expansion(self):
  x=expand_registry_test(TEST)
  self.assertEqual(x["states"][0]["state"]["all"][0]["value"], "dword")
  self.assertEqual(x["states"][0]["state"]["all"][1], {"field":"value", "value":1, "operation":"equals", "datatype":"integer", "match":"all", "existence":"one_or_more"})
  self.assertEqual(x["object"]["select"]["hive"], "local_machine")
  self.assertIsNone(x["test_title"])
  self.assertEqual(x["object"]["select"]["key"]["value"], r"SYSTEM\CurrentControlSet\Control\Lsa")
 def test_native_v03_schema_accepts_expansion(self):
  from pathlib import Path
  from validate_native_json_schemas import build_validators, document_errors
  root = Path(__file__).resolve().parents[1]
  validators = build_validators(root / "schema/v0.3.0")
  assessment = {
   "assessment": {
    "id": "research.registry-type-check",
    "version": 1,
    "assessment_title": "Registry type and value fidelity",
    "mode": "automated",
    "class": "compliance",
    "purpose": "assessment",
    "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"},
    "tests": {"restrict-anonymous-test": expand_registry_test(TEST)},
    "evaluate": {"test": "restrict-anonymous-test"},
   }
  }
  errors = list(document_errors(validators["assessment.schema.json"], assessment))
  self.assertEqual([], [str(e) for e in errors])

 def test_sv278217_fixture_compiles_without_changing_meaning(self):
  from pathlib import Path
  import yaml
  from research_expand_registry_authoring import expand_registry_assessment
  root = Path(__file__).resolve().parents[1]
  path = root / "research/iterations/003/examples/stig-derived/SV-278217/readable-authoring.prototype.yaml"
  authored = yaml.safe_load(path.read_text(encoding="utf-8"))
  canonical = expand_registry_assessment(authored)
  test = canonical["assessment"]["tests"]["restrict-anonymous-test"]
  self.assertEqual(test["object"]["select"]["hive"], "local_machine")
  self.assertEqual(test["states"][0]["state"]["all"][0]["value"], "dword")
  self.assertEqual(test["states"][0]["state"]["all"][1]["value"], 1)
  self.assertEqual(test["states"][0]["state"]["all"][1]["datatype"], "integer")

 def test_refuse_string_one(self):
  t=copy.deepcopy(TEST); t["states"][0]["expect"]["value"]={"equals":"1"}
  with self.assertRaises(AuthoringError): expand_registry_test(t)
 def test_refuse_ambiguous_type(self):
  t=copy.deepcopy(TEST); del t["states"][0]["expect"]["type"]
  with self.assertRaises(AuthoringError): expand_registry_test(t)
 def test_refuse_multistring_shortcut(self):
  t=copy.deepcopy(TEST); t["states"][0]["expect"]["type"]={"equals":"multi_string"}
  with self.assertRaises(AuthoringError): expand_registry_test(t)
 def test_refuse_implicit_selector(self):
  t=copy.deepcopy(TEST); t["object"]["select"]["hive"]="local_machine"
  with self.assertRaises(AuthoringError): expand_registry_test(t)
 def test_refuse_unknown_operator(self):
  t=copy.deepcopy(TEST); t["object"]["select"]["key"]={"magic": "x"}
  with self.assertRaises(AuthoringError): expand_registry_test(t)
 def test_refuse_missing_exists(self):
  t=copy.deepcopy(TEST); del t["states"][0]["expect"]["existence"]
  with self.assertRaises(AuthoringError): expand_registry_test(t)

if __name__ == "__main__":
 unittest.main()
