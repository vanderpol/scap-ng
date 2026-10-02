#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class CiscoIosCapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text())
        collected=json.loads((ROOT/"schema/v0.1.0/collected-item.schema.json").read_text())
        result_types=json.loads((ROOT/"schema/v0.1.0/result-types.schema.json").read_text())
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))
    def schema(self,cap):
        m=json.loads((ROOT/f"schema/v0.1.0/capability-mappings/{cap}.json").read_text())
        return generate(m,ROOT)
    def validate(self,cap,kind,value):
        jsonschema.Draft202012Validator(self.schema(cap)["$defs"][kind],registry=self.registry).validate(value)
    def e(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_shared_bgp_model(self):
        for fam in ("ios","iosxe"):
            with self.subTest(fam=fam):
                self.validate(f"{fam}.bgpneighbor","object",{
                    "object_title":"peer","capability":f"{fam}.bgpneighbor",
                    "select":{"neighbor":self.e("192.0.2.1")}
                })
                self.validate(f"{fam}.bgpneighbor","collected_item",{
                    "id":fam+"-bgp","capability":f"{fam}.bgpneighbor","status":"exists",
                    "fields":{"password":{"datatype":"string","value":"secret"}},"provenance":{}
                })

    def test_section_config_line_is_multivalue(self):
        for fam in ("ios","iosxe"):
            self.validate(f"{fam}.section","collected_item",{
                "id":fam+"-sec","capability":f"{fam}.section","status":"exists",
                "fields":{"config_line":[
                    {"datatype":"string","value":"line one"},
                    {"datatype":"string","value":"line two"}
                ]},"provenance":{}
            })

    def test_routing_ospf_area_dual_type(self):
        for fam in ("ios","iosxe"):
            self.validate(f"{fam}.routingprotocolauthintf","state",{
                "state_title":None,"capability":f"{fam}.routingprotocolauthintf",
                "state":{"field":"ospf_area","value":0,"operation":"equal","datatype":"integer",
                         "mask":False,"match":"all","existence":"some"}
            })

    def test_interface_platform_difference_is_preserved(self):
        self.validate("ios.interface","state",{
            "state_title":None,"capability":"ios.interface",
            "state":{"field":"ip_directed_broadcast_command","value":"ip directed-broadcast",
                     "operation":"equal","datatype":"string","mask":False,"match":"all","existence":"some"}
        })
        self.validate("iosxe.interface","state",{
            "state_title":None,"capability":"iosxe.interface",
            "state":{"field":"ip_directed_broadcast","value":False,
                     "operation":"equal","datatype":"boolean","mask":False,"match":"all","existence":"some"}
        })

    def test_iosxe_version_singleton(self):
        self.validate("iosxe.version","test",{
            "test_title":"IOS-XE version","capability":"iosxe.version","existence":"some","match":"all"
        })

if __name__=="__main__":
    unittest.main()
