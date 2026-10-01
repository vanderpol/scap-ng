"""Validate explicit Collection typing in the native named-Collection graph.

Collections are independently meaningful/reusable acquisition nodes.  They keep
their own capability instead of inheriting it from a consuming Test or Variable.
Tests and States keep their own capabilities as well; this module validates the
current compatibility contract without erasing those identities.
"""

def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def _require_capability(value, label):
    if not isinstance(value, str) or "." not in value:
        raise ValueError(f"Missing {label} capability")
    return value


def collection_types(assessment):
    """Return declared Collection capabilities after validating references.

    The returned mapping is derived from the Collections themselves.  Consumers
    may constrain compatibility, but they do not provide or overwrite a
    Collection's type.
    """
    registry = assessment.get("collections", {})
    types = {}
    active = set()

    def bind(name):
        if name not in registry:
            raise ValueError(f"Unknown Collection reference: {name}")
        if name in active:
            raise ValueError(f"Collection dependency cycle: {name}")
        if name in types:
            return types[name]

        payload = registry[name]
        capability = _require_capability(
            payload.get("capability"), f"Collection {name}"
        )
        types[name] = capability
        active.add(name)

        # OVAL set members are type-compatible with the parent Object/Collection.
        for item in nodes(payload.get("set", {})):
            member = item.get("collection")
            if isinstance(member, str):
                member_capability = bind(member)
                if member_capability != capability:
                    raise ValueError(
                        "Collection set capability mismatch: "
                        f"{name}({capability})!={member}({member_capability})"
                    )
        active.remove(name)
        return capability

    for name in registry:
        bind(name)

    for test_name, test in assessment.get("tests", {}).items():
        test_capability = _require_capability(
            test.get("capability"), f"Test {test_name}"
        )
        collection = test.get("collection")
        if isinstance(collection, str):
            collection_capability = bind(collection)
            if collection_capability != test_capability:
                raise ValueError(
                    "Test/Collection capability mismatch: "
                    f"{test_name}({test_capability})!="
                    f"{collection}({collection_capability})"
                )

        assertion = test.get("assertion", {})
        state_capability = assertion.get("state_capability")
        if state_capability is not None and state_capability != test_capability:
            raise ValueError(
                "Test/State capability mismatch: "
                f"{test_name}({test_capability})!={state_capability}"
            )
        for state in assertion.get("states", []):
            cap = state.get("capability")
            if cap is not None and cap != test_capability:
                raise ValueError(
                    "Test/State capability mismatch: "
                    f"{test_name}({test_capability})!={cap}"
                )

    for variable_name, var in assessment.get("variables", {}).items():
        # Named Collection references are self-describing; Variables do not
        # redeclare their capabilities.
        if "collection_capabilities" in var:
            raise ValueError(
                "Variable-side Collection capability declarations are obsolete: "
                f"{variable_name}"
            )

        for item in nodes(var.get("expression", {})):
            values = item.get("values")
            if not isinstance(values, dict):
                continue

            collection = values.get("collection")
            if isinstance(collection, str):
                bind(collection)
            elif isinstance(collection, dict):
                # An embedded/private Collection must also remain independently
                # typed; Variable capability is not a substitute.
                _require_capability(
                    collection.get("capability"),
                    f"embedded Collection in Variable {variable_name}",
                )
                parent_capability = collection["capability"]
                for member in nodes(collection.get("set", {})):
                    member_name = member.get("collection")
                    if isinstance(member_name, str):
                        member_capability = bind(member_name)
                        if member_capability != parent_capability:
                            raise ValueError(
                                "Embedded Collection set capability mismatch: "
                                f"{parent_capability}!={member_capability}"
                            )

    return types


def validate_capabilities(assessment):
    """Validate independently declared Test/Collection/State capabilities."""
    collection_types(assessment)

    # Filters carry State/predicate capability because they are independently
    # typed comparison nodes.  Validate rather than deleting that information.
    for name, payload in assessment.get("collections", {}).items():
        collection_capability = payload["capability"]
        for item in nodes(payload):
            if "match" in item and "capability" in item:
                if item["capability"] != collection_capability:
                    raise ValueError(f"Filter capability mismatch: {name}")

    return assessment


def place_capabilities(assessment):
    """Backward-compatible entry point; capability relocation is no longer done."""
    return validate_capabilities(assessment)
