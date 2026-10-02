#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
COMMON=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
REGISTRY=Registry().with_resource(COMMON["$id"],Resource.from_contents(COMMON))


def generated(name):
    mapping=json.loads((ROOT/f"schema/v0.1.0/capability-mappings/{name}.json").read_text(encoding="utf-8"))
    return mapping,generate(mapping,ROOT)


def validate(schema,name,value):
    jsonschema.Draft202012Validator(schema["$defs"][name],registry=REGISTRY).validate(value)


def entity(value,operation="equal",datatype="string"):
    return {"value":value,"operation":operation,"datatype":datatype}


class UnixSysctlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("unix.sysctl")

    def test_name_selector_and_anysimple_value(self):
        validate(self.schema,"object",{
            "object_title":"IPv4 forwarding",
            "capability":"unix.sysctl",
            "select":{"name":entity("net.ipv4.ip_forward")},
        })
        validate(self.schema,"state",{
            "state_title":None,
            "capability":"unix.sysctl",
            "state":{
                "field":"value","value":0,"operation":"equal","datatype":"integer","match":"all","existence":"some",
            },
        })


class LinuxPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("linux.partition")

    def test_mount_point_selector_and_integer_capacity_fields(self):
        validate(self.schema,"object",{
            "object_title":"tmp partition",
            "capability":"linux.partition",
            "select":{"mount_point":entity("/tmp")},
        })
        for field in ("total_space","space_used","space_left","space_left_for_unprivileged_users","block_size"):
            with self.subTest(field=field):
                validate(self.schema,"state",{
                    "state_title":None,
                    "capability":"linux.partition",
                    "state":{
                        "field":field,"value":1,"operation":"greater_or_equal","datatype":"integer","match":"all","existence":"some",
                    },
                })

    def test_mount_options_completeness_rule_is_retained(self):
        ids={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("linux.partition.mount_options_complete",ids)


class LinuxSystemdUnitPropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("linux.systemdunitproperty")

    def test_unit_property_pair_is_required(self):
        validate(self.schema,"object",{
            "object_title":"sshd active state",
            "capability":"linux.systemdunitproperty",
            "select":{
                "unit":entity("sshd.service"),
                "property":entity("ActiveState"),
            },
        })
        with self.assertRaises(jsonschema.ValidationError):
            validate(self.schema,"object",{
                "object_title":None,
                "capability":"linux.systemdunitproperty",
                "select":{"unit":entity("sshd.service")},
            })

    def test_property_value_retains_anysimple_datatype(self):
        validate(self.schema,"state",{
            "state_title":None,
            "capability":"linux.systemdunitproperty",
            "state":{
                "field":"value","value":"active","operation":"equal","datatype":"string","match":"all","existence":"some",
            },
        })


if __name__=="__main__":
    unittest.main()
