# Results and Evidence

**Status:** pre-alpha normative draft

## 1. Separation of concerns

SCAP-NG SHALL distinguish:

- evaluation truth;
- evaluation completeness;
- result characterization;
- retained evidence;
- optional non-authoritative analysis.

These concepts SHALL NOT be conflated.

## 2. Result package

A complete scan SHOULD produce a normalized result package containing run-,
target-, Benchmark-, Profile-, scanner-, and summary-level information once per
run and Rule-specific results for each evaluated Rule.

The canonical result package need not use the same denormalized representation
used by SIEM exports.

## 3. Target identity

Hostnames and IP addresses SHALL NOT be assumed to be globally unique or
stable target identifiers.

Results SHOULD support one or more typed target identifiers, such as:

- SMBIOS UUID;
- cloud instance identifier;
- hardware serial number;
- scanner-managed asset identifier;
- organization-managed asset UUID.

Hostname and relevant addresses SHOULD remain available as descriptive
correlation data.

## 4. Target product inventory

A complete scan result SHOULD support target product inventory independently
from per-Rule compliance results.

At minimum, when available, target inventory SHOULD be able to identify:

- the operating system;
- detected applications relevant to the scan;
- standardized external product identifiers associated with those products.

CPE MAY be used as one such standardized product identifier.

Illustrative result structure:

    target:
      inventory:
        operating_system:
          name: Microsoft Windows 11
          identifiers:
            - scheme: cpe
              version: "2.3"
              value: "cpe:2.3:o:microsoft:windows_11:*:*:*:*:*:*:*:*"

        applications:
          - name: PostgreSQL
            version: "16"
            identifiers:
              - scheme: cpe
                version: "2.3"
                value: "cpe:2.3:a:postgresql:postgresql:16:*:*:*:*:*:*:*"

Product identifiers SHALL NOT be treated as unique asset identifiers.

The inventory representation SHOULD preserve identifier scheme and version so
multiple CPE generations or other identifier systems can coexist.

Whether a reported CPE is later used for content applicability is a separate
policy/evaluation concern.

When product inventory is emitted by a Platform Assessment, the result SHOULD
retain enough provenance to identify the producing Platform Assessment and the
supporting observed evidence.

Product inventory is descriptive target data. It SHALL NOT be interpreted as a
Rule result, compliance finding, or implicit applicability decision.

## 5. Rule result self-description

A Rule result SHOULD contain enough Rule context for common downstream use
without requiring the consumer to possess the original Benchmark.

This SHOULD include, as applicable:

- stable Rule identity;
- important publisher identifiers;
- title;
- severity;
- outcome;
- concise deterministic message;
- structured failure reason;
- bounded evidence;
- Assessment mode;
- effective check selector and Assessment Method identity;
- `expected_state`, always present;
- Tailoring and Organizational Input provenance where relevant.

The full Rule discussion, remediation, Manual Assessment procedure, and
Assessment implementation SHOULD NOT automatically be copied into every Rule
result.

## Expected-state visibility

Every Rule Result SHALL expose an `expected_state` collection, including when
all expected values come directly from publisher-authored Assessment State and
no Organizational Input is involved.

The purpose is interoperability: consumers SHALL NOT be required to discover a
rare result element only when an exceptional policy source is encountered.
`expected_state` is therefore a stable part of the Rule Result contract.

For an automated Rule Result, each expected-state entry SHOULD identify, as
applicable:

- State identity or structural path;
- State slot/entity identity;
- datatype;
- comparison operation;
- entity/state quantifier semantics needed to interpret the value;
- effective expected value or protected/redacted representation;
- source of that value, such as `publisher`, `publisher_profile`, or
  `organizational_input`;
- source/provenance reference when the value was not directly publisher-authored.

When a Rule has no materialized expected State (for example, a procedure-only
Manual Assessment), `expected_state` SHALL still be present as an empty
collection unless the final manual-result model defines an equivalent populated
representation. Absence of the field SHALL NOT be used to signal 'not used'.

For organization-defined expected values, the same expected-state entry format
SHALL be used. Organizational Input therefore changes the `source` and adds a
provenance reference; it does not introduce a separate hidden result surface.


## Rule result instances and fan-out

