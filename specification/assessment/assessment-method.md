# Assessment Method

**Status:** pre-alpha normative draft

## 1. Purpose

An Assessment Method defines how a fact, applicability condition, Platform
identity, or Rule compliance condition is evaluated.

Policy and Assessment implementation SHALL remain separate concepts.

## 2. Rule binding

A Rule SHALL explicitly reference the Assessment Method or Methods used to
evaluate it.

The forward Rule-to-Assessment relationship is authoritative.

An Assessment Method SHALL NOT require authors to maintain a hand-edited
reverse `used_by` list.

Tooling SHOULD generate reverse usage indexes when useful.

## 3. Modality

An Assessment Method SHALL declare its own execution mode.

Examples include:

- `manual`;
- `automated`.

A Rule SHALL NOT duplicate the Assessment Method's mode as independent
authoritative metadata.

Manual and automated methods MAY be peer methods for the same Rule.

## 4. Automated semantics

Automated Assessments SHALL make behavior-affecting cardinality, existence, and
quantifier semantics explicit.

SCAP-NG SHALL NOT rely on hidden OVAL-style defaults where omission can change
evaluation behavior.

Collection semantics and assertion semantics SHALL remain distinguishable.

Assessment result/evidence limits SHALL NOT redefine compliance truth.

## 5. Expected state and existence

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

## 6. Capabilities

Assessment collection SHALL be expressed using defined capabilities.

A capability identifies a portable collection/evaluation interface rather than
a Benchmark-specific Rule.

The `independent.shellcommand` capability is platform-independent. An
Assessment explicitly supplies the shell/interpreter it intends to use; use of
Bash makes that Assessment operationally Unix/Linux-oriented without changing
the capability family.

## 7. Inventory facts from Platform Assessments

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

## 8. Descriptive titles

Automated Assessment nodes MAY carry concise human-readable descriptive titles
that explain what is being collected or evaluated.

When present, the preferred native field names are:

- `definition_title` for a named Assessment/definition-level description;
- `test_title` for a test/evaluation description;
- `object_title` for a collection/object description;
- `state_title` for an expected-state/predicate description;
- `variable_title` for a variable/derived-input description.

These titles are descriptive metadata. Changing only a title SHALL NOT change
Assessment truth or technical semantic identity.

Migration tooling SHOULD preserve useful OVAL Test/Object/State/Variable
`comment` attributes by mapping them to the corresponding typed title fields.

OVAL `criteria` and `criterion` comments SHALL NOT be promoted into native
SCAP-NG Boolean-expression titles merely because they exist in legacy content.
They MAY be retained in migration provenance for source traceability.

## 9. Reuse

Reusable Assessments SHOULD use semantic identities describing the fact they
establish rather than the first Rule or Benchmark that used them.

Benchmark-specific Assessments MAY use Rule-oriented identities until reuse is
demonstrated.

Reuse SHALL be promoted only when semantic equivalence has been established.

## 10. Source references and compiled identity

Authoring paths MAY be used to reference Assessment source files.

Paths SHALL NOT be stable semantic identity.

During compilation, source references SHALL resolve to stable logical
Assessment identities.

Moving or renaming a source file SHALL NOT change Assessment identity.

## 11. Historical provenance

Legacy XCCDF/OVAL/OCIL lineage SHOULD be retained as authoring comments or in
separate conversion reports when useful for migration and review.

Historical lineage SHALL NOT be required in scanner-facing Assessment semantics.

Runtime provenance needed to identify what actually executed is a separate
result/package concern.
