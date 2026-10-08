# Assessment Method

For field-level authoring and implementation guidance, start with the
[Assessment reference](reference/README.md). It links the shared evaluation
contract and the initial Unix file/direct-Variable references; catalog coverage
is still incomplete.

**Status:** pre-alpha normative draft

## 1. Purpose

An Assessment Method defines how a fact, applicability condition, Platform
identity, or Rule compliance condition is evaluated.

Rule requirements and Assessment implementation SHALL remain separate concepts.


## Assessment specification identity and standalone role

SCAP-NG uses the generic term **Assessment** for an executable assessment
component. That term SHALL NOT by itself identify the technical assessment
language or specification governing the Assessment.

The machine-executable assessment language derived from OVAL semantics is
expected to remain independently implementable and usable outside SCAP-NG,
subject to OVAL Board ratification and naming. SCAP-NG SHALL therefore avoid
making automated Assessment semantics depend unnecessarily on Benchmark or Rule
constructs.

An automated Assessment SHALL identify the exact assessment specification it
conforms to using a stable specification identifier and version. The eventual
name and identifier of the OVAL successor are OVAL Board decisions. The name
`OVAL 6` SHALL NOT be reused for this work because that designation was used
by a prior OVAL 6 effort.

Until the Board ratifies the final standards identity, project prototypes and
conformance fixtures use the explicitly provisional implementation identifier
`scap-ng.pre-alpha.assessment` with version `0.1.0`. This identifier is an
implementation/testing handle only. It SHALL NOT be presented as the final name
or identifier of the OVAL successor, and it SHALL be replaced consistently in
Benchmarks, automated Assessments, schemas, fixtures, and conformance tests when
the Board-defined identity is adopted.

Conceptually:

    assessment:
      specification:
        id: <board-defined-assessment-specification>
        version: "1.0"

An otherwise self-contained automated Assessment SHALL be independently valid
and executable without requiring a Benchmark or Rule wrapper. Standalone
execution MAY use an Assessment Request to supply explicitly declared inputs,
target context, or execution parameters.

Standalone Assessment execution SHALL produce an Assessment Result without
requiring a fabricated Benchmark Result or Rule Result.

This separation preserves the independent assessment role historically
provided by OVAL for use cases such as inventory, vulnerability assessment,
patch assessment, applicability, evaluator testing, self-assertion, reusable
assessment libraries, and migration tooling.

SCAP-NG is a consumer of such automated Assessments. It adds policy semantics
including Benchmark, Rule, Profile, Tailoring, Organizational Input, policy
interpretation, scoring, aggregate results, packaging, and trust.

Manual Assessment is not part of the OVAL-successor language by default.
Manual Assessment is a native SCAP-NG assessment method defined separately in
`manual-assessment.md`. A future standards decision MAY define a separate
manual-assessment specification, but such a decision SHALL NOT implicitly make
manual procedures part of the OVAL successor.

## 2. Rule binding

A Rule SHALL expose named Assessment selections and identify its default
selection when appropriate. Authored selections SHALL resolve through explicit
Assessment YAML paths relative to the referring Rule.

The authoritative binding chain is Benchmark → Rule → selected Assessment.
There is no separate Policy object or file in the current working design.

An Assessment Method SHALL NOT require authors to maintain a hand-edited
reverse `used_by` list.

Tooling SHOULD generate reverse usage indexes when useful.

## Source presentation order

Assessment source SHOULD present metadata first, followed by `objects`, `variables`, `states`, `tests`, and
`evaluate`, omitting sections that are absent.
This recommendation supports consistent reading and review.

Mapping key order SHALL NOT affect Assessment semantics or reference resolution.
An implementation SHALL permit references to named Objects and Variables
regardless of whether their definitions appear before or after the reference.
An otherwise valid Assessment SHALL NOT be rejected solely for differing from
the recommended presentation order. Sequence order SHALL retain its defined
meaning, including the position of function arguments.

Project generation checks enforce the recommended presentation order for our
generated artifacts; that check is not a language-validity requirement.

## 3. Modality

An Assessment Method SHALL declare its own execution mode.

Examples include:

- `manual`;
- `automated`.

A Rule SHALL NOT duplicate the Assessment Method's mode as independent
authoritative metadata.

Manual and automated methods MAY be peer methods for the same Rule.

## Assessment input contracts and Rule bindings

An Assessment that consumes policy data SHALL declare named typed input
contracts. The Assessment SHALL describe the data it needs without hard-coding
a Benchmark-specific Parameter identity.

A Rule Assessment selection SHALL bind Benchmark Parameters to the named inputs
of the selected Assessment.

Illustrative structure:

    assessment:
      id: time-source-check
      inputs:
        required_time_sources:
          datatype: string
          cardinality: one_or_more
          required: true

    rule:
      assessment_choices:
        automated:
          assessment: time-source-check
          inputs:
            required_time_sources:
              parameter: approved_time_sources

This binding model is the native semantic successor to XCCDF `check-export`
feeding an OVAL external Variable, but it does not require the Assessment to
know the publisher's Parameter ID.

