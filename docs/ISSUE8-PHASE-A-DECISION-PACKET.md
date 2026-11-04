# Issue #8 Phase A — native Organizational Input contract audit

**Status:** evidence-only decision packet; no contract or implementation change
**Date:** 2026-11-04
**Scope:** `vanderpol/scap-ng#8`, owner-requested Phase A after the 2026-11-04
comment

This packet records the reproducible public evidence needed to implement the
owner-approved native discovery amendment. It deliberately does **not** change
JSON Schema, converter/compiler behavior, editor metadata, CI contracts,
frozen artifacts, source proofs, or historical goldens. Issue #8 remains open.

## Executive decision record

The current public 0.4 Assessment grammar has a real contract gap:

* an Assessment can declare a typed Input and consume it from a native
  `require.fields` predicate, with an `evaluate.if.input_provided` guard;
* the Rule schema still describes Organizational Input use locations as the
  legacy `test`/`state`/`state_slot` tuple; and
* the current tools converter emits an empty
  `organizational_input_requirements` map rather than deriving native use
  locations.

The latest owner comment approves a **pre-release 0.4.0 amendment**, not a
0.4.1 release: native use records are `{kind: value|presence, source_path}`;
`source_path` is an RFC 6901 JSON Pointer relative to the selected Assessment
body, and the enclosing discovery entry's `input` remains the Benchmark
Parameter ID. Locations are compiler-derived. Legacy 0.3 tuples remain
version-directed compatibility; no synthetic State identifiers are permitted.

### Recommended implementation shape (non-normative until integrated)

Derive a complete, ordered/multiset-preserving location index from the selected
Assessment and the Rule choice. For each Input-to-Parameter binding, emit one
record for each exact native consumer:

```yaml
# Illustrative only; not accepted by the current public Rule schema.
rule:
  assessment_choices:
    automated:
      assessment: windows-lock-screen-organizational-demo-assessment
      expected_version: 1
      inputs:
        slideshow-value-input:
          parameter: expected-lock-screen-value
  organizational_input_requirements:
    automated:
      - input: expected-lock-screen-value
        required: false
        uses:
          - kind: value
            source_path: /tests/verifies-prevent-enabling-screen-slide-show-is-set-enabled-test/require/fields/value/equals/input
          - kind: presence
            source_path: /evaluate/if/input_provided
```

The pointers above are examples of the proposed scalar-reference granularity:
the `value` pointer identifies the actual Input reference in the comparison and
the `presence` pointer identifies the actual `input_provided` reference. They
are not a schema change in this Phase A packet. Pointer escaping, arrays,
branch paths, duplicate references, and exact multiset comparison must be
implemented and tested in the owner-approved follow-on phase.

## Baseline and evidence boundary

| Boundary | Exact reference | Use in this audit |
| --- | --- | --- |
| Public schema baseline | `vanderpol/scap-ng` main `5c89c98033ed8e7b56ef8d6a0522253555faefd7` | Current post-merge 0.4 candidate |
| Public tools baseline | `vanderpol/scap-ng-tools` main `64cb33145a10ad5c65d91ee10f65492f547385dc` | Converter/semantic inspection only |
| Public schema pin | `schema/` frozen family, 145 JSON files, digest `d2d8d59bcc722eacdba80342232f6d92d5bba812aab077753486268c3f74aa2d` | Must not change in Phase A |
| Source semantic baseline | OVAL 5.12.3, as pinned by the reviewed project/source evidence | Preserves source State/function behavior; no new runtime claim |
| Audit worktree | `codex/issue8-phase-a`, based on public `main` | Documentation-only branch |

The private research implementation and source files were inspected only as
supporting evidence. This public packet does not publish private source content
or treat research CI as a public schema/runtime proof.

## Reproduction: current native Assessment and Rule path

### 1. Canonical Assessment is native and schema-shaped

`examples/windows-optional-organizational-input.assessment.yaml` contains:

```yaml
inputs:
  slideshow-value-input:
    datatype: integer
    cardinality: exactly_one
    required: false

# inside the Test:
require:
  fields:
    value:
      equals:
        input: slideshow-value-input

# at Assessment level:
evaluate:
  if:
    input_provided: slideshow-value-input
  then:
    test: verifies-prevent-enabling-screen-slide-show-is-set-enabled-test
  else:
    not_evaluated: ...
```

Evidence: `examples/windows-optional-organizational-input.assessment.yaml:11-48`.
The example README explicitly limits this file to Assessment-level presence
branching and calls out the open Rule-level discovery gap
(`examples/README.md:12`). It is not a scanner or compliance proof.

