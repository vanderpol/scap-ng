#!/usr/bin/env python3
"""Research-only quantifier preset compiler guardrail tests."""
import unittest
from copy import deepcopy
from research_04_quantifier_aliases import (
    shorten_pair, expand_pair, ITEM_PAIR, FIELD_PAIR, ITEM_ALIAS, FIELD_ALIAS
)

class QuantifierAliasTests(unittest.TestCase):
    def test_item_roundtrip_preserves_payload(self):
        data={"object":{"capability":"unix.file"}, "existence":"one_or_more",
              "match":"all", "reported_elements":"all"}
        alias=shorten_pair(data,pair=ITEM_PAIR,label=ITEM_ALIAS)
        self.assertNotIn("existence",alias)
        self.assertNotIn("match",alias)
        self.assertEqual(expand_pair(alias,pair=ITEM_PAIR,label=ITEM_ALIAS),data)
    def test_field_roundtrip_preserves_predicate(self):
        data={"field":"mount_options","value":"nosuid","operation":"equals",
              "existence":"one_or_more","match":"one_or_more"}
        alias=shorten_pair(data,pair=FIELD_PAIR,label=FIELD_ALIAS)
        self.assertEqual(expand_pair(alias,pair=FIELD_PAIR,label=FIELD_ALIAS),data)
    def test_no_missing_pair_defaults(self):
        with self.assertRaisesRegex(ValueError,"partial"):
            shorten_pair({"match":"all"},pair=ITEM_PAIR,label=ITEM_ALIAS)
    def test_nonmatching_rare_pair_remains_explicit(self):
        with self.assertRaisesRegex(ValueError,"does not match"):
            shorten_pair({"existence":"none_exist","match":"all"},pair=ITEM_PAIR,label=ITEM_ALIAS)
    def test_no_collision(self):
        with self.assertRaisesRegex(ValueError,"collision"):
            shorten_pair({"existence":"one_or_more","match":"all","require":"other"},
                         pair=ITEM_PAIR,label=ITEM_ALIAS)
    def test_no_mixed_explicit_shorthand(self):
        with self.assertRaisesRegex(ValueError,"conflict"):
            expand_pair({"require":ITEM_ALIAS,"match":"all"},pair=ITEM_PAIR,label=ITEM_ALIAS)
    def test_no_unknown_alias(self):
        with self.assertRaisesRegex(ValueError,"Unrecognized"):
            expand_pair({"require":"probably_all"},pair=ITEM_PAIR,label=ITEM_ALIAS)
    def test_explicit_identity_with_extra_field(self):
        original={"field":"values","value":"x","operation":"not_equal",
                  "entity_check":"all",**FIELD_PAIR}
        shorter=shorten_pair(original,pair=FIELD_PAIR,label=FIELD_ALIAS)
        self.assertEqual(expand_pair(shorter,pair=FIELD_PAIR,label=FIELD_ALIAS),original)
    def test_input_not_mutated(self):
        obj={"existence":"one_or_more","match":"all","reported_elements":"all"}
        prior=deepcopy(obj)
        shorten_pair(obj,pair=ITEM_PAIR,label=ITEM_ALIAS)
        self.assertEqual(obj,prior)

if __name__=="__main__":
    unittest.main()