A Parameter-to-input binding SHALL be type/cardinality compatible. Compilation
or policy resolution SHALL reject an unknown input, unknown Parameter, or
incompatible binding.

Within an Assessment, an input MAY feed a Variable, State value, or another
explicitly permitted policy-data location. It SHALL NOT alter Test selection,
Object collection semantics, operations, commands, privileges, or executable
control flow.

## 4. Assessment class and invocation purpose

An Assessment Method SHALL declare an assessment `class` describing the
semantic intent of a true result.

The initial inherited class vocabulary is:

- `compliance`;
- `vulnerability`;
- `patch`;
- `inventory`;
- `miscellaneous`.

These values preserve the corresponding OVAL definition-class concepts.

Assessment `class` SHALL remain distinct from invocation `purpose`.

The initial purpose vocabulary is:

- `assessment`: normal evaluation of the Assessment's declared class;
- `applicability`: evaluation used to determine whether other content applies.

A conforming implementation SHALL NOT infer class from purpose. For example,
an inventory-class Assessment MAY be invoked for applicability, while another
applicability Assessment may have a different class.

The Boolean truth of an Assessment SHALL be interpreted according to its
declared class and invocation context. In particular:

- `compliance: true` means the evaluated condition complies;
- `vulnerability: true` means the vulnerability condition is present;
- `patch: true` means the patch/remediation condition represented by the
  Assessment is present as defined by that Assessment;
- `inventory: true` means the represented product/item condition is present;
- `miscellaneous` SHALL define its interpretation explicitly.

### Candidate NG class: information

`information` is reserved as a candidate SCAP-NG Assessment class for
non-compliance, non-vulnerability observations whose primary purpose is to
report useful information. It is a semantic class/characterization, **not** a
seventh Assessment truth-table result. An informational Assessment still uses
the normal six-state technical result domain (`true`, `false`, `error`,
`unknown`, `not_evaluated`, `not_applicable` as applicable).

`information` is NOT an inherited OVAL class and is NOT currently normative
SCAP-NG vocabulary.

Adding `information` to the normative class enumeration requires an
affirmative OVAL Board / SCAP-NG governance decision. Until such approval,
conforming implementations SHALL NOT emit or require `class: information` as
a standardized class.

Research implementations MAY experiment with the concept only when clearly
marked as non-conformant/experimental.

#### Placement of informational semantics

Informational behavior does not need to be a Benchmark-level property.

The design distinguishes two cases:

1. **Intrinsic informational Assessment** — if an Assessment's purpose is
   inherently informational wherever it is reused, that intent SHOULD live with
   the Assessment itself. If the Board adopts `class: information`, that class
   is the preferred standardized expression.
2. **Policy-context informational disposition** — if an otherwise ordinary
   compliance/vulnerability/patch/inventory Assessment is treated as
   reporting-only in one Rule context, that disposition belongs to the Rule
   binding/result policy and SHALL NOT mutate the reusable Assessment's class or
   technical truth.

A Benchmark SHALL NOT be required to carry informational disposition merely to
support either case. Benchmark-wide policy MAY influence scoring/reporting in
future profiles, but it is not the authoritative home for the meaning of one
Assessment or one Rule's reporting disposition.

Canonical Results SHOULD record both the technical Assessment outcome and the
effective informational/reporting disposition when they differ. A result
consumer SHALL NOT be required to infer informational treatment by rewriting
or replacing the technical Assessment outcome.


## Assessment-result dependencies

An automated Assessment MAY statically declare another Assessment as a
dependency and consume that dependent Assessment's final result within its
`evaluate` expression.

This is a first-class Assessment composition mechanism. It is distinct from:

- sharing or importing collected Items;
- reusing an Object collection execution;
- policy-layer Rule applicability;
- conditional `if/then/else` syntax.

A dependent Assessment result SHALL be usable as an ordinary logical leaf in
the consuming Assessment's evaluation tree. A consumer SHALL NOT be required
to duplicate the dependency's Tests, Objects, States, Variables, or collection
logic.

Illustrative source form:

    assessment:
      dependencies:
        server_role:
          assessment: ../applicability/server-role.assessment.yaml
          expected_id: example.server-role
          expected_version: 1
          purpose: applicability

      evaluate:
        all:
          - assessment: server_role
          - test: local-setting-correct

The exact final `evaluate` serialization remains subject to schema
stabilization. The semantic contract is normative:

1. Every dependency SHALL be statically declared in signed/validated source.
2. Source references SHALL resolve deterministically during compilation.
3. The compiled package SHALL bind the dependency to immutable Assessment
   identity/version/content.
4. A dependency graph SHALL be acyclic. Cycles SHALL fail validation rather
   than being resolved by runtime recursion limits.
5. The dependent Assessment's complete result domain SHALL be preserved.
   `error`, `unknown`, `not_evaluated`, and `not_applicable` SHALL NOT
   be silently coerced to Boolean false.
