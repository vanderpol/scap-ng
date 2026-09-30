# OVAL 5.12.3 to SCAP-NG Migration Mapping

**Status:** pre-alpha normative migration draft  
**Source language:** OVAL 5.12.3

## 1. Purpose

This section defines how supported OVAL 5.12.3 assessment semantics map into
SCAP-NG.

The goal is not to reproduce the OVAL XML object model. The goal is to preserve
its effective semantics during Stage-1 migration and then permit deliberate
Stage-2 native refactoring.

A converter SHALL account for every reachable OVAL construct required by a
converted Definition.

A converter SHALL NOT silently discard an OVAL construct merely because no
direct one-to-one SCAP-NG syntax exists.

## 2. Conversion stages

OVAL migration SHALL distinguish:

1. **Stage 1 — lossless conversion**  
   Preserve effective OVAL evaluation behavior, including defaults,
   redundancies, quirks, and source defects when necessary for equivalence.

2. **Stage 2 — native refactoring**  
   Replace legacy implementation structure with clearer native SCAP-NG
   capabilities or expressions after equivalence has been established.

Stage-2 output SHOULD be regression-tested against the Stage-1 baseline.

## 3. Core construct mapping

| OVAL 5.12.3 construct | SCAP-NG construct | Migration rule |
| --- | --- | --- |
| Definition | Assessment Method or named Assessment expression | Preserve complete effective criteria semantics. |
| criteria | Boolean assertion/expression | Preserve AND/OR/negation and nesting explicitly. |
| criterion | assertion/test reference | Resolve to the migrated Test semantics. |
| extend_definition | reusable/named assertion or Assessment reference | Preserve referenced Definition truth semantics; do not duplicate or simplify unless proven equivalent. |
| Test | collection + assertion contract using a Capability | Split collection semantics from result assertion while preserving check/check_existence behavior. |
| Object | collection selector | Preserve target selection, behaviors, set membership, variable bindings, and object operations. |
| State | assertion condition | Preserve datatype, operation, entity_check, var_check, and state-level semantics. |
| Variable | Parameter, Organizational Input, derived value, or local constant | Classification depends on semantic role, not XML element name alone. |
| constant_variable | constant/derived local value | Preserve datatype and ordered values. |
| external_variable | typed Parameter / Organizational Input binding | May supply expected-state data only in native NG. Legacy uses that affect execution require lossless compatibility or review. |
| local_variable | derived value/expression | Preserve component/function semantics. |
| object_component | derived value from collected data | Preserve source object/item/entity selection. |
| variable_component | derived value from another variable | Preserve dependency ordering and cardinality. |
| literal_component | constant expression operand | Preserve datatype/value. |
| function components | derived expression | Preserve operation, ordering, datatype, and error behavior. |
| set | collection set composition | Preserve union/intersection/complement semantics and nesting. |
| filter | collection include/exclude filter | Preserve referenced State and filter action. |
| behaviors | Capability collection options | Preserve behavior-affecting settings explicitly. |
| datatype | typed NG value semantics | Preserve datatype; conversion SHALL NOT coerce merely for authoring convenience. |
| operation | explicit comparison/operator | Preserve exact operator semantics. |
| check | explicit item/result quantifier | OVAL defaults SHALL be made explicit in Stage 1. |
| check_existence | explicit existence/cardinality requirement | OVAL defaults SHALL be made explicit in Stage 1. |
| entity_check | explicit entity/value quantifier | Preserve explicitly. |
| var_check | explicit variable-value quantifier | Preserve explicitly. |
| negate | Boolean `not` | Preserve at the same logical scope. |
| applicability-class Definition | Platform or applicability Assessment | Classify by semantic role after preserving source truth. |
| compliance-class Definition | compliance Assessment | Bind explicitly from the Rule. |
| inventory-class Definition | inventory/Platform/applicability Assessment as appropriate | Final use-case classification remains subject to NG use-case specification. |
| vulnerability-class Definition | vulnerability Assessment as appropriate | Final vulnerability use-case model remains under design. |

## 4. OVAL Definition mapping

An OVAL Definition SHALL be converted from its effective criteria tree, not
from title, class, metadata, or naming conventions alone.

For example:

    <criteria operator="AND">
      <criterion test_ref="A"/>
      <criteria operator="OR">
        <criterion test_ref="B"/>
        <criterion test_ref="C"/>
      </criteria>
    </criteria>

maps conceptually to:

    assert:
      all_of:
        - assertion: A
        - any_of:
            - assertion: B
            - assertion: C

Negation SHALL remain explicit at its original logical scope.

A converter SHALL NOT apply Boolean algebra simplification during Stage 1 if
doing so makes source traceability or error/result propagation less certain.

