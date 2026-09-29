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
- Tailoring and Organizational Input provenance where relevant.

The full Rule discussion, remediation, Manual Assessment procedure, and
Assessment implementation SHOULD NOT automatically be copied into every Rule
result.

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