6. If a dependency invocation with the same target and effective bindings is
   already available in the execution graph, a processor SHOULD reuse that
   result rather than execute it again.
7. Result reuse SHALL NOT erase provenance. The consuming Assessment Result
   SHALL identify the dependency execution/result it consumed.
8. An Assessment-result dependency SHALL NOT implicitly import the dependent
   Assessment's Items into the consumer. Item/collection reuse is a separate
   mechanism with separate provenance and completeness rules.

### OVAL `extend_definition` migration

OVAL 5.12.3 `extend_definition` maps to an Assessment-result dependency plus a
leaf reference in the native `evaluate` tree.

Migration SHALL preserve:

- the referenced Definition identity;
- the position of the reference within the criteria tree;
- surrounding criteria operators and nesting;
- `negate` semantics;
- the full result-domain behavior of the referenced Definition;
- source provenance.

Migration SHALL NOT inline the referenced Definition merely to avoid an
Assessment dependency when doing so would duplicate semantics, lose reusable
identity, change evaluation/result provenance, or obscure the original graph.

OVAL `applicability_check` on an `extend_definition`, `criterion`, or
`criteria` node is a separate applicability semantic marker and SHALL NOT be
discarded merely because the referenced Definition has been represented as an
Assessment dependency. Its exact native migration is defined with the
applicability model.


## Intrinsic Assessment applicability

An automated Assessment MAY define an intrinsic applicability expression that
determines whether that Assessment is valid for the current target before its
normal `evaluate` expression is interpreted.

Intrinsic Assessment applicability is part of the standalone assessment
language. It is distinct from SCAP-NG Rule applicability:

- **Assessment applicability** answers whether this Assessment itself is valid
  for the current target/execution context and can produce
  `not_applicable`.
- **Rule applicability** is SCAP-NG policy-layer logic deciding whether a Rule
  applies before selecting/executing its compliance Assessment.

Illustrative native shape:

    assessment:
      applicability:
        all:
          - test: product-installed
          - assessment: supported-platform

      evaluate:
        all:
          - test: version-in-range
          - test: configuration-correct

The same logical leaf forms available to `evaluate` SHALL be usable by the
intrinsic applicability expression when semantically appropriate, including
local Test results and statically declared Assessment-result dependencies.

Evaluation SHALL conceptually proceed as follows:

1. If no intrinsic applicability expression is present, the Assessment is
   intrinsically applicable.
2. If intrinsic applicability evaluates `true`, evaluate the normal
   `evaluate` expression.
3. If intrinsic applicability evaluates `false`, the Assessment outcome SHALL
   be `not_applicable`; the normal evaluation expression need not execute.
4. `error`, `unknown`, or `not_evaluated` produced while establishing
   applicability SHALL remain distinguishable and SHALL NOT be coerced to
   `false` or `not_applicable`.
5. An implementation MAY short-circuit work whose result cannot affect the
   final outcome, subject to the normal dependency/evidence/completeness rules.

### OVAL `applicability_check` migration

OVAL 5.12.3 permits `applicability_check=true` on `criteria`,
`criterion`, and `extend_definition` nodes. Those markers identify portions
of the Definition criteria used to determine whether the Definition applies to
the target.

Lossless migration SHALL preserve that distinction. A false applicability
condition SHALL NOT be collapsed into an ordinary false Assessment result when
the source semantics require `not_applicable`.

A converter SHOULD derive the native intrinsic applicability expression from
the source applicability-marked criteria while preserving source nesting,
operators, negation, referenced Tests/Definitions, and provenance. If the source
graph cannot be separated into applicability and normal evaluation without a
provably equivalent transformation, migration SHALL retain an explicit
compatibility representation or report a blocker rather than silently dropping
the applicability marker.

This intrinsic applicability mechanism is required independently of SCAP-NG so
that a standalone converted OVAL Definition retains its result semantics even
when it is executed without a Benchmark or Rule wrapper.


## Composed Assessments and XCCDF complex-check migration

An automated Assessment MAY be a **composed Assessment** whose evaluation is
defined partly or entirely by the results of statically declared dependent
Assessments.

This permits a Rule to retain the simple relationship:

    Rule -> selected Assessment

even when legacy policy used a Boolean composition of several independent
checking-system checks.

A composed Assessment MAY have no local Objects, States, or Tests when its
result is derived entirely from dependent Assessment results. Its
`dependencies` and `evaluate` expression remain sufficient executable
content.

### XCCDF `complex-check`

An XCCDF `complex-check` SHOULD migrate to a composed Assessment when its
children represent independently executable checks.

The converter SHALL preserve:

- recursive AND/OR grouping;
- child ordering for provenance even when the logical operator is commutative;
- `negate` at every complex-check node;
- each child check's checking-system identity and resolved content;
- the source XCCDF multi-valued result-combination semantics.

Each executable child check SHOULD become or resolve to an independently
identified Assessment dependency. The composed Assessment's `evaluate`
expression combines those dependency results.

A converter SHALL NOT flatten nested complex-check groups when flattening could
change negation, result-domain propagation, provenance, or source traceability.

