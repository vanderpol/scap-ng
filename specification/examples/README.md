# SCAP-NG examples

This page is a short feature tour of SCAP-NG. Each section explains the practical
difference from SCAP 1.4 and shows a small representative example. Full files and
the complete review build are linked when more detail is useful.

> **Status:** SCAP-NG 0.3.0 is pre-alpha. Accepted 0.3 requirements and deferred
> post-0.3 research are labeled separately. An example does not become normative
> merely because it validates or appears on this page.

## 0.3 at a glance

SCAP-NG 0.3 is now backed by both focused conformance tests and production-scale
migration evidence:

- **6/6 representative benchmarks pass** schema and semantic validation: RHEL 9,
  Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS, and
  Apache 2.4 UNIX.
- The final **65-package NIWC census converts 61 packages**, with the remaining
  **4 blocked only by the already-known unsupported SQL extension** and **0
  unexpected blockers**.
- Proven automatic modernization found **55 real `for_each` rewrites** and folded
  **509 compile-time constant Variables** while keeping runtime/dataflow Variables
  explicit.
- Across 6,916 Rule Assessments, the modernized authoring view reduces top-level
  Object entries by **95.68%**, State entries by **100%**, Variables by **59.69%**,
  and named component references by **94.42%**.

**How these numbers were measured:** the final census used the pinned current
NIWC SCAP 1.4 corpus (65 packages; 61 convertible; 6,916 Rule Assessments). For
each generated Assessment, it compared the fidelity-first SCAP-NG conversion
with the same content after only accepted, exact/reversible 0.3 authoring
transformations. The percentages above count **top-level named graph
structures/references**, not source XML bytes and not scanner runtime. For
perspective, normalized serialized output decreased by only **3.13% in bytes**
and **5.20% in lines**—the much larger reductions are specifically the
indirection an author or reviewer must navigate.

See the [0.3 modernization review guide](../../review/current/REVIEW-GUIDE.md)
for real before/after STIG examples and the
[current review page](../../review/current/README.md) for the validated build,
pinned corpus revision, and full census evidence.