The local check performed for this packet parsed the YAML and ran
`Draft202012Validator.check_schema` against `assessment.schema.json`,
`rule.schema.json`, and `assessment-result.schema.json`; all three schema
meta-checks passed. Full example reference validation was not claimed in this
working environment because the declared `referencing==0.36.2` dependency is
not installed (the available runtime has `jsonschema 4.10.3`). Historical CI
is the authoritative receipt for the frozen candidate.

### 2. Current Rule schema cannot describe that native use honestly

`schema/rule.schema.json:121-170` provides the current Assessment choice and
Input-to-Benchmark-Parameter binding:

```yaml
assessment_choices:
  automated:
    assessment: windows-lock-screen-organizational-demo-assessment
    inputs:
      slideshow-value-input:
        parameter: expected-lock-screen-value
```

However, `schema/rule.schema.json:180-229` requires each current
`organizational_input_requirements.*[].uses[]` entry to contain nonempty
`test`, `state`, and `state_slot` strings. The native Assessment has no named
State registry, and `schema/assessment.schema.json:122-190` explicitly rejects
legacy Test `state`, `states`, `states_match`, and `state_fields_require`
properties. Therefore an empty map avoids a false claim but does not describe a
Rule that resolves this native Input.

### 3. Current tools behavior

The inspected tools checkout is the public tools baseline above.

* `src/scap_ng_tools/converter/_v04_semantic/v04_input_presence.py:23-42`
  validates Input identity, datatype, cardinality, requiredness, constraints,
  and returns canonical contracts.
* `.../v04_input_presence.py:45-153` walks declared Tests, Objects,
  Variables, dependencies, `evaluate` branches, and direct
  `input_provided` guards. It checks optional-consumer guard dominance and
  returns `guards` and `consumers`.
* `.../v04_input_presence.py:203-251` requires explicit binding states and
  preserves `provided`, `omitted`, `error`, `unknown`, and `pending`; it does
  not infer defaults or empty values.
* `src/scap_ng_tools/converter/_v04_semantic/v04_comparison_types.py:100-108`
  invokes `presence_contract(assessment)` before comparison type checking and
  then visits native `require` field paths.
* `src/scap_ng_tools/converter/_v04_runtime/v04_direct_converter.py:883-906`
  emits the Assessment and Rule documents. The Rule initializer sets
  `organizational_input_requirements` to `{}`; external XCCDF export handling
  can add `assessment_choices.<choice>.inputs`, but no native Rule discovery
  records are derived here.
* `.../v04_draft_inputs.py:27-67` shows the existing source-conversion bridge:
  an XCCDF exported Value becomes a typed Assessment Input and a Benchmark
  Parameter binding. This is source conversion metadata, not a native Rule
  discovery map.

Running `presence_contract()` over the canonical Assessment produced this
actual result (the tool currently reports a Test consumer, not the exact
`require.fields` pointer):

```json
{
  "version": 1,
  "guards": ["slideshow-value-input"],
  "contracts": {
    "slideshow-value-input": {
      "cardinality": "exactly_one",
      "datatype": "integer",
      "required": false
    }
  },
  "consumers": [
    {
      "kind": "test",
      "id": "verifies-prevent-enabling-screen-slide-show-is-set-enabled-test",
      "path": ["evaluate", "then"],
      "inputs": ["slideshow-value-input"]
    }
  ]
}
```

This verifies useful contract and dominance behavior, but it does **not** prove
Rule binding, Parameter identity, native discovery completeness, or exact
source-pointer derivation.

## Evidence matrix for `state` and `state_slot`