### XCCDF simple-check negation

XCCDF check-level `negate=true` SHALL be represented in the composed/native
evaluation expression surrounding the referenced Assessment result. Negation
changes the consuming expression's interpretation of the child result; it SHALL
NOT mutate the child Assessment's independently executable truth.

This distinction permits the same Assessment to be reused by both negated and
non-negated consumers without creating semantically duplicated Assessment
files.

## 5. Automated semantics

Automated Assessments SHALL make behavior-affecting cardinality, existence, and
quantifier semantics explicit.

SCAP-NG SHALL NOT rely on hidden OVAL-style defaults where omission can change
evaluation behavior.

Object selection/collection semantics and State assertion semantics SHALL remain distinguishable.

Assessment result/evidence limits SHALL NOT redefine compliance truth.

## 6. Expected state and existence

Automated Assessments SHALL be able to express expected state independently
from collection.

An expected state MAY constrain value, existence, or cardinality. Existence is
a first-class state condition and SHALL NOT be represented only by incidental
string comparison or scanner-specific control flow.

At minimum, the following semantics SHALL be representable:

- expected `none`: zero matching observations are required;
- expected `one_or_more`: at least one matching observation is required;
- explicit cardinality constraints where an exact or bounded count is part of
  the policy.

For an expected state of `none`:

- zero matching observations SHALL evaluate true;
- one or more matching observations SHALL evaluate false.

For an expected state of `one_or_more`:

- zero matching observations SHALL evaluate false;
- one or more matching observations SHALL evaluate true.

These semantics apply uniformly to capability result entities such as files,
packages, processes, accounts, configuration entries, Registry values, command
output entities, and other collected facts.

Illustrative authoring syntax:

    state:
      stdout:
        existence: none

The exact final serialization remains subject to schema design, but a conforming
implementation SHALL preserve the above truth semantics.

A failed existence assertion SHOULD produce both a deterministic human-readable
message and a structured failure reason. Examples include
`unexpected_existence` and `required_item_missing`.

SCAP 1.4 migration SHALL preserve source existence/cardinality semantics,
including OVAL `check_existence`, or SHALL fail explicitly.

## 7. Capabilities

Assessment collection SHALL be expressed using defined capabilities.

Each named or embedded Object SHALL carry its own capability because an Object is an independently meaningful authored selection node and MAY be referenced by more than one Test or Variable. A Test capability SHALL NOT substitute for, relocate, or implicitly define the capability of a referenced Object. Test, Object, and State capability identities SHALL be validated for compatibility without erasing their independent declarations.

An **Object** describes what observations are selected. **Collection** is the runtime act of evaluating an Object against a target and producing zero or more Items plus collection status. Native authoring SHALL use Object for the authored construct; result/runtime documentation MAY describe Object collection execution.

A capability identifies a portable collection/evaluation interface rather than
a Benchmark-specific Rule.

The `independent.shellcommand` capability is platform-independent. An
Assessment explicitly supplies the shell/interpreter it intends to use; use of
Bash makes that Assessment operationally Unix/Linux-oriented without changing
the capability family.

## OVAL-aligned native vocabulary

SCAP-NG SHALL use the established OVAL semantic terms **Test**, **Object**,
**State**, **Variable**, and **Item** when the native construct retains the same
substantive meaning. This is a vocabulary alignment decision, not a requirement
to reproduce OVAL XML serialization.

The following intentional native divergences remain:

- OVAL Definition maps to an **Assessment**;
- OVAL criteria/criterion maps to **evaluate** while preserving full nested
  logical expressive power;
- OVAL generic `comment` metadata maps to the typed descriptive fields
  `test_title`, `object_title`, `state_title`, and `variable_title`.

SCAP-NG 0.3 Tests SHALL expose the inherited semantics through the native
fields `existence`, `match`, and (when multiple States require composition)
`states_match`. Migration maps OVAL Test `check_existence`, `check`, and
`state_operator` to those fields without changing truth semantics. The shorter
native field names do not merge their distinct semantic stages: existence,
per-Item/State satisfaction, and State composition remain separately defined.

Objects and States SHOULD be independently named in native Assessment source.
Stable local identities support reuse, filters, result-to-source traceability,
semantic comparison, and generated capability schemas.

Objects and States MAY instead be embedded directly within a Test when they
are private to that Test and are not referenced elsewhere.

For embedded/private nodes, containment defines scope and identity. An embedded
Object or State SHALL NOT require an authored ID solely to support execution or
result reporting. A node that must be referenced outside its containing Test
SHALL be promoted to a named Object or State.

This yields the following authoring principle:

> **Containment implies private scope; IDs imply referenceable scope.**

A conforming normalizer MAY inline a named Object or State when it can prove
that the node is used only by one Test and is not independently referenced by a
Variable, set, filter, other Test, or other dependency. Such normalization
SHALL preserve evaluation semantics and migration provenance.

Likewise, a conforming normalizer MAY promote equivalent private inline nodes
to named reusable nodes when reuse is established. The normalizer SHALL NOT
infer reuse solely from similar human-readable titles.

