#!/usr/bin/env python3
"""ID-independent semantic comparator for OVAL 5.12.3 stress cases."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
FAMS={
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#independent":"independent",
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#linux":"linux",
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#unix":"unix",
}
def split(tag):
    if tag.startswith("{"):
        ns,local=tag[1:].split("}",1); return ns,local
    return "",tag
def typed(el,suffix):
    ns,local=split(el.tag)
    if not local.endswith(suffix): raise ValueError(local)
    fam=FAMS.get(ns)
    if not fam: raise ValueError(f"unsupported namespace {ns}")
    return fam+"."+local[:-len(suffix)]
def sval(v):
    return "" if v is None else v
def attrs(el, names, defaults=None):
    defaults=defaults or {}
    return tuple((n,el.attrib.get(n,defaults.get(n))) for n in names)
class Model:
    def __init__(self,path):
        self.root=ET.parse(path).getroot()
        self.tests={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}tests") for e in sec}
        self.objects={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}objects") for e in sec}
        self.states={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}states") for e in sec}
        self.vars={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}variables") for e in sec}
        self.memo={}
    def entity(self,e):
        ns,local=split(e.tag)
        base=("entity",local,
              e.attrib.get("datatype","string"),
              e.attrib.get("operation","equals"),
              e.attrib.get("var_check","all"),
              e.attrib.get("entity_check","all"))
        vr=e.attrib.get("var_ref")
        if vr: return base+("var",self.variable(vr))
        return base+("value",sval(e.text))
    def component(self,e):
        ns,local=split(e.tag)
        if ns!=OD: raise ValueError(f"unsupported component ns {ns}")
        if local=="literal_component":
            return ("literal",e.attrib.get("datatype","string"),sval(e.text))
        if local=="variable_component":
            return ("variable",self.variable(e.attrib["var_ref"]))
        if local=="object_component":
            return ("object_component",self.obj(e.attrib["object_ref"]),e.attrib["item_field"],e.attrib.get("record_field"))
        if local=="concat":
            return ("concat",tuple(self.component(c) for c in e))
        if local=="arithmetic":
            return ("arithmetic",e.attrib["arithmetic_operation"],tuple(self.component(c) for c in e))
        if local=="count":
            return ("count",tuple(self.component(c) for c in e))
        raise ValueError(f"unsupported component {local}")
    def variable(self,vid):
        key=("var",vid)
        if key in self.memo:return self.memo[key]
        e=self.vars[vid]; _,local=split(e.tag)
        head=(local,e.attrib["datatype"])
        self.memo[key]=("recursion",vid)
        if local=="constant_variable":
            out=head+(tuple(sval(x.text) for x in e.findall(f"{{{OD}}}value")),)
        elif local=="local_variable":
            kids=list(e)
            if len(kids)!=1: raise ValueError(f"{vid}: expected one expression")
            out=head+(self.component(kids[0]),)
        else: raise ValueError(f"unsupported variable {local}")
        self.memo[key]=out; return out
    def state(self,sid):
        key=("state",sid)
        if key in self.memo:return self.memo[key]
        e=self.states[sid]
        self.memo[key]=("recursion",sid)
        out=("state",typed(e,"_state"),e.attrib.get("operator","AND"),
             tuple(self.entity(c) for c in e))
        self.memo[key]=out; return out
    def setexpr(self,e):
        return ("set",e.attrib.get("set_operator","UNION"),
                tuple(self.obj(c.text.strip()) for c in e.findall(f"{{{OD}}}object_reference")),
                tuple((f.attrib.get("action","exclude"),self.state(f.text.strip()))
                      for f in e.findall(f"{{{OD}}}filter")))
    def obj(self,oid):
        key=("obj",oid)
        if key in self.memo:return self.memo[key]
        e=self.objects[oid]
        self.memo[key]=("recursion",oid)
        body=[]
        for c in e:
            ns,local=split(c.tag)
            if ns==OD and local=="set": body.append(self.setexpr(c))
            elif ns==OD and local=="filter": body.append(("filter",c.attrib.get("action","exclude"),self.state(c.text.strip())))
            elif local=="behaviors": body.append(("behaviors",tuple(sorted(c.attrib.items()))))
            else: body.append(self.entity(c))
        out=("object",typed(e,"_object"),tuple(body))
        self.memo[key]=out; return out
    def test(self,tid):
        e=self.tests[tid]
        body=[]
        ns,_=split(e.tag)
        for c in e:
            cns,local=split(c.tag)
            if local=="object": body.append(("object",self.obj(c.attrib["object_ref"])))
            elif local=="state": body.append(("state",self.state(c.attrib["state_ref"])))
            else: raise ValueError(f"unsupported test child {local}")
        return ("test",typed(e,"_test"),
                e.attrib.get("check_existence","at_least_one_exists"),
                e.attrib["check"],e.attrib.get("state_operator","AND"),tuple(body))
    def test_multiset(self):
        return collections.Counter(repr(self.test(t)) for t in self.tests)

def compare(a,b):
    am=Model(a); bm=Model(b)
    A=am.test_multiset(); B=bm.test_multiset()
    only_a=list((A-B).elements()); only_b=list((B-A).elements())
    return {"equal":not only_a and not only_b,"only_source":only_a,"only_regenerated":only_b,
            "source_test_count":sum(A.values()),"regenerated_test_count":sum(B.values())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path); ap.add_argument("regenerated",type=Path)
    ap.add_argument("--json",action="store_true")
    a=ap.parse_args()
    r=compare(a.source,a.regenerated)
    print(json.dumps(r,indent=2) if a.json else ("EQUAL" if r["equal"] else json.dumps(r,indent=2)))
    raise SystemExit(0 if r["equal"] else 1)
if __name__=="__main__": main()