A Benchmark Result SHALL retain one policy-facing Rule Result record for each
effectively selected Rule. A Rule Result MAY contain one or more **result
instances** when the Rule's selected assessment method is intentionally
evaluated separately for multiple target instances or multiple independently
reported checks.

The Rule Result's top-level `outcome` is the aggregate policy outcome for the
Rule. Each result instance retains its own outcome and detailed Assessment
Result reference.

Illustrative shape:

    rule_result:
      rule_id: example-rule
      outcome: fail
      instances:
        - id: account:root
          kind: target_instance
          outcome: pass
          assessment_result_ref: assessment-result-1
        - id: account:example
          kind: target_instance
          outcome: fail
          assessment_result_ref: assessment-result-2

Result-instance identity SHALL be stable within the Benchmark Result and SHALL
preserve enough context to distinguish why multiple executions/results exist.
An instance MAY identify:

- a target/component instance;
- an independently reported check;
- both, when both dimensions are present.

A Rule with no fan-out SHOULD still expose the common Rule-result contract
without requiring consumers to reconstruct a legacy XCCDF multiple-result
model. Whether the final schema represents the ordinary execution as a single
entry in `instances` or retains direct common-case fields alongside an empty
`instances` collection remains a serialization decision; the semantic
requirement is that fan-out is explicit and does not create ambiguous duplicate
Rule identities.

The aggregate Rule outcome SHALL be deterministically derived from the
instance/check outcomes according to the selected Rule assessment method's
declared aggregation semantics. Aggregation SHALL NOT silently discard
`error`, `unknown`, `not_evaluated`, or `not_applicable`.

### XCCDF `multi-check` migration

For a nameless XCCDF `check-content-ref`:

- when `multi-check=false` (the default), the executed checks are combined
  into one Rule result using the source XCCDF aggregation semantics;
- when `multi-check=true`, each executed check SHALL remain separately
  identifiable in the migrated Rule Result's result instances.

The converter SHALL preserve which underlying check produced each instance and
the source aggregation behavior.

### XCCDF Rule `multiple` migration

For XCCDF Rule `multiple=true`, distinct target/component instances that were
reported separately SHALL remain separately identifiable as Rule result
instances.

`multiple` and `multi-check` are independent dimensions. If both apply, a
result instance SHALL preserve both the target-instance identity and the
executed-check identity needed to reconstruct the source result semantics.

For legacy `multiple=false` or `multi-check=false` behavior that combines
several component outcomes into one Rule outcome, migration SHALL preserve the
source aggregation semantics rather than treating the first or last result as
authoritative.

## 6. Deterministic message

Every Rule result SHOULD contain a concise deterministic human-readable
message suitable for logs, APIs, Splunk, Elastic, dashboards, and review tools.

The message SHALL be derived from the same authoritative result data as the
machine-readable outcome/failure reason.

For standard existence/cardinality patterns, conforming implementations SHOULD
generate semantically equivalent deterministic messages from the observed count
and expected state rather than requiring content authors to hand-author
scanner-specific prose.

Heuristic or AI-generated analysis SHALL NOT replace the authoritative
message.

## 7. Failure reason

Failed results SHOULD provide a machine-readable reason.

Core reason categories SHOULD include stable machine-readable identities for
at least:

- `unexpected_existence`;
- `required_item_missing`;
- `required_match_missing`;
- `value_mismatch`;
- `cardinality_mismatch`.

For an expected-absence condition, observing one or more prohibited matching
items SHOULD produce `unexpected_existence`.

For an expected-presence condition, observing zero required matching items
SHOULD produce `required_item_missing` unless the more specific
`required_match_missing` accurately describes the case.

## 8. Concrete evidence

When failure is established by a concrete violating item, at least one concrete
failing example SHALL be retained unless collection/evaluation failed before
one could be captured.

Evidence SHOULD identify what failed and why.

A missing required item or condition SHALL be represented as a missing
requirement, not as a fabricated collected object.

## 9. Evidence limits and short circuiting

Evidence-retention limits SHALL NOT be compliance thresholds.

A scanner MAY short-circuit once the logical result is known and required
evidence/characterization has been satisfied, provided short-circuiting cannot
change the result.

