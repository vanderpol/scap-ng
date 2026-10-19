"""#245 conservative read-only source State consumer census.

The supplied inventory is NOT proof of completeness. Source identities must
be globally qualified. This tool never authorizes semantic migration.
"""

def inventory_state_consumers(documents, state_id, *, inventory_complete=False):
    if type(state_id) is not str or not state_id or not isinstance(documents, list):
        raise ValueError("explicit state identity and document list required")
    consumers, concerns, seen = [], [], set()

    def walk(node, docid, objid, path):
        if isinstance(node, dict):
            for key, value in node.items():
                current = f"{path}/{key}"
                if key == "state" and value == state_id:
                    consumers.append({"document": docid, "kind": "object_state_reference",
                                      "owner": objid, "path": current})
                elif key == "states" and isinstance(value, list) and state_id in value:
                    consumers.append({"document": docid, "kind": "nested_state_list",
                                      "owner": objid, "path": current})
                walk(value, docid, objid, current)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, docid, objid, f"{path}/{index}")

    for index, doc in enumerate(documents):
        if not isinstance(doc, dict) or not isinstance(doc.get("source_id"), str):
            concerns.append(f"document[{index}] source identity unavailable")
            continue
        docid = doc["source_id"]
        if docid in seen:
            concerns.append(f"duplicate source document identity: {docid}")
            continue
        seen.add(docid)
        for section in ("tests", "objects"):
            mapping = doc.get(section)
            if not isinstance(mapping, dict):
                concerns.append(f"{docid}: missing/unsupported {section} mapping")
                continue
            for owner, data in mapping.items():
                if not isinstance(data, dict):
                    concerns.append(f"{docid}: unsupported {section}/{owner}")
                    continue
                if section == "tests":
                    refs = data.get("states")
                    if isinstance(refs, list):
                        if state_id in refs:
                            consumers.append({"document": docid, "kind": "test_state_reference",
                                              "owner": owner, "path": f"tests/{owner}/states"})
                    else:
                        concerns.append(f"{docid}: unsupported Test state refs {owner}")
                else:
                    walk(data, docid, owner, f"objects/{owner}")

    return {
        "state_id": state_id,
        "known_consumers": consumers,
        "concerns": concerns,
        "inventory_claimed_complete": inventory_complete is True,
        "global_source_consumers_independently_verified": False,
        "source_conversion_authorized": False,
        "status": "KNOWN_CONSUMERS_ONLY_NO_SOURCE_MIGRATION_APPROVAL",
    }
