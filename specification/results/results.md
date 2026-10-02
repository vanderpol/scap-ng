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

### Candidate simplification: canonical results versus OVAL result directives

**Board decision pending.** OVAL Results currently permits per-result/per-class
`reported` controls, `thin` versus `full` result content, and
`include_source_definitions`.

The current SCAP-NG design preference is to simplify this to one stable,
self-describing canonical logical result contract and treat reduced-detail or
filtered views as explicit projections/exports. Under that candidate design, a
canonical result would not disappear merely because it is pass/false, not
applicable, unknown, or another outcome selected for suppression by a legacy
directive.

A projection/export could then reduce detail, filter outcome classes, omit
embedded source content, or denormalize records for transport/consumer needs.
If this approach is adopted, such a projection should:

- be identified as a projection rather than the canonical signed result;
- not change the underlying technical outcome;
- identify the canonical result/package from which it was derived;
- apply deterministic, documented selection/redaction rules;
- not be required in order to interpret the canonical result package.

Migration of an OVAL Results document should preserve its source directives as
legacy/result provenance describing why that source document contains or omits
particular data.

This simplification is **not yet normative**. The OVAL Board should explicitly
decide whether SCAP-NG/next-generation OVAL retains, revises, or drops:

- per-result/per-class `reported` suppression;
- `thin` versus `full` result content;
- `include_source_definitions` as a result-shaping control.

The argument for dropping them is reduced scanner/result-consumer complexity:
one canonical result model plus ordinary projections can provide the same
transport/reporting flexibility without making the core result schema vary by
directive. The argument for retaining them is compatibility with established
OVAL result-generation workflows and the ability to reduce result size at the
source. Both positions should be reviewed before schema freeze.

## 3. Technical outcome versus reporting/scoring disposition

Assessment evaluation SHALL preserve technical truth independently from
Rule-level reporting and scoring policy.

The native Assessment outcome domain SHALL NOT use `informational` as a
replacement for an otherwise determinable technical result. When an Assessment
can determine true/false (and therefore a compliance Rule can determine
pass/fail), that technical outcome remains available even if policy says the
Rule is excluded from scoring or primarily presented for information.

A Rule Result MAY carry orthogonal disposition fields such as:

- whether it contributes to a score;
- whether it is informational/reporting-only;
- why execution was intentionally suppressed;
- legacy projection metadata needed to reproduce an imported format.

This separation prevents scoring policy from destroying technical evidence.

### XCCDF Rule role migration

For legacy XCCDF 1.2 `role`:

- **full** — execute normally; the Rule is scoring-eligible according to the
  selected scoring model.
- **unscored** — execute the selected Assessment normally and preserve its
  technical result. Mark the Rule Result as excluded from scoring and with an
  informational/reporting disposition. A legacy XCCDF projection MAY emit
  XCCDF's required `informational` Rule status, but canonical NG results SHALL
  retain the underlying technical outcome.
- **unchecked** — do not execute the Rule's Assessment. Emit a Rule Result with
  `not_evaluated` (or the final schema's equivalent technical non-execution
  outcome), a stable reason such as `policy_unchecked`, and scoring excluded.

Legacy `role` therefore SHALL NOT survive as a native XCCDF-style
Assessment attribute that forces Assessment truth. Its effective source
semantics are mapped into explicit Rule policy/result disposition during
migration.

Organizational Input replaces only the subset of historical `unscored` usage
whose real limitation was an organization-specific expected policy value. When
supplying that input makes compliance objectively determinable, the migrated
Rule SHOULD use an ordinary compliance Assessment with an explicit
Organizational Input binding and preserve the resulting technical pass/fail
outcome.

Missing or invalid required Organizational Input SHALL follow the
Organizational Input evaluation contract (for example `not_evaluated` with a
specific input reason); it SHALL NOT be converted to `informational` merely
because older content used `unscored` as a workaround.

Organizational Input does **not** replace every historical use of `role`.
Content that is genuinely intended to be reporting-only even when all required
policy inputs are available still needs an explicit Rule reporting/scoring
disposition (or a future standardized informational Assessment class, if that
candidate is adopted). Likewise, legacy `unchecked` remains a policy decision
not to execute the Assessment and maps to an explicit non-execution result.

Owner working decision, 2026-10-01: retain `role` on the Rule for now so
informational/reporting-only content remains expressible. It is policy metadata,
not an Assessment truth value. The current Rule schema and converted source
retain this control; the migration helper preserves technical truth separately.
An assessment-native informational model remains deferred research and SHALL
NOT be treated as permission to remove the working Rule control.

The earlier proposed replacement of the single `role` switch remains a future
design candidate that would represent its distinct concerns separately:

- Assessment technical truth;
- Organizational Input dependencies;
- Rule scoring eligibility;
- Rule reporting disposition;
- explicit policy-driven non-execution.

## 4. Target identity

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

## 5. Target product inventory

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

