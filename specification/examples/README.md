# SCAP-NG examples

This page is a short feature tour of SCAP-NG. Each section explains the practical
difference from SCAP 1.4 and shows a small representative example. Full files and
the complete review build are linked when more detail is useful.

> **Status:** SCAP-NG 0.3.0 is pre-alpha. Accepted 0.3 requirements and deferred
> post-0.3 research are labeled separately. An example does not become normative
> merely because it validates or appears on this page.

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
    library-directory-owner-test:
      capability: unix.file
      object: ...
      states: ...

  evaluate:
    test: library-directory-owner-test
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
    - test: zone-is-ad-integrated-test
    - test: zone-is-dnssec-signed-test
    - test: zone-has-rrsig-test
```

Canonical executable content keeps an explicit `evaluate` root even for a one-Test
Assessment. This avoids a second hidden execution default while preserving one
composition model.

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
For 0.3 the inherited conditional form is retained unchanged. Broader
`case`/`elseif` procedural syntax is not added.

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

Portable database/site/product-instance routing is deferred beyond 0.3; that
remains an orchestration/vendor concern until a common cross-product contract is proven.

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

# Accepted 0.3 authoring modernizations

These are part of the 0.3 requirement set. The final Board package will include
schema-valid examples for each accepted form.

## Consumer-local components and shared Objects

**SCAP 1.4:** Private Objects and States normally live in top-level registries and
are reached by IDs even when only one semantic consumer exists.

**SCAP-NG 0.3:** Keep private acquisition/predicates with their consumer. Keep a
named Object only when its acquisition identity is intentionally reusable or
referenceable. Assessment-scoped named acquisitions are declared under
`shared_objects:`; use sites still say simply `object: <name>-object`.

```yaml
shared_objects:
  users-object:
    capability: unix.password
    ...

tests:
  home-permissions-test:
    object:
      capability: unix.file
      ...
```

The 65-package modernization census reduces top-level Objects from 13,402 to 491
and States from 9,121 to 435 while preserving exact re-expansion.

## Static values without Variable plumbing

**SCAP 1.4:** Fixed multi-valued constants often require named Variables because
an XML entity can reference only one lexical body.

**SCAP-NG 0.3:** Direct scalar or typed literal-array values are allowed where the
source graph is compile-time static and source-equivalent quantifier behavior is
explicit. Named Variables remain for genuine runtime computation/dataflow.

This simplification does not replace Object-derived Variables or runtime
iteration.

## Runtime collection `for_each`

**SCAP 1.4:** Object → ObjectComponent → Variable → target-Object plumbing, or
shell/PowerShell loops, may be required simply to collect something for each Item
from another collection.

**SCAP-NG 0.3:** `for_each` expresses collection expansion directly while the
Test keeps its original aggregation/existence boundary.

```yaml
for_each:
  item: user
  in: users-object

select:
  directory:
    from: user.home_dir
```

Nested collected-data iteration is also an accepted 0.3 requirement. It remains
collection iteration—not “run one Test per Item”—and must retain outer-binding
lineage, explicit correlation, completeness/error semantics, and cycle/resource
protection. The DNS benchmark is the primary nested proving family.

# Deferred beyond normative 0.3

## Observation

Shared Observation has demonstrated real value: the corpus proof found 9
package-local Observation candidates and 69 consumers across Apache, Windows,
RHEL, and Oracle Linux.

It is **deferred**, not rejected. A normative Observation would add a second
cross-Assessment execution interface with typed exports, result/provenance,
binding, manifest dependency/cycle, and cache/reuse contracts. Those contracts
will be completed in a later version rather than rushed into the 0.3 Board
checkpoint. See [#166](https://github.com/vanderpol/scap-ng/issues/166).

## No separate shared-applicability artifact

0.3 keeps applicability explicit and reuses ordinary applicability Assessments
where useful. It does not add another dedicated sharing construct.

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
