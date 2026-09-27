# SCAP-NG Iteration 001 — Decisive Outcome Explanation Model

**Status:** Prototype result contract  
**Purpose:** Define structured data that explains why an assessment produced its outcome without requiring consumers to reconstruct the complete assessment graph.

## 1. Terminology

The normative concept should be called a **decisive outcome explanation** rather than root-cause analysis.

A scanner can determine the logical and evidentiary reason an assessment expression evaluated to Pass, Fail, Not Applicable, or Error. It normally cannot determine the operational or human cause of the underlying configuration state.

User interfaces may label the information "root cause" when appropriate, but the serialized data represents an **evaluation cause**, not causal inference about why a system was configured that way.

## 2. Core requirement

For every automated Fail result, the scanner SHALL be able to emit a structured explanation containing the smallest evaluated expression subtree, or set of subtrees, sufficient to prove the reported outcome.

This is the **decisive explanation set**.

The explanation:

- references assessment expression/assertion identifiers where available;
- records actual, expected, operator, and subject for decisive atomic assertions;
- references the evidence supporting those observations;
- preserves enough Boolean structure to explain nested alternatives;
- distinguishes decisive facts from optional additional findings;
- identifies relevant unevaluated branches and why they were skipped;
- records whether the outcome is complete and whether diagnostics are complete;
- never requires repetition of the full static assessment definition.

## 3. Proposed result shape

```yaml
outcome: fail

explanation:
  expression_ref: expr-root
  kind: all
  outcome: fail
  decisive:
    - expression_ref: expr-password-length
      kind: comparison
      outcome: fail
      subject: minimum_password_length
      actual: 12
      operator: ge
      expected: 14
      evidence_refs: [ev-password]

additional_findings: []

unevaluated: []

evaluation:
  outcome_complete: true
  diagnostics_complete: true
```

`explanation` is structured normative data.

A short `summary` string MAY be supplied for display, but a consumer must not have to parse that string to determine why the rule failed.

## 4. Boolean proof semantics

The decisive explanation is derived from the semantics of the expression, not from scanner preference.

### 4.1 AND / all

For:

```text
A AND B AND C
```

a single failed child is sufficient to prove the parent Fail.

Therefore a minimal failure explanation for an AND contains at least one failed child.

If B and C were also evaluated and failed, they may appear as `additional_findings`, subject to diagnostic/evidence limits.

### 4.2 OR / any

For:

```text
A OR B OR C
```

the parent can fail only if **every alternative fails**.

Therefore a failure explanation for an OR must contain a decisive failure explanation for every alternative whose failure is necessary to prove the OR failed.

This is why an OR failure can legitimately require more explanation data than an AND failure.

### 4.3 NOT

If:

```text
NOT A
```

fails, A evaluated true.

The explanation should report the decisive successful condition that caused the prohibited condition to be present.

### 4.4 Nested expressions

The result retains only the necessary Boolean nesting.

For:

```text
A AND (B OR C) AND D
```

if A passes, B fails, C fails, and D is not evaluated because the parent AND is already false, the explanation is conceptually:

```yaml
explanation:
  expression_ref: root
  kind: all
  outcome: fail
  decisive:
    - expression_ref: BC
      kind: any
      outcome: fail
      reason: no_alternative_satisfied
      decisive:
        - expression_ref: B
          outcome: fail
          decisive:
            - <atomic failure sufficient to prove B failed>
        - expression_ref: C
          outcome: fail
          decisive:
            - <atomic failure sufficient to prove C failed>

unevaluated:
  - expression_ref: D
    reason: logical_short_circuit
```

A consumer does not need the successful A subtree or the full assessment graph to understand the failure.

## 5. Atomic assertion explanation

A decisive atomic comparison should normally contain:

```yaml
kind: comparison
assertion_ref: password-minimum
subject: minimum_password_length
actual: 12
operator: ge
expected: 14
outcome: fail
evidence_refs: [ev-password]
```

Additional optional fields may include:

- normalized actual/expected values;
- datatype;
- units;
- source location within structured configuration;
- item identity for population checks;
- parameter references;
- derivation references when the actual value was computed.

The assertion result should not duplicate large raw evidence values when an evidence reference is sufficient.

## 6. Quantifiers and population checks

### EVERY / ALL ITEMS

A universal requirement fails when at least one violating item is found.