Migration evidence SHALL preserve the source identity of an inlined legacy
node, including its source OVAL Object or State identity where available, even
when that identity is no longer exposed as a native authored ID.

Assessment Results MAY identify private inline nodes by deterministic structural
identity derived from the containing Test; an authored node ID SHALL NOT be
required merely for result traceability.

Filters are part of Object semantics. The Item population participating in a
Test is the effective population after Object selection, set operations, and
filters. A scanner MAY implement filtering during collection/query planning and
is not required to materialize or count a pre-filter candidate population.

The working vocabulary decision and migration crosswalk are recorded in
[Assessment vocabulary alignment with OVAL](../../research/iterations/003/design/assessment-oval-vocabulary-alignment.md).


## Native authored literal datatypes

For specification version 0.2.0, authored scalar literals SHALL use the native
JSON/YAML value kind corresponding to their declared SCAP-NG datatype. Authors
and editors SHALL NOT rely on OVAL/XML lexical strings where the native
serialization provides an unambiguous typed value.

In particular:

- `datatype: boolean` SHALL use a Boolean literal such as `true` or `false`;
  strings such as `"true"`, `"false"`, `"1"`, and `"0"` are invalid
  native authored Boolean literals;
- `datatype: integer` SHALL use a JSON/YAML integer and SHALL NOT accept a
  Boolean or numeric string as an authored literal;
- `datatype: float` SHALL use a finite JSON/YAML numeric value rather than a
  numeric string or Boolean;
- string-based datatypes, including `string`, `binary`, `version`,
  IP-address and package/version lexical datatypes, SHALL use string literals
  unless a capability-specific contract defines a structured representation;
- record values SHALL use the structured record representation rather than a
  scalar literal.

A Variable reference is not a literal and is validated against the referenced
Variable's declared/effective datatype separately.

SCAP 1.4 migration tooling MAY accept source lexical forms that are valid under
the pinned OVAL/XML datatype contract, but it SHALL convert them into the native
SCAP-NG representation before emitting 0.2.0 authored content. Source lexical
spelling MAY be retained in migration provenance when needed for round-trip or
audit evidence. An importer SHALL NOT force native authors to preserve XML
lexical aliases merely because the legacy source permitted them.

This rule deliberately separates source compatibility from native authoring:
for example, OVAL Boolean lexical values `true`, `false`, `1`, and `0`
remain valid migration inputs where the source schema permits them, while native
SCAP-NG Boolean literals are the JSON/YAML Boolean values `true` and `false`.

### 0.3 State comparison datatype versus collected Item datatype

For OVAL-derived Assessments, **the datatype declared on an authored State
predicate is the datatype used for comparison, not necessarily the native
datatype of the collected Item field**. These are separate contracts:

- The capability's collected-Item field schema identifies the observed value's
  native representation and preserves that representation in evidence.
- The authored State's explicit `datatype` governs the comparison. The
  evaluator attempts the corresponding OVAL-compatible conversion of the
  collected value before applying the authored comparison operation.
- An unsupported or unsuccessful required cast SHALL produce an evaluation
  error under the applicable OVAL result-propagation rules. The evaluator SHALL
  NOT silently reinterpret the authored datatype, treat an uncastable value as
  an ordinary mismatch, or weaken a comparison to string equality.

This does **not** permit an authored integer State literal to be expressed as
the string `"10"`; native authored literals remain correctly typed. For
example, real Windows 11 SV-253447 and Windows Server 2025 SV-278181 may
collect Registry `REG_SZ` data yet compare the numeric cached-logon threshold
using an integer State. The collected Item retains the Registry string type
and contents; the State expresses the integer comparison. Such source content
SHALL NOT be rejected merely because the two datatypes differ.

