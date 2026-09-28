#!/usr/bin/env python3
"""Regression: deprecated OVAL tests are hard SCAP-NG conversion blockers."""
from __future__ import annotations

import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("converter",HERE/"scap14_corpus_convert.py")
converter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

WIN="http://oval.mitre.org/XMLSchema/oval-definitions-5#windows"
BASE="http://oval.mitre.org/XMLSchema/oval-definitions-5"

xml=f"""<oval_definitions xmlns="{BASE}" xmlns:win="{WIN}">
<definitions>
  <definition id="oval:test:def:1" version="1" class="compliance">
    <metadata><title>deprecated</title><description>deprecated</description></metadata>
    <criteria><criterion test_ref="oval:test:tst:1"/></criteria>
  </definition>
  <definition id="oval:test:def:2" version="1" class="compliance">
    <metadata><title>supported</title><description>supported</description></metadata>
    <criteria><criterion test_ref="oval:test:tst:2"/></criteria>
  </definition>
</definitions>
<tests>
  <win:accesstoken_test id="oval:test:tst:1" version="1"><win:object object_ref="oval:test:obj:1"/></win:accesstoken_test>
  <win:userright_test id="oval:test:tst:2" version="1"><win:object object_ref="oval:test:obj:2"/></win:userright_test>
</tests>
<objects>
  <win:accesstoken_object id="oval:test:obj:1" version="1"><win:security_principle>Administrators</win:security_principle></win:accesstoken_object>
  <win:userright_object id="oval:test:obj:2" version="1"><win:userright>SeDebugPrivilege</win:userright></win:userright_object>
</objects>
<states/>
<variables/>
</oval_definitions>"""

root=ET.fromstring(xml)
deprecated={
    f"{WIN}#accesstoken_test":{
        "deprecated":True,
        "deprecation_evidence":"Deprecated as of 5.11; replaced by userright_test.",
    }
}
inv=converter.inventory_oval(root,deprecated)
defs={x["id"]:x for x in inv["definitions"]}

blocked=defs["oval:test:def:1"]
assert blocked["migration_status"]=="unsupported", blocked
assert blocked["conversion_error"]["code"]=="deprecated_oval_test", blocked
assert blocked["conversion_error"]["deprecated_tests"][0]["qualified_type"]==f"{WIN}#accesstoken_test"

supported=defs["oval:test:def:2"]
assert supported["migration_status"]=="requires_review", supported
assert "conversion_error" not in supported, supported

tests={x["id"]:x for x in inv["tests"]}
assert tests["oval:test:tst:1"]["deprecated"] is True
assert tests["oval:test:tst:2"]["deprecated"] is False

print("PASS: deprecated OVAL tests block conversion; supported replacements remain eligible")


# Historical deprecated_info does not block a test that OVAL governance later reinstated.
with TemporaryDirectory() as td:
    catalog_path=Path(td)/"catalog.json"
    catalog_path.write_text(json.dumps({
        "test_elements":[
            {
                "namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#solaris",
                "name":"package511_test",
                "deprecated":True,
                "effective_deprecated":False,
                "reinstated":True,
            },
            {
                "namespace":WIN,
                "name":"accesstoken_test",
                "deprecated":True,
                "effective_deprecated":True,
                "reinstated":False,
            },
        ]
    }),encoding="utf-8")
    effective=converter.load_deprecated_tests(catalog_path)

assert "http://oval.mitre.org/XMLSchema/oval-definitions-5#solaris#package511_test" not in effective
assert f"{WIN}#accesstoken_test" in effective

print("PASS: OVAL governance reinstatement overrides historical deprecated_info")
