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

## 5. Capabilities

Assessment collection SHALL be expressed using defined capabilities.

A capability identifies a portable collection/evaluation interface rather than
a Benchmark-specific Rule.

The `independent.shellcommand` capability is platform-independent. An
Assessment explicitly supplies the shell/interpreter it intends to use; use of
Bash makes that Assessment operationally Unix/Linux-oriented without changing
the capability family.

## 6. Reuse

Reusable Assessments SHOULD use semantic identities describing the fact they
establish rather than the first Rule or Benchmark that used them.

Benchmark-specific Assessments MAY use Rule-oriented identities until reuse is
demonstrated.

Reuse SHALL be promoted only when semantic equivalence has been established.

## 7. Source references and compiled identity

Authoring paths MAY be used to reference Assessment source files.

Paths SHALL NOT be stable semantic identity.

During compilation, source references SHALL resolve to stable logical
Assessment identities.

Moving or renaming a source file SHALL NOT change Assessment identity.

## 8. Historical provenance

Legacy XCCDF/OVAL/OCIL lineage SHOULD be retained as authoring comments or in
separate conversion reports when useful for migration and review.

Historical lineage SHALL NOT be required in scanner-facing Assessment semantics.

Runtime provenance needed to identify what actually executed is a separate
result/package concern.