A schema-valid predicate does not prove cast execution or scanner behavior.
Known-result evaluator tests SHALL cover successful casts, invalid lexical
casts, collected-value absence, and relevant error propagation before
claiming runtime equivalence. Evidence for the source/schema correction:
[0.3 fidelity CI](https://github.com/vanderpol/scap-ng/actions/runs/37809832383).

## Structured record values

The Assessment language SHALL support **record** values as first-class
structured data. Record support is required for real OVAL capabilities including
Windows WMI57, PowerShell cmdlet, LDAP/YAML-related structures, database-style
query results, and other capabilities that collect multiple related named
fields as one logical value.

A record SHALL preserve the relationship among its fields. Implementations
SHALL NOT flatten a record into unrelated scalar values when doing so would
lose field identity, grouping, cardinality, or evaluation semantics.

Conceptually, an Item field whose datatype is `record` contains one or more
named typed fields:

    result:
      datatype: record
      fields:
        - name: Name
          datatype: string
          value: example
        - name: Enabled
          datatype: boolean
          value: true

The final serialization remains subject to capability-schema generation, but
the following semantic requirements are normative:

- record fields SHALL retain their names;
- each field SHALL retain its datatype and collection/status information;
- repeated field names SHALL be representable when the source capability
  permits them;
- a State SHALL be able to assert requirements against individual record
  fields;
- State evaluation SHALL preserve the record's field grouping rather than
  treating fields as independent Items;
- result/evidence output SHALL retain enough structure to explain which field
  caused a match or failure;
- Variables/Object components SHALL be able to extract a specific record field
  where the inherited OVAL semantics require it.

For OVAL-compatible record entities, migration SHALL preserve the inherited
constraints that the enclosing record entity has datatype `record`, uses
`equals` at the record-entity level, and does not use the ordinary scalar
`var_ref` / `var_check` mechanism where OVAL prohibits those attributes.
Field-level operations, datatypes, statuses, and cardinality SHALL follow the
capability and Assessment-language rules applicable to those fields.

Constraints that depend on relationships among fields or attributes and cannot
be expressed safely in JSON Schema SHALL be enforced by the semantic validator.
The generated disposable capability schemas SHALL record which constraints are
schema-enforced and which require semantic validation.

Record support is a retained semantic capability, not legacy serialization
baggage, and SHALL be covered by positive and negative conformance fixtures.

## 8. Inventory facts from Platform Assessments

A Platform Assessment MAY emit descriptive target-inventory facts in addition
to its Boolean Platform result.

Inventory emission SHALL NOT alter the truth of the Platform Assessment.

A Platform Assessment that establishes an operating system or application MAY
emit, when supported by collected evidence:

- product kind, such as `operating_system` or `application`;
- product name and version;
- standardized product identifiers such as CPE;
- provenance identifying the Platform Assessment and collected evidence that
  produced the inventory fact.

Illustrative output contract:

    inventory:
      product:
        kind: operating_system
        identifiers:
          - scheme: cpe
            value: "cpe:/o:redhat:enterprise_linux:9.0"

Such inventory output is descriptive scan data. It SHALL NOT be consumed as an
implicit Rule-selection, applicability, or compliance input.

A processor MAY deduplicate equivalent inventory facts emitted by multiple
Platform Assessments, provided provenance sufficient to explain the reported
inventory is retained.

## 9. Descriptive titles

Automated Assessment nodes MAY carry concise human-readable descriptive titles
that explain what is being collected or evaluated.

When present, the preferred native field names are:

- `assessment_title` for the Assessment Method description;
- `test_title` for a test/evaluation description;
- `object_title` for a collection/object description;
- `state_title` for an expected-state/predicate description;
- `variable_title` for a variable/derived-input description.

These titles are descriptive metadata. Changing only a title SHALL NOT change
Assessment truth or technical semantic identity.

`assessment_title` is a standard Assessment field in the current draft and SHOULD remain
visible in human-authored/review source even when unset. Its value MAY be null.
Native content SHOULD NOT populate it merely by copying the governing Rule title.
It is most useful when an Assessment has a meaningful standalone or reusable
description that differs from the Rule.

Migration tooling SHOULD preserve an OVAL Definition
`metadata/title` as `assessment_title` when present. Migration tooling SHOULD
also preserve useful OVAL Test/Object/State/Variable `comment` attributes by
mapping them to the corresponding typed title fields.

An absent source title SHALL be represented as `assessment_title: null` rather
than being synthesized solely to populate the field.

OVAL `criteria` and `criterion` comments SHALL NOT be promoted into native
SCAP-NG Boolean-expression titles merely because they exist in legacy content.
They MAY be retained in migration provenance for source traceability.

## 10. Reuse

Reusable Assessments SHOULD use semantic identities describing the fact they
establish rather than the first Rule or Benchmark that used them.

Benchmark-specific Assessments MAY use Rule-oriented identities until reuse is
demonstrated.

Reuse SHALL be promoted only when semantic equivalence has been established.

## 11. Source references and compiled identity

Human-readable native authoring files SHOULD use **explicit relative
source-file paths** for each Rule-owned Assessment selection. Relative paths
SHALL resolve against the directory containing the referring Rule file, SHALL
be normalized and confined to the declared source boundary, and SHALL be
validated before compilation. The authoring tool SHALL NOT infer a path from
a logical identity, matching basename, or arbitrary directory search.

Assessment identities SHALL be read from the referenced Assessment objects and
remain distinct from file paths. Moving or renaming an Assessment source file
SHALL NOT by itself change its semantic identity; referring Rules may need
their paths updated. Different named Rule selections MAY deliberately resolve
to the same Assessment, but selector identity SHALL remain visible.

During compilation, Rule Assessment references SHALL resolve to logical IDs
and versions and to explicit packaged members with integrity digests in the
package manifest. Runtime scanners SHALL resolve through this published
manifest, not relative authoring paths or assumed file layout. Resolution
errors, duplicate conflicting identities, wrong object types, missing package
members, and escaping the source/package boundary SHALL fail validation, not
trigger fallback lookup.

A separate Policy object or author-maintained Assessment index SHALL NOT be
required for this linkage. ID-only authoring references MAY be introduced only
with a defined, unambiguous registry and conformance tests; an opaque ID alone
is not a complete portable source-file link.

## 12. Historical provenance

Legacy XCCDF/OVAL/OCIL lineage SHOULD be retained as authoring comments or in
separate conversion reports when useful for migration and review.

Historical lineage SHALL NOT be required in scanner-facing Assessment semantics.

Runtime provenance needed to identify what actually executed is a separate
result/package concern.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Parameters and Organizational Input](../policy/parameters-and-organizational-input.md) · [Contents](../README.md) · [Next: Manual Assessment →](manual-assessment.md)

