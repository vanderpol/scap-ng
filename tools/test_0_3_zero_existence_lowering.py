"""Real IIS source: OVAL 'none exist' has explicit zero-item semantics."""
import unittest
from normalize_0_3_review_surface import normalize_scalar_tree


def lower(test):
    edits=[]
    doc={"assessment":{"tests":{"no-forbidden-files-test":test}}}
    out=normalize_scalar_tree(doc,(),edits)
    return out["assessment"]["tests"]["no-forbidden-files-test"],edits


class LegacyNoItemsTest(unittest.TestCase):
    def test_iis_no_forbidden_files_is_explicit_zero_collected_items(self):
        test,edits=lower({
            "capability":"windows.file","check_existence":"none_exist",
            "check":"none exist","reported_elements":"all",
        })
        self.assertEqual("none",test["existence"])
        self.assertEqual("all",test["match"])
        self.assertTrue(any(edit.get("original_value")=="none exist"
                            and edit.get("candidate_value")=="all" for edit in edits))

    def test_refuse_ambiguous_none_exist_with_states(self):
        with self.assertRaisesRegex(ValueError,"Cannot losslessly lower"):
            lower({"existence":"none","match":"none exist","states":["expected-state"]})

    def test_refuse_none_exist_without_zero_item_contract(self):
        with self.assertRaisesRegex(ValueError,"Cannot losslessly lower"):
            lower({"existence":"one_or_more","match":"none exist"})


if __name__=="__main__":
    unittest.main()
