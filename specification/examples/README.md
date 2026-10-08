# SCAP-NG examples

This page is a short feature tour of SCAP-NG. Each section explains the practical
difference from SCAP 1.4 and shows a small representative example. Full files and
the complete review build are linked when more detail is useful.

> **Status:** SCAP-NG 0.3.0 is pre-alpha. Accepted 0.3 requirements and deferred
> post-0.3 research are labeled separately. An example does not become normative
> merely because it validates or appears on this page.

**Source-first example policy:** Prefer a real published DISA STIG Rule for every
feature, with Rule ID, benchmark/version, original check text or automation,
native assessment, and a concrete explanation of the improvement. Distinguish
(a) faithfully converted automated checks, (b) formerly manual checks with
*demonstrated and validated* new automation, and (c) real checks extended by
explicit publisher-delegated organizational values. Never imply a synthetic
requirement was part of a STIG. A fictional fixture may explain an unproven
feature, but it must be marked research-only and does not count as proof of
modernization. If no defensible real case exists, leave the feature out of the
Board showcase rather than inventing a result.

The excerpts below are from the **validated 0.3.0 candidate** produced by [workflow run 37755622654](https://github.com/vanderpol/scap-ng/actions/runs/37755622654), source commit `138c1d2f7695f1c1fe73ceb4f49de16e509dcfde`. Download the `scap-ng-0.3-human-review-candidate` artifact and follow the exact paths shown. Excerpts omit surrounding fields and are **not standalone Assessments**. **Converted** means the converter emitted the file; **native example** means authored content, not an automatic rewrite; **fixture** means invented test data, not a live scan.

## Benchmark → Rule → Assessment

**SCAP 1.4:** XCCDF generally embeds the complete Rule definitions inside the Benchmark, and those Rules reference separate OVAL checks. **SCAP-NG:** The Benchmark instead **lists references to individual Rule files**. Each Rule owns its policy text and references its available automated/manual Assessment files. The Benchmark does **not** contain the full Rule definitions.

The file relationship is:

```text
benchmark.yaml
  rules:
    - rules/SV-257923.rule.yaml
              |
              v
rules/SV-257923.rule.yaml
  assessment_choices:
    automated: ../assessments/automated/SV-257923.automated.yaml
    manual:    ../assessments/manual/SV-257923.manual.yaml
```

This is a **structural illustration** (showing only one Rule), not the entire RHEL 9 Benchmark. In the actual Benchmark, `rules:` is a list of Rule-file paths; the Rule file contains the title, severity, rationale, remediation, and Assessment bindings. The compiler resolves the references and the compiled package manifest identifies the corresponding logical members.

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


### Local Objects versus shared Objects

In the RHEL 9 example above, `object:` is **inside the Test**: that Object is
private to that Test. This is the normal choice when the acquisition has one
consumer. No separate Object ID or top-level registry entry is needed.

If two Tests need **the same acquisition within one Assessment**, the author
can instead declare a descriptive, named Object under `shared_objects:`
and reference it from the consuming Tests. Unlike an inline Object, this
explicitly preserves reusable identity. This short comparison is
**illustrative syntax** (omitting fields for readability):

```yaml
# Private: owned by one Test
tests:
  file-owner-test:
    capability: unix.file
    object:
      capability: unix.file
      select: {filepath: /etc/ssh/sshd_config}

# Shared: one named Object, available to multiple Tests in this Assessment
shared_objects:
  ssh-configuration-object:
    capability: unix.file
    select: {filepath: /etc/ssh/sshd_config}
tests:
  file-owner-test:
    capability: unix.file
    object: ssh-configuration-object
  file-permissions-test:
    capability: unix.file
    object: ssh-configuration-object
```

These are two **alternative authoring shapes**, not one file to concatenate:
normally choose a local Object, and promote it to `shared_objects` when
the shared acquisition is intentional. Sharing an Object *within* an
Assessment is distinct from consuming the **result of another Assessment**,
shown next. The later [production-derived RHEL 9 example](#consumer-local-components-and-shared-objects)
demonstrates local and shared acquisition in the same converted Assessment.

### Referencing another Assessment file

SCAP-NG also supports a separate form of reuse: an Assessment may statically
declare a **dependency on another Assessment's result**, and use that result
inside its own `evaluate` tree. Here is a **manufactured native illustration**,
adapted from the existing [Assessment dependency fixture](../../research/iterations/003/examples/assessment-result-dependency/composed.assessment.yaml),
not an automatically converted STIG example:

```yaml
assessment:
  id: example.composed-assessment
  dependencies:
    platform-applicable:
      assessment: ../applicability/example-platform.assessment.yaml
      expected_id: example.platform-applicable
      expected_version: 1
      purpose: applicability
  evaluate:
    all:
      - assessment: platform-applicable
      - test: local-setting-correct
```

The `assessment:` path identifies the **external authored YAML file**;
`expected_id` and `expected_version` protect against accidentally binding
the wrong content; `platform-applicable` is the local alias referenced by
`evaluate`. The other Assessment remains an independent unit with its own
technical result and evidence. The compiler must resolve and validate
dependencies, including rejecting cycles. The result is reused without
copying the referenced Assessment's Tests or collected Items into this file.

**Important distinction:** this is **Assessment-result reuse**, not
cross-Assessment Object/Item collection sharing. The latter remains a
separate, deferred design topic. For the normative contract, see
[Assessment-result dependencies](../assessment/assessment-method.md#assessment-result-dependencies).


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

A **native authoring alternative derived from this same real STIG Rule** could put the role choice at the point of decision:

```yaml
evaluate:
  all:
    - test: default-permissions-hkey-local-machine-security-registry-key-maintained-test
    - test: default-non-domain-controller-permissions-hkey-local-machine-software-registry-test
    - if:
        test: system-windows-domain-controller-test
      then:
        test: default-domain-controller-permissions-hkey-local-machine-system-registry-key-test
      else:
        test: default-non-domain-controller-permissions-hkey-local-machine-system-registry-test
```

This is **source-derived native syntax, not generated candidate output**: a publisher choosing it must accept the defined conditional behavior for non-Boolean role results. The source-equivalent converter does not silently make that policy choice. For example, if the role Test is `unknown` and *both* permission Tests are `false`, the original Boolean expression is `false` but the conditional branch cannot be selected and returns `unknown`.

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

**SCAP 1.4:** Site-specific expected values often require XCCDF Values,
Tailoring and OVAL external Variables. **SCAP-NG:** A Benchmark declares a
typed organization-resolved Parameter; a Rule maps it to an Assessment input;
the Assessment consumes the value directly. The Input Set is supplied and
authorized independently, without changing publisher Test logic.

**Worked example (fictional policy, real supported capability):** The publisher
requires the filesystem mounted at `/home` to have an organization-approved
type. The organization approves `ext4` and `xfs`. Unlike an earlier example
built around an unimplemented `linux.chrony` collector, this uses the supported
`linux.partition` mapping, which exposes `mount_point` as a selector and
`fs_type` as a State field. **This is still an integration research fixture:
direct input resolution and evaluator behavior have not been proved
end-to-end.** The fictional rule is not a DISA requirement. **Provenance clarification:** this is a newly authored, hypothetical policy requirement built on a supported OVAL-derived collection capability. It is **not** a converted DISA rule, not a known formerly manual STIG check, and not evidence of a manual-to-automated conversion. No legacy Rule ID or SCAP 1.4 source definition is claimed.

The explicit linkage is:

| Owner | Authored identity | Meaning |
| --- | --- | --- |
| Input Set | `values.approved_filesystem_types` | Organization-approved `[ext4, xfs]` |
| Benchmark | `parameters[].id: approved_filesystem_types` | Publisher-delegated type/constraints |
| Rule | `inputs.approved-filesystem-types-input.parameter` | Bind Parameter to Assessment contract |
| Assessment | `inputs.approved-filesystem-types-input` | Named typed input |
| State in Test | `value.input: approved-filesystem-types-input` | Compare collected `fs_type` against approved values |

**Benchmark Parameter fragment:**

```yaml
parameters:
  - id: approved_filesystem_types
    resolution: organization
    datatype: string
    cardinality: one_or_more
    required: true
    constraints:
      min_items: 1
      unique_items: true
```

**Rule binding (fragment):**

```yaml
assessment_choices:
  automated:
    assessment: home-filesystem.assessment.yaml
    inputs:
      approved-filesystem-types-input:
        parameter: approved_filesystem_types
```

**Assessment Test (fragment):**

```yaml
inputs:
  approved-filesystem-types-input:
    datatype: string
    cardinality: one_or_more
    required: true
tests:
  home-filesystem-test:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          value: /home
          operation: equals
          datatype: string
    states:
      - capability: linux.partition
        state:
          field: fs_type
          operation: equals
          datatype: string
          variable_match: one_or_more
          match: one_or_more
          existence: one_or_more
          value:
            input: approved-filesystem-types-input
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-filesystem-test
```

The State consumes an input **without a pass-through Variable**. The
`variable_match` quantifier makes the expected-value aggregation explicit;
`match: all` on the Test applies to collected partitions. The shorter
`operation: in` expression is [under research](../../research/iterations/003/design/membership-comparison-research.md),
not valid 0.3 syntax.

**Completed Organization Input Set:** The separate
[example Input Set](../../research/iterations/003/examples/organizational-input/site.organizational-input.yaml)
records `approved_filesystem_types: [ext4, xfs]`, source/authority,
organization, supplier, timestamps, approver and authorization status. These
values are fictional. The
[Assessment Request](../../research/iterations/003/examples/organizational-input/assessment-request.yaml)
explicitly selects that Input Set; descriptive scope metadata never selects a
target implicitly. Missing required input produces `not_evaluated`, not an
invented pass/fail.

**Why is the binding in the Rule?** The Assessment remains reusable and does
not hard-code the Benchmark's policy Parameter ID. Different Rules may bind
different authorized policy Parameters to its same technical input. The
additional Rule-level `organizational_input_requirements` discovery map may
ultimately be generated at compilation instead of authored twice; this is
still an architecture-audit question, not an accepted change.

### Who provides templates?

For **publisher-delegated Organizational Input**, the preferred path is for
the content author/build process to generate a ready-to-fill, typed Input Set
template at publication. The scanner should be able to present or validate
it; people should not author complex YAML from scratch.

If the OVAL Board later permits Tailoring of otherwise fixed expected-State
values, a scanner could generate an input template for an eligible
Rule/Assessment on demand. That is **a different, future capability**, requiring
policy-deviation identity, approval, precise State-slot bindings and semantics.
It is not an authority to overwrite published requirements in 0.3. See
[issue #196](https://github.com/vanderpol/scap-ng/issues/196).

The [worked files](../../research/iterations/003/examples/organizational-input/README.md)
illustrate the Benchmark Parameter, Rule fragment, Assessment, Input Set,
request and resolved context. **The integrated fixture remains research-only
until schema, compiler and evaluator conformance are demonstrated.**

## Profiles and Tailoring

**SCAP 1.4:** Profile selection and refinement require resolving multiple XCCDF structures. **SCAP-NG 0.3:** The default is explicit, and publisher Profiles record Rule-selection differences.

**Converted RHEL 9** `benchmarks/rhel9/candidate-authoring/benchmark.yaml` sets `default_selection: true`. Its real `CAT_I_Only` profile disables non-CAT-I Rules. Excerpt (only the first three disable entries shown):

```yaml
default_selection: true
profiles:
  - id: CAT_I_Only
    title: CAT I Only
    disabled_rules:
      - SV-257778
      - SV-257779
      - SV-257781
      # More disabled Rules in the complete source
```

An external Tailoring example needs invented local policy decisions; the [RHEL 9 worked tailoring fixture](../../research/iterations/003/examples/tailoring-all-options/tailoring/rhel9-example.tailoring.yaml) explicitly identifies its authorization and exceptions as fictional rather than claiming publisher approval.

**Result provenance:** All result snippets in the following sections are deliberately **synthetic 0.3 conformance fixtures**, not results produced by scanning a real STIG target. They demonstrate the output schema and root-cause/completeness fields; source Assessment conversion and observed target evidence are separate claims. See the [fixture index](0.3.0/results/README.md).

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

**SCAP 1.4:** Even private Objects/States live in separate registries. **SCAP-NG 0.3:** Keep the private parts with the Test, while preserving named acquisitions when they are genuinely referenced.

**Converted RHEL 9 SV-258029** combines a shared dconf directory acquisition with a private `independent.textfilecontent54` Object. From `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258029.automated.yaml` (the shared Object's Set/Filter and the private select fields continue in the full file):

```yaml
shared_objects:
  dconf-database-directories-object:
    capability: unix.file
    set:
      operator: union
      # Operands and Filter remain in the full file
tests:
  dconf-disable-restart-buttons-true-test:
    capability: independent.textfilecontent54
    object:
      capability: independent.textfilecontent54
      for_each:
        item: item
        in: dconf-database-directories-object
```

The [review guide](../../review/current/REVIEW-GUIDE.md) links the complete faithful and modernized files.

## Static values without Variable plumbing

**SCAP 1.4:** Static multi-value constants often require separate Variables. **SCAP-NG 0.3:** Inline exact compile-time literals while retaining datatype and source quantifiers.

**Converted RHEL 9 SV-257923** puts the actual library directory set directly in a `unix.file` selector. From `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-257923.automated.yaml`:

```yaml
select:
  directory:
    value:
      - /lib
      - /lib64
      - /usr/lib
      - /usr/lib64
    operation: equals
    datatype: string
    variable_match: one
```

Unlike static constants, runtime values remain named. This is a reduction in graph indirection, not a change in compliance logic.

## Predictable named component IDs

**SCAP 1.4:** Internal OVAL identifiers are often difficult to interpret by inspection. **SCAP-NG 0.3:** Descriptive kebab-case names carry the component-type suffix.

**Converted RHEL 9 SV-258045** uses actual names such as `interactive-users-object`, `count-passwd-entries-variable`, `count-unique-uids-variable`, and `uids-unique-test`. These are taken from `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258045.automated.yaml`. Private inline components do not receive artificial IDs.

## Runtime collection `for_each`

**SCAP 1.4:** Object → ObjectComponent → Variable → Object chains may exist simply to feed each collected Item into another collection.

**SCAP-NG 0.3:** **RHEL 9 SV-258029** is a *mechanically converted* use of collection iteration. This actual excerpt belongs to its text-file Test Object:

```yaml
for_each:
  item: item
  in: dconf-database-directories-object
select:
  directory:
    from: item.directory
```

This expands a collection, not one Test per Item, and does not change Test aggregation.

**Nested production case — Windows Server DNS SV-259388:** The original PowerShell code iterates zones and A/AAAA hosts and checks RRSIG responses. Native correlated nested iteration is illustrated in the [0.3 review guide](../../review/current/REVIEW-GUIDE.md), but it is **production-derived native authoring, not an automatic rewrite**: the converter cannot prove arbitrary PowerShell semantics, so the real generated candidate retains the command.

## Direct Variable evaluation

**SCAP 1.4:** Comparing computed values can require an artificial Variable Object. **SCAP-NG 0.3:** The real **RHEL 9 SV-258045** UID-uniqueness check uses `variable.value` directly, retaining both runtime Variables.

```yaml
tests:
  uids-unique-test:
    capability: variable.value
    variable: count-passwd-entries-variable
    states:
      - capability: variable.value
        state:
          field: value
          value:
            variable: count-unique-uids-variable
          operation: equals
          datatype: integer
```

This is an excerpt: explicit quantifiers and reporting fields remain in `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258045.automated.yaml`.

## Localized Set and Filter semantics

**SCAP 1.4:** Separate Objects may be necessary even for one check's local Set. **SCAP-NG 0.3:** **Oracle Linux 9 SV-271608**, verifying MFA certificate status checking, puts the two SSSD configuration-file acquisitions inside the Test's Object while **retaining their `union` operator**. The underlying files are `/etc/sssd/sssd.conf` and `/etc/sssd/conf.d/*.conf`. See `benchmarks/oracle-linux9/candidate-authoring/assessments/automated/SV-271608.automated.yaml`.

The same principle applies to Filters: locality is a presentation improvement, not a reason to alter set membership or filter action.

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

## 0.3 migration results — the broader picture

The examples above are a **six-benchmark human-review set**, selected to make the
new authoring model understandable across Linux, Windows, and services. They are
not the whole migration experiment.

**Where the 65 benchmarks came from.** NIWC Atlantic publishes a public
[SCAP 1.4 content library](https://github.com/niwc-atlantic/scap-content-library).
For a reproducible baseline, this project pinned its `Current/` directory to
[revision `8c8e5dff`](https://github.com/niwc-atlantic/scap-content-library/tree/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current).
That snapshot contains **65 individual signed benchmark ZIPs** for operating
systems and applications, plus **one consolidated bundle**. The bundle is not a
66th distinct benchmark. These are existing production SCAP 1.4 artifacts,
not 65 examples written specifically for SCAP-NG. We used them to see whether
the new design works beyond hand-picked demonstrations.

**What we did.** We ran conversion and modernization across that frozen
source set, compared fidelity-first generated Assessments with the same
Assessments after supported, semantics-preserving 0.3 authoring simplifications,
and separately validated six representative benchmark trees for human review.
The figures below describe **conversion and authoring structure**, not scans
of live machines or a claim that all SCAP 1.4 constructs are supported.

| Measure | Observed result |
| --- | --- |
| Individual SCAP 1.4 benchmark packages examined | **65** |
| Packages converted | **61** |
| Known blockers | **4**, all from the unsupported SQL extension; **0 unexpected** |
| Representative benchmark trees passing schema and semantic validation | **6 of 6** |
| Rule Assessments in the measured modernization set | **6,916** |
| Confirmed automatic `for_each` rewrites | **55** |
| Compile-time constant Variables folded | **509** |
| Fewer top-level named Objects / States | **95.68% / 100%** |
| Fewer top-level Variables / named component references | **59.69% / 94.42%** |
| Reduction in normalized serialized bytes / lines | **3.13% / 5.20%** |

**How to read the reductions.** The dramatic percentages refer to the
*top-level named component graph* that an author must navigate: many Objects
and States moved next to their consuming Test rather than disappearing as
actual collection or comparison behavior. They are **not** a 95% reduction
in file size, scanner work, or runtime, and do not mean all real-world
assessment complexity disappeared. The much smaller byte/line changes
provide an important cross-check on that distinction. The converter deliberately
retains complex structures when simpler syntax would alter OVAL results.

For the actual before/after STIG cases, see the
[modernization review guide](../../review/current/REVIEW-GUIDE.md).
The [current review page](../../review/current/README.md) maintains the
validated build, detailed census evidence, and links to the downloadable
artifact. The [corpus manifest](../../tests/corpus-manifest.yaml) records
the exact source snapshot and separates real production migration evidence
from synthetic conformance fixtures.

## Version rule

Examples presented for a prerelease must be regenerated or revalidated against
that exact schema/specification version. Completed review iterations preserve the
exact reviewed example set under `review/iterations/`; later changes start a new
review checkpoint.