Results SHOULD distinguish:

- `logical_complete`;
- `population_complete`;
- `evidence_complete`.

If the full population was not evaluated, a total population failure count
SHALL be reported as unknown rather than inferred from observed failures.

## 10. Summary

A result package SHOULD provide precomputed aggregate counters so common
consumers are not required to scan every Rule result merely to construct a
summary.

Useful aggregates include:

- total/pass/fail/not-applicable/not-evaluated/error counts;
- failures by severity;
- automated/manual counts;
- failure-reason counts.

Publisher-specific projections MAY add aliases such as DISA CAT I/II/III
counts, but core SCAP-NG SHALL NOT require publisher-specific severity labels.

## 11. SIEM projection

A result exporter MAY project the normalized package into denormalized event
formats such as JSONL.

A SIEM projection MAY emit one scan-summary event followed by one independent
event per Rule result.

Consumer-specific denormalization SHALL NOT dictate the canonical result model.

## 12. Manual results

Manual Assessment default behavior and completed outcome semantics are defined
in `../assessment/manual-assessment.md`.

Manual results SHOULD distinguish factual finding/evidence details from general
reviewer comments.

A completed Manual Assessment Result SHALL identify the evaluator/respondent
who supplied the result and the time the result was completed. It SHALL also
identify the corresponding Assessment execution/request context so that the
response cannot be detached from the target/run in which it was made.

Manual results SHOULD support typed evaluator identity, display name,
organizational role, authentication/identity source, response source
(direct/imported/delegated), comments, and evidence references.

A later reviewer/approver SHALL be represented as a separate provenance event
and SHALL NOT replace the identity or timestamp of the original evaluator.

## Organizational Input result provenance

Results SHALL make every effective Organizational Input value that affected
evaluation reconstructable without requiring the original Input Set to remain
externally available forever.

For each consumed organization-resolved Parameter, results SHOULD record:

- Parameter identity;
- effective typed value, or a protected/redacted representation when required;
- value source (`organizational_input`, interactive, API/integration, or other
  standardized source);
- Organizational Input Set identity/version when a persisted set was used;
- supplier/source-system provenance;
- supplied timestamp;
- authorization status and available authorization reference;
- whether the value was redacted in the result.

Result provenance SHALL distinguish publisher-resolved Parameter values from
organization-resolved values. Supplying Organizational Input SHALL NOT make the
run appear Tailored.

If a required value is missing, the affected Assessment SHALL report
`not_evaluated` or the final standardized equivalent with structured reason
`missing_organizational_input` and the unresolved Parameter identity. It SHALL
NOT report an ordinary compliance failure or not-applicable result merely
because policy data was absent.

## Organizational Input provenance propagation

Organizational Input provenance SHALL be normalized at the run/Benchmark-result
level and referenced by lower-level results rather than copied in full into
every Assessment or Rule result.

The canonical propagation model is:

    Organizational Input source
        -> frozen effective policy snapshot
        -> Benchmark Result organizational-input registry
        -> Assessment Result consumed-input binding(s)
        -> Rule Result references Assessment Result
        -> optional SIEM/export denormalization

The Benchmark Result SHALL preserve the authoritative run-time snapshot of each
effective Organizational Input assertion used by the run, including its typed
value (or protected representation), organization, supplier, authority basis,
authorization information, scope, effective period, source system, and other
required provenance.

Each such effective assertion SHALL have a stable result-local identity, for
example `organizational_input_ref`, that is immutable within the result
package.

An Assessment Result that consumes Organizational Input SHALL identify each
consumed input slot and SHALL record:

- the Assessment input/State slot identity;
- the effective value used, or a protected/redacted representation;
- the corresponding Benchmark-result Organizational Input provenance reference;
- whether the completed State/value was materialized successfully;
- any validation/redaction status needed to interpret the binding.

The Assessment Result SHALL NOT need to duplicate the complete authority and
contact record when the referenced Benchmark Result is part of the same
canonical result package. It SHALL nevertheless retain enough local information
to identify which value affected that Assessment execution.

A Rule Result that was evaluated using Organizational Input SHALL expose the
effective organization-defined value(s) directly in that Rule Result so a human
or downstream consumer can see what expected policy state the Rule was evaluated
against without opening the detailed Assessment Result.

