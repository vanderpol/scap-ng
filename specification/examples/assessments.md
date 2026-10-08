# SCAP-NG 0.3 examples — Assessments

For policy context, see the [Benchmark and Rule examples](README.md). This page covers **how requirements are checked**, from simple converted Assessments to 0.3 authoring modernizations. Practical examples come first; engineering indexes, exception boundaries and statistics are collected at the bottom.

**Provenance:** automatic/manual Assessment snippets are from named STIG conversions unless explicitly labeled *illustrative*, *research*, or *synthetic result fixture*. Source paths refer to the six-benchmark review ZIP, not committed generated trees. SCAP-NG 0.3.0 is still pre-alpha.

## Automated Assessments

**SCAP 1.4:** A Rule points to an OVAL Definition; following its Tests, Objects and States usually means jumping among separate IDs. **SCAP-NG:** The Rule still says *what is required*, but its Assessment shows *how to check it*, with private Objects and States directly beside their Test.

### 1. The Rule points to an Assessment

Here is **real converted RHEL 9 STIG Rule SV-257851**. Its requirement is that the `/home` filesystem use the `nosuid` mount option. These `assessment_choices` are the actual current source-path form (the rest of the Rule is omitted):

```yaml
rule:
  id: SV-257851
  assessment_choices:
    default:
      assessment: ../../shared/assessments/home-is-mounted-with-the-nosuid-option.assessment.yaml
    automated:
      assessment: ../../shared/assessments/home-is-mounted-with-the-nosuid-option.assessment.yaml
    manual:
      assessment: ../assessments/manual/SV-257851.manual.yaml
```