The excerpts below are from the **validated 0.3.0 candidate** produced by [workflow run 37755622654](https://github.com/vanderpol/scap-ng/actions/runs/37755622654), source commit `138c1d2f7695f1c1fe73ceb4f49de16e509dcfde`. Download the `scap-ng-0.3-human-review-candidate` artifact and follow the exact paths shown. Excerpts omit surrounding fields and are **not standalone Assessments**. **Converted** means the converter emitted the file; **native example** means authored content, not an automatic rewrite; **fixture** means invented test data, not a live scan.

## Benchmark → Rule → Assessment

**SCAP 1.4:** XCCDF Rules reference separate OVAL checks. **SCAP-NG:** A Rule identifies its available automated and manual Assessments without hiding policy text inside technical checks.

**Converted RHEL 9 SV-257923**, from `benchmarks/rhel9/candidate-authoring/rules/SV-257923.rule.yaml`:

```yaml
rule:
  id: SV-257923
  title: RHEL 9 library directories must be group-owned by root or a system account.
  assessment_choices:
    automated:
      assessment: ../assessments/automated/SV-257923.automated.yaml
    manual:
      assessment: ../assessments/manual/SV-257923.manual.yaml
  default_assessment_choice: default
```

The complete Rule also carries severity, rationale, references, and remediation.

## Automated Assessments

**SCAP 1.4:** One OVAL check may require chasing separate Test, Object and State IDs. **SCAP-NG:** Keep private Object/State content beside its Test.

**Converted RHEL 9 SV-257851:** the `/home` mount must have `nosuid`. The following is from `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-257851.automated.yaml`, omitting presentation fields:

```yaml
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          value: .*\\/home
          operation: pattern_match
          datatype: string
    states:
      - capability: linux.partition
        state:
          field: mount_options
          value: nosuid
          operation: equals
          datatype: string
          match: one_or_more
          existence: one_or_more
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-mounted-nosuid-option-test
```

The full Assessment preserves required metadata and its explicit execution root.

## Explicit evaluation logic

**SCAP 1.4:** `criteria` composes Boolean Tests, sometimes with many references. **SCAP-NG:** `evaluate` preserves genuine multi-Test logic instead of burying it in execution code.

**Converted Windows Server DNS SV-259388**, in `benchmarks/windows-server-dns/candidate-authoring/assessments/automated/SV-259388.automated.yaml`, retains three ways to satisfy the Rule: caching-only, AD-integrated zones, or both IPv4 and IPv6 RRSIG checks:

```yaml
evaluate:
  any:
    - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
    - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
    - all:
        - test: there-at-least-one-rrsig-resource-record-signature-associated-each-test
        - test: there-at-least-one-rrsig-resource-record-signature-associated-each-2-test
```

This is the actual converted tree, not a fabricated `evaluate` example.

## Conditional evaluation

**SCAP 1.4:** Environment-sensitive checks can use nested guard Tests, which are hard to recognize as role-dependent requirements. **SCAP-NG:** Native content supports explicit `if/then/else`, but source OVAL Boolean graphs cannot generally be converted into procedural branches without changing six-state outcomes.

**Converted Windows Server 2025 SV-278001** checks `HKEY_LOCAL_MACHINE\\SYSTEM` registry permissions differently for domain controllers and other servers. The 0.3 candidate **correctly preserves** the source's guarded Boolean expression. From `benchmarks/windows-server-2025/candidate-authoring/assessments/automated/SV-278001.automated.yaml`:

```yaml
evaluate:
  all:
    - test: default-permissions-hkey-local-machine-security-registry-key-maintained-test
    - test: default-non-domain-controller-permissions-hkey-local-machine-software-registry-test
    - any:
        - all:
            - test: system-windows-domain-controller-test
            - test: default-domain-controller-permissions-hkey-local-machine-system-registry-key-test
        - all:
            - not:
                test: system-windows-domain-controller-test
            - test: default-non-domain-controller-permissions-hkey-local-machine-system-registry-test
```

For an *authored* `if/then/else` form, use the [conditional conformance suite](../../tests/conditional-0.2.0/README.md), explicitly labeled as a fixture. It is **not** the output for SV-278001. [Production conditional research](../../research/assessment-simplification/conditional-10/README.md) demonstrates why the rewrite is unsafe for error, unknown, not-evaluated, and not-applicable outcomes. The conditional syntax itself predates 0.3.

## Manual Assessments

**SCAP 1.4:** Manual STIG Check Text generally lives in XCCDF. **SCAP-NG:** The real procedure becomes a first-class Assessment with explicit recorded responses.

**Converted RHEL 9 SV-257851**, from `benchmarks/rhel9/candidate-authoring/assessments/manual/SV-257851.manual.yaml`: the full procedure directs the assessor to verify the `/home` `nosuid` mount. Response excerpt:

```yaml
assessment:
  id: SV-257851.manual
  mode: manual
  response:
    type: compliance
    choices:
      - value: pass
        label: Pass
        outcome: 'true'
      - value: fail
        label: Fail
        outcome: 'false'
    allow_comment: true
    allow_evidence: true
```

The [0.3 Manual Assessment Result](0.3.0/results/manual-assessment-result.json) illustrates attribution and evidence **using synthetic result data**, not an actual assessment.

## Explicit applicability

**SCAP 1.4:** Applicability can be scattered among CPE, XCCDF, and OVAL. **SCAP-NG:** Applicability refers to explicit technical Assessments.

**Converted RHEL 9 candidate** `benchmarks/rhel9/candidate-authoring/applicability.yaml` contains:

```yaml
applicability:
  id: benchmark.rhel_9.applicability
  conditions:
    benchmark.rhel_9.condition.gnome-shell-package:
      assessment: assessments/applicability/condition.gnome-shell-package.yaml
```

The referenced file tests the real `gnome-shell` package using `linux.rpminfo` or `linux.dpkginfo`. Product identifiers may be captured as inventory, but not silently used to decide applicability.

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

**The result excerpts below are conformance fixtures, not real target scans.** They demonstrate 0.3 result fields with synthetic outcomes and evidence. They must not be described as scanner-generated proof. Full JSON examples and their provenance are indexed in the [result-fixture overview](0.3.0/results/README.md).

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

These are part of the 0.3 requirement set. The current owner-review package
includes schema-valid production-derived coverage for each accepted form.

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

The final corpus census confirms that this locality model applies broadly, not
just to hand-picked examples; the headline measurements are summarized above.

## Static values without Variable plumbing

**SCAP 1.4:** Fixed multi-valued constants often require named Variables because
an XML entity can reference only one lexical body.

**SCAP-NG 0.3:** Direct scalar or typed literal-array values are allowed where the
source graph is compile-time static and source-equivalent quantifier behavior is
explicit. Named Variables remain for genuine runtime computation/dataflow.

This simplification does not replace Object-derived Variables or runtime
iteration.

Example:

```yaml
select:
  shell:
    value: ["/bin/bash", "/bin/sh"]
    datatype: string
    variable_match: one_or_more
```

The literal collection keeps the source-equivalent datatype and quantifier;
array syntax does not silently mean OR/ANY.

## Predictable named component IDs

**SCAP 1.4:** IDs often encode XML type/version namespaces and generated source
identity, which makes repository searching noisy.

**SCAP-NG 0.3:** Named internal components use meaningful kebab-case IDs ending
in their type.

```yaml
shared_objects:
  forward-zones-object: ...

variables:
  zone-names-variable: ...

tests:
  zone-signing-test: ...
```

Inline/private components do not receive artificial IDs solely to satisfy the
naming convention.

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
protection.

```yaml
shared_objects:
  zones-object: ...

  hosts-object:
    for_each:
      item: zone
      in: zones-object
    select:
      zone:
        from: zone.name

  dnssec-responses-object:
    for_each:
      item: host
      in: hosts-object
    select:
      name:
        from: host.fqdn
      zone:
        from: zone.name
```

Here the inner collection inherits the correlated outer `zone` lineage; this
does not imply an independent Cartesian product. The DNS benchmark is the primary
production proving family.

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

## Review the complete 0.3 sample set

Start with the maintained [modernization review guide](../../review/current/REVIEW-GUIDE.md),
then use the six complete faithful/candidate benchmark trees and scorecards in the
validated owner-review artifact. The [current review page](../../review/current/README.md)
is the single source for the active build, provenance, and download instructions.

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
