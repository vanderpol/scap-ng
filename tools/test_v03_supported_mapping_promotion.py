"""Release gate: active 0.3 capability mappings cannot rely on legacy bypasses."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUPPORTED=ROOT/"schema/v0.3.0/capability-mappings/supported"


class V03SupportedPromotionTests(unittest.TestCase):
    def test_every_supported_capability_is_strictly_promoted(self):
        paths=sorted(SUPPORTED.glob("*.json"))
        self.assertEqual(100,len(paths),"Review source mapping corpus change explicitly")
        missing=[]
        for path in paths:
            doc=json.loads(path.read_text(encoding="utf-8"))
            if (doc.get("native") or {}).get("post_alignment_ready") is not True:
                missing.append(doc.get("capability",path.stem))
        self.assertEqual([],missing,"0.3 supported capabilities must never skip capability-schema checks")


if __name__=="__main__":
    unittest.main()
