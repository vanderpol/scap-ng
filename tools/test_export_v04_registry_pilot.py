#!/usr/bin/env python3
"""Positive/negative Windows registry 0.4 OVAL exporter fixtures (#248)."""
from copy import deepcopy
import unittest

from export_v04_oval_registry_pilot import emit, WIN, OD


def fixture():
    return {"assessment":{
        "id":"SV-253291.automated","version":18,
        "assessment_title":"Bluetooth radio must be turned off",
        "class":"compliance","purpose":"assessment","mode":"automated",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "tests":{"bluetooth-registry-test":{
            "test_title":"Bluetooth radio must be turned off.",
            "capability":"windows.registry",
            "object":{"object_title":"Verify the Bluetooth radio is turned off",
                      "select":{"hive":{"equals":"local_machine"},
                                "key":{"equals":"SOFTWARE\\Microsoft\\PolicyManager\\current\\device\\Connectivity"},
                                "name":{"equals":"AllowBluetooth"}}},
            "states":[{"value":{"require":"at_least_one_exists_and_all_match",
                                "equals":"0"}}],
            "reported_elements":"all",
            "require":"at_least_one_exists_and_only_one_matches"}},
        "evaluate":{"test":"bluetooth-registry-test"}}}


class RegistryPilotTests(unittest.TestCase):
    def test_original_ordered_registry_selection_and_string_state(self):
        tree,rootid=emit(fixture())
        self.assertEqual(rootid,"oval:scap-ng.v04.registry.pilot:def:1")
        root=tree.getroot()
        t=next(root.iter("{"+WIN+"}registry_test"))
        self.assertEqual(t.get("check"),"only one")
        self.assertEqual(t.get("comment"),"Bluetooth radio must be turned off.")
        obj=next(root.iter("{"+WIN+"}registry_object"))
        self.assertEqual([c.tag.split("}")[-1] for c in obj],["hive","key","name"])
        self.assertEqual(next(obj.iter("{"+WIN+"}hive")).text,"HKEY_LOCAL_MACHINE")
        self.assertEqual(next(root.iter("{"+WIN+"}value")).text,"0")
        self.assertEqual(list(root.iter("{"+OD+"}set")),[])

    def test_data_loss_and_ambiguous_registry_sources_are_rejected(self):
        for change in (
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"]["object"]["select"]["hive"].update(equals="current_user"),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"]["object"].update(set={"operator":"union","operands":[]}),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"]["states"].append(
                deepcopy(a["assessment"]["tests"]["bluetooth-registry-test"]["states"][0])),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"].update(require="may_be_absent"),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"]["states"][0]["value"].update(equals=0),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"]["states"][0]["value"].update(greater_than=0),
            lambda a:a["assessment"]["tests"]["bluetooth-registry-test"].update(test_title=""),
            lambda a:a["assessment"]["specification"].update(version="0.3.0"),
        ):
            candidate=fixture()
            with self.subTest(change=str(change)):
                change(candidate)
                with self.assertRaises(ValueError):
                    emit(candidate)


if __name__=="__main__":
    unittest.main()
