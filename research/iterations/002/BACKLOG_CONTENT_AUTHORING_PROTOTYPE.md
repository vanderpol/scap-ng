# Medium-range backlog: SCAP-NG content-authoring prototype

**Priority horizon:** medium range — after the OVAL effective-default/behavior audit and substantial semantic round-trip tests establish a trustworthy model.
**Status:** proposed research prototype, not a frozen syntax or product commitment.

## Objective

Demonstrate the everyday workflow of an author creating or modifying a split **Benchmark → Policy (including named check selections) → Assessment** without needing to understand the old XCCDF/OVAL serialization. Make the authoring experience simple while preserving explicit compiled assessment semantics.

## Proposed capabilities

- Start with a benchmark and browse Rule, check text, fix text, manual/automated checks, parameters, and applicability in context.
- Navigate from a Rule to its Policy and selected Assessment; show provenance and other Rules using the same Assessment.
- Create/edit small native YAML source files; use the developing JSON Schema descriptions for inline documentation, completion, and validation.
- Present organizational inputs, tailoring values, profiles, and check selectors distinctly.
- Surface implicit source authoring conveniences, but **preview the exact effective explicit semantics** supplied to assessors (existence, cardinality, behaviors, variable quantifiers, operator, errors).
- Show migration/provenance links and why a source OVAL construct maps to each NG construct without embedding legacy XML as runtime data.
- Provide validation and diagnostics with actionable field-level messages, including unsupported/deprecated constructs and ambiguous conversion.
- Preview representative result/evidence messages and explain absent-item failures vs noncompliant collected items.
- Offer a readable view of the generated assessment documentation drawn from reviewed JSON Schema annotations and linked semantics.

## Narrow initial pilot

- Prototype one command-line-assisted or local-browser editor workflow; do not commit to an IDE plugin or full GUI until the author workflow is tested.
- Use a small, independently validated subset from RHEL 9 and Windows 11, then demonstrate reuse with Oracle Linux 9.
- Test routine actions: locate a rule by STIG ID; view check/fix text; author a file/registry check; set check selector and value; validate; preview resolved semantics; inspect anticipated evidence.
- Ask experienced OVAL/SCAP authors and newcomers to perform the same tasks; record friction, time, mistakes, discoverability, and missing schema documentation.

## Entry criteria

1. Confirmed and documented effective OVAL defaults and behavior exceptions for pilot test families.
2. Converter preserves semantics for substantive OVAL test cases with structural-diff noise classified.
3. Draft NG schemas and linked normative semantic definitions exist for pilot families.
4. Native split policy/assessment file layout and check selector binding are sufficiently stable for hands-on review.

## Exit criteria

- Authors complete selected tasks without editing OVAL/XCCDF XML or relying on hidden assessor behavior.
- Tool diagnoses errors and shows explicit effective configuration.
- Every example is traceable to an independently validated semantic fixture.
- Feedback produces specific improvements to the native format and documentation; no premature claim that UI design is normative.

**Scheduling:** This backlog item must not displace the ongoing XSD audit, normalization, semantic round-trip validation, and converter hardening.
