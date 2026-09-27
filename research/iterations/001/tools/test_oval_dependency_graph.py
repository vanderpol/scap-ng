#!/usr/bin/env python3
"""Regression test for variable-driven OVAL dependency closure and XCCDF exports."""
from pathlib import Path
import importlib.util
from lxml import etree

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("splitter", HERE/"scap14_rule_splitter.py")
splitter=importlib.util.module_from_spec(spec);spec.loader.exec_module(splitter)

O="http://oval.mitre.org/XMLSchema/oval-definitions-5"
I=O+"#independent"
X="http://checklists.nist.gov/xccdf/1.2"
q=lambda ns,name:f"{{{ns}}}{name}"

root=etree.Element(q(O,"oval_definitions"),nsmap={None:O,"ind":I})
etree.SubElement(root,q(O,"generator"))
sections={n:etree.SubElement(root,q(O,n)) for n in splitter.SECTION_ORDER}

d=etree.SubElement(sections["definitions"],q(O,"definition"),id="oval:x:def:1",version="1",**{"class":"compliance"})
etree.SubElement(d,q(O,"metadata"))
crit=etree.SubElement(d,q(O,"criteria"))
etree.SubElement(crit,q(O,"criterion"),test_ref="oval:x:tst:1")

t=etree.SubElement(sections["tests"],q(I,"textfilecontent54_test"),id="oval:x:tst:1",version="1",check="all",check_existence="at_least_one_exists")
etree.SubElement(t,q(I,"object"),object_ref="oval:x:obj:1")
etree.SubElement(t,q(I,"state"),state_ref="oval:x:ste:1")

o1=etree.SubElement(sections["objects"],q(I,"textfilecontent54_object"),id="oval:x:obj:1",version="1")
etree.SubElement(o1,q(I,"filepath"),var_ref="oval:x:var:1")
etree.SubElement(o1,q(I,"pattern")).text=".*"
etree.SubElement(o1,q(I,"instance")).text="1"

v1=etree.SubElement(sections["variables"],q(O,"local_variable"),id="oval:x:var:1",version="1",datatype="string")
etree.SubElement(v1,q(O,"object_component"),object_ref="oval:x:obj:2",item_field="filepath")

o2=etree.SubElement(sections["objects"],q(I,"file_object"),id="oval:x:obj:2",version="1")
s=etree.SubElement(o2,q(O,"set"))
etree.SubElement(s,q(O,"object_reference")).text="oval:x:obj:3"
etree.SubElement(s,q(O,"filter"),action="include").text="oval:x:ste:2"

o3=etree.SubElement(sections["objects"],q(I,"file_object"),id="oval:x:obj:3",version="1")
etree.SubElement(o3,q(I,"filepath"),var_ref="oval:x:var:2")

v2=etree.SubElement(sections["variables"],q(O,"local_variable"),id="oval:x:var:2",version="1",datatype="string")
vc=etree.SubElement(v2,q(O,"variable_component"))
etree.SubElement(vc,q(O,"var_ref")).text="oval:x:var:3"

v3=etree.SubElement(sections["variables"],q(O,"constant_variable"),id="oval:x:var:3",version="1",datatype="string")
etree.SubElement(v3,q(O,"value")).text="/etc/example"

external=etree.SubElement(sections["variables"],q(O,"external_variable"),id="oval:x:var:99",version="1",datatype="string")

st1=etree.SubElement(sections["states"],q(I,"textfilecontent54_state"),id="oval:x:ste:1",version="1")
etree.SubElement(st1,q(I,"subexpression")).text="ok"
st2=etree.SubElement(sections["states"],q(I,"file_state"),id="oval:x:ste:2",version="1")
etree.SubElement(st2,q(I,"filepath"),operation="pattern match").text=".*"

component=splitter.OvalComponent("component-oval",root)
closure,missing,edges=component.closure(["oval:x:def:1","oval:x:var:99"])
expected={
 "oval:x:def:1","oval:x:tst:1","oval:x:obj:1","oval:x:ste:1",
 "oval:x:var:1","oval:x:obj:2","oval:x:obj:3","oval:x:ste:2",
 "oval:x:var:2","oval:x:var:3","oval:x:var:99",
}
assert not missing,missing
assert closure==expected,(sorted(expected-closure),sorted(closure-expected))
kinds={e["kind"] for e in edges}
assert {"criterion_test","test_object","test_state","variable_reference","object_component","set_object_reference","set_filter_state"} <= kinds,kinds

bench=etree.Element(q(X,"Benchmark"),nsmap={None:X})
value=etree.SubElement(bench,q(X,"Value"),id="xccdf:value:1",type="string")
etree.SubElement(value,q(X,"value")).text="example"
rule=etree.SubElement(bench,q(X,"Rule"),id="xccdf_rule_1")
check=etree.SubElement(rule,q(X,"check"),system=O)
etree.SubElement(check,q(X,"check-export"),**{"export-name":"oval:x:var:99","value-id":"xccdf:value:1"})
etree.SubElement(check,q(X,"check-content-ref"),name="oval:x:def:1",href="component-oval.xml")
row=splitter.rule_oval_refs(bench)[0]
export=row["checks"][0]["exports"][0]
assert export["export_name"]=="oval:x:var:99"
assert export["value_id"]=="xccdf:value:1"
assert export["value_definition"]["name"]=="Value"
print(f"PASS: {len(closure)} dependency nodes, {len(edges)} typed edges, XCCDF export preserved")
