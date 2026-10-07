#!/usr/bin/env python3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scap_upconvert_v003.convert_collection_review import source_rule_resolver


DS = "http://scap.nist.gov/schema/scap/source/1.2"
XCCDF = "http://checklists.nist.gov/xccdf/1.2"
OVAL = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
WIN = "http://oval.mitre.org/XMLSchema/oval-definitions-5#windows"


def package_xml():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ds:data-stream-collection xmlns:ds="{DS}">
  <ds:component id="scap_example_comp_product-xccdf.xml">
    <Benchmark xmlns="{XCCDF}" id="example">
      <Rule id="xccdf_example_rule_SV-1r1_rule">
        <title>Example</title>
        <check system="{OVAL}">
          <check-content-ref href="product-oval.xml" name="oval:example:def:1"/>
        </check>
      </Rule>
    </Benchmark>
  </ds:component>
  <ds:component id="scap_example_comp_product-oval.xml">
    <oval_definitions xmlns="{OVAL}" xmlns:win="{WIN}">
      <definitions>
        <definition id="oval:example:def:1" version="1" class="compliance">
          <metadata><title>Main definition</title></metadata>
          <criteria><criterion test_ref="oval:example:tst:1" comment="main"/></criteria>
        </definition>
      </definitions>
      <tests>
        <win:registry_test id="oval:example:tst:1" version="1" check="all" check_existence="at_least_one_exists">
          <win:object object_ref="oval:example:obj:1"/>
        </win:registry_test>
      </tests>
      <objects>
        <win:registry_object id="oval:example:obj:1" version="1">
          <win:hive>HKEY_LOCAL_MACHINE</win:hive>
          <win:key>SOFTWARE\\Main</win:key>
          <win:name>Value</win:name>
        </win:registry_object>
      </objects>
      <states/>
      <variables/>
    </oval_definitions>
  </ds:component>
  <ds:component id="scap_example_comp_product-cpe-oval.xml">
    <oval_definitions xmlns="{OVAL}" xmlns:win="{WIN}">
      <definitions>
        <definition id="oval:example:def:1" version="1" class="inventory">
          <metadata><title>CPE definition</title></metadata>
          <criteria><criterion test_ref="oval:example:tst:1" comment="cpe"/></criteria>
        </definition>
      </definitions>
      <tests>
        <win:registry_test id="oval:example:tst:1" version="1" check="all" check_existence="at_least_one_exists">
          <win:object object_ref="oval:example:obj:1"/>
        </win:registry_test>
      </tests>
      <objects>
        <win:registry_object id="oval:example:obj:1" version="1">
          <win:hive>HKEY_LOCAL_MACHINE</win:hive>
          <win:key>SOFTWARE\\CPE</win:key>
          <win:name>Value</win:name>
        </win:registry_object>
      </objects>
      <states/>
      <variables/>
    </oval_definitions>
  </ds:component>
</ds:data-stream-collection>
"""


def object_key(root):
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "key":
            return node.text
    return None


class SourceComponentResolutionTests(unittest.TestCase):
    def test_same_oval_ids_in_main_and_cpe_components_resolve_by_href(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "source.zip"
            with zipfile.ZipFile(package, "w") as zf:
                zf.writestr("source.xml", package_xml())

            benchmark, resolve = source_rule_resolver(package)
            self.assertEqual(benchmark.tag.rsplit("}", 1)[-1], "Benchmark")

            main = resolve("product-oval.xml", "oval:example:def:1")
            cpe = resolve("product-cpe-oval.xml", "oval:example:def:1")

            self.assertEqual(object_key(main), "SOFTWARE\\Main")
            self.assertEqual(object_key(cpe), "SOFTWARE\\CPE")
            self.assertNotEqual(object_key(main), object_key(cpe))


if __name__ == "__main__":
    unittest.main()