Each exposed Rule-level value SHALL include a stable reference to the canonical
Benchmark-result Organizational Input assertion. The Rule Result SHOULD include
a concise provenance summary such as organization, authority/authorization
reference, and effective period when useful, but it SHOULD NOT duplicate the
entire canonical provenance/contact record.

An exporter that emits standalone per-Rule or per-Assessment events MAY
denormalize the referenced Organizational Input value and provenance into each
event. Such denormalization SHALL preserve the canonical identities and SHALL
NOT create a second independent provenance truth.

This model permits compact canonical storage while allowing SIEM/Splunk/Elastic
events to be independently useful.

## Organizational Input result conformance

Result producers SHALL use standardized structured reasons when an
Organizational-Input-dependent Rule cannot be evaluated:

| Condition | Rule outcome | reason.code |
| --- | --- | --- |
| Scanner lacks Organizational Input capability | `not_evaluated` | `unsupported_organizational_input` |
| Scanner supports capability but required input is absent | `not_evaluated` | `missing_organizational_input` |
| Input is present but invalid | `not_evaluated` | `invalid_organizational_input` |
| Input is valid | normal evaluation | ordinary result/failure reason |

These states SHALL NOT be represented as `fail`, `not_applicable`, or generic
`error` merely because policy data was unavailable or unsupported.

The Benchmark Result SHALL identify whether the scanner advertises
Organizational Input capability. Rule Results SHALL continue to contain
`expected_state` even in the not-evaluated cases; unresolved slots MAY omit or
redact the value but SHALL retain enough structure/source information to show
what expected State could not be resolved.

Versioned result schemas SHOULD validate these standardized reason codes and
required result surfaces. Semantic validators SHALL additionally verify
cross-object constraints that JSON Schema cannot prove by itself, including
that `organizational_input_ref` resolves, Rule declarations agree with the
selected Assessment contract, and supplied values conform to capability-specific
State schemas.

## 13. Decisive outcome explanation

For nontrivial automated results, the result model SHOULD support a structured
decisive outcome explanation: the smallest evaluated expression subtree, or set
of subtrees, sufficient to justify the reported outcome.

This explanation SHALL represent logical/evidentiary cause, not speculate about
the operational or human reason a system became misconfigured.

For example:

- a failed `all` expression may require one decisive failed child;
- a failed `any` expression requires the failed alternatives necessary to
  prove that no acceptable alternative succeeded;
- a failed `none` expression may require one prohibited matching item;
- a branch/conditional result should distinguish branch-selection evidence from
  the decisive result inside the selected branch.

Additional independently useful failures MAY be retained as bounded diagnostics
without being confused with the minimal proof of the result.

Collection errors, unsupported capabilities, and applicability decisions SHALL
use structured reason/applicability data rather than pretending to be
compliance failures.

The final exact explanation serialization remains under design.


## 14. Assessment class and result interpretation

Results SHALL retain the effective Assessment class when it is needed to
interpret Boolean truth correctly.

A Boolean true result SHALL NOT be universally translated to `pass`.

At minimum:

- `compliance: true` represents satisfaction of the compliance condition;
- `vulnerability: true` represents presence of the vulnerability condition;
- `inventory: true` represents presence of the represented inventory
  condition;
- `patch` truth SHALL be interpreted according to the standardized patch
  class semantics;
- `miscellaneous` SHALL carry sufficient context to interpret its truth.

Applicability is invocation context, not an Assessment class. An applicability
decision SHOULD retain both `purpose: applicability` and the Assessment's
actual class.

`information` is reserved as a candidate future class and SHALL NOT be
treated as normative until approved through OVAL Board / SCAP-NG governance.

Assessment truth SHALL be interpreted at the Rule layer according to Assessment class.
At minimum, the following mappings are normative for Boolean outcomes:

| Assessment class | Assessment truth | Rule outcome |
| --- | --- | --- |
| compliance | true | pass |
| compliance | false | fail |
| vulnerability | true | fail |
| vulnerability | false | pass |

The `error`, `unknown`, `not_evaluated`, and `not_applicable` truth values SHALL
remain distinct and SHALL NOT be coerced through the Boolean mapping above.