The automated choice leads to the technical check; the manual choice leads to a human procedure. The `default` and `automated` selections can share one Assessment. The compiler resolves these relative source paths when packaging content. Logical-ID references are [planned but not yet supported in authoring](https://github.com/vanderpol/scap-ng/issues/199).

### 2. The actual Assessment, with a local Object and State

This excerpt is from the same **real converted RHEL 9 check**, not invented syntax. It contains the selected filesystem, required mount option and evaluation root together in one Assessment file; only surrounding metadata is omitted.

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

Read the check from top to bottom: the **Test** checks the mount options; its local **Object** selects the `/home` filesystem; its local **State** expects `nosuid`; and **`evaluate`** identifies the Test that supplies the Assessment's technical outcome.

In SCAP 1.4, readers would usually follow Test, Object and State references through separate OVAL structures. Here those private parts are together, making the check easier to author and review. The actual Rule's policy title, severity and fix remain on the [Benchmark and Rule page](README.md#rhel-9-rule--the-requirement).

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

## Assessment Results: actual system data beside every Test

**OVAL / SCAP 1.4:** A Definition's outcome, the Test verdicts, and collected System Characteristics live in separate structures. Understanding a failure requires joining Tests, Objects, States and Items.

**SCAP-NG:** One Assessment execution produces a self-contained Assessment Result. Each Test has its **technical outcome**, reported system Items and expected-versus-observed comparisons **together**. This works for standalone Assessment scans as well as for Benchmark-linked results.

### One failed file ownership Test

The [single-file synthetic Assessment Result](0.3.0/results/assessment-result.json) includes this Test-local observation (other fields and comparisons omitted here):

```json
{
  "id": "file-owner-is-root",
  "outcome": "false",
  "per_item_results": [{
    "item_ref": "config-file-1",
    "item": {
      "id": "config-file-1",
      "capability": "unix.file",
      "status": "exists",
      "fields": {
        "full_path": {"datatype": "string", "value": "/etc/example.conf", "status": "exists"},
        "owner_uid": {"datatype": "integer", "value": 1001, "status": "exists"}
      }
    },
    "outcome": "false"
  }]
}
```

The complete result also shows the decisive comparison: **UID 1001 found; UID 0 required**, along with the owner's name, collection provenance and other authorized attributes.

### Three files, one failed comparison

Our [three-Item synthetic Assessment Result](0.3.0/results/assessment-result-multi-file.json) retains each Item's path, type, owner, group, mode, size and provenance directly beside the per-Item Test verdict:

| File or directory | UID found | UID required | Technical outcome |
| --- | ---: | ---: | --- |
| `/etc/example.d` | 0 | 0 | `true` |
| `/etc/example.d/agent.conf` | **1001** | 0 | **`false`** |
| `/etc/example.d/network.conf` | 0 | 0 | `true` |

This fixture also checks the **same `agent.conf` file a second time**, against a *different* requirement:

- **Owner Test:** UID **1001** was found; UID **0** was required.
- **Permissions Test:** mode **`0644`** was found; mode **`0600`** was required.

Both Tests include the reported file attributes beside their own comparison. The repeated file data is intentional: each Test asks a different question about that file. The scanner may reuse its single collection operation.


### Normal and diagnostic reporting use the same content

The **scanner application**, not a separate Benchmark or Assessment file, selects the evidence-retention limit. A diagnostic run may override it, without modifying the authored checks or verdict.

| | Normal scan | Diagnostic run |
| --- | --- | --- |
| Per-Test maximum reported Items | 2 | 50 |
| Failing Items observed | 20 | 20 |
| Detailed Items retained | 2 | 20 |
| Assessment outcome | `false` | `false` |
| Entire population evaluated? | No | No |

Compare the [normal bounded-evidence fixture](0.3.0/results/assessment-result-bounded-evidence.json) with the [diagnostic override fixture](0.3.0/results/assessment-result-diagnostic-override.json). These are **synthetic examples**, not real scanner runs. Their `evidence_retention` object records the effective per-Test maximum and whether it came from scanner configuration or an operator override, including the override reason. **50 is an example setting, not a hidden default.**

An evidence cap limits retained examples, **not what the Test evaluates**. If actual collection stops early, the result separately reports incomplete population and an unknown final mismatch total. Raising the reporting limit does not bypass scanner resource safeguards or author-controlled `reported_elements` and redaction. The [Benchmark Result](README.md#readable-benchmark-and-rule-results) needs only the concise decisive finding; the Assessment Result preserves the detailed technical evidence.

## Applicability Assessment (technical example)

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


## Authoring improvements

SCAP-NG makes the same underlying checks easier to read and maintain by reducing indirection. The following examples use real converted source unless stated otherwise.

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

## Predictable named component IDs

**SCAP 1.4:** Internal OVAL identifiers are often difficult to interpret by inspection. **SCAP-NG 0.3:** Descriptive kebab-case names carry the component-type suffix.

**Converted RHEL 9 SV-258045** uses actual names such as `interactive-users-object`, `count-passwd-entries-variable`, `count-unique-uids-variable`, and `uids-unique-test`. These are taken from `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258045.automated.yaml`. Private inline components do not receive artificial IDs.

## Localized Set and Filter semantics

**SCAP 1.4:** Separate Objects may be necessary even for one check's local Set. **SCAP-NG 0.3:** **Oracle Linux 9 SV-271608**, verifying MFA certificate status checking, puts the two SSSD configuration-file acquisitions inside the Test's Object while **retaining their `union` operator**. The underlying files are `/etc/sssd/sssd.conf` and `/etc/sssd/conf.d/*.conf`. See `benchmarks/oracle-linux9/candidate-authoring/assessments/automated/SV-271608.automated.yaml`.

The same principle applies to Filters: locality is a presentation improvement, not a reason to alter set membership or filter action.

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

## More advanced features

These features deserve special care. The examples distinguish converter output from authored or research-only demonstrations.

## Conditional evaluation

**SCAP 1.4:** Platform-dependent requirements often hide behind nested Boolean
criteria and guard Tests. **SCAP-NG:** `evaluate: if/then/else` is available
for explicitly authored branch semantics (inherited from 0.2), **but a converter
must not silently rewrite a source Boolean graph**.

**Real Windows Server 2025 SV-278001:** Domain controllers and other servers
have different Registry-permission requirements. The converted 0.3 Assessment
preserves the source `evaluate: all/any/not` expression; see
[SV-278001 in the actual review bundle](../../review/current/REVIEW-GUIDE.md#7-explicit-evaluate-where-composition-is-real).

Conceptually a publisher might author:

```yaml
evaluate:
  if:
    test: system-windows-domain-controller-test
  then:
    test: default-domain-controller-permissions-hkey-local-machine-system-registry-key-test
  else:
    test: default-non-domain-controller-permissions-hkey-local-machine-system-registry-test
```

**This excerpt is not the converted result or a complete equivalent Assessment.**
If the role Test is `unknown` and *both* permission Tests are `false`, the
source Boolean graph can resolve `false`, while the conditional cannot select a
branch and yields `unknown`. An author may intentionally choose conditional
behavior; a lossless converter cannot guess that choice. See the
[existing conformance fixtures](../../tests/conditional-0.2.0/README.md)
and [source-pattern research](../../research/assessment-simplification/conditional-10/README.md).

## Organizational Input

**SCAP 1.4:** Site-specific expected values often require a chain of XCCDF
Value → Tailoring → external OVAL Variable. **SCAP-NG:** The publisher declares
a typed Benchmark Parameter, the Rule binds it to an Assessment Input, and an
approved Organizational Input Set supplies the value **without changing the
published Test logic**.

**Integration research fixture, not a DISA STIG Rule:** The publisher delegates
the allowed filesystem types for `/home` to the organization. The site supplies
`[ext4, xfs]`, and a `linux.partition` Assessment evaluates the collected
`fs_type` against that input:

```yaml
states:
  - capability: linux.partition
    state:
      field: fs_type
      value:
        input: approved-filesystem-types-input
      operation: equals
      datatype: string
      variable_match: one_or_more
      match: one_or_more
      existence: one_or_more
```

The Benchmark parameter, Rule binding, Assessment input contract, completed
Input Set, request and resolution context are shown together in the
[worked source files](../../research/iterations/003/examples/organizational-input/README.md).
**Status:** illustrative fragments and a research Assessment—not a complete
compiler/evaluator-verified 0.3 package. The direct input-resolution contract
still requires end-to-end proof; these are *fictional approved values*, not a
publisher-approved change to a real STIG requirement.

**Template ownership:** The publisher/build should provide a typed Input Set
template for declared organization-resolved Parameters; the scanner may help
populate and validate it. Arbitrary scanner-created Tailoring of fixed policy
values is a different, deferred capability ([#196](https://github.com/vanderpol/scap-ng/issues/196)).
Missing required input must not produce a fabricated pass.

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

Run-level summaries and result indexing are shown alongside the policy in the [Benchmark and Rule results](README.md#readable-benchmark-and-rule-results).

## Real-world design cases — 0.3.0 review

**Flagship integration example: [Windows Server 2025 SV-278029 — time synchronization](../../research/iterations/003/examples/stig-derived/SV-278029/README.md).** Combines reusable domain/PDC applicability, conditional evaluation, existing Registry collection, approved organizational time sources, and explainable results. [Readable proposed authoring](../../research/iterations/003/examples/stig-derived/SV-278029/readable-authoring.proposal.yaml) is **research-only, not schema-valid or executable**; PDC resolution, NTP token parsing and missing-input semantics remain open. This example supports side-by-side comparison of original requirements and proposed authoring.

**Focused companion: [Windows Server 2025 SV-278217 — DWORD Registry type/value](../../research/iterations/003/examples/stig-derived/SV-278217/README.md).** Tests whether streamlined authoring preserves `REG_DWORD` versus `REG_SZ` versus `REG_MULTI_SZ`, numeric type and explicit existence. This is **also proposed research syntax** and does **not** replace the NTP case.

## Additional authoring details

These optional examples explain when an Object should be shared and how a separate Assessment can be referenced. They are not needed for the introductory examples.

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

### Referencing another Assessment

An Assessment can depend on another Assessment's result and combine it in its own `evaluate` expression. That is **result reuse**, distinct from sharing collected Objects or Items across Assessments.

**Agreed logical-ID authoring target (illustrative; not yet compiler-supported):**

```yaml
assessment:
  id: example.composed-assessment
  dependencies:
    platform-applicable:
      assessment: example.platform-applicable
      expected_version: 1
      purpose: applicability
  evaluate:
    all:
      - assessment: platform-applicable
      - test: local-setting-correct
```

The publisher refers to the stable Assessment ID; the build resolves it within a declared source/import scope, checks the type and version, rejects cycles, and packages the dependency. The alias `platform-applicable` remains local to the requesting Assessment.

**Current implementation differs:** the existing [research fixture](../../research/iterations/003/examples/assessment-result-dependency/composed.assessment.yaml) uses a relative file path and a duplicate `expected_id`. Both the compiler and schema must be migrated before the logical-ID version is a valid 0.3 file; this is tracked in [#199](https://github.com/vanderpol/scap-ng/issues/199). The target syntax is not yet executable. For the current dependency contract, see [Assessment-result dependencies](../assessment/assessment-method.md#assessment-result-dependencies).

## Detailed reference and evidence

The feature maps and audit numbers below are optional reference material. You do not need them to understand the examples above.

### Modernization example cross-reference

These examples demonstrate *what changed*, not merely which syntax is permitted. The source Rule is retained; only the explicitly described authoring structure is simplified.

| Improvement over SCAP 1.4 | Start with this real STIG Rule | Evidence |
| --- | --- | --- |
| Private Object/State beside the Test; shared acquisition remains named | **RHEL 9 SV-258029** | [Converted before/after](../../review/current/REVIEW-GUIDE.md#1-consumer-local-components-plus-a-genuinely-shared-object) |
| Static Variables become typed literal arrays | **RHEL 9 SV-257923** | [Before/after](../../review/current/REVIEW-GUIDE.md#2-static-typed-values-without-variable-plumbing) |
| Runtime Variable evaluated directly, without its legacy Variable Object | **RHEL 9 SV-258045** | [Before/after](../../review/current/REVIEW-GUIDE.md#3-direct-variable-evaluation-without-a-legacy-variable-object) |
| Multi-pass ObjectComponent Variable becomes native `for_each:` | **RHEL 9 SV-258029** | [Before/after](../../review/current/REVIEW-GUIDE.md#4-runtime-collection-for_each) |
| Set membership and filters remain explicit without global graph navigation | **Oracle Linux 9 SV-271608** | [Before/after](../../review/current/REVIEW-GUIDE.md#6-set-and-filter-semantics-remain-explicit) |
| Complex checks retain precise, readable `evaluate:` logic | **Windows Server 2025 SV-278001** | [Real converted example](#explicit-evaluation-logic) |
| Stable component names replace opaque generated references | **RHEL 9 SV-258029** | [Naming example](../../review/current/REVIEW-GUIDE.md#8-meaningful-component-ids) |
| A single reusable Assessment serves multiple Rules/benchmarks | **Six-benchmark normalized set** | [Verified exact-reuse measurements](../../research/iterations/003/evidence/validation-gates-2026-10-08/README.md) |

**Included but separately labeled:** [0.3 Scan/Benchmark/Assessment result fixtures](0.3.0/results/README.md) demonstrate smaller, explainable results and bounded evidence; they are **synthetic**, not reports from a live host. [SV-278029](../../research/iterations/003/examples/stig-derived/SV-278029/README.md) illustrates conditional authoring and Organizational Input against an actual STIG requirement, but the proposed authoring is **not executable or validated 0.3 content**. [DNS SV-259388](../../review/current/REVIEW-GUIDE.md#5-nested-for_each-production-dns-use-case-fail-closed-conversion) explains correlated nested collection research; its existing PowerShell loop was **not** automatically replaced.

**What this proves:** source-conversion and static schema/semantic/package tests on selected benchmarks. **What it does not prove:** target scanner runtime equivalence, automatic conversion of opaque shell scripts, or implementation of every research proposal.

### Finding features inside the six-benchmark review ZIP

The [validated review bundle from run 37813594321](https://github.com/vanderpol/scap-ng/actions/runs/37813594321) contains `scap-ng-board-representative-review`. Search its **`authoring/` directory using the exact YAML keys** below. Counts describe that one bundle, not all 65 source packages.

| Search string | Actual instances | Example location in the ZIP |
| --- | ---: | --- |
| `for_each:` (**underscore**, not `foreach`) | 8 instances in 7 Assessments | `authoring/shared/assessments/all-local-interactive-user-home-directories-are-0750-or-less.assessment.yaml` |
| `shared_objects:` | 79 | `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml` |
| `filters:`, `set:` | 248 filters, 163 Sets | `authoring/ms_windows_11/assessments/applicability/condition.bluetooth-installation.yaml` |
| `value:` followed by a YAML list | 48 list-valued predicates in 31 files | `authoring/ms_windows_11/assessments/automated/SV-253274.automated.yaml` |
| `evaluate:`, `all:`, `any:` | 883 evaluate entries; composite logical expressions | `authoring/ms_windows_server_2025/assessments/automated/SV-278001.automated.yaml` |
| `record:` | 86 | `authoring/ms_windows_11/assessments/applicability/condition.windows-domain-member-workstation.yaml` |
| `reported_elements:` | 1,390, all set to `all` | Automated Assessments; **not** a demonstration of selective redaction |
| `assessment_choices:` | 1,567 Rules | `authoring/ms_windows_server_2025/rules/SV-278001.rule.yaml` |
| `groups:`, `profiles:` | Both appear in all six Benchmarks | `authoring/rhel_9/benchmark.yaml` |

**Not in this six-benchmark authoring bundle:** native `if:/then:/else:`
conditional branches, Organizational Input `inputs:` bindings, selective
`reported_elements` redaction, cross-Assessment dependency/import examples,
and **observed** assessment/benchmark result samples. Synthetic 0.3 result
fixtures are [maintained in Git](0.3.0/results/README.md) and staged into
future review ZIPs as `results/synthetic-fixtures/`. They are not live scanner results, and the six-benchmark
`authoring/` tree does not demonstrate every 0.3 feature.

Literal PowerShell `foreach` occurs inside some `independent.shellcommand`
code. Those loops are **opaque executed program text**, not SCAP-NG `for_each`
semantics; translating them would require a separately reviewed and
equivalence-tested native collector replacement.

### Source and validation notes

This page is a technical feature tour of SCAP-NG. Each section explains the practical
difference from SCAP 1.4 and shows a small representative example. Full files and
the complete review build are linked when more detail is useful.

> **Status:** SCAP-NG 0.3.0 is pre-alpha. Accepted 0.3 requirements and deferred
> post-0.3 research are labeled separately. An example does not become normative
> merely because it validates or appears on this page.

**Current 0.3 verification:** The [six-benchmark regression](https://github.com/vanderpol/scap-ng/actions/runs/37809832500) completed source conversion, 0.3 schema and Assessment-semantic validation, package-graph validation, exact normalization and compilation. Its downloadable `scap-ng-board-representative-review` artifact contains two Linux benchmarks, two Windows benchmarks, Windows Server DNS and Apache 2.4 UNIX Server. See [source-linked gate measurements](../../research/iterations/003/evidence/validation-gates-2026-10-08/README.md). The separately tracked [65-source 0.3 checkpoint](https://github.com/vanderpol/scap-ng/issues/202) remains a distinct release gate; scanner-runtime equivalence is not established by these static checks.

**Measured reuse (six-benchmark reference):** The verified [normalizer report from run 37809832500](https://github.com/vanderpol/scap-ng/actions/runs/37809832500) records **3,007 referenced Assessment instances → 2,433 unique definitions** after exact semantic normalization: **574 duplicate definitions avoided (19.09%)**, over **1,567 Rules** in six benchmarks. This is a reduction in *distinct repository Assessment definitions*, not a claim of fewer Rules, faster runtime scans, or 19.09% smaller standalone bundles. Source: `representative-board-conversion-evidence` artifact, `normalizer-report.json`.


Some historical source excerpts were originally drawn from the **validated 0.3.0 candidate** produced by [workflow run 37755622654](https://github.com/vanderpol/scap-ng/actions/runs/37755622654), source commit `138c1d2f7695f1c1fe73ceb4f49de16e509dcfde`. Download the `scap-ng-0.3-human-review-candidate` artifact and follow the exact paths shown. Excerpts omit surrounding fields and are **not standalone Assessments**. **Converted** means the converter emitted the file; **native example** means authored content, not an automatic rewrite; **fixture** means invented test data, not a live scan.

### 0.3 migration results — the broader picture

The examples on this page are part of a **six-benchmark human-review set**, selected to make the
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

### Historical 0.2 examples

The frozen 0.2 Board-review examples remain available for historical comparison
under [board/review-content/0.2.0](../../board/review-content/0.2.0/README.md).
They are not presented as current 0.3 examples.

## Deferred beyond normative 0.3

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


