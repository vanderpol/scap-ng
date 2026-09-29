#!/usr/bin/env python3
"""Lower standalone OVAL 5.12.3 into the iteration-003 round-trip NG fixture model.

This is a conformance bridge, not final native authoring syntax. It is intended
to preserve the semantic graph so the result can be regenerated as OVAL and
compared against the source.
"""
from __future__ import annotations
import argparse, json, re, hashlib
from pathlib import Path
from lxml import etree as E

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
XSI="http://www.w3.org/2001/XMLSchema-instance"
FAMS={
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#independent":"independent",
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#linux":"linux",
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#unix":"unix",
 "http://oval.mitre.org/XMLSchema/oval-definitions-5#windows":"windows",
}

def local(el): return E.QName(el).localname
def ns(el): return E.QName(el).namespace or ""

def text(el):
    return "" if el.text is None else el.text

def logical(kind, oid, el=None):
    tail=oid.rsplit(":",1)[-1]
    suffix={"def":"definition","tst":"check","obj":"collection","ste":"state","var":"variable"}[kind]
    if el is not None:
        lname=local(el)
        for ending in ("_test","_object","_state","_variable"):
            if lname.endswith(ending):
                lname=lname[:-len(ending)]
                break
        fam=FAMS.get(ns(el), "oval")
        stem=f"{fam}-{lname}-{tail}"
    else:
        stem=f"{kind}-{tail}"
    digest=hashlib.sha256(oid.encode("utf-8")).hexdigest()[:8]
    safe=re.sub(r"[^A-Za-z0-9_.-]+","-",stem).strip("-").lower()
    return f"{safe}-{digest}-{suffix}"

def type_name(el,suffix):
    fam=FAMS.get(ns(el))
    if not fam: raise ValueError(f"unsupported namespace {ns(el)} for {local(el)}")
    name=local(el)
    if not name.endswith(suffix): raise ValueError(name)
    return fam+"."+name[:-len(suffix)]

def attr_local_map(el):
    return {E.QName(k).localname:v for k,v in el.attrib.items()}

def bool_value(v):
    return str(v).lower()=="true"