A scanner SHALL NOT assume that Assessment `true` universally means Rule
`pass`; Assessment truth and policy-facing Rule outcome are separate result
layers.



## Assessment invocation and effective input identity

One Assessment Result represents exactly one Assessment invocation against one
target and one effective input/binding set.

If the same Assessment is evaluated more than once with different effective
input values, each evaluation SHALL have a distinct `execution_id` and a
distinct Assessment Result. Implementations SHALL NOT collapse such executions
merely because the Assessment logical identity/version is identical.

An automated Assessment Result SHOULD expose the effective named input bindings
that materially affected that invocation. Each binding SHOULD identify:

- the Assessment input name;
- the effective typed value or protected/redacted representation;
- the source of the value;
- a source/provenance reference when applicable.

A processor MAY additionally provide a deterministic binding-set identifier or
digest to simplify reuse and correlation. Such an identifier SHALL be derived
from the complete effective binding semantics needed to distinguish executions
and SHALL NOT substitute for the actual provenance required by the result
model.

### OVAL `variable_instance` migration

OVAL Results `variable_instance` differentiates repeated evaluations of a
Definition, Test, or extended Definition when different variable values are
supplied. Its default is instance `1`.

SCAP-NG/standalone Assessment migration SHALL map semantically distinct OVAL
variable instances to distinct Assessment invocations/results when the
different bindings can affect evaluation. The source `variable_instance`
number MAY be retained as migration provenance, but it SHALL NOT become the
native semantic identity of an Assessment.

Within one migrated invocation, Test/Assessment dependency references SHALL
resolve to the result instance associated with the same effective source
variable-binding context. A converter or result importer SHALL NOT join a Test
from one variable instance to Items, Variables, or an extended Definition
result from another instance.

## 15. Assessment Result file cardinality

A canonical SCAP-NG result package SHALL produce one Assessment Result artifact
for each Assessment invocation that contributes to the run.

For the common case in which a Benchmark-selected Assessment is invoked once
against one target with one effective binding, this is a 1:1 relationship:

- one authored Assessment file;
- one corresponding Assessment Result file for that invocation.

If the same Assessment is invoked more than once with materially different
bindings, targets, or execution contexts, each invocation SHALL have its own
execution identity and Assessment Result artifact.

Assessment Result artifacts SHALL be independently understandable. They SHALL
NOT require another Assessment Result file merely to resolve the Tests, Objects,
Items, Variable bindings, or evidence needed to explain their outcome. Shared
runtime collection work MAY be reused, but observations required by the
consuming Assessment Result SHALL be represented in that result according to
the final imported-Item rules.

Benchmark/Rule results SHOULD reference the corresponding Assessment Result
execution identity rather than embedding the complete detailed execution graph.

## 16. Failure counts and evidence maximums

Assessment Result and Benchmark/Rule Result reporting SHOULD use the same
terminology for bounded failure evidence.

The canonical terms are:

- `observed_failures`: failures actually encountered during evaluation;
- `actual_failures`: the total failure population when known, otherwise
  `unknown`;
- `maximum`: the configured maximum number of failure-evidence records to
  retain/return; this is an evidence maximum, **not** a compliance threshold;
- `returned`: failure-evidence records actually retained in the result;
- `truncated_population`: whether the returned failure evidence represents
  only part of the known/observed failing population;
- `logical_complete`: enough evaluation occurred to determine the Assessment
  truth/result;
- `population_complete`: the relevant population was evaluated completely;
- `evidence_complete`: all evidence required by the configured retention
  policy was retained;
- `stop_reason`: why evaluation stopped, including
  `evidence_maximum_reached` where appropriate.

A fully evaluated example may report:

    evaluation:
      logical_complete: true
      population_complete: true
      evidence_complete: true
      stop_reason: complete
      evaluated_items: 34

    summary:
      observed_failures: 3
      actual_failures: 3

    evidence:
      failures:
        maximum: 50
        returned: 3
        truncated_population: false

If evaluation is deliberately stopped after 20 failures because the configured
evidence maximum has been reached, the result may instead report:

    evaluation:
      logical_complete: true
      population_complete: false
      evidence_complete: false
      stop_reason: evidence_maximum_reached
      evaluated_items: 1847

    summary:
      observed_failures: 20
      actual_failures: unknown

    evidence:
      failures:
        maximum: 20
        returned: 20
        truncated_population: true

