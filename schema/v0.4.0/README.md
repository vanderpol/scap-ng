# SCAP-NG v0.4.0 — working schema draft

**Pre-alpha draft, not accepted or Board approved.** The v0.3.0 schemas are unchanged.

This directory is a complete physically independent version-local copy-forward of the 0.3 schema and capability mapping surface. Versioned metadata, IDs and references identify v0.4.0; each unchanged file preserves its substantive modification date.

## Draft Assessment grammar

- A single versioned authoring grammar: no mixed legacy `field:/value:/operation:/existence:/match:` State forms.
- Every Test explicitly declares `require:`; State-free and State-bearing Tests have separate valid requirement names.
- State fields use observed field keys, e.g. `- owner_uid: {equals: 0, require: at_least_one_exists_and_all_match}`.
- **Object selectors now use the same comparison-as-key vocabulary**, e.g. `select.directory: {equals: [/lib, /lib64], datatype: string, value_match: one}`, but SHALL NOT carry `require` or consume Organizational Input. Legacy `value` + `operation` Object selectors fail draft 0.4 validation. This is enforced by the full Assessment schema for native inline/shared Object `select` properties and the version-local shared schema.
- Exactly one comparison operation per scalar predicate; arrays, Variables and Organizational Input references retain explicit `value_match` and datatype requirements.
- Windows record and nested field requirements are distinct. Object Set filters use `include:` or `exclude:` on a field-key predicate.
- `evaluate`, `for_each`, typed Variable graphs, manual choices and collected Items/results do not acquire new semantics.

## Native generator and real-content evidence

The [version-local native 0.4 capability generator](../../tools/generate_capability_schema_v04.py) successfully emits JSON Schema draft contracts for **all 100 supported reviewed capability mappings** ([successful 100-capability CI](https://github.com/vanderpol/scap-ng/actions/runs/38759490558)). The frozen 0.3 generator remains unchanged. This proves schema generation, reference locality and selected native field-name checks, **not** acceptance of all real authored Tests.

A separate [real-source deep validation census](https://github.com/vanderpol/scap-ng/actions/runs/38760164659) resolved the referenced automated/applicability Assessments from RHEL 9, Windows 11 and Windows Server 2025 and recorded **541 Test occurrence failures out of 1,407** against the newly generated native capability schemas. The audit ran successfully *as an audit*, but the deep content acceptance gate is **not yet passing**. Main clusters involve reviewed enum Object selectors, special fixed-result Test requirements, WMI/cmdlet collection/selection grammar and complex Set/foreach sources. Details and remedies are tracked in [#228](https://github.com/vanderpol/scap-ng/issues/228). Do not add legacy YAML alternatives or classify these as manual/shell-only solely to make the schemas pass.

## Source provenance for constant Variables

The original Windows 11 / Windows Server 2025 OVAL userright selectors
reference a 45-value constant Variable. The source omits `var_check` and
`operation`. Under OVAL 5.12.3, those mean **all** and **equals**,
respectively. The 0.4 research migration therefore uses an explicit
array with `value_match: all`, **not** `one` (which would change truth
semantics). See [#228](https://github.com/vanderpol/scap-ng/issues/228)
and the pinned-source verification workflow. This is a source-semantic
conversion guard, not a scanner correctness claim.

## Verified six-anchor draft integration

The complete six-STIG native-structure audit covers RHEL 9, Oracle Linux 9,
Windows 11, Windows Server 2025, Windows Server DNS and Apache. It validates
the complete authored automated Assessment document as well as each generated
capability-specific Test schema, preserving individual source re-expansion
and distinguishing source-exact changes from separately documented State-free
model normalizations. This is **not** scanner execution and does not promote
a candidate semantic change to normative specification.

## Promotion gates still open

Generic inline/shared Object selector grammar has focused positive/negative tests ([passing CI](https://github.com/vanderpol/scap-ng/actions/runs/38757998163)); **capability-specific selector names and datatype/operation narrowing** remain open. WMI/cmdlet `selection_match`, list edge cases, strong cross-capability scope/type validation, generated v0.4 capability schemas, complete migration lowering and six-valued reference parity still need completion. 0.3 compilation/validation is **not** asserted to implement 0.4. Variable source-module imports and variable debug graphs are separate [research #223](https://github.com/vanderpol/scap-ng/issues/223), **not** adopted language features.

See [0.4 scope and release gates](../../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md), [issue #227](https://github.com/vanderpol/scap-ng/issues/227) and [variable research #223](https://github.com/vanderpol/scap-ng/issues/223).
