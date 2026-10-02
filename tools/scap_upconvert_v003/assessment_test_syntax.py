"""Review-candidate Test vocabulary; no full-source generation until owner review."""
import copy

def assessment_test_syntax(document):
    """Rename authoring vocabulary without changing evaluation semantics."""
    result = copy.deepcopy(document)
    assessment = result["assessment"]
    if "deprecated" in assessment:
        if assessment["deprecated"] is not False:
            raise ValueError("Deprecated Assessment cannot become native executable source")
        del assessment["deprecated"]
    if "checks" not in assessment:
        return result  # Manual assessments have no technical Tests.
    original = assessment.pop("checks")
    names = {name: "test-" + name for name in original}
    assessment["tests"] = {names[name]: test for name, test in original.items()}
    for test in assessment["tests"].values():
        assertion = test.get("assert")
        if assertion is not None and "check" in assertion:
            assertion["item_quantifier"] = assertion.pop("check")

    def rename(expression):
        """Rename check references without relying on Python recursion depth."""
        if not isinstance(expression, (dict, list)):
            return expression

        root = {} if isinstance(expression, dict) else [None] * len(expression)
        stack = [(expression, root)]
        while stack:
            source, target = stack.pop()
            if isinstance(source, dict):
                check_target = source.get("check")
                if check_target is not None and check_target not in names:
                    raise ValueError(f"Unknown technical Test reference: {check_target}")
                for key, value in source.items():
                    new_key = "test" if key == "check" else key
                    if key == "check":
                        target[new_key] = names[value]
                    elif isinstance(value, dict):
                        child = {}
                        target[new_key] = child
                        stack.append((value, child))
                    elif isinstance(value, list):
                        child = [None] * len(value)
                        target[new_key] = child
                        stack.append((value, child))
                    else:
                        target[new_key] = value
            else:
                for index, value in enumerate(source):
                    if isinstance(value, dict):
                        child = {}
                        target[index] = child
                        stack.append((value, child))
                    elif isinstance(value, list):
                        child = [None] * len(value)
                        target[index] = child
                        stack.append((value, child))
                    else:
                        target[index] = value
        return root

    assessment["evaluate"] = rename(assessment["evaluate"])
    return result

def verify_assessment_test_syntax(original, converted):
    """Compare complete payloads, allowing only the declared vocabulary rename."""
    if converted != assessment_test_syntax(original):
        raise ValueError("Assessment changed beyond the declared Test vocabulary rename")
