#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT=Path(__file__).resolve().parents[1]


class OvalSchemaSemanticCatalogTests(unittest.TestCase):
    def test_deprecated_enum_values_are_inventoried_with_context(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"catalog.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT/"tools/build_oval_schema_semantic_catalog.py"),
                    str(ROOT/"third_party/scap-1.4-schemas/oval_5.12.3"),
                    "--parser", str(ROOT/"tools/oval_semantic_ir.py"),
                    "--output", str(output),
                ],
                check=True,
                cwd=ROOT,
            )
            doc=json.loads(output.read_text(encoding="utf-8"))

        rows=doc["deprecated_enum_values"]
        self.assertEqual(doc["deprecated_enum_value_count"], len(rows))
        self.assertGreater(len(rows), 0)

        file_behavior_rows=[
            row for row in rows
            if row.get("schema")=="unix-definitions-schema.xsd"
            and row.get("complex_type")=="FileBehaviors"
        ]
        by_attr_value={(row.get("attribute"),row["value"]) for row in file_behavior_rows}

        self.assertIn(("recurse_direction","up"), by_attr_value)
        self.assertIn(("recurse","none"), by_attr_value)
        self.assertIn(("recurse","files"), by_attr_value)
        self.assertIn(("recurse","files and directories"), by_attr_value)

        up=next(
            row for row in file_behavior_rows
            if row.get("attribute")=="recurse_direction" and row["value"]=="up"
        )
        self.assertIn("5.12.3", up["deprecation_evidence"])
        self.assertIn("unused", up["deprecation_evidence"])


if __name__=="__main__":
    unittest.main()
