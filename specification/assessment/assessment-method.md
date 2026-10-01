# Assessment Method

**Status:** pre-alpha normative draft

## 1. Purpose

An Assessment Method defines how a fact, applicability condition, Platform
identity, or Rule compliance condition is evaluated.

Rule requirements and Assessment implementation SHALL remain separate concepts.

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
An implementation SHALL permit references to named Collections and Variables
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
report useful information.

`information` is NOT an inherited OVAL class and is NOT currently normative
SCAP-NG vocabulary.

Adding `information` to the normative class enumeration requires an
affirmative OVAL Board / SCAP-NG governance decision. Until such approval,
conforming implementations SHALL NOT emit or require `class: information` as
a standardized class.

Research implementations MAY experiment with the concept only when clearly
marked as non-conformant/experimental.

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

Tests SHALL retain the established behavior-affecting names `check_existence`,
`check`, and `state_operator` when those inherited semantics are preserved.
SCAP-NG SHALL NOT rename OVAL Test `check` to `item_quantifier` merely for
stylistic clarity; instead, the specification SHALL define Item and Test
aggregation precisely.

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

Each supported native Collection Capability SHALL define a typed, versioned
behavior contract: its allowed settings, allowed values, effective defaults,
validity conditions, collection/existence/error effects and supported
combinations. SCAP-NG SHALL NOT make authors rely on undocumented
collector-specific defaults.

Stage-1 migration SHALL preserve all behavior settings explicitly provided by
the source and SHALL materialize behavior defaults **only when their effective
meaning is established for the relevant OVAL Object type**. Absence of the
optional `behaviors` element SHALL NOT automatically be assumed equivalent to
an empty element or a partially specified element without verifying the source
language's omission semantics.

Native Collection authoring SHOULD expose applicable effective behaviors with
concrete values. Conversion provenance SHALL distinguish values explicitly
authored in OVAL from values inferred through a documented default. If a
behavior is unsupported or its effective semantics cannot be established,
migration SHALL report the affected Definition instead of silently choosing a
default.

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
