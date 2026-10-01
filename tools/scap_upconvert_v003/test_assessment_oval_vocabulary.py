import unittest

from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary, legacy_intermediate_vocabulary


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

    def test_effective_mask_false_is_omitted_from_native_authoring(self):
        source = {
            "assessment": {
                "id": "a", "version": 1, "assessment_title": None,
                "mode": "automated", "class": "compliance", "purpose": "assessment",
                "collections": {
                    "config-collection": {
                        "collection_title": None,
                        "capability": "unix.file",
                        "select": {
                            "filepath": {
                                "value": "/etc/passwd",
                                "operation": "equals",
                                "datatype": "string",
                                "mask": False,
                            }
                        },
                    }
                },
                "tests": {
                    "test-config": {
                        "test_title": None,
                        "capability": "unix.file",
                        "collection": "config-collection",
                        "assertion": {
                            "existence": "at_least_one_exists",
                            "item_quantifier": "all",
                            "state_title": None,
                            "state_capability": "unix.file",
                            "state": {
                                "field": "user_id",
                                "value": "0",
                                "operation": "equals",
                                "datatype": "int",
                                "mask": False,
                            },
                        },
                    }
                },
                "evaluate": {"test": "test-config"},
            }
        }
        result = align_assessment_vocabulary(source)["assessment"]
        self.assertNotIn(
            "mask",
            result["objects"]["config-object"]["select"]["filepath"],
        )
        state_ref=result["tests"]["test-config"]["states"][0]
        self.assertNotIn("mask", result["states"][state_ref]["state"])

    def test_mask_true_fails_closed_until_redaction_mapping_exists(self):
        source = {
            "assessment": {
                "id": "a", "version": 1, "assessment_title": None,
                "mode": "automated", "class": "compliance", "purpose": "assessment",
                "collections": {
                    "secret-collection": {
                        "collection_title": None,
                        "capability": "unix.file",
                        "select": {
                            "filepath": {
                                "value": "/etc/shadow",
                                "operation": "equals",
                                "datatype": "string",
                                "mask": True,
                            }
                        },
                    }
                },
                "tests": {
                    "test-secret": {
                        "test_title": None,
                        "capability": "unix.file",
                        "collection": "secret-collection",
                        "assertion": {
                            "existence": "at_least_one_exists",
                            "item_quantifier": "all",
                        },
                    }
                },
                "evaluate": {"test": "test-secret"},
            }
        }
        with self.assertRaisesRegex(ValueError, "redaction mapping"):
            align_assessment_vocabulary(source)

    def test_alignment_round_trips_through_legacy_bridge(self):
        source = {
            "assessment": {
                "id": "a", "version": 1, "assessment_title": None,
                "mode": "automated", "class": "compliance", "purpose": "assessment",
                "collections": {
                    "config-collection": {
                        "collection_title": "Config",
                        "capability": "unix.file",
                        "select": {"filepath": "/etc/example"},
                    }
                },
                "variables": {},
                "tests": {
                    "test-config": {
                        "test_title": "Config",
                        "capability": "unix.file",
                        "collection": "config-collection",
                        "assertion": {
                            "existence": "at_least_one_exists",
                            "item_quantifier": "all",
                            "state_title": "Mode",
                            "state_capability": "unix.file",
                            "state": {"field": "mode", "value": "0644"},
                        },
                    }
                },
                "evaluate": {"test": "test-config"},
            }
        }
        aligned = align_assessment_vocabulary(source)
        restored = legacy_intermediate_vocabulary(aligned)
        self.assertEqual(restored, source)


if __name__ == "__main__":
    unittest.main()