class Converter:
    def __init__(self,path:Path):
        self.path=path
        self.root=E.parse(str(path)).getroot()
        self.defs={e.get("id"):e for sec in self.root.findall(f"{{{OD}}}definitions") for e in sec}
        self.tests={e.get("id"):e for sec in self.root.findall(f"{{{OD}}}tests") for e in sec}
        self.objects={e.get("id"):e for sec in self.root.findall(f"{{{OD}}}objects") for e in sec}
        self.states={e.get("id"):e for sec in self.root.findall(f"{{{OD}}}states") for e in sec}
        self.vars={e.get("id"):e for sec in self.root.findall(f"{{{OD}}}variables") for e in sec}
        self.maps={
            "def":{x:logical("def",x,e) for x,e in self.defs.items()},
            "tst":{x:logical("tst",x,e) for x,e in self.tests.items()},
            "obj":{x:logical("obj",x,e) for x,e in self.objects.items()},
            "ste":{x:logical("ste",x,e) for x,e in self.states.items()},
            "var":{x:logical("var",x,e) for x,e in self.vars.items()},
        }
        self.diagnostics=[]

    def root_definitions(self):
        incoming=set()
        for d in self.defs.values():
            for e in d.iter(f"{{{OD}}}extend_definition"):
                if e.get("definition_ref"): incoming.add(e.get("definition_ref"))
        candidates=[x for x in self.defs if x not in incoming]
        if not candidates:
            raise ValueError(f"{self.path}: cannot identify any root definition")
        return candidates

    def edge_attrs(self,el):
        out={}
        if "negate" in el.attrib: out["negate"]=bool_value(el.get("negate"))
        if "applicability_check" in el.attrib: out["applicability_check"]=bool_value(el.get("applicability_check"))
        return out

    def criteria(self,el,stack=()):
        out={"operator":el.get("operator","AND"),"children":[]}
        out.update(self.edge_attrs(el))
        for c in el:
            n=local(c)
            if n=="criterion":
                child={"check":self.maps["tst"][c.get("test_ref")]}
                child.update(self.edge_attrs(c)); out["children"].append(child)
            elif n=="criteria":
                out["children"].append(self.criteria(c,stack))
            elif n=="extend_definition":
                ref=c.get("definition_ref")
                if ref in stack: raise ValueError(f"definition cycle {' -> '.join(stack+(ref,))}")
                d=self.defs[ref]
                ce=d.find(f"{{{OD}}}criteria")
                if ce is None: raise ValueError(f"{ref}: missing criteria")
                child=self.criteria(ce,stack+(ref,))
                edge=self.edge_attrs(c)
                # Edge negate/applicability are semantically attached to the
                # extend_definition edge. Represent by wrapping criteria.
                if edge:
                    child={"operator":"AND","children":[child],**edge}
                out["children"].append(child)
            else:
                raise ValueError(f"unsupported criteria child {n}")
        return out

    def entity(self,el):
        attrs=attr_local_map(el)
        allowed={"datatype","operation","var_ref","var_check","entity_check","check_existence","mask","nil","name"}
        unknown=set(attrs)-allowed
        # xsi:nil appears as local name nil and is allowed above.
        if unknown:
            raise ValueError(f"{local(el)} unsupported entity attrs {sorted(unknown)}")
        spec={}
        for k in ("datatype","operation","var_check","entity_check","check_existence"):
            if k in attrs: spec[k]=attrs[k]
        if "mask" in attrs: spec["mask"]=bool_value(attrs["mask"])
        if el.get(f"{{{XSI}}}nil")=="true":
            spec["nil"]=True
            return spec
        fields=[x for x in el if local(x)=="field"]
        if fields:
            spec["fields"]=[]
            for f in fields:
                fs=self.entity(f)
                fs["name"]=f.get("name")
                spec["fields"].append(fs)
            return spec
        vr=el.get("var_ref")
        if vr:
            spec["variable"]=self.maps["var"][vr]
            return spec
        if local(el)=="var_ref" and text(el).strip() in self.vars:
            spec["variable_id_value"]=self.maps["var"][text(el).strip()]
            return spec
        spec["value"]=text(el)
        return spec

    def component(self,el):
        n=local(el)
        if n=="literal_component":
            out={"literal":text(el)}
            if el.get("datatype") is not None: out["datatype"]=el.get("datatype")
            return out
        if n=="variable_component":
            return {"variable":self.maps["var"][el.get("var_ref")]}
        if n=="object_component":
            oc={"collection":self.maps["obj"][el.get("object_ref")],
                "item_field":el.get("item_field")}
            if el.get("record_field") is not None: oc["record_field"]=el.get("record_field")
            return {"object_component":oc}
        args=[self.component(c) for c in el if isinstance(c.tag,str)]
        if n=="concat": return {"concat":args}
        if n=="arithmetic": return {"arithmetic":{"operation":el.get("arithmetic_operation"),"components":args}}
        if n=="count": return {"count":args}
        if n=="unique": return {"unique":args}
        if n=="split":
            if len(args)!=1: raise ValueError("split requires one component")
            return {"split":{"delimiter":el.get("delimiter"),"component":args[0]}}
        if n=="begin":
            return {"begin":{"character":el.get("character"),"component":args[0]}}
        if n=="end":
            return {"end":{"character":el.get("character"),"component":args[0]}}
        if n=="escape_regex":
            return {"escape_regex":args[0]}
        if n=="substring":
            return {"substring":{"start":el.get("substring_start"),"length":el.get("substring_length"),"component":args[0]}}
        if n=="time_difference":
            return {"time_difference":{
                "format_1":el.get("format_1","year_month_day"),
                "format_2":el.get("format_2","year_month_day"),
                "components":args}}
        if n=="regex_capture":
            return {"regex_capture":{"pattern":el.get("pattern"),"component":args[0]}}
        if n=="merge":
            return {"merge":{
                "delimiter":el.get("delimiter",""),
                "sort":el.get("sort","document"),
                "order":el.get("order","ascending"),
                "components":args}}
        if n=="glob_to_regex":
            return {"glob_to_regex":{
                "glob_noescape":bool_value(el.get("glob_noescape","false")),
                "component":args[0]}}
        raise ValueError(f"unsupported variable function {n}")

    def set_spec(self,el):
        nested=[c for c in el if local(c)=="set"]
        refs=[c for c in el if local(c)=="object_reference"]
        filters=[c for c in el if local(c)=="filter"]
        out={"operator":el.get("set_operator","UNION")}
        if nested:
            if refs or filters: raise ValueError("mixed nested/leaf set form")
            out["sets"]=[self.set_spec(c) for c in nested]
        else:
            out["collections"]=[self.maps["obj"][text(c).strip()] for c in refs]
            if filters:
                out["filters"]=[
                    {"action":f.get("action","exclude"),"state":self.maps["ste"][text(f).strip()]}
                    for f in filters
                ]
        return out

    def collection(self,oid,el):
        out={"id":self.maps["obj"][oid],"type":type_name(el,"_object")}
        kids=[c for c in el if isinstance(c.tag,str)]
        sets=[c for c in kids if ns(c)==OD and local(c)=="set"]
        if sets:
            if len(sets)!=1 or len(kids)!=1: raise ValueError(f"{oid}: invalid set object shape")
            out["set"]=self.set_spec(sets[0]); return out
        selectors={}
        filters=[]
        for c in kids:
            n=local(c)
            if n=="behaviors":
                out["behaviors"]=attr_local_map(c)
            elif ns(c)==OD and n=="filter":
                filters.append({"action":c.get("action","exclude"),"state":self.maps["ste"][text(c).strip()]})
            else:
                if n in selectors: raise ValueError(f"{oid}: duplicate entity {n}")
                selectors[n]=self.entity(c)
        if selectors: out["selectors"]=selectors
        if filters: out["filters"]=filters
        return out

    def state(self,sid,el):
        preds={}
        for c in el:
            n=local(c)
            if n in preds: raise ValueError(f"{sid}: duplicate state entity {n}")
            preds[n]=self.entity(c)
        out={"id":self.maps["ste"][sid],"type":type_name(el,"_state"),"predicates":preds}
        if "operator" in el.attrib: out["operator"]=el.get("operator")
        return out

    def variable(self,vid,el):
        kind=local(el)
        base={"id":self.maps["var"][vid],"datatype":el.get("datatype")}
        if kind=="constant_variable":
            base["kind"]="constant"; base["values"]=[text(c) for c in el if local(c)=="value"]
        elif kind=="external_variable":
            base["kind"]="external"; base["possible_values"]=[]; base["possible_restrictions"]=[]
            for c in el:
                if local(c)=="possible_value":
                    base["possible_values"].append({"hint":c.get("hint"),"value":text(c)})
                elif local(c)=="possible_restriction":
                    base["possible_restrictions"].append({
                        "hint":c.get("hint"),"operator":c.get("operator","AND"),
                        "restrictions":[{"operation":r.get("operation"),"value":text(r)}
                                        for r in c if local(r)=="restriction"]})
                else: raise ValueError(f"{vid}: unknown external variable child {local(c)}")
        elif kind=="local_variable":
            base["kind"]="local"
            kids=[c for c in el if isinstance(c.tag,str)]
            if len(kids)!=1: raise ValueError(f"{vid}: local variable component count {len(kids)}")
            base["expression"]=self.component(kids[0])
        else: raise ValueError(f"unsupported variable kind {kind}")
        return base

    def check(self,tid,el):
        obj=[c for c in el if local(c)=="object"]
        states=[c for c in el if local(c)=="state"]
        other=[c for c in el if local(c) not in {"object","state"}]
        if len(obj)!=1 or other: raise ValueError(f"{tid}: unsupported test children")
        out={
            "id":self.maps["tst"][tid],
            "type":type_name(el,"_test"),
            "check_existence":el.get("check_existence","at_least_one_exists"),
            "check":el.get("check"),
            "collection":self.maps["obj"][obj[0].get("object_ref")],
        }
        if states: out["states"]=[self.maps["ste"][s.get("state_ref")] for s in states]
        if "state_operator" in el.attrib: out["state_operator"]=el.get("state_operator")
        return out

    def convert(self):
        root_ids=self.root_definitions()
        sem={
            "checks":[self.check(k,v) for k,v in self.tests.items()],
            "collections":[self.collection(k,v) for k,v in self.objects.items()],
            "states":[self.state(k,v) for k,v in self.states.items()],
            "variables":[self.variable(k,v) for k,v in self.vars.items()],
        }
        source={"local_path":str(self.path).replace("\\","/")}
        if len(root_ids)==1:
            root_id=root_ids[0]
            rootdef=self.defs[root_id]
            crit=rootdef.find(f"{{{OD}}}criteria")
            if crit is None: raise ValueError(f"{root_id}: missing criteria")
            sem["definition_class"]=rootdef.get("class","compliance")
            sem["root"]=self.criteria(crit,(root_id,))
            source["root_definition"]=root_id
        else:
            sem["roots"]=[]
            source["root_definitions"]=root_ids
            for root_id in root_ids:
                rootdef=self.defs[root_id]
                crit=rootdef.find(f"{{{OD}}}criteria")
                if crit is None: raise ValueError(f"{root_id}: missing criteria")
                sem["roots"].append({
                    "id":self.maps["def"][root_id],
                    "definition_class":rootdef.get("class","compliance"),
                    "root":self.criteria(crit,(root_id,)),
                })
        # omit empty sections to keep fixtures readable
        for k in ("states","variables"):
            if not sem[k]: sem.pop(k)
        return {
            "fixture_version":1,
            "id":self.path.parent.name.replace("_","-") or self.path.stem,
            "source":source,
            "ng_semantics":sem,
        }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("oval",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    d=Converter(a.oval).convert()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
