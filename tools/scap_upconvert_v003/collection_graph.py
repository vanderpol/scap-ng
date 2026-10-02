"""Validate explicit Collection typing in the native named-Collection graph.

Collections are independently meaningful/reusable acquisition nodes.  They keep
their own capability instead of inheriting it from a consuming Test or Variable.
Tests and States keep their own capabilities as well; this module validates the
current compatibility contract without erasing those identities.
"""

def nodes(value):
    """Yield mapping nodes iteratively so deep valid graphs are stack-safe."""
    stack=[value]
    while stack:
        current=stack.pop()
        if isinstance(current,dict):
            yield current
            stack.extend(reversed(list(current.values())))
        elif isinstance(current,list):
            stack.extend(reversed(current))


def _require_capability(value, label):
    if not isinstance(value, str) or "." not in value:
        raise ValueError(f"Missing {label} capability")
    return value


def collection_types(assessment):
    """Return declared Collection capabilities after validating references.

    Resolution is iterative so valid deep Collection DAGs do not depend on
    Python recursion depth. Consumers constrain compatibility but never provide
    or overwrite a Collection's declared capability.
    """
    registry = assessment.get("collections", {})
    types = {}
    adjacency = {}

    for name, payload in registry.items():
        types[name] = _require_capability(
            payload.get("capability"), f"Collection {name}"
        )

    def require_collection(name):
        if name not in registry:
            raise ValueError(f"Unknown Collection reference: {name}")
        return types[name]

    # Validate set-member references/types and build the dependency graph.
    for name, payload in registry.items():
        capability = types[name]
        members = []
        for item in nodes(payload.get("set", {})):
            member = item.get("collection")
            if not isinstance(member, str):
                continue
            member_capability = require_collection(member)
            if member_capability != capability:
                raise ValueError(
                    "Collection set capability mismatch: "
                    f"{name}({capability})!={member}({member_capability})"
                )
            members.append(member)
        adjacency[name] = members

    # Iterative DFS cycle detection. A deep but acyclic graph is valid.
    color = {name: 0 for name in registry}  # 0=unseen, 1=active, 2=done
    for root in registry:
        if color[root]:
            continue
        color[root] = 1
        stack = [(root, 0)]
        while stack:
            name, index = stack[-1]
            members = adjacency[name]
            if index >= len(members):
                color[name] = 2
                stack.pop()
                continue
            member = members[index]
            stack[-1] = (name, index + 1)
            if color[member] == 1:
                raise ValueError(f"Collection dependency cycle: {member}")
            if color[member] == 0:
                color[member] = 1
                stack.append((member, 0))

    for test_name, test in assessment.get("tests", {}).items():
        test_capability = _require_capability(
            test.get("capability"), f"Test {test_name}"
        )
        collection = test.get("collection")
        if isinstance(collection, str):
            collection_capability = require_collection(collection)
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
                require_collection(collection)
            elif isinstance(collection, dict):
                _require_capability(
                    collection.get("capability"),
                    f"embedded Collection in Variable {variable_name}",
                )
                parent_capability = collection["capability"]
                for member in nodes(collection.get("set", {})):
                    member_name = member.get("collection")
                    if isinstance(member_name, str):
                        member_capability = require_collection(member_name)
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