The word `threshold` SHOULD NOT be used for this evidence-retention setting,
because it may incorrectly imply that compliance truth changes when the value
is reached.


<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Source, Compilation, Packaging, and Integrity](../package/package-and-integrity.md) · [Contents](../README.md) · [Next: SCAP 1.4 Migration →](../migration/scap-1.4-migration.md)

<!-- spec-nav:end -->


## Signed Benchmark Result packages

SCAP-NG SHOULD make cryptographic signing of completed Benchmark Results simple
enough to be routinely implemented by scanners and enterprise assessment
pipelines.

The preferred baseline model is **one signature over the immutable result
package manifest**, not separate signatures embedded throughout every Rule,
Assessment Result, or evidence object.

A signed result package SHALL contain an integrity manifest that identifies the
authoritative Benchmark Result and every package member needed to interpret
that result, including referenced Assessment Results and retained evidence when
those are stored as separate members.

Each manifest entry SHALL include, at minimum:

- package-relative member identity/path;
- member type;
- cryptographic digest;
- content size SHOULD be included.

The manifest SHALL also identify the digest algorithm and the exact result
format/schema versions needed to interpret the package.

A signature SHALL bind the complete manifest representation. Therefore, changing
the Benchmark Result, a referenced Assessment Result, evidence, or another
integrity-bound member changes the manifest verification outcome without
requiring every nested object to carry its own signature.

Conceptually:

    result-package/
      manifest.json
      manifest.sig
      benchmark-result.json
      assessment-results/
        ...
      evidence/
        ...

The exact signature envelope/algorithm profile remains a security-profile
decision, but the core result model SHALL NOT depend on XML Signature.

### Signing and verification behavior

A conforming signed-result implementation SHALL provide deterministic answers
to at least:

1. Is the result package internally intact?
2. Does every integrity-bound member match the digest recorded in the signed
   manifest?
3. Is the manifest signature cryptographically valid?
4. What signer/key/certificate identity produced the signature?
5. What trust decision, if any, was made for that signer?

Cryptographic validity and signer trust SHALL be reported separately. A valid
signature from an untrusted or unknown key SHALL NOT be described as a trusted
result.

Signature verification SHALL NOT change Assessment truth or Rule outcomes.
Signature/trust status is provenance/integrity metadata about the result
artifact.

### Canonicalization and implementation simplicity

The signature design SHOULD minimize canonicalization complexity.

The preferred implementation pattern is:

1. serialize each result member in its specified scanner-facing deterministic
   form;
2. hash the exact member bytes;
3. create a deterministic manifest containing those hashes;
4. sign the exact canonical manifest bytes;
5. verify by reproducing the member hashes and verifying the signature over the
   manifest.

A verifier SHALL NOT need to reconstruct the original Benchmark, replay the
scan, or canonicalize arbitrary semantically equivalent JSON merely to verify
result integrity.

### Signer metadata and enterprise use

A signed result SHOULD identify enough signer metadata to support both local
scanner keys and enterprise signing services. This MAY include:

- signer/key identifier;
- certificate chain or reference, when certificate-based trust is used;
- signing time when supplied by an authenticated signing process;
- scanner/product identity associated with result production;
- organization or service identity when an enterprise signer is used.

The standard SHOULD define a small mandatory interoperable signing profile and
permit additional enterprise trust profiles without changing the result data
model.

### Unsigned results

An unsigned Benchmark Result remains structurally valid unless a deployment or
conformance profile requires signing. Its signature status SHALL be explicit;
absence of a signature SHALL NOT be confused with verification failure.

Organizations MAY require signed results as local policy.

### Legacy XML signatures

Legacy XCCDF/OVAL XML signatures, when encountered during migration/import, are
source-integrity/provenance information. They SHALL NOT require SCAP-NG result
packages to reproduce XML Signature structures.

A migration tool MAY verify and record the status of a legacy source signature.
The authoritative integrity mechanism for a native completed SCAP-NG result
package is the SCAP-NG result-package signature defined above.

