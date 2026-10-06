#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
V02=ROOT/"schema/v0.2.0"
V03=ROOT/"schema/v0.3.0"


class SchemaV03Independence(unittest.TestCase):
    def files(self,root):
        return {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file()
        }

    def test_v03_has_complete_v02_inventory(self):
        self.assertEqual(self.files(V02),self.files(V03))

    def test_v03_contains_no_v02_schema_references(self):
        offenders=[]
        for path in sorted(V03.rglob("*")):
            if not path.is_file():
                continue
            text=path.read_text(encoding="utf-8")
            if "v0.2.0" in text or "schema/v0.2.0" in text:
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders,[])

    def test_v03_json_schema_identity_is_v03(self):
        offenders=[]
        for path in sorted(V03.glob("*.json")):
            text=path.read_text(encoding="utf-8")
            if '"$id"' in text and "/v0.3.0/" not in text:
                offenders.append(path.name)
        self.assertEqual(offenders,[])


if __name__=="__main__":
    unittest.main()
