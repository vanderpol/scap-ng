# 2026-09-28 Design Reconciliation

**Status:** active implementation checkpoint  
**Purpose:** prevent iteration-001 / earlier iteration-002 tooling from overriding design decisions made during the 2026-09-28 working session.

This note is an implementation reconciliation checklist. Normative requirements remain
in the specification and accepted decision records referenced below.

## Governing rule

Current design decisions take precedence over older prototype behavior.

Existing scripts and generated examples MAY be reused as implementation scaffolding,
but generated output is not accepted merely because it validates or reproduces an
older prototype. The implementation SHALL be checked against the current semantic
requirements.

SCAP 1.4 conversion SHALL be semantically lossless for supported source constructs
or SHALL fail explicitly for the affected conversion path.

A converter SHALL NOT silently:

- drop source semantics;
- weaken or strengthen an assertion;
- replace an unsupported automated check with a manual check;
- discard an XCCDF selectable check;
- choose a different check selector;
- fall back to a default after an explicit selector request; or
- treat successful YAML/schema generation as proof of semantic equivalence.

## Decisions that must survive regeneration

### Split policy / assessment architecture

The effective resolution chain is:

    Benchmark Rule -> Policy -> selected check -> Assessment

A Benchmark Rule identifies policy; it does not directly hard-code the executable
Assessment implementation.

Policy exposes named check alternatives. Selector names are extensible and are not
restricted to `automated` and `manual`.

Profile/Tailoring MAY select among alternatives using a check selector. An explicitly
requested selector that is not exposed by the governing policy is a resolution error.

See:

- `decisions/check-selection-and-tailoring.md`
- `../../../specification/policy/policy-resolution.md`
- `../../../specification/policy/profiles-and-tailoring.md`

### Rule-centric authoring context

A content author must be able to work from the Rule and readily see the policy text,
Check Text/manual procedure, remediation context, policy binding, and available
Assessment choices without reverse-engineering generated package internals.

See:

- `decisions/rule-centric-authoring-view.md`
- `decisions/check-text-manual-assessment.md`
- `decisions/manual-check-authoring-location.md`

### Manual assessment

Publisher Check Text is a valid Manual Assessment procedure. Conversion SHALL NOT
require OCIL questionnaire scaffolding merely to preserve a manual requirement.

Automated and manual implementations may coexist as selectable alternatives when the
source semantics provide them.

See:

- `decisions/check-text-manual-assessment.md`
- `decisions/manual-assessment-results.md`

### Organizational/user-supplied input

The NG model must support organizationally defined input without recreating the
XCCDF-to-OVAL stovepipe. Input may require structured data rather than a single text
value, and provenance must survive into effective policy/results where relevant.

See:

- `decisions/user-supplied-inputs.md`
- `decisions/parameter-model.md`
- `../../../specification/policy/parameters-and-organizational-input.md`

### File naming

Authoring artifacts use predictable type-bearing suffixes rather than unconstrained
filenames. Regeneration SHALL follow the accepted naming convention.

See `decisions/file-naming-convention.md`.

### Assessment object/state/test semantics

NG retains the useful semantic separation between collection/object, expected state,
and evaluation/test logic while simplifying OVAL's serialization.

Existence and non-existence are first-class assessment semantics. They SHALL NOT be
flattened into incidental string comparison behavior.

Base/conformance cases must include at least:

- expected none, observed zero -> pass;
- expected none, observed one -> fail;
- expected none, observed many -> fail;
- expected one-or-more, observed zero -> fail;
- expected one-or-more, observed one/many -> pass.

Equivalent existence/cardinality semantics apply across capability families, not only
shell-command output.

See:

- `decisions/oval-to-ng-conversion-strategy.md`
- `decisions/oval-test-type-crosswalk.md`
- `decisions/assessment-evaluation-and-result-evidence.md`

### Result/evidence model

Canonical results are normalized and bounded rather than embedding the entire source
Benchmark/OVAL content, but Rule results must be sufficiently self-describing for
operational consumers.

Failures should include:

- stable Rule identity and useful policy context;
- deterministic concise human-readable outcome message;
- structured failure reason;
- bounded concrete evidence when a concrete violating item exists;
- enough provenance to identify the effective Assessment/check selector.

Existence/non-existence failures are first-class reason categories, including
`unexpected_existence`, `required_item_missing`, `required_match_missing`,
`value_mismatch`, and `cardinality_mismatch` as applicable.

The canonical package is distinct from consumer-specific JSONL/SIEM denormalization.

See:

- `decisions/assessment-evaluation-and-result-evidence.md`
- `decisions/result-package-and-siem-projection.md`

## Four-anchor acceptance corpus

The standing reference corpus is:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

These are not only demonstrations. They are migration/conformance evidence.

New SCAP 1.4/XCCDF/OVAL constructs discovered while processing these anchors SHOULD
become permanent regression tests. Unsupported constructs SHALL remain visible as
explicit blockers until a semantically equivalent NG representation exists.

See `four-anchor-review-plan.md`.

## Implementation reconciliation performed in this checkpoint

The active conversion tooling was reviewed against the current decisions.

Changes include:

- `tools/scap14_rule_splitter.py` now preserves XCCDF check selector, negate,
  and multi-check attributes in split provenance;
- `tools/scap14_to_scapng.py` now emits explicit policy check/default bindings,
  lowers the common default/automated/manual XCCDF selector pattern to distinct
  Assessment alternatives, and blocks unsupported fallback patterns rather than
  collapsing them;
- resolved XCCDF `refine-rule/@selector` actions are projected into native
  Profile check-selector data;
- `tools/verify_scap14_to_scapng_conversion.py` checks selector preservation
  and rejects silent collapse;
- `tools/test_xccdf_check_selector_conversion.py` provides permanent focused
  selector regression cases;
- `research/iterations/002/examples/conformance/existence-state-cases.yaml`
  and `tools/test_ng_existence_semantics.py` provide the base expected-state
  existence truth table and OVAL `check_existence` preservation cases;
- `.github/workflows/check-selector-conformance.yml` runs syntax and selector
  regression checks;
- `.github/workflows/four-anchor-reuse-analysis.yml` now runs automatically
  when migration-semantic tooling changes;
- `specification/assessment/assessment-method.md`,
  `specification/core/conformance.md`, and `specification/results/results.md`
  now carry the expected-state existence truth semantics, mandatory base
  conformance cases, stable existence failure reasons, effective selector
  identity, and deterministic-message requirements into the normative draft.

## Completion rule

This reconciliation is not complete merely because the focused tests pass.

The four-anchor conversion must be rerun under the current tooling. Any newly exposed
blocker is evidence of an unsupported semantic construct to model or document, not a
reason to restore silent compatibility behavior.
