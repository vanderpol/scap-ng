# SCAP-NG 0.4 — Joval technical discussion preview

**For technical discussion on October 16, 2026.** This is a **pre-alpha authoring-language candidate**, not a final standard, OVAL Board decision, or executable scanner bundle. The current 0.3 release is not changed.

## What to review first (about five minutes)

The shareable [six-STIG YAML/JSON preview release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r2) contains two complete corresponding authoring ZIPs: one YAML and one JSON. Each contains all six real benchmark structures, Rules, manual fallbacks, relevant shared Assessments and automated/applicability Assessments. Open the internal `MEETING-START-HERE.md`, then a few converted files.

### Representative content

| STIG | Reason to inspect |
| --- | --- |
| RHEL 9 | Unix/Linux native file, process, account and policy checks; native field expressions |
| Oracle Linux 9 | Cross-Linux readability and potential reuse without flattening assessment semantics |
| Windows 11 | Registry `SV-253254` (AND/OR matching) and shellcommand `SV-253274` (stderr may have to be absent) |
| Windows Server 2025 | Native Windows records, security policy and registry checks |
| Windows Server DNS | Domain-specific Windows DNS assessment patterns |
| Apache 2.4 UNIX | Variables, multi-step configuration discovery and remaining complex native checks |

## Windows 11 SV-253495 — why some requirements remain on individual States

This source-backed example deserves special review. It contains seven Tests: **five** single-field `windows.userright` Tests and **two** `windows.wmi.query` record Tests. On the user-right Tests, `collected_items_require: at_least_one_exists_and_some_match` means at least one assigned trustee must match, while `trustee_name.require: at_least_one_exists_and_all_match` constrains each field's cardinality. The two scopes **cannot be merged**. For a single-field Test, the automatic minimum-declaration authoring form keeps `require` on the field, because moving it to `state_fields_require` saves no declarations.

A **semantically identical alternative**, useful if explicit scope separation reads better, is:

```yaml
collected_items_require: at_least_one_exists_and_some_match
state_fields_require: at_least_one_exists_and_all_match
states:
  - trustee_name: {case_insensitive_equals: Guests}
```

The real WMI Tests contain `result.record.require` and `result.record.fields.domainrole.require`. Although their phrases happen to match, they quantify **different populations** (records and record members); the scalar State-field scope is deliberately not inherited into records. Whether to favor Test-level field scopes for every single-field Test is **an authoring style decision**, not a missing semantic feature. No extra inheritance level across unrelated Tests is proposed for 0.4.

## Proposal: one human-readable Assessment grammar

The value of the redesign is straightforward: authors name actual observed fields and comparison operations, rather than having to follow indirect Object/Test/State entities or repeat `field`, `operation`, `value`, `existence`, `match` at every node.

The important distinctions remain explicit:
1. Test `collected_items_require` concerns collected Items and State matching. It is never a hidden field default. Individual field/record `require` remains scoped locally.
2. The **proposed** `state_fields_require` declares common requirements for ordinary State fields at the Test or logical State group level. A particular field can override it using its own `require`. Missing effective requirements are errors, not defaults.
3. `and`/`or` represent logical State expressions; `states_match: any` combines alternative State entries, and `value_match` independently governs multiple expected operands from arrays/Variables.
4. Native records retain record and record-field semantics, including absent/error/unknown behavior; scalar field inheritance does not silently enter record members.
5. Object selectors and dynamic Variables retain native source/reference behavior; no inferred value matching or flattened arrays.

Example (selected State lines from Windows 11 `SV-253254`, not a complete Assessment):

```yaml
collected_items_require: at_least_one_exists_and_all_match
state_fields_require: at_least_one_exists_and_all_match
states_match: any
states:
  - and:
      - type: {equals: string}
      - value: {equals: Enterprise}
  - and:
      - type: {equals: string}
      - value: {equals: EnterpriseS}
```

A shellcommand State can keep an absence exception, for example `stderr_line: {require: none_exist, equals: ''}`, independently from the common scope applied to successful output fields.

## Why this is more than presentation-only research

The scope-language prototype has proven reversible across the six representative published authoring benchmarks: **1,396 automated/applicability Assessments, 2,144 Tests**. The 2,550 leaf-level field requirement declarations become 1,444 explicit declarations after Test/group/field factoring (**43.4% fewer**), without dropping the original independent distinctions. Source-exact versus separately proved State-free normalizations is reported rather than concealed.

The new Joval preview output separately validates **each complete candidate Assessment**, expands explicit scopes to the present 0.4 draft baseline, validates the full native capability-specific Test schema, and asserts that the JSON mirror equals the parsed YAML authoring document. A passed CI proves authoring/schema/source reconstruction, **not execution-time scanner agreement**.

**Known open issues:** unusual human-readable `require` names, approval of Test/group/field scoping, reference six-valued missing/error/unknown behavior, provenance of multi-valued Variables, future compiler packaging/signing, and live scanner conformance. Current published 0.3 converter regressions are separately tracked in [issue #226](https://github.com/vanderpol/scap-ng/issues/226).

## Questions for the Joval authors

- Are the Test/item, logical group, and individual field requirement scopes a clean evaluation model, including six-valued OVAL semantics and potentially incomplete collection?
- Are there native Windows registry, shellcommand, WMI/cmdlet or nested record cases that still require a more explicit syntax?
- Where would you expect meaningful regression differences when translating OVAL 5.12.3 sources into this authoring grammar?
- Does this preserve adequate source provenance and evidence lineage for enterprise scanners and audit?
- Which semantics should be settled in the specification before independent scanner implementations begin?

## References

- [0.4 single-grammar candidate and Board vocabulary discussion](https://github.com/vanderpol/scap-ng/issues/227)
- [Full six-anchor validation and release gate](https://github.com/vanderpol/scap-ng/issues/228)
- [Scoped requirement before/after and formal caveats](SCOPED-FIELD-REQUIRE-REVIEW.md)
- [Versioned 0.4 draft schema](../../../schema/v0.4.0/README.md)

**Distribution note:** The two preview ZIPs are *independently readable representations* of the same Assessment content. Path references copied from the original YAML remain YAML-looking inside JSON for fidelity; the JSON mirror is not presently guaranteed to be buildable without a JSON-aware reference resolver.
