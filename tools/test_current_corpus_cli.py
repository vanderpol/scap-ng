"""Exercise the actual corpus CLI so broad regression requires OVAL-aligned authored syntax."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_named_collection_graph import NamedCollections

ROOT = Path(__file__).resolve().parents[1]

class CorpusCLI(unittest.TestCase):
    def run_layout(self, layout=None):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            corpus = folder / "source"
            corpus.mkdir()
            ET.ElementTree(NamedCollections().linked_source()).write(corpus / "fixture.xml", encoding="utf-8")
            command = [sys.executable, str(ROOT / "tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py"),
                       "--corpus", str(corpus), "--out", str(folder / "out"),
                       "--report", str(folder / "report.json")]
            if layout:
                command.extend(["--layout", layout])
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((folder / "report.json").read_text())
            native = json.loads(next((folder / "out").glob("*.native.json")).read_text())
            return report, native["assessment"]

    def test_default_cli_preserves_current_named_graph(self):
        report, native = self.run_layout()
        self.assertEqual(report["native_layout"], "current")
        self.assertEqual(report["semantic_equal"], 1)
        self.assertIn("objects", native)
        self.assertIn("tests", native)
        self.assertNotIn("checks", native)
        self.assertEqual(len(native["objects"]), 2)
        ref = next(iter(native["variables"].values()))["expression"]["values"]["object"]
        self.assertIn(ref, [node["object"] for node in native["tests"].values()])
        sections = [key for key in native if key in ("objects", "variables", "states", "tests", "evaluate")]
        self.assertEqual(sections, ["objects", "variables", "states", "tests", "evaluate"])

    def test_historical_baseline_requires_explicit_switch(self):
        report, native = self.run_layout("historical")
        self.assertEqual(report["native_layout"], "historical")
        self.assertEqual(report["semantic_equal"], 1)
        self.assertIn("checks", native)

if __name__ == "__main__":
    unittest.main()
