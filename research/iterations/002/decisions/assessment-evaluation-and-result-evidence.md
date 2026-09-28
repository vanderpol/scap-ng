# Assessment Evaluation and Result Evidence

**Status:** working design decision  
**Iteration:** 002  
**Scope:** short-circuit evaluation, concise result messages, aggregate counts, and bounded concrete evidence

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Core principle

SCAP-NG SHALL separate:

1. **evaluation semantics** — what must be examined to determine truth;
2. **evaluation completeness** — whether enough of the population was examined
   to prove the result;
3. **result characterization** — aggregate counts and summary information;
4. **retained evidence** — bounded concrete examples included in results; and
5. **analysis** — optional explanatory text that does not determine truth.

These concepts SHALL NOT be conflated.

## Compliance semantics versus evidence maximum

The number of retained or characterized failure examples SHALL NOT be interpreted
as the number of failures required for the Assessment to fail.

For an assertion such as "all matching files must be owned by root", the first
real violation establishes a fail result.

A separate evidence maximum MAY request additional failing examples for human
diagnosis and result reporting.

For example:

    assert:
      all:
        ...

    results:
      failure_examples:
        maximum: 20

The value `20` above means "attempt to retain up to 20 useful failure
examples." It does NOT mean "fail only after 20 failures."

A native syntax SHOULD avoid names such as `stop_after_failures` when they can
be misread as a compliance threshold.

If the policy itself legitimately permits a non-zero number or percentage of
violations, that tolerance SHALL be expressed explicitly in the assertion
semantics, not in evidence-retention settings.

## Short-circuit evaluation

A scanner MAY stop evaluating additional items once the logical result is
decisively known and any requested characterization/evidence maximum has been
met.

For an `all` assertion, one failure can prove the assertion false.

For an `any` assertion, one passing item can prove the assertion true.

For a `none` assertion, one forbidden match can prove the assertion false.

A scanner SHALL NOT short-circuit in a way that could change the logical result.

A scanner MAY impose an operational safety limit tighter than the content
author's requested characterization limit, provided the logical result remains
valid and the result records that evaluation was truncated.

## Explicit author controls

Hidden defaults are prohibited.

If an Assessment requests a number of failure examples for characterization,
that number SHALL be explicit in source.

Illustrative source:

    results:
      failure_examples:
        maximum: 20

The exact final syntax remains under design.

## Completeness metadata

Results SHOULD distinguish at least:

- `logical_complete`: enough evidence was examined to prove the result;
- `population_complete`: the full in-scope population was examined;
- `evidence_complete`: all relevant item-level evidence was retained.

Example:

    result: fail
    logical_complete: true
    population_complete: false
    evidence_complete: false

## Observed versus actual failure counts

SCAP-NG SHALL distinguish the number of violations actually encountered from
the total number of violations in the complete in-scope population.

`observed_failures` is the exact number of failing items encountered before
evaluation ended.

`actual_failures` is the exact total number of failing items in the complete
population. If the population was not fully evaluated, `actual_failures`
SHALL be `unknown`.

Example after short-circuiting on an evidence maximum:

    summary:
      observed_failures: 20
      actual_failures: unknown

Example after complete population evaluation:

    summary:
      observed_failures: 19
      actual_failures: 19

The result SHALL NOT imply that the evidence maximum is a pass/fail threshold.
If even one observed violation is sufficient to prove the assertion false, the
result is `fail` regardless of whether the requested evidence maximum was
reached.

## Concise deterministic result message

Every Rule result SHOULD contain a concise, deterministic human-readable
message suitable for:

- SIEM ingestion;
- Splunk / Elastic indexing;
- dashboards;
- logs;
- STIG Viewer comments;
- API clients.

The specification SHOULD define deterministic message-generation requirements
for standard assertion/result patterns so scanner implementations do not invent
incompatible interpretations.

Example for short-circuited failure:

    message: >
      FAIL: 20 files were observed with incorrect ownership; total failures are
      unknown because evaluation stopped after the requested evidence sample was
      collected.

Example when the complete population contains 19 failures:

    message: >
      FAIL: 19 files were found with incorrect ownership.

The message SHALL be derived from authoritative Assessment/result data.

An AI-generated or heuristic explanation SHALL NOT replace the authoritative
result message.


## Failure reason semantics

A failed compliance result SHOULD include a concise machine-readable failure
reason in addition to the human-readable `message`.

Existence and non-existence failures are common enough to be first-class reason
types rather than being represented only as free-form text.

Illustrative reason kinds include:

- `unexpected_existence` — one or more prohibited items exist;
- `required_item_missing` — an item required to exist was not found;
- `required_match_missing` — collected data exists, but no item satisfies a
  required condition;
