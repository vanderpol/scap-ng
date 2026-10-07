# SCAP-NG examples

This page is a short feature tour of SCAP-NG. Each section explains the practical
difference from SCAP 1.4 and shows a small representative example. Full files and
the complete review build are linked when more detail is useful.

> **Status:** SCAP-NG 0.3.0 is pre-alpha. Established model features and pending
> 0.3 modernization candidates are labeled separately. An example does not become
> normative merely because it validates or appears on this page.

## Benchmark → Rule → Assessment

**SCAP 1.4:** Policy lives in XCCDF while automated checks commonly live in
separate OVAL content connected through check-system, href, names, and legacy IDs.

**SCAP-NG:** A Benchmark contains Rules, and each Rule directly names its available
Assessments. Policy text stays with the Rule; technical evaluation stays with the
Assessment.

```yaml
rule:
  id: SV-257923
  title: RHEL 9 library directories must be group-owned correctly.
  assessment_choices:
    automated:
      assessment: ../assessments/automated/SV-257923.automated.yaml
    manual:
      assessment: ../assessments/manual/SV-257923.manual.yaml
  default_assessment_choice: automated
```

This keeps the policy requirement readable without embedding or duplicating the
technical check.

## Automated Assessments

**SCAP 1.4:** OVAL Definitions, Tests, Objects, States, and Variables are usually
separate graph nodes that must be followed by ID to understand one check.

**SCAP-NG:** Automated Assessments retain the useful OVAL concepts and six-state
truth model, but use meaningful names and a compact authoring structure.

```yaml
assessment:
  id: SV-257923.automated
  mode: automated
  class: compliance
  purpose: assessment

  tests:
    library-directory-owner:
      capability: unix.file
      object: ...
      states: ...

  evaluate:
    test: library-directory-owner
```

The goal is not to hide evaluation semantics; it is to remove serialization
indirection that does not help the author.

## Explicit evaluation logic

**SCAP 1.4:** OVAL `criteria` can express powerful Boolean decision trees, but the
logic is often separated from the Tests it references.

**SCAP-NG:** `evaluate` keeps multi-Test composition explicit and uses meaningful
Test names. Genuine decision trees remain visible rather than being hidden in
procedural code.

```yaml
evaluate:
  all:
    - test: zone-is-ad-integrated
    - test: zone-is-dnssec-signed
    - test: zone-has-rrsig
```

