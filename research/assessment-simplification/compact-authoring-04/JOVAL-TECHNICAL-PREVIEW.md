# SCAP-NG 0.4 — Joval technical discussion preview

**For technical discussion on October 16, 2026.** This is a **pre-alpha authoring-language candidate**, not a final standard, OVAL Board decision, or executable scanner bundle. The current 0.3 release is not changed.

## Start with the original OVAL → NG 0.4 feature showcase

**[Download the ten real OVAL-single/NG side-by-side comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015)**. The 86 KB ZIP is a better starting point for the Joval meeting than the multi-megabyte six-STIG bundles. It contains actual archived OVAL single XML, the **correct** linked 0.4 authoring Assessment in **YAML and JSON**, and its Rule, grouped together by SV-ID. **[Open the concise showcase guide](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-joval-oval-to-ng-showcase-20261015/SHOWCASE-START-HERE.md)** for real side-by-side static Variable and Set/filter examples and the validated, separately labeled conditional illustration.

Feature highlights: **SV-257889** (OVAL ObjectComponent → separately proved opt-in collection `for_each`), **SV-278028** (filters), **SV-278001** (multi-valued constant Variable → literal arrays; role-sensitive `evaluate` and a separately labeled `if/then/else` native authoring illustration), **SV-278138** (exclude filters), **SV-258179** (shared Assessment and OVAL extend-definition), **SV-259345** (DNS runtime Variables), **SV-214228** (Apache regex capture). The current six-STIG converter intentionally leaves some source graphs faithful rather than enabling a potentially unsafe automatic modernization.

**Evidence classification:** The full OVAL/NG pairs are source-backed and copied verbatim; the extra `for_each` fixture is an accepted 0.3 authoring/proof example rather than emitted by 0.4 r2; the `if/else` fragment is valid 0.4 grammar but **not** claimed to be six-state-equivalent to the archived OVAL Boolean expression. The result fixture is synthetic. These are essential distinctions for an evaluator-implementation discussion.

## Suggested 20-minute meeting flow

- **3 minutes — motivation:** one Assessment grammar, inline native fields and verbs, explicit cardinality with less repetition. Existing SCAP 1.4 is a forward-conversion source, not an authoring dependency.
- **7 minutes — examine three Windows 11 files:** `SV-253254` (two matching State alternatives and one shared field requirement), `SV-253274` (shell-command `stderr_line` absence override), `SV-253495` (five user-right single-field Tests plus two WMI nested-record Tests). Include one RHEL 9 file for contrast.
- **7 minutes — request semantic criticism:** user-right `some_match`, nested record/field quantifiers, absent versus error/unknown/incomplete collection, and preservation of evaluation semantics.
- **3 minutes — capture next actions:** which semantics require normative tests, counterexamples or source-backed migration proof? No request to approve 0.4 or attest scanner equivalence at this meeting.

**Status to say aloud:** The revision 2 packet is a verified *pre-alpha technical proposal*. The research overlay validates this language, and source reconstructions pass, but the frozen/current normative v0.4 schema has **not** adopted scoped State requirements or renamed Test `collected_items_require`. No SCAP-NG scanner or 0.4 compiled bundles exist yet; no runtime parity is claimed. The JSON files mirror the YAML content but retain YAML-looking reference paths, so independent JSON compilation is a separate future gate. The legacy 0.3 converter CI regressions tracked in #226 are **not** evidence of a new 0.4 Assessment-language failure.

## What to review first (about five minutes)

The shareable [six-STIG YAML/JSON preview release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3) contains two complete corresponding authoring ZIPs, now **4,001 authored documents each** (including the 12 previously omitted shared manual Assessments). All **2,958 Rule Assessment-choice links resolve**, as verified by the [new closure gate](https://github.com/vanderpol/scap-ng/issues/230): one YAML and one JSON. Each contains all six real benchmark structures, Rules, manual fallbacks, relevant shared Assessments and automated/applicability Assessments. Open the internal `MEETING-START-HERE.md`, then a few converted files.

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

## Open question: native `if/else` versus lossless OVAL `AND/OR`

**[Joval conditional review questions](../conditional-10/JOVAL-IF-ELSE-QUESTIONS.md)** detail the decision we need before normalizing any OVAL branch tree. The real **SV-278001** and **SV-258004** examples read well as `if/else`, but ordinary OVAL `OR(AND(G,P),AND(NOT G,Q))` and procedural `if` differ for **81 of 216** generic six-state input combinations. We must distinguish author-authored procedural branching from lossless source conversion; `error`, `unknown`, `not_evaluated`, `not_applicable`, skipped-branch evidence and applicability are not mere syntax questions. Bring the question sheet to Joval. **The actual source-faithful Assessment remains unchanged in the showcase.**

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