The decisive explanation may contain the first violating item. Additional violations are diagnostics and may be capped.

For large populations:

```yaml
explanation:
  kind: population_violations
  outcome: fail
  subject: filesystem_owner_resolves
  violations:
    observed: 50
    count_type: at_least
  evidence_refs: [ev-001, ev-002, ...]

collection:
  complete: false
  termination:
    reason: violation_threshold_reached
    threshold: 50
```

### EXISTS / ANY ITEM

A positive existence requirement fails only after the scanner has established that no satisfying item exists in the complete required scope.

A failure explanation therefore requires scope/completeness evidence. An incomplete search must not be reported as a normal Fail merely because no match was seen yet.

### NONE

A prohibited-existence requirement fails as soon as one prohibited item is found. That item is sufficient decisive evidence.

### COUNT / CARDINALITY

The explanation records the observed count quality, comparison, threshold, and collection completeness necessary to support the outcome.

## 7. Conditional expressions

Branch-selection evidence is different from failure evidence.

For:

```text
if role == member_server:
    assert server_requirement
else:
    assert client_requirement
```

a Fail result should record:

1. the condition evidence that selected the branch; and
2. the decisive explanation inside the selected branch.

Conceptually:

```yaml
decision:
  branch: member_server
  condition:
    subject: system_role
    actual: member_server
    operator: eq
    expected: member_server
    outcome: pass

explanation:
  <failure inside selected branch>
```

Unselected branches are not failures and should not appear as root causes.

## 8. Errors are not compliance root causes

Collection/parse/permission/unsupported-capability failures should use a structured `reason` or error object rather than pretending they are compliance failures.

Example:

```yaml
outcome: error
reason:
  code: collection_permission_denied
  capability: windows.certificate-store
  message: Access to the machine TrustedPublisher store was denied.
evaluation:
  outcome_complete: false
```

Likewise, Not Applicable should report applicability evidence, not a failure explanation.

## 9. Decisive findings versus additional diagnostics

SCAP-NG should distinguish:

- **decisive** — required to prove the outcome;
- **additional findings** — independently useful failures collected after the outcome was already known;
- **supporting** — passing or contextual assertions useful to understand the decision;
- **unevaluated** — branches/items not evaluated, with a reason.

This distinction supports both efficient short-circuiting and richer remediation diagnostics.

A content or scanner policy may request a bounded number of additional failure causes after the outcome is known.

## 10. Completeness

Two result properties remain essential:

```yaml
evaluation:
  outcome_complete: true
  diagnostics_complete: false
```

`outcome_complete: true` means enough evaluation occurred to prove the reported outcome.

`diagnostics_complete: false` means additional independent findings may exist because evaluation stopped once the required diagnostic policy was satisfied.

Collection completeness is separate and is reported on affected evidence/collection scopes.

## 11. Human-readable summary

The scanner SHOULD generate a short display summary from the structured explanation.

Examples:

> Failed: minimum password length is 12; required at least 14.

> Failed: neither TPM readiness nor an approved virtualization exception was satisfied.

> Failed: at least 50 files under /usr have unresolved owners; collection stopped after 50 violations.

The summary is convenience text. The structured explanation is authoritative.

## 12. Why this is preferable to a full result graph

A complete forensic trace remains useful for debugging and migration validation, but it should not be necessary for ordinary reporting.

The decisive explanation model scales with the amount of information necessary to justify the outcome, not with the size of the entire assessment graph.

This is particularly important for:

- deeply nested AND/OR trees;
- large filesystem populations;
- expensive alternate branches;
- shared evidence used by many rules;
- fleet-scale result storage.

## 13. Open questions for review

1. Should the term `explanation`, `decision_explanation`, or another name be normative?
2. Should expression/assertion IDs be mandatory for every nontrivial Boolean node?
3. What exact algorithm defines a minimal decisive explanation when multiple equally minimal proofs exist?
4. Should scanners choose one deterministic minimal proof or return all equivalent minimal proofs up to a diagnostic cap?
5. Should `additional_findings` be a sibling of `explanation` or embedded at relevant Boolean nodes?
6. How much supporting Pass information belongs in Explain versus Forensic result profiles?
7. How should derived values expose their derivation without reconstructing a full OVAL-style variable graph?
8. How should explanation semantics map exactly from OVAL true/false/error/unknown/not-evaluated result propagation during migration?