| Occurrence/class | Evidence | Classification | Phase A conclusion |
| --- | --- | --- | --- |
| Native Test authoring | `schema/assessment.schema.json:122-190`; `schema/assessment-language.schema.json` Test/require definitions | Current native authoring: **no named State layer** | Do not restore State IDs to make native Inputs fit the old Rule shape. |
| Native field predicates | `examples/windows-optional-organizational-input.assessment.yaml:29-38`; `schema/assessment.schema.json:122-126` | Current native authoring: `require.fields` consumes the Input | Discovery must point to this actual reference, not a synthetic State. |
| Native presence guard | Example `:40-48`; `schema/expression.schema.json:250-273` | Current native authoring: direct `evaluate.if/else_if` presence guard | Preserve presence versus value as distinct `kind` values. |
| Rule discovery tuple | `schema/rule.schema.json:180-229` | Legacy-shaped Rule metadata retained in current schema | Genuine mismatch with native Assessment; do not guess a compatibility alias. |
| Rule choice binding | `schema/rule.schema.json:121-170` | Current policy binding: Assessment Input → Benchmark Parameter | Keep this identity authoritative; discovery entry `input` is the Parameter ID. |
| Converter State visitor | Tools `v04_direct_converter.py:249-275` | Source conversion implementation | OVAL State predicates are lowered into native field predicates; this is not native State authoring. |
| Converter Set/filter State | Tools `v04_direct_converter.py:410-462` | Source conversion/provenance path | Filter State identity remains source-bound and capability checked; it is unrelated to Organizational Input discovery. |
| Converter Input bridge | Tools `v04_draft_inputs.py:27-67` | Compiler-derived source metadata | Creates typed Input/Parameter binding, but not Rule discovery locations. |
| Semantic presence traversal | Tools `v04_input_presence.py:45-153` | Compiler-derived validation | Finds transitive Input consumers and guard dominance, but current returned paths are not exact field/presence pointers. |
| Result consumption | `schema/assessment-result.schema.json:281-342` | Result compatibility | `consumed_organizational_inputs[].state_slot` remains optional and nullable; preserve it. |
| Result diagnostic | `schema/assessment-result.schema.json:344-386` | Result compatibility | Structured reason `state_slot` remains optional and nullable; do not reinterpret or delete it. |
| Result technical evidence | `schema/test-result.schema.json:135`; `schema/assessment-result.schema.json:100-105` | Historical/result vocabulary | Result descriptions retain State/Entity comparison language while native authoring is State-free. |
| Mapping/source notes | e.g. `schema/capability-mappings/supported/unix.file.json:202-214`, `windows.file.json:220-229`, generated catalog | Historical provenance and source semantics | State references/fields document OVAL source crosswalks and semantic rules; they do not authorize native State properties. |
| Legacy authoring keys | `schema/assessment.schema.json:153-190`; generated reference `docs/generated/schema-reference.md:14,44` | Obsolete/unsupported in native 0.4 | Reject wrong-version legacy shapes; retain compatibility only where version-directed contracts explicitly require it. |

This classification intentionally distinguishes the word “State” in OVAL
source/provenance and result reporting from a native authoring State registry.
A repository-wide identifier census also bounds the result: outside this
packet, the literal `state_slot` appears only in the two nullable Result fields
(`schema/assessment-result.schema.json:296-300, 372-376`), the legacy Rule
`uses` requirement (`schema/rule.schema.json:205-222`), and the compatibility
summary (`specification/README.md:81`). Other `State` occurrences are source
lineage, mapping rules, editor OVAL policy, or Result descriptions as classified
above; they are not additional native Organizational Input authoring sites.

No claim is made that every source State can be replaced by a native field
predicate without an independent equivalence proof.

## End-to-end trace and current gap

```text
Assessment.inputs
  └─ slideshow-value-input : integer / exactly_one / optional
      ├─ Test.require.fields.value.equals.input
      │    └─ value consumer (kind=value)
      └─ evaluate.if.input_provided
           └─ presence guard (kind=presence)

Rule.assessment_choices.automated.inputs
  └─ slideshow-value-input → Benchmark Parameter expected-lock-screen-value

Rule.organizational_input_requirements
  └─ current schema expects uses[].test/state/state_slot
  └─ current converter initializes {}

Assessment Result
  └─ input_bindings / consumed_organizational_inputs
  └─ optional nullable state_slot retained for compatibility
```

The first half is represented and partially checked. The Rule-level edge is
not derived or checked by the public converter path inspected here. The Result
schemas provide runtime/reporting locations but do not repair authoring or
packaging discovery metadata.

## Compatible implementation options (non-normative)

1. **Derived native map (recommended).** During compilation, walk all
   grammar-owned native sites and emit exact `{kind, source_path}` records for
   every resolved Input reference. Derive from the selected Assessment and the
   choice binding; authors edit real Inputs, predicates, guards, and Rule
   bindings. A packaged map is generated, not hand-maintained. This is the
   smallest representation that preserves source identity and avoids fake
   State names.
2. **Optional authored map with proof-equivalence.** Permit an authoring-time
   map only where a workflow needs precompiled discoverability, then require
   the compiler to derive the map and compare exact pointer/kind/Parameter
   multisets. Missing, duplicate, unexpected, wrong-kind, wrong-Input, and
   wrong-Parameter entries fail closed. The packaged representation remains
   derived.
3. **Version-directed compatibility bridge.** Retain legacy
   `{test,state,state_slot}` only for legacy Assessment/Rule pairs; reject it
   against native 0.4 and reject native records against legacy pairs. This
   preserves old imports/results while the native path is adopted. It is not a
   final native design and must not be used to synthesize State labels.

Option 1 is recommended. Option 2 is useful only if a concrete authoring or
packaging consumer requires an explicit precompile map. Option 3 is necessary
for historical compatibility but cannot close the native gap alone.

## Illustrative Result shape

The following is a compatibility illustration, not a proposed Result schema
change. Existing `state_slot` is retained and may be null:

