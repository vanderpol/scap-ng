#!/usr/bin/env python3
import unittest

from prove_rhel_dconf_observation import (
    ITEM_EXPORT,
    VALUE_EXPORT,
    extract,
    flatten,
    observation_document,
    validate_consumer_binding,
)


class RhelDconfObservationTests(unittest.TestCase):
    def source(self):
        object_name="dconf-user-databases-object"
        variable_name="dconf-user-database-locks-directories-variable"
        return {
            "assessment":{
                "id":"SV-test",
                "mode":"automated",
                "objects":{
                    object_name:{
                        "object_title":"dconf user databases",
                        "capability":"independent.textfilecontent54",
                        "select":{
                            "filepath":{"operation":"equals","datatype":"string","value":"/etc/dconf/profile/user"},
                            "pattern":{"operation":"pattern match","datatype":"string","value":r"^system-db:(\S+)\s*$"},
                            "instance":{"operation":"greater than or equal","datatype":"integer","value":1},
                        },
                    },
                    "rule-object":{
                        "object_title":"rule-specific dconf lock",
                        "capability":"independent.textfilecontent54",
                        "select":{
                            "path":{
                                "operation":"equals",
                                "datatype":"string",
                                "value":{"variable":variable_name},
                            }
                        },
                    },
                },
                "variables":{
                    variable_name:{
                        "title":"dconf user database locks directories",
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"literal":{"value":"/etc/dconf/db/","datatype":"string"}},
                                {"values":{"object":object_name,"field":"subexpression"}},
                                {"literal":{"value":".d/locks","datatype":"string"}},
                            ]
                        },
                    }
                },
                "tests":{
                    "database-exists":{
                        "capability":"independent.textfilecontent54",
                        "object":object_name,
                        "check_existence":"at_least_one_exists",
                        "check":"all",
                    },
                    "rule-test":{
                        "capability":"independent.textfilecontent54",
                        "object":"rule-object",
                        "check_existence":"at_least_one_exists",
                        "check":"all",
                    },
                },
                "evaluate":{"all":[{"test":"database-exists"},{"test":"rule-test"}]},
            }
        }

    def test_mixed_item_and_value_exports_roundtrip(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        self.assertIsNotNone(observation)
        extracted,oname,vname,counts=extract(source,observation)
        self.assertGreater(counts[ITEM_EXPORT],0)
        self.assertGreater(counts[VALUE_EXPORT],0)
        a=extracted["assessment"]
        self.assertNotIn(oname,a.get("objects",{}))
        self.assertNotIn(vname,a.get("variables",{}))
        self.assertEqual(
            a["tests"]["database-exists"]["object"],
            {"observation":"dconf","export":ITEM_EXPORT},
        )
        self.assertEqual(
            a["objects"]["rule-object"]["select"]["path"]["value"]["variable"],
            {"observation":"dconf","export":VALUE_EXPORT},
        )
        self.assertEqual(flatten(extracted,observation,oname,vname),source)

    def test_id_mismatch_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_,_,_=extract(source,observation)
        extracted["assessment"]["observations"]["dconf"]["expected_id"]="wrong"
        with self.assertRaisesRegex(ValueError,"expected_id mismatch"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_version_mismatch_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_,_,_=extract(source,observation)
        extracted["assessment"]["observations"]["dconf"]["expected_version"]=999
        with self.assertRaisesRegex(ValueError,"expected_version mismatch"):
            validate_consumer_binding(extracted["assessment"],observation)

    def test_unknown_export_fails_closed(self):
        source=self.source()
        observation=observation_document(source["assessment"])
        extracted,_,_,_=extract(source,observation)
        extracted["assessment"]["tests"]["database-exists"]["object"]={
            "observation":"dconf","export":"missing"
        }
        with self.assertRaisesRegex(ValueError,"unknown Observation export"):
            validate_consumer_binding(extracted["assessment"],observation)


if __name__=="__main__":
    unittest.main()