Whether a one-Test `evaluate` root should remain mandatory is still being reviewed
in [#167](https://github.com/vanderpol/scap-ng/issues/167).

## Conditional evaluation

**SCAP 1.4:** Environment-dependent logic is commonly represented through nested
OVAL criteria and guard Tests, so intentionally conditional authoring may be
difficult to recognize at a glance.

**SCAP-NG:** Explicit `if/then/else` evaluation is already part of the frozen
0.2 baseline. It lets native content state an intentional conditional directly
while retaining defined six-state outcomes.

```yaml
evaluate:
  if:
    test: server-is-domain-controller
  then:
    test: domain-controller-permissions
  else:
    test: member-server-permissions
```

This does **not** mean arbitrary SCAP 1.4 Boolean graphs can be automatically
rewritten as procedural branches; the production research found counterexamples.
The 0.3 review in [#173](https://github.com/vanderpol/scap-ng/issues/173) is
whether the inherited conditional form should remain unchanged or be simplified,
not whether conditionals should be introduced.

## Manual Assessments

**SCAP 1.4:** Manual STIG procedures are commonly carried as XCCDF Check Text and
may require separate product-specific workflows to record the human determination.

**SCAP-NG:** Manual checks are first-class Assessments using the same
Benchmark → Rule → Assessment model as automated checks.

```yaml
assessment:
  id: SV-257851.manual
  mode: manual
  class: compliance
  procedure: Verify /home is mounted with the nosuid option ...
  response:
    type: compliance
    choices:
      - value: pass
        outcome: true
      - value: fail
        outcome: false
```

Manual results preserve who made the determination, when it was made, and the
supporting evidence. See the
[0.3 manual Assessment Result](0.3.0/results/manual-assessment-result.json).

## Explicit applicability

**SCAP 1.4:** Applicability may be spread across XCCDF platform references, CPE
dictionaries, and check content.

**SCAP-NG:** Applicability is an explicit technical determination. Inventory facts
such as CPE may be captured, but a product identifier alone does not silently
decide applicability.

```yaml
platform:
  id: product.rhel_9
  applicability:
    operator: any
    conditions:
      - rhel-9-platform-assessment
      - compatible-rhel-9-platform-assessment
```

## Organizational Input

**SCAP 1.4:** Organization-specific expected values can involve XCCDF Values,
Tailoring, external OVAL variables, or scanner-specific interaction.

**SCAP-NG:** Organizational Input supplies typed expected values with provenance.
It may fill an allowed input slot, but it does not rewrite Tests or inject commands.

```yaml
organizational_input:
  id: site-time-source
  values:
    approved_time_source:
      value: time.example.mil
      provenance:
        source: organization-policy
```

Instance-targeting beyond explicit Assessment inputs is still under review in
[#175](https://github.com/vanderpol/scap-ng/issues/175).

## Profiles and Tailoring

**SCAP 1.4:** Profile inheritance and selection can require resolving Benchmark,
Group, Rule, Profile, `select`, and refinement behavior together.

**SCAP-NG:** The Benchmark exposes an explicit default selection. Publisher
Profiles remain compact by recording deviations, while external Tailoring records
the organization's policy choices separately.

```yaml
default_selection: true
profiles:
  - id: CAT_I_Only
    disabled_rules:
      - SV-257778
      - SV-257779
```

## Compact Benchmark and Rule Results

**SCAP 1.4:** ARF/XCCDF/OVAL result layers can require substantial correlation to
answer basic questions such as how many Rules failed and why one Rule failed.

**SCAP-NG:** Benchmark Results are deliberately policy-facing: concise counters,
Rule outcomes, a human-readable message/reason, and a reference to the detailed
Assessment Result.

```json
{
  "summary": {
    "total": 2,
    "pass": 0,
    "fail": 2,
    "not_applicable": 0,
    "not_evaluated": 0,
    "error": 0,
    "unknown": 0
  },
  "rule_results": [
    {
      "rule_id": "rule-file-owner",
      "outcome": "fail",
      "message": "Observed UID 1001; expected UID 0.",
      "reason": {"code": "value_mismatch"},
      "instances": [{
        "assessment_result_ref": "example-file-owner-1"
      }]
    }
  ]
}
```

Full example: [0.3 Benchmark Result](0.3.0/results/benchmark-result.json).

## Assessment Results that explain the root cause

**SCAP 1.4:** Detailed OVAL Results/System Characteristics can preserve the
technical data, but finding the decisive Test, State, Item, and comparison often
requires traversing several ID-based structures.

**SCAP-NG:** The detailed Assessment Result keeps technical truth separate from
policy pass/fail and records the decisive comparison directly.

```json
{
  "outcome": "false",
  "logical_complete": true,
  "population_complete": true,
  "evidence_complete": true,
  "tests": [{
    "id": "file-owner-is-root",
    "outcome": "false",
    "reason": {
      "code": "value_mismatch",
      "message": "The collected file owner did not match the required owner."
    }
  }]
}
```

Full example: [0.3 automated Assessment Result](0.3.0/results/assessment-result.json).

## Bounded evidence without hiding completeness

**SCAP 1.4:** Large System Characteristics and detailed results can become very
large when a check examines thousands or millions of Items.

**SCAP-NG:** Content/results may bound retained evidence, but the result explicitly
states whether the logical answer, observed population, and retained evidence are
complete.

```json
{
  "logical_complete": true,
  "population_complete": false,
  "evidence_complete": false,
  "evidence_summary": {
    "observed_failures": 20,
    "actual_failures": "unknown",
    "maximum": 20,
    "returned": 2,
    "truncated_population": true,
    "stop_reason": "evidence_maximum_reached"
  }
}
```

Full example:
[0.3 bounded-evidence Assessment Result](0.3.0/results/assessment-result-bounded-evidence.json).

## Manual result attribution

**SCAP 1.4:** A final result can record status without providing a uniform
Assessment-level contract for the human actor and supporting evidence.

**SCAP-NG:** A completed Manual Assessment Result records the technical outcome
along with assessor identity, time, comments, and evidence references.

```json
{
  "mode": "manual",
  "outcome": "false",
  "manual_response": {
    "completed_at": "2026-10-07T16:04:00Z",
    "response_source": "direct",
    "evaluator": {
      "display_name": "Example Assessor",
      "organization": "Example Organization"
    },
    "evidence_refs": ["evidence-home-mount-1"]
  }
}
```

Full example:
[0.3 Manual Assessment Result](0.3.0/results/manual-assessment-result.json).

## Normalized Scan, Benchmark, and Assessment results

**SCAP 1.4:** ARF commonly packages several result layers into one XML document,
which can make reuse, streaming, indexing, and selective retrieval awkward.

**SCAP-NG:** Scan, Benchmark, and Assessment Results are independently addressable.
The Scan Result indexes targets and result members without duplicating the
detailed Assessment graph.

```json
{
  "benchmark_results": [{
    "benchmark_result_ref": "benchmark-result.json",
    "target_ref": "target-1"
  }],
  "assessment_result_refs": [
    "assessment-result.json",
    "manual-assessment-result.json"
  ]
}
```

Full example: [0.3 Scan Result](0.3.0/results/scan-result.json).

## Manifest-based packaging and integrity

**SCAP 1.4:** Datastream packaging and XML signatures rely on XML-specific
composition, catalog, canonicalization, and signature machinery.

**SCAP-NG:** A compiled package uses a manifest to bind logical members, versions,
digests, and integrity information. Runtime resolution does not depend on the
author's source-directory layout.

See the [0.3 package manifest schema](../../schema/v0.3.0/package-manifest.schema.json).

## Forward migration with explicit blockers

**SCAP 1.4:** Existing content contains two decades of XCCDF/OVAL behavior,
including deprecated or publisher-specific constructs.

**SCAP-NG:** The converter preserves supported meaning, records provenance, and
fails explicitly when semantics cannot be carried forward. Unsupported or
deprecated constructs are blockers rather than silently changed checks.

This is central to [O1 — preserve meaning through migration](../objectives.md).

# 0.3 modernization candidates under review

The following examples are intentionally visible because they are part of the
0.3 design review. They are **not accepted merely because the research build is
green**.

## Candidate: consumer-local Objects, States, and simple bindings

**SCAP 1.4:** Even a private Object or State normally has a global ID and lives
away from its consuming Test.

**0.3 candidate:** Put a private component beside the Test/Filter/Variable that
uses it; keep a meaningful name only when the component is genuinely shared or
independently addressable.

```yaml
tests:
  library-directory-owner:
    capability: unix.file
    object:
      capability: unix.file
      select:
        path:
          value:
            variable:
              kind: constant
              expression:
                literal: [/lib, /lib64, /usr/lib, /usr/lib64]
    states:
      - state:
          field: group_id
          operation: less_than
          value: 1000
```

The full-corpus evidence shows this removes most ordinary Object/State
cross-referencing without changing the underlying semantics. Review decision:
[#165](https://github.com/vanderpol/scap-ng/issues/165) and
[#169](https://github.com/vanderpol/scap-ng/issues/169).

## Candidate: shared Observation

**SCAP 1.4:** Splitting one monolithic OVAL document into one Assessment per Rule
can duplicate expensive shared discovery/dataflow that was previously shared by
many Definitions.

**0.3 candidate:** A truthless Observation performs shared acquisition/dataflow
once and exposes typed values; each Rule Assessment still owns its Tests and
technical truth.

```yaml
observation:
  id: shared.apache.httpd.discovery
  exports:
    primary_and_included_configs:
      kind: values
      datatype: string
      cardinality: zero_or_more
    httpd_executable:
      kind: values
      datatype: string
```

This solves a real Apache/Windows/Linux reuse pattern, but adds a new artifact
and runtime interface. It is receiving an explicit complexity/value decision in
[#166](https://github.com/vanderpol/scap-ng/issues/166).

## Reusable applicability Assessments

**SCAP 1.4:** Repeated applicability may be represented through XCCDF/CPE and
OVAL structures that are difficult to trace and may be duplicated across Rules.

**SCAP-NG:** A Benchmark applicability catalog gives a condition a stable name
and binds it once to an applicability Assessment. Many Rules can reference the
same condition without copying its technical check.

```yaml
applicability:
  windows.camera-installed:
    assessment: assessments/applicability/windows-camera-installed.assessment.yaml

rules:
  - id: WN11-EXAMPLE-1
    when: windows.camera-installed
  - id: WN11-EXAMPLE-2
    when: windows.camera-installed
```

This reuse is already part of the applicability model. The open 0.3 question is
whether cross-benchmark or more complex cases justify **another dedicated shared
applicability construct**, or whether ordinary reusable Assessments and result
reuse are sufficient. Review decision:
[#178](https://github.com/vanderpol/scap-ng/issues/178).

## Candidate: bounded `for_each`

**SCAP 1.4:** Some checks require Object → ObjectComponent → Variable → target
Object plumbing simply to apply the same collection to values from another
collection.

**0.3 candidate:** A narrow `for_each` form expresses that collection expansion
directly while preserving one combined target population.

```yaml
objects:
  initialization-files:
    capability: unix.file
    for_each:
      item: user
      in: users
    select:
      directory:
        from: user.home_dir
```

The exact rewrite is uncommon in the measured corpus, so its value must justify
the added language/conformance surface. Current review:
[#164](https://github.com/vanderpol/scap-ng/issues/164).

## Complete six-benchmark 0.3 review build

The current generated review set contains RHEL 9, Oracle Linux 9, Windows 11,
Windows Server 2025, Windows Server DNS, and Apache 2.4 UNIX Server, with
faithful and modernized authoring trees.

[Open the current successful workflow run](https://github.com/vanderpol/scap-ng/actions/runs/37662165669)
and download `scap-ng-0.3-human-review-candidate` from its **Artifacts** section.

Direct Actions artifact URLs are intentionally not used because they are not
durable navigation links. At the stable 0.3 review checkpoint, the reviewed ZIP
will be published as a versioned GitHub Release asset with its SHA-256 and linked
here.

## Current 0.3 result files

- [Result example overview](0.3.0/results/README.md)
- [Scan Result](0.3.0/results/scan-result.json)
- [Benchmark Result](0.3.0/results/benchmark-result.json)
- [Automated Assessment Result](0.3.0/results/assessment-result.json)
- [Bounded-evidence Assessment Result](0.3.0/results/assessment-result-bounded-evidence.json)
- [Manual Assessment Result](0.3.0/results/manual-assessment-result.json)

## Historical 0.2 examples

The frozen 0.2 Board-review examples remain available for historical comparison
under [board/review-content/0.2.0](../../board/review-content/0.2.0/README.md).
They are not presented as current 0.3 examples.

## Version rule

Examples presented for a prerelease must be regenerated or revalidated against
that exact schema/specification version. Completed review iterations preserve the
exact reviewed example set under `review/iterations/`; later changes start a new
review checkpoint.