- `value_mismatch` — a collected value does not satisfy the expected value;
- `cardinality_mismatch` — the observed population does not satisfy an
  explicit count/cardinality requirement.

Example: prohibited package exists:

    outcome: fail
    message: >
      FAIL: The sendmail package is installed; this requirement requires it to
      be absent.

    failure_reason:
      kind: unexpected_existence
      source: sendmail_packages
      observed_items: 1
      expected_existence: none

Example: required sysctl item missing:

    outcome: fail
    message: >
      FAIL: No net.ipv4.conf.default.send_redirects item was found; at least
      one is required.

    failure_reason:
      kind: required_item_missing
      source: redirect_default
      observed_items: 0
      expected_existence: at_least_one

Example: required audit-rule combination missing:

    outcome: fail
    message: >
      FAIL: Required audit-rule combination fsetxattr / b64 / root was not
      found.

    failure_reason:
      kind: required_match_missing
      expected:
        syscall: fsetxattr
        architecture: b64
        identity_class: root

The `message` remains the primary concise human explanation. The
`failure_reason` object exists so downstream systems such as Splunk and
Elastic can categorize, filter, and aggregate failures without parsing prose.

A scanner SHALL derive the human-readable message and structured reason from
the same authoritative Assessment outcome so they cannot contradict one
another.

## Concrete failure evidence

An item-level failure SHALL NOT be represented only by an aggregate statement
such as:

    "50 files failed ownership."

When a result is `fail` because one or more concrete collected items violate
an assertion, the result SHALL retain at least one concrete failing example,
unless the collection/evaluation failed before any failing item could be
captured.

The retained item SHOULD contain the minimum fields needed to identify:

1. **what object failed**; and
2. **why it failed**.

For example:

    evidence:
      failures:
        returned: 3
        truncated: true
        items:
          - path: /opt/app/file1
            actual:
              owner: appuser
            expected:
              owner: root
            reason: owner does not equal required value

          - path: /opt/app/file2
            actual:
              owner: nobody
            expected:
              owner: root
            reason: owner does not equal required value

          - path: /opt/app/file3
            actual:
              owner: 1001
            expected:
              owner: root
            reason: owner does not equal required value

The exact result serialization remains under design.

## Evidence maximum

Assessment content SHOULD be able to request:

- which fields are useful to retain as evidence;
- how many passing examples, if any, are useful;
- how many failing examples SHOULD be retained for diagnosis.

The scanner/runtime MAY enforce a stricter result-size or resource safety cap.

If the scanner reduces the requested evidence maximum, it SHALL report the
effective cap and truncation reason.

A failure caused by an item-level assertion SHOULD normally retain multiple
examples when available, not merely one, so operators can distinguish an
isolated defect from a repeated pattern without requiring full population
retention.

## Aggregate information

When available without requiring further evaluation, results SHOULD include
aggregate counters such as:

- evaluated items;
- passing items;
- observed failing items;
- actual failing items, when known;
- retained evidence items.

Counts SHALL distinguish observations from complete-population totals.

## Structured evidence versus human-readable explanation

Structured evidence and a one-line result message serve different purposes and
both are valuable.

The result message explains the outcome concisely.

Structured evidence supports troubleshooting, auditability, machine analysis,
and proof.

One SHALL NOT be considered a substitute for the other.

## Optional result analysis

SCAP-NG MAY support an additional non-authoritative analysis field.

Example:

    analysis: >
      Most retained failures are under /opt/vendor/cache and appear to share
      permissions inherited from the application installer.

Analysis MAY be produced by:

- deterministic scanner logic;
- a plugin;
- a post-processing component;
- a future AI-assisted analyzer.

Analysis SHALL NOT determine or modify the authoritative compliance result.

Results SHOULD retain provenance describing which component produced analysis.

## Large-population example

For an assertion that all matching files must be owned by root:

    result: fail
    message: >
      FAIL: 20 files were observed with incorrect ownership; total failures are
      unknown because evaluation stopped after the requested evidence sample
      was collected.

    evaluation:
      logical_complete: true
      population_complete: false
      stop_reason: evidence_maximum_reached
      evaluated: 1847

    summary:
      observed_failures: 20
      actual_failures: unknown

    evidence:
      failures:
        returned: 20
        truncated: true
        items:
          ...

This permits fast decisive failure while preserving concrete proof and honest
reporting about incomplete population characterization.

## Design consequence

SCAP-NG SHALL NOT require scanners to retain all collected system data merely
because it participated in evaluation.

Assessment authors SHOULD be able to state the minimum useful evidence contract,
while scanner/runtime policy retains authority to enforce resource safety
limits.

Evidence maximums SHALL NOT be used to encode compliance thresholds.

This design is intended to support both high-volume compliance scanning and
concise operational integrations such as SCC -> Splunk / Elastic.