For the current ownership audit and architectural guard rationale, see [Result schema scope audit](result-schema-scope-audit.md).

## 6. Rule result self-description

A Rule Result SHOULD be compact, policy-facing, and independently useful for
ordinary reporting without becoming a second copy of the Assessment execution
record.

A Rule Result SHOULD contain, as applicable:

- stable Rule identity;
- important publisher identifiers;
- title and severity;
- effective scoring weight and reporting/scoring disposition when defined;
- policy-facing outcome;
- concise deterministic message;
- structured Rule-level reason;
- identity/version of the effective selected Assessment;
- effective check selector;
- effective Parameters that are policy inputs to the Rule;
- Rule applicability disposition plus references to the applicability
  Assessment Results that established it;
- one or more result instances containing the policy-facing instance outcome
  and a reference to the corresponding detailed Assessment Result;
- optional references to decisive evidence members.

A Rule Result SHALL NOT duplicate the detailed Assessment execution graph.
In particular, collected Items, observed State/entity values, Variable results,
Test/Object/State/Entity evaluation detail, Assessment completeness counters,
bounded-evidence accounting, and consumed Organizational Input execution detail
belong to the referenced Assessment Result.

The full Rule discussion, remediation, Manual Assessment procedure, and
Assessment implementation SHOULD NOT automatically be copied into every Rule
Result.

### Expected and observed values

Expected and observed technical values are Assessment execution data.

For automated evaluation, the authoritative expected values SHALL be retained
in the detailed Assessment Result through the preserved Test/State/Entity and
effective input-binding data. Authoritative observations SHALL be retained
through collected Items and the corresponding State/Entity/Test results.

A Rule Result MAY reference the Assessment Result or a bounded evidence member
needed for ordinary reporting, but SHALL NOT embed an independent
`expected_state`, `observed_state`, or equivalent technical mini-graph.
This avoids creating two separately evolving sources of truth for the same
evaluation.

Organizational Input values that affect execution SHALL be retained in the
Assessment Result's effective/consumed input bindings and in the Benchmark
Result's effective-policy provenance as appropriate. The Rule Result MAY
identify the relevant policy Parameter or reason, but SHALL NOT duplicate the
full Organizational Input execution/provenance record.

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

A Rule with no fan-out SHALL still use the same Rule-result shape as a Rule
with fan-out: exactly one policy-facing Rule Result containing a non-empty
`instances` collection. The common single-invocation case therefore has one
instance rather than a separate direct-result representation.

This avoids two equivalent canonical serializations for the same semantics.
Consumers can always find invocation/check/target-specific results in
`instances`, while the Rule Result's top-level `outcome` remains the
deterministic aggregate policy outcome.

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

### Assessment invocation identity and legacy OVAL `variable_instance`

One authored Assessment MAY be evaluated more than once within a run when its
effective runtime bindings differ. Each such execution SHALL have a distinct
**Assessment invocation identity** in results.

An Assessment invocation SHALL bind together:

- the authored Assessment identity/version;
- the effective Variable/Parameter/input bindings used for that execution;
- the target/component instance when applicable;
- the resulting Assessment/Test execution graph.

Two executions SHALL NOT be collapsed merely because they reference the same
authored Assessment or Test IDs. Conversely, scanners SHOULD reuse one invocation
result when the same Assessment is intentionally shared under the same effective
binding context and target instance.

The invocation identifier is a runtime/result identity, not an authored content
field. Its serialized spelling remains a schema decision (for example,
`assessment_invocation_id` or `execution_id`), but it SHALL be stable and
unique within the canonical result package.

For OVAL migration, `variable_instance` is a legacy discriminator for repeated
Definition/Test evaluations under different variable bindings. Migration SHALL
map each distinct legacy variable instance to a distinct Assessment invocation
when those instances represent distinct effective bindings. The legacy integer
MAY be retained as migration provenance, but native SCAP-NG source SHALL NOT
require authors to assign or manage `variable_instance` numbers.

Detailed Assessment results SHALL preserve the effective typed bindings needed
to explain why two invocations differ. A result consumer SHALL be able to
distinguish separate executions without relying on array position, first/last
ordering, or reconstructed legacy XML identity.

## 7. Deterministic message

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

## 8. Failure reason

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

## 9. Concrete evidence

When failure is established by a concrete violating item, at least one concrete
failing example SHALL be retained unless collection/evaluation failed before
one could be captured.

Evidence SHOULD identify what failed and why.

A missing required item or condition SHALL be represented as a missing
requirement, not as a fabricated collected object.

## 10. Evidence limits and short circuiting

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

## 11. Summary

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

## 12. SIEM projection

A result exporter MAY project the normalized package into denormalized event
formats such as JSONL.

A SIEM projection SHOULD emit one scan-summary event followed by one independent
event per Rule result. Each Rule event SHOULD be independently useful after
indexing and SHOULD therefore repeat the minimum run, target, Benchmark, Profile,
and Rule context needed for ordinary search and dashboard use.

