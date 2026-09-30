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
    if not fam and ns.startswith(OD+"#"):
        fam=ns.split("#",1)[1]
    if not fam: raise ValueError(f"unsupported namespace {ns}")
    return fam+"."+local[:-len(suffix)]
def sval(v):
    return "" if v is None else v

class Model:
    def __init__(self,path):
        self.root=ET.parse(path).getroot()
        self.definitions={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}definitions") for e in sec}
        self.tests={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}tests") for e in sec}
        self.objects={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}objects") for e in sec}
        self.states={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}states") for e in sec}
        self.vars={e.attrib["id"]:e for sec in self.root.findall(f"{{{OD}}}variables") for e in sec}
        self.memo={}

    def entity(self,e):
        _,local=split(e.tag)
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
        if local=="unique":
            return ("unique",tuple(self.component(c) for c in e))
        if local=="split":
            return ("split",e.attrib["delimiter"],tuple(self.component(c) for c in e))
        if local in ("begin","end"):
            return (local,e.attrib["character"],self.component(list(e)[0]))
        if local=="escape_regex":
            return ("escape_regex",self.component(list(e)[0]))
        if local=="substring":
            return ("substring",e.attrib["substring_start"],e.attrib["substring_length"],self.component(list(e)[0]))
        if local=="regex_capture":
            return ("regex_capture",e.attrib.get("pattern"),self.component(list(e)[0]))
        if local=="glob_to_regex":
            return ("glob_to_regex",e.attrib.get("glob_noescape","false"),self.component(list(e)[0]))
        if local=="time_difference":
            return ("time_difference",e.attrib.get("format_1","year_month_day"),e.attrib.get("format_2","year_month_day"),tuple(self.component(c) for c in e))
        if local=="merge":
            return ("merge",e.attrib.get("delimiter",""),e.attrib.get("sort","document"),e.attrib.get("order","ascending"),tuple(self.component(c) for c in e))
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
        self.memo[key]=("recursion-state",sid)
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
        self.memo[key]=("recursion-object",oid)
        body=[]
        for c in e:
            ns,local=split(c.tag)
            if ns==OD and local=="set":
                body.append(self.setexpr(c))
            elif ns==OD and local=="filter":
                body.append(("filter",c.attrib.get("action","exclude"),self.state(c.text.strip())))
            elif local=="behaviors":
                body.append(("behaviors",tuple(sorted(c.attrib.items()))))
            else:
                body.append(self.entity(c))
        out=("object",typed(e,"_object"),tuple(body))
        self.memo[key]=out; return out

    def test(self,tid):
        e=self.tests[tid]
        body=[]
        for c in e:
            _,local=split(c.tag)
            if local=="object":
                body.append(("object",self.obj(c.attrib["object_ref"])))
            elif local=="state":
                body.append(("state",self.state(c.attrib["state_ref"])))
            else:
                raise ValueError(f"unsupported test child {local}")
        return ("test",typed(e,"_test"),
                e.attrib.get("check_existence","at_least_one_exists"),
                e.attrib["check"],e.attrib.get("state_operator","AND"),tuple(body))

    def criteria(self,e):
        op=e.attrib.get("operator","AND")
        neg=e.attrib.get("negate","false")=="true"
        app=e.attrib.get("applicability_check","false")=="true"
        kids=[]
        for child in e:
            _,local=split(child.tag)
            cneg=child.attrib.get("negate","false")=="true"
            capp=child.attrib.get("applicability_check","false")=="true"
            if local=="criteria":
                node=self.criteria(child)
            elif local=="criterion":
                node=("test",self.test(child.attrib["test_ref"]))
            elif local=="extend_definition":
                node=self.definition(child.attrib["definition_ref"])
            else:
                raise ValueError(f"unsupported criteria child {local}")
            if cneg or capp:
                node=("edge",cneg,capp,node)
            kids.append(node)
        # Common source wrappers containing one child do not change truth semantics.
        if op=="AND" and not neg and not app and len(kids)==1:
            return kids[0]
        return ("criteria",op,neg,app,tuple(sorted(kids,key=repr)))

    def definition(self,did):
        key=("definition",did)
        if key in self.memo:return self.memo[key]
        e=self.definitions[did]
        self.memo[key]=("recursion-definition",did)
        crit=e.find(f"{{{OD}}}criteria")
        if crit is None: raise ValueError(f"{did}: definition has no criteria")
        out=self.criteria(crit)
        self.memo[key]=out; return out

    def test_multiset(self):
        return collections.Counter(repr(self.test(t)) for t in self.tests)

    def object_multiset(self):
        return collections.Counter(repr(self.obj(o)) for o in self.objects)

    def state_multiset(self):
        return collections.Counter(repr(self.state(s)) for s in self.states)

    def variable_multiset(self):
        return collections.Counter(repr(self.variable(v)) for v in self.vars)

def compare(a,b,source_root=None,regenerated_root=None,root_only=False):
    am=Model(a); bm=Model(b)
    result={"equal":True}
    if not root_only:
        for label, A, B in [
        ("test", am.test_multiset(), bm.test_multiset()),
        ("object", am.object_multiset(), bm.object_multiset()),
        ("state", am.state_multiset(), bm.state_multiset()),
            ("variable", am.variable_multiset(), bm.variable_multiset()),
        ]:
            only_a=list((A-B).elements()); only_b=list((B-A).elements())
            result[label+"_equal"]=not only_a and not only_b
            result["only_source_"+label]=only_a
            result["only_regenerated_"+label]=only_b
            result["source_"+label+"_count"]=sum(A.values())
            result["regenerated_"+label+"_count"]=sum(B.values())
            result["equal"]=result["equal"] and result[label+"_equal"]
    if source_root:
        if not regenerated_root:
            if len(bm.definitions)!=1:
                raise ValueError("regenerated root must be supplied when output contains != 1 definition")
            regenerated_root=next(iter(bm.definitions))
        sd=am.definition(source_root); rd=bm.definition(regenerated_root)
        result["definition_equal"]=sd==rd
        result["source_definition"]=repr(sd)
        result["regenerated_definition"]=repr(rd)
        result["equal"]=result["equal"] and result["definition_equal"]
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path); ap.add_argument("regenerated",type=Path)
    ap.add_argument("--source-root"); ap.add_argument("--regenerated-root")
    ap.add_argument("--root-only",action="store_true")
    ap.add_argument("--json",action="store_true")
    a=ap.parse_args()
    r=compare(a.source,a.regenerated,a.source_root,a.regenerated_root,a.root_only)
    print(json.dumps(r,indent=2) if a.json else ("EQUAL" if r["equal"] else json.dumps(r,indent=2)))
    raise SystemExit(0 if r["equal"] else 1)
if __name__=="__main__": main()
