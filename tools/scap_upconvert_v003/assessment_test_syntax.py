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
        if isinstance(expression, list):
            return [rename(term) for term in expression]
        if not isinstance(expression, dict):
            return expression
        if "check" in expression:
            target = expression["check"]
            if target not in names:
                raise ValueError(f"Unknown technical Test reference: {target}")
            return {("test" if key == "check" else key):
                    (names[target] if key == "check" else rename(value))
                    for key, value in expression.items()}
        return {key: rename(value) for key, value in expression.items()}
    assessment["evaluate"] = rename(assessment["evaluate"])
    return result

def verify_assessment_test_syntax(original, converted):
    """Compare complete payloads, allowing only the declared vocabulary rename."""
    if converted != assessment_test_syntax(original):
        raise ValueError("Assessment changed beyond the declared Test vocabulary rename")
