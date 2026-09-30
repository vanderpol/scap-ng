#!/usr/bin/env python3
"""Conservative transitive XSD attribute-default inventory.

Only globally named complex types, attribute groups and attributes are resolved.
An unresolved reference, cycle or ambiguous declaration makes the affected
type INCOMPLETE; no speculative defaults are reported as complete semantics.
This tool is audit evidence, not an executable OVAL default oracle.
"""
from __future__ import annotations

import collections
from pathlib import Path
from lxml import etree as ET

XSD = "http://www.w3.org/2001/XMLSchema"
XS = "{" + XSD + "}"


def qname(node, value):
    if not value:
        return None
    if ":" in value:
        prefix, name = value.split(":", 1)
        uri = node.nsmap.get(prefix)
        return (uri, name) if uri else None
    # QName-valued XSD attributes use the in-scope default namespace.
    return (node.nsmap.get(None, ""), value)


def catalog(folder):
    definitions = collections.defaultdict(list)
    for path in sorted(Path(folder).glob("*.xsd")):
        root = ET.parse(str(path)).getroot()
        namespace = root.get("targetNamespace", "")
        for node in root:
            if not isinstance(node.tag, str):
                continue
            kind = ET.QName(node).localname
            if kind in {"complexType", "attributeGroup", "attribute"} and node.get("name"):
                definitions[(namespace, kind, node.get("name"))].append((path.name, node))
    return definitions


def effective_type_attributes(definitions, namespace, typename):
    """Return (attributes, blockers). Attributes are keyed by XML QName/local name.

    A derived local declaration replaces an inherited attribute: a replacement
    without default/fixed removes the inherited default, not just its provenance.
    A prohibited attribute similarly removes it. XSD restriction checks remain
    the responsibility of schema validation; invalid restrictions do not become
    authority for behavior.
    """
    active = set()
    cache = {}

    def lookup(kind, key):
        matches = definitions.get((key[0], kind, key[1]), [])
        if len(matches) != 1:
            return None, [{
                "reason": "ambiguous" if matches else "not_found",
                "kind": kind, "name": list(key),
                "matches": len(matches),
            }]
        return matches[0], []

    def resolve(kind, key):
        identity = (kind, key)
        if identity in cache:
            attrs, blockers = cache[identity]
            return dict(attrs), list(blockers)
        if identity in active:
            return {}, [{"reason": "cycle", "kind": kind, "name": list(key)}]
        if kind == "complexType" and key[0] == XSD:
            return {}, []
        result, errors = lookup(kind, key)
        if errors:
            return {}, errors
        path, node = result
        active.add(identity)
        attrs = {}
        blockers = []

        def apply_attribute(attr):
            name = attr.get("name")
            ref = attr.get("ref")
            if ref:
                referred = qname(attr, ref)
                if referred is None:
                    blockers.append({"reason": "unknown_namespace", "reference": ref,
                                     "file": path})
                    return
                source, missing = lookup("attribute", referred)
                if missing:
                    blockers.extend(missing)
                    return
                _, original = source
                if name is None:
                    name = referred[1]
                default = attr.get("default", original.get("default"))
                fixed = attr.get("fixed", original.get("fixed"))
            else:
                default = attr.get("default")
                fixed = attr.get("fixed")
            if not name:
                blockers.append({"reason": "unnamed_attribute", "file": path})
                return
            if attr.get("use") == "prohibited":
                attrs.pop(name, None)
                return
            # Override inherited defaults even if the derived declaration
            # provides no new default/fixed.
            attrs.pop(name, None)
            if default is not None or fixed is not None:
                attrs[name] = {
                    "value": fixed if fixed is not None else default,
                    "kind": "fixed" if fixed is not None else "default",
                    "declaration": name,
                    "declared_in": path,
                    "owner_type": key[1],
                }

        # Attribute-bearing nodes: direct complexType/attributeGroup children,
        # or an extension/restriction reached through (simple|complex)Content.
        bases = [n for n in node
                 if isinstance(n.tag, str)
                 and n.tag in (XS + "simpleContent", XS + "complexContent")]
        owner = node
        if bases:
            derivations = [
                c for c in bases[0]
                if isinstance(c.tag, str)
                and c.tag in (XS + "extension", XS + "restriction")
            ]
            if len(derivations) != 1:
                blockers.append({"reason": "unrecognized_content_derivation",
                                 "file": path, "type": key[1]})
            else:
                owner = derivations[0]
                base_name = owner.get("base")
                base = qname(owner, base_name)
                if base is None:
                    blockers.append({"reason": "unknown_base_namespace",
                                     "reference": base_name, "file": path})
                else:
                    inherited, failed = resolve("complexType", base)
                    attrs.update(inherited)
                    blockers.extend(failed)

        for child in owner:
            if not isinstance(child.tag, str):
                continue
            if child.tag == XS + "attribute":
                apply_attribute(child)
            elif child.tag == XS + "attributeGroup":
                reference = child.get("ref")
                group = qname(child, reference)
                if group is None:
                    blockers.append({"reason": "unknown_group_namespace",
                                     "reference": reference, "file": path})
                else:
                    inherited, failed = resolve("attributeGroup", group)
                    attrs.update(inherited)
                    blockers.extend(failed)
            elif child.tag == XS + "anyAttribute":
                # Wildcard declarations have no enumerable defaults, but may
                # affect the complete attribute *surface*; explicitly flag.
                blockers.append({"reason": "attribute_wildcard", "file": path})
        active.remove(identity)
        cache[identity] = (dict(attrs), list(blockers))
        return attrs, blockers

    attrs, blockers = resolve("complexType", (namespace, typename))
    return attrs, blockers


def inventory(folder):
    definitions = catalog(folder)
    types = []
    for namespace, kind, name in sorted(definitions, key=str):
        if kind != "complexType":
            continue
        attrs, blockers = effective_type_attributes(definitions, namespace, name)
        types.append({
            "namespace": namespace, "type": name,
            "defaults": attrs,
            "blockers": blockers,
            "status": "incomplete" if blockers else "resolved",
        })
    return {
        "scope": "named complex types only; structural attribute defaults, not runtime semantics",
        "types": types,
        "summary": {
            "named_complex_types": len(types),
            "resolved_types": sum(t["status"] == "resolved" for t in types),
            "incomplete_types": sum(t["status"] != "resolved" for t in types),
            "types_with_defaults": sum(bool(t["defaults"]) for t in types),
            "incomplete_type_details": [
                {"namespace": t["namespace"], "type": t["type"],
                 "blockers": t["blockers"]} for t in types
                if t["status"] == "incomplete"
            ],
            "blockers_by_reason": dict(sorted(collections.Counter(
                b["reason"] for t in types for b in t["blockers"]
            ).items())),
        },
    }
