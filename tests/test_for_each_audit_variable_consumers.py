from lxml import etree as ET

from tools.audit_for_each_candidates import variable_consumer_roles

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent"


def test_variable_object_text_reference_is_direct_variable_test_consumer():
    objects={}
    obj=ET.fromstring(f"""
      <variable_object xmlns="{IND}" id="oval:test:obj:1" version="1">
        <var_ref>oval:test:var:1</var_ref>
      </variable_object>
    """)
    objects[obj.get("id")]=obj

    test=ET.fromstring(f"""
      <variable_test xmlns="{IND}" id="oval:test:tst:1" version="1"
                     check_existence="all_exist" check="all">
        <object object_ref="oval:test:obj:1"/>
      </variable_test>
    """)
    tests={test.get("id"):test}

    roles=variable_consumer_roles(
        "oval:test:var:1",
        objects,
        {},
        {},
        tests,
    )
    assert roles == [{
        "kind":"direct_variable_test",
        "consumer":"oval:test:tst:1",
        "entity":"value",
        "var_check":None,
    }]


def test_variable_object_is_not_reported_as_ordinary_object_selector():
    obj=ET.fromstring(f"""
      <variable_object xmlns="{IND}" id="oval:test:obj:2" version="1">
        <var_ref>oval:test:var:2</var_ref>
      </variable_object>
    """)
    roles=variable_consumer_roles(
        "oval:test:var:2",
        {obj.get("id"):obj},
        {},
        {},
        {},
    )
    assert roles == [{
        "kind":"variable_object_source",
        "consumer":"oval:test:obj:2",
        "entity":"var_ref",
        "var_check":None,
    }]