<!-- spec-nav:end -->


## Assessment versioning

An Assessment Method SHALL have a stable logical identity and SHOULD carry an
explicit version/revision.

Assessment identity and Assessment version SHALL be distinct concepts. A
semantic revision of an Assessment SHOULD retain the same logical Assessment
identity and increment or otherwise change its version according to the
applicable versioning policy.

For migrated OVAL Definitions, migration tooling SHOULD preserve the source
OVAL Definition version as the initial Assessment version when that mapping is
semantically faithful.

Independent versioning of nested Assessment nodes corresponding conceptually
to OVAL Tests, Objects, States, and Variables remains an open standards
question. SCAP-NG SHALL NOT require such lower-level versions until the
reuse/change-tracking benefit and authoring cost have been reviewed.

## Generator/build provenance

SCAP-NG SHALL NOT silently discard useful source generator metadata during
migration.

Whether generator identity, generator version, schema/specification version,
and generation timestamp belong in native Assessment source, Benchmark
publication metadata, package/build provenance, or migration evidence remains
an open standards question.

Until resolved, migration tooling SHOULD preserve source generator metadata in
conversion evidence/provenance even when it is not emitted into native
Assessment semantics.


## OVAL-derived collection behavior contracts

**Status: compatibility requirement; schema-wide and execution conformance
coverage is still open.**

Each supported native Object capability SHALL define a typed, versioned
behavior contract: its allowed settings, allowed values, validity conditions,
Object collection/existence/error effects and supported combinations. Native
SCAP-NG SHALL NOT define a behavior choice by omission. When two or more
behavior values are semantically possible, authored content SHALL state the
effective value explicitly and schema validation SHALL reject its absence.

Stage-1 migration SHALL preserve all behavior settings explicitly provided by
the source and SHALL materialize every applicable OVAL default as an explicit
native value **only when its effective meaning is established for the relevant
OVAL Object type**. Absence of the optional `behaviors` element SHALL NOT
automatically be assumed equivalent to an empty element or a partially
specified element without verifying the source language's omission semantics.

Native Object authoring SHALL expose applicable effective behaviors with
concrete values. Conversion provenance SHALL distinguish values explicitly
authored in OVAL from values materialized from a documented OVAL default. If a
behavior is unsupported or its effective semantics cannot be established,
migration SHALL report the affected Definition instead of silently choosing a
value. A behavior that has exactly one possible meaning because it is intrinsic
to the native construct is not a default and need not be redundantly authored.

Conformance tests SHALL distinguish XML attribute preservation from actual
collector behavior and SHALL cover conditional semantics (for example,
`max_depth=-1` does not enable recursion when
`recurse_direction=none`), inherited behavior types, error-flagging options,
regular-expression modes and item-existence/creation behaviors.

See [the OVAL Object behaviors audit](../../research/iterations/003/design/oval-object-behaviors-audit.md).

## Derived requirements from OVAL 5.12.3 round-trip evidence

This section captures provisional assessor contracts supported by iterative
semantic regression tests. Its terminology describes **native behavior**, not
an obligation to reproduce the OVAL XML object model.

### Typed components and compatible references

An automated Assessment SHALL distinguish (a) Test/evaluation capability,
(b) authored Object capability, and (c) expected State/predicate capability
wherever all three concepts are present. A producer SHALL NOT
silently change a referenced component's capability to match its caller.

A semantic validator SHALL verify that a Test is compatible with the Object
and State interfaces it references. An incompatible combination SHALL be
reported with reference identities and source locations, even where the input
is otherwise XSD-valid. Preserving a malformed published source for migration
diagnostics is **not** an assertion that the configuration is executable or
valid native SCAP-NG.

### Typed dependency closure

Assessment dependency resolution SHALL include every reachable Definition
expression, Test, Object, State, set, filter, Variable, component,
function operand, and nested reference required for evaluation. Validation,
unsupported-feature detection, provenance accounting, and execution planning
SHALL use equivalent graph-closure semantics and SHALL reject unresolved
required references.

The evaluator SHALL NOT assume that Variables can be substituted in a single
pre-collection pass. Dataflow can depend recursively on collection results.
Cycle handling and termination outcomes SHALL be deterministic; exact
cycle/error propagation cases require an execution conformance suite.

### State associations and quantifiers

An automated Test MAY associate multiple individually defined States.
Its **Test-level State combiner** SHALL remain distinct from the internal
Boolean/entity operator of each State. Existence, item-check aggregation,
entity-check aggregation, and variable-value aggregation SHALL each have
explicitly specified scope; a producer SHALL NOT collapse these scopes merely
because some Boolean-only cases evaluate equally.