At minimum, a standalone Rule event SHOULD expose:

- event type and result-schema version;
- run identity and relevant timestamps;
- scanner identity/version;
- stable target reference plus useful target identifiers/hostname;
- Benchmark identity/version and executed package digest when available;
- effective Profile and Tailoring identity when applicable;
- Rule identity, title, severity, effective weight, outcome, and deterministic message;
- structured reason, expected state, and decisive observed state when applicable;
- effective check selector, relevant Parameters, and applicability disposition;
- selected Assessment identity/version and Rule-result instance(s);
- references to detailed Assessment Result/evidence rather than embedding the
  complete detailed execution graph;
- source signed-result/manifest identity or verification status when the
  projection derives from a signed canonical result.

A scan-summary event SHOULD expose the run identity, target set, Benchmark
result references, aggregate counters, and source signature/verification status
needed to correlate the following Rule events.

For a fixed canonical input and projection version, JSONL generation SHOULD be
deterministic. Event ordering SHOULD follow canonical Benchmark-result ordering
and Rule-result ordering unless an explicitly identified projection profile
defines another deterministic order.

A projection SHALL NOT change Assessment truth, Rule outcome, evidence
completeness, or provenance. It SHALL NOT become a second canonical result
source. When a Rule event references a detailed Assessment Result, that
reference SHALL continue to identify the authoritative detailed result.

Consumer-specific denormalization SHALL NOT dictate the canonical result model.

## 13. Manual results

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

## 14. Decisive outcome explanation

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


## 15. Assessment class and result interpretation

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

Assessment truth SHALL be interpreted at the Rule layer using the consuming
Rule's explicit policy interpretation. Assessment class defines what technical
truth means; it does not by itself dictate the policy-facing Rule outcome.

For ordinary compliance Assessments, the default interpretation is
`true -> pass` and `false -> fail`. For vulnerability, patch, inventory,
miscellaneous, or other non-compliance classes used directly by a pass/fail
Rule, the Rule binding SHALL explicitly define how technical truth maps to the
policy outcome unless a future standards profile defines an unambiguous default.

A scanner SHALL NOT infer hidden class-name inversions such as
`vulnerability: true -> fail` or `patch: true -> pass` merely from the
Assessment class name. Detailed results SHALL preserve both the technical
Assessment outcome and the effective Rule interpretation used.

The `error`, `unknown`, `not_evaluated`, and `not_applicable` truth values SHALL
remain distinct and SHALL NOT be coerced through Boolean policy mappings.

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

## 16. Assessment Result file cardinality

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

### Detailed result normalization and evidence placement

The canonical result package SHALL be normalized across the scan, Benchmark,
Rule, and Assessment layers, but one Assessment Result SHALL remain
self-contained for the logical evaluation data needed to understand that
Assessment invocation.

Within an Assessment Result, Test Results, Object collection results, collected
Items, Variable Results, State Results, and Entity Results MAY be represented as
normalized arrays keyed by stable result-local identities and referenced from
one another. Implementations SHALL NOT require a consumer to retrieve a
different Assessment Result merely to resolve the logical Test/Object/Item/
Variable graph for the current invocation.

Collected Items that materially participate in the Assessment's logical result
or decisive explanation SHALL be represented in that Assessment Result. Large
auxiliary evidence such as complete command output, packet captures, screenshots,
or other bulky artifacts MAY be stored as separate integrity-bound result-package
members referenced by stable identity and digest. Moving such auxiliary evidence
out of line SHALL NOT remove the typed observations needed to interpret the
Assessment result.

A separate duplicate "debug tree" is not mandatory when the preserved
Test/Item/State/Entity graph already provides enough structured information to
reconstruct and explain the outcome. For a nontrivial automated result, the
Assessment Result SHALL retain sufficient structured intermediate results to
explain the final outcome. A compact `decisive_expression` or equivalent
minimal-proof projection SHOULD be emitted when useful, but it SHALL be derived
from the authoritative evaluation graph rather than becoming a second source of
truth.

### Typed scalar, multi-valued, and record results

Result values SHALL carry explicit datatypes.

A single scalar value is represented as one typed value. A multi-valued entity
or Variable is represented as an ordered or unordered collection of typed values
according to the semantics of the producing capability; it SHALL NOT be hidden
inside an untyped scalar container.

A record value SHALL expose a structured set of named record fields. Each record
field SHALL itself carry typed value information, and a record field MAY contain
multiple typed values when the source capability permits repeated fields.

For OVAL-compatible migration, Variables SHALL NOT be record-typed. Record
structures are retained on collected Item/entity data. This preserves the OVAL
record constraint while still allowing record-producing capabilities such as
WMI57/cmdlet-style collection to retain their observed structure.

## 17. Failure counts and evidence maximums

Assessment Result reporting SHOULD use the canonical terminology below for bounded failure evidence. Benchmark and Rule Results MAY reference that evidence but SHALL NOT duplicate the detailed bounded-evidence accounting.

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
