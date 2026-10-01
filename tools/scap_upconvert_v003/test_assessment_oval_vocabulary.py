import unittest

from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary


class VocabularyAlignmentTests(unittest.TestCase):
    def test_collection_assertion_becomes_object_state_test(self):
        source = {
            "assessment": {
                "id": "a",
                "version": 1,
                "assessment_title": None,
                "mode": "automated",
                "class": "compliance",
                "purpose": "assessment",
                "collections": {
                    "config-collection": {
                        "collection_title": "Config",
                        "capability": "unix.file",
                        "select": {"filepath": "/etc/example"},
                    }
                },
                "tests": {
                    "test-config": {
                        "test_title": "Config is correct",
                        "capability": "unix.file",
                        "collection": "config-collection",
                        "assertion": {
                            "existence": "at_least_one_exists",
                            "item_quantifier": "all",
                            "state_title": "Required mode",
                            "state_capability": "unix.file",
                            "state": {"field": "mode", "value": "0644"},
                        },
                    }
                },
                "evaluate": {"test": "test-config"},
            }
        }
        result = align_assessment_vocabulary(source)["assessment"]
        self.assertNotIn("collections", result)
        self.assertIn("config-object", result["objects"])
        self.assertEqual(result["tests"]["test-config"]["object"], "config-object")
        self.assertEqual(result["tests"]["test-config"]["check_existence"], "at_least_one_exists")
        self.assertEqual(result["tests"]["test-config"]["check"], "all")
        self.assertNotIn("assertion", result["tests"]["test-config"])
        self.assertEqual(len(result["states"]), 1)
        state_ref = result["tests"]["test-config"]["states"][0]
        self.assertEqual(result["states"][state_ref]["state_title"], "Required mode")

    def test_equivalent_states_are_shared(self):
        state = {
            "state_title": "Masked",
            "capability": "linux.systemdunitproperty",
            "state": {"field": "value", "value": "masked"},
        }
        source = {
            "assessment": {
                "id": "a", "version": 1, "assessment_title": None,
                "mode": "automated", "class": "compliance", "purpose": "assessment",
                "collections": {
                    "one-collection": {"collection_title": None, "capability": "linux.systemdunitproperty"},
                    "two-collection": {"collection_title": None, "capability": "linux.systemdunitproperty"},
                },
                "tests": {
                    "test-one": {
                        "test_title": None, "capability": "linux.systemdunitproperty",
                        "collection": "one-collection",
                        "assertion": {"existence": "any_exist", "item_quantifier": "all", **state},
                    },
                    "test-two": {
                        "test_title": None, "capability": "linux.systemdunitproperty",
                        "collection": "two-collection",
                        "assertion": {"existence": "any_exist", "item_quantifier": "all", **state},
                    },
                },
                "evaluate": {"all": [{"test": "test-one"}, {"test": "test-two"}]},
            }
        }
        result = align_assessment_vocabulary(source)["assessment"]
        self.assertEqual(len(result["states"]), 1)
        self.assertEqual(
            result["tests"]["test-one"]["states"],
            result["tests"]["test-two"]["states"],
        )


if __name__ == "__main__":
    unittest.main()