```yaml
assessment_result:
  assessment: windows-lock-screen-organizational-demo-assessment
  input_bindings:
    - input: slideshow-value-input
      value: 1
      source: organization-policy
      source_ref: policy://example/expected-lock-screen-value
  consumed_organizational_inputs:
    - input: slideshow-value-input
      organizational_input_ref: expected-lock-screen-value
      materialized: true
      state_slot: null       # retained compatibility field; not a native pointer
```

The exact surrounding Result required fields are governed by
`schema/assessment-result.schema.json`; this excerpt is explanatory and is not
claimed to validate as a standalone Result document.

## Migration and compatibility impact

* **Native 0.4 authoring:** add a compiler-derived discovery representation;
  no author-entered pointer strings are required.
* **Legacy 0.3 conversions:** keep State tuples and source State provenance
  behind version-directed validation. Do not reinterpret a legacy tuple as a
  native pointer record.
* **Results:** keep `state_slot`, Result A, existing input-binding statuses,
  and nullable/error/unknown/pending distinctions. No wire redesign is in
  scope.
* **Existing content and evidence:** no converted content, manual Assessment,
  source ZIP, proof, provenance record, historical golden, or schema hash is
  changed by this packet.
* **Compatibility risk:** a future schema/compiler change that accepts only
  native pointers could reject legacy-shaped data if version selection is not
  explicit. The migration gate must test both directions and fail closed on a
  wrong-version shape.
* **Semantic limit:** the pointer map describes discoverability locations; it
  does not claim provider resolution, scanner execution, compliance, or OVAL
  runtime equivalence.

## Required implementation and acceptance tests

The follow-on implementation should add tests at all of these boundaries.

### Positive contracts

* Required Input consumed by a native `require.fields` predicate.
* Optional Input consumed only beneath `evaluate.if` and each valid
  `else_if`/`else` branch.
* Value and presence references to one Input, multiple consumers of one Input,
  and multiple Inputs in one Assessment.
* Nested `require` `and`/`or`/`one`/`xor` groups, shared Objects, Variables,
  and transitive Test/Assessment dependencies.
* Correct Rule choice, Assessment identity/version, Input name, and Benchmark
  Parameter binding.
* RFC 6901 escaping (`~0`, `~1`) and array indexes in emitted paths.

### Negative contracts

* Undeclared Input in a value or presence reference.
* Unknown Rule binding, nonexistent Benchmark Parameter, wrong datatype, or
  wrong cardinality.
* Missing, duplicate, unexpected, wrong-kind, or wrong-Input pointer.
* Honest native consumer with a dishonest empty discovery map.
* Unguarded optional consumer, including a guard in the wrong logical scope.
* Legacy tuple against native Assessment; native pointer record against legacy
  Assessment.
* Explicit authored map that differs from mechanical derivation.

### Binding-state semantics

Test omitted optional Input separately from supplied empty population (where
cardinality permits), supplied value, invalid value, unknown, error, and
pending resolution. No truthiness check or default value may collapse these
states. Error propagation must remain explicit.

### Evidence gates

Use actual compiler entrypoints and package verification, not helper-only
unit tests. Retain the legacy 0.3 tests and source proofs. Record exact source
revisions, schema-family hash, generated metadata hash, artifact counts, and
CI receipts. Do not claim scanner results or full-corpus equivalence from
schema/validator acceptance.

## Owner decision status

The latest owner comment already resolves the Phase A contract direction:

* amend pre-release 0.4.0;
* use native `kind: value|presence` and RFC 6901 `source_path` relative to the
  selected Assessment body;
* keep `input` as the Benchmark Parameter identity;
* derive locations mechanically and validate any explicit map against the
  derivation;
* preserve legacy State tuples, Result `state_slot`, Result A, source proofs,
  historical artifacts, and provenance;
* keep Issue #8 open through implementation and end-to-end acceptance.

No additional semantic decision is requested by this evidence packet. During
implementation, the recommended default is that a pointer terminates at the
actual Input reference scalar (as illustrated), with exact duplicate/multiset
semantics. If a real grammar site cannot be assigned an unambiguous pointer or
branch meaning, stop that narrow decision and return the evidence rather than
guessing.

## Phase A non-change declaration

This commit changes only this Markdown decision packet. It does not modify:

* `schema/` or generated schema/reference artifacts;
* compiler, converter, package verification, or editor code;
* CI workflows or test contracts;
* examples, converted content, manual Assessments, source ZIPs, proofs,
  provenance, or historical goldens;
* unique-function arity, binary32, selector, or unrelated language semantics.

The next phase may implement the approved contract in focused, reviewable
PRs. This packet itself is the review boundary; it is not a merge or release
claim.