### External input constraints

An externally supplied typed value MAY have enumerated allowed values or
typed restrictions. Conforming input binding SHALL validate the supplied
values against those constraints before Assessment execution; invalid inputs
SHALL not silently broaden the permissible domain. The constraint model SHALL
support multiple values where the source semantics permit them.

The exact restriction-expression syntax, multiplicity truth tables, and error
outcomes remain to be specified and independently execution-tested.

### Inherited result aggregation semantics

For OVAL-compatible migrated assessments, generic Boolean/result aggregation
SHALL preserve the OVAL 5.12.3 evaluation tables for `CheckEnumeration`,
`OperatorEnumeration`, and `ExistenceEnumeration`, including the precedence
and propagation of `true`, `false`, `error`, `unknown`, `not evaluated`,
and `not applicable`.

A conforming migration implementation SHALL NOT replace these multi-valued
semantics with ordinary two-valued Boolean logic. In particular, a decisive
`false` for an ALL/AND aggregation and a decisive `true` for an
AT-LEAST-ONE/OR aggregation may determine the result even when other inputs
are `error` or `unknown`, exactly as specified by the authoritative OVAL
tables.

Test/object existence aggregation SHALL remain a separate evaluation stage
from item-to-State satisfaction aggregation. `any_exist` is not synonymous
with `at_least_one_exists`; the inherited OVAL table intentionally permits
`any_exist` to evaluate true when zero matching objects exist and no
collection error prevents that conclusion.

The project's reference truth-table fixture is
`tools/oval_result_truth_tables.py` with conformance tests in
`tools/test_oval_result_truth_tables.py`. This helper is test evidence, not
the reference scanner itself.

### Collected-object flag control flow

For OVAL-compatible migrated assessments, the collected-object status/flag
SHALL affect Test result evaluation according to the pinned OVAL 5.12.3
Results schema:

- `error` produces Test `error`;
- `not collected` produces Test `unknown`;
- `not applicable` produces Test `not applicable`;
- `does not exist` is resolved solely from the Test existence mode:
  `none_exist` and `any_exist` produce true, while `all_exist`,
  `at_least_one_exists`, and `only_one_exists` produce false;
- `complete` evaluates existence first and evaluates item/State satisfaction
  only when existence is true;
- `incomplete` normally produces `unknown`, but a decisive false or true
  SHALL be preserved when the OVAL 5.12.3 rules establish the outcome despite
  incomplete collection.

In particular, incomplete collection SHALL produce false when
`none_exist` already has one or more existing items, when
`only_one_exists` already has more than one existing item, or when the item
check has already become decisively false. For an AT-LEAST-ONE item check,
one known satisfying item MAY produce true despite the incomplete collection.
Implementations SHALL NOT collapse all incomplete collections to `unknown`.

When a collected-objects section is present but no collected-object record
matches the referenced Object, the Test result SHALL be `unknown`. The
separate OVAL behavior for a System Characteristics document that omits the
entire collected-objects section requires item matching against system data and
remains a distinct evaluator conformance case.

### State entity and variable aggregation order

When a State entity references multiple Variable values and a collected Item
contains multiple corresponding entity instances, evaluation SHALL preserve
the OVAL 5.12.3 many-to-many aggregation order:

1. compare one system/item entity value against each Variable value;
2. combine those comparison results with that State entity's `var_check`;
3. repeat for each corresponding system/item entity instance;
4. combine the per-instance results with that State entity's `entity_check`;
5. combine distinct entity/predicate results inside the State using the
   State's own Boolean operator;
6. when a Test references multiple States, combine those State results for
   each item using the Test's `state_operator`; and
7. combine item results at the Test level using the Test's `check`.

These scopes SHALL remain independent. A producer or evaluator SHALL NOT
commute, merge or substitute `var_check`, `entity_check`, State operator,
`state_operator`, or Test `check` merely because a particular two-valued
example happens to produce the same result. Error/unknown/not-evaluated/not-
applicable propagation occurs at each aggregation layer.

The current independent fixture exercises non-commutative and error-precedence
cases. Zero-row/zero-value edge cases that are not fully established by the
authoritative text SHALL remain explicit conformance questions rather than
being guessed.

Item comparison operations themselves, omitted collected-objects-section
behavior, remaining zero-cardinality cases, early-termination completeness and
differential evaluator testing remain separate conformance work.

### Structural compatibility versus execution equivalence

Passing a source-to-native-to-source semantic graph comparison, XSD
validation, and source-relative Schematron checks is **migration
compatibility evidence**, not proof that two evaluators agree at runtime.
Execution-equivalence claims SHALL require reference evaluation cases
covering actual collection, typed comparison, cardinality and error states.

Detailed rationale and staged extraction criteria are recorded in
[OVAL-derived specification lessons](../../research/iterations/003/design/oval-derived-specification-lessons.md).