## 5. Test mapping

An OVAL Test combines:

- an Object describing what to collect;
- zero or more States describing expected values;
- existence semantics;
- item/state checking semantics.

SCAP-NG separates those concerns.

Conceptually:

    OVAL Test
       |
       +-- Object ----------> collect/select
       |
       +-- State(s) --------> condition/assert
       |
       +-- check -----------> explicit quantifier
       |
       +-- check_existence -> explicit existence requirement

A Stage-1 converter SHALL preserve all four dimensions.

An OVAL Test with no State remains meaningful. Its result may depend only on
existence/cardinality.

## 6. Object mapping

An OVAL Object SHALL map to a collection selector for the corresponding
SCAP-NG Capability.

Object entities SHALL remain collection criteria.

Behaviors SHALL remain collection behavior.

OVAL sets SHALL remain explicit collection composition when needed.

Filters SHALL retain include/exclude semantics.

A converter SHALL NOT move expected-state comparisons from State semantics into
Object selection merely to shorten the source if that would change result or
evidence behavior.

## 7. State mapping

An OVAL State SHALL map to one or more explicit assertion conditions.

State entity semantics that affect truth SHALL be retained, including:

- datatype;
- comparison operation;
- entity_check;
- variable references;
- var_check;
- missing-entity behavior where defined by the Capability semantics.

A State that is used as an Object filter and a State used as a compliance
assertion may share field comparison semantics but have different roles.
SCAP-NG SHALL preserve that role distinction.

## 8. Variable classification

OVAL Variables SHALL NOT all map to one SCAP-NG concept.

The converter SHALL classify each Variable by semantic role.

### 8.1 Constant variable

A constant variable normally becomes a local constant or derived value.

### 8.2 Local variable

A local variable normally becomes a derived expression over constants,
collected values, or other derived values.

### 8.3 External variable

An OVAL external variable that represents expected policy state SHOULD become a
typed SCAP-NG Parameter/Organizational Input binding.

Native SCAP-NG Organizational Input SHALL NOT be permitted to alter commands,
collection targets, query text, collector choice, privileges, or other
execution behavior.

If legacy OVAL uses an external variable in such an execution-affecting
position, Stage 1 SHALL preserve the behavior through an explicitly marked
legacy-compatible representation or report the construct for review. Stage 2
SHALL NOT silently retain unsafe execution injection as native policy input.

## 9. Variable dependency closure

OVAL migration SHALL follow references to a fixed point.

Dependency closure SHALL include, as applicable:

- Definitions;
- Tests;
- Objects;
- States;
- Variables;
- variable-to-variable references;
- object components;
- set references;
- filter State references;
- function/component operands;
- extend_definition references.

A Definition/Test/Object-only traversal is insufficient.

A converter SHALL report unresolved reachable references as conversion errors.

## 10. OVAL defaults

Behavior-affecting OVAL defaults SHALL be made explicit in Stage-1 SCAP-NG.

This includes defaults such as:

- criteria operator;
- Test `check`;
- Test `check_existence`;
- State/entity quantifiers;
- filter action;
- behavior values;
- datatype/operation defaults where applicable.

Making a default explicit SHALL preserve the OVAL default value; it SHALL NOT
be used as an opportunity to choose a more convenient native default.

## 10A. Object behaviors and inherited defaults

Stage-1 OVAL migration SHALL NOT equate copying an explicit
`<behaviors>` attribute map with full behavior compatibility. For each
standard Object's schema-declared behavior type, the converter SHALL
resolve inherited attributes, enumerations, effective defaults, and
conditional applicability. It SHALL distinguish an omitted `behaviors`
element from an empty or partially populated element until their equivalence
has been established by source documentation and conformance cases.

Effective behavior settings that affect item collection, recursion, filters,
existence, regex matching, collector error status or execution SHALL be
explicit in SCAP-NG native Collections. Defaults may be recorded as
`source_default` in the separate provenance ledger; they SHALL NOT be
invisible scanner magic. Unsupported or ambiguous behavior settings SHALL
result in exact per-Definition diagnostics.

The semantic comparator SHALL eventually compare effective behavior
signatures, not just raw source attribute spelling. Until that independent
gate and execution tests exist, successful OVAL document round trips SHALL
NOT be represented as proof of full Object-behavior support.

See [behavior audit](../../research/iterations/003/design/oval-object-behaviors-audit.md).

## 11. Result semantics

OVAL result propagation includes more than true/false.

Stage-1 conversion SHALL preserve distinctions needed to represent:

- true;
- false;
- error;
- unknown;
- not evaluated;
- not applicable where produced by the surrounding SCAP processing model.

The final SCAP-NG cross-mode outcome vocabulary remains under specification
review.

A converter SHALL NOT collapse OVAL error/unknown/not-evaluated into ordinary
pass/fail merely to simplify the result model.

## 12. System characteristics and evidence

OVAL System Characteristics are not mapped by copying the entire legacy
system-characteristics document into NG results.

Instead, the SCAP-NG Assessment declares the fields needed for evaluation, and
the result model retains bounded evidence sufficient to justify the outcome.

Stage-1 differential testing MAY retain additional forensic collection data
outside normal production result profiles when needed to prove equivalence.

## 13. Capability mapping

Supported OVAL platform-family Test types map to SCAP-NG Capabilities.

The default naming rule under review is:

    <OVAL family>:<basename>_test
        ->
    <NG family>.<basename>

Examples:

    unix:file_test
        -> unix.file

    linux:rpminfo_test
        -> linux.rpminfo

    windows:registry_test
        -> windows.registry

    independent:shellcommand_test
        -> independent.shellcommand

Historical numeric suffixes such as `53`, `54`, `57`, `58`, `511`,
and `512` SHALL NOT be silently removed until semantic equivalence with a
replacement Capability is formally established.

The detailed OVAL 5.12.3 Test-type inventory is maintained in
`oval-5.12.3-capability-crosswalk.md`.

## 14. Deprecated OVAL tests

An OVAL Test type that is effectively deprecated and explicitly out of the
native SCAP-NG scope SHALL NOT be automatically rewritten into a different Test
family merely because the converter believes a likely replacement exists.

The converter SHALL:

1. identify the deprecated Test type;
2. identify a documented replacement when one exists;
3. mark the source component unsupported or requiring source remediation;
4. permit conversion to be retried after the source is repaired.

OVAL governance decisions that explicitly reinstate a historically deprecated
Test SHALL take precedence over a stale schema annotation when the project's
versioned governance ledger records that decision.

## 15. Source defects

Lossless migration SHALL preserve published defects.

If repeated structure strongly suggests that a source author intended a
different Test, Object, State, architecture, path, value, or variable binding,
the converter SHALL NOT silently repair it.

The anomaly SHOULD be recorded in authoring comments and/or a conversion report.

Correction is a separate reviewed content-maintenance action.

## 16. OVAL descriptive comments

OVAL Test, Object, State, and Variable `comment` attributes SHOULD be
preserved during migration when present because they provide useful
human-readable context about what is collected or tested.

Native SCAP-NG SHOULD expose those values using typed descriptive fields:

- Test `comment` -> `test_title`;
- Object `comment` -> `object_title`;
- State `comment` -> `state_title`;
- Variable `comment` -> `variable_title`.

Definition metadata titles SHOULD map to `definition_title` when the mapping
is unambiguous.

These fields are descriptive metadata and SHALL NOT affect evaluation truth,
result semantics, or exact technical reuse fingerprints.

OVAL `criteria` and `criterion` comments MAY be retained in Stage-1
migration provenance for source traceability but SHOULD NOT be emitted as
native SCAP-NG Boolean-expression titles. Their omission from native
scanner-facing semantics is intentional and SHALL NOT be treated as semantic
loss.

## 17. Stage-2 native refactoring

Once Stage-1 equivalence is established, Stage 2 MAY:

- replace Object/State/Variable chains with named derived values;
- replace repeated low-level collection patterns with higher-level native
  Capabilities;
- consolidate provably equivalent logic;
- replace legacy platform machinery with explicit Platform/applicability
  composition;
- promote exact reusable Assessment semantics into shared Assessments.

Stage-2 refactoring SHALL NOT be described as lossless if behavior changes.

## 18. Example migration chain

The recommended review chain is:

    source OVAL 5.12.3
          |
          v
    Stage-1 lossless SCAP-NG
          |
          +---- differential/regression test
          |
          v
    Stage-2 native SCAP-NG candidate

Reviewers can therefore distinguish migration correctness from language
elegance.

## 19. Conversion report

A converter SHOULD emit a machine-readable conversion report containing, at
minimum:

- source Definition identity;
- complete reachable dependency inventory;
- source Test/Object/State/Variable identities;
- explicit defaults materialized during conversion;
- deprecated/unsupported constructs;
- source anomalies;
- conversion status;
- Stage-2 transformations, if any;
- semantic fingerprints/digests used for equivalence or reuse analysis.

This report is migration evidence. It is not required scanner-facing Assessment
semantics.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: SCAP 1.4 Migration](scap-1.4-migration.md) · [Contents](../README.md) · [Next: OVAL 5.12.3 Capability Crosswalk →](oval-5.12.3-capability-crosswalk.md)

<!-- spec-nav:end -->
