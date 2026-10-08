# SCAP-NG 0.3 examples — Benchmark and Rules

**SCAP-NG 0.3.0 is pre-alpha.** Begin with the **policy**, not the machinery: a Benchmark says *what is covered*; a Rule says *what is required and why*; an Assessment says *how to check it*.

This page illustrates real converted **Red Hat Enterprise Linux 9 STIG** content. Continue to [Assessment examples](assessments.md) for automatic checks, manual procedures, `for_each`, Variables, and other technical features. For the complete current review, see [review/current](../../review/current/README.md).

## Benchmark → Rule → Assessment

**SCAP 1.4:** Benchmark and Rule material is largely combined in one XCCDF document, with checks elsewhere. **SCAP-NG:** A Benchmark references independent Rules; each Rule retains readable policy prose and chooses an Assessment. There is **no extra Policy file** between Rule and Assessment.

## A real Benchmark — RHEL 9

From `authoring/rhel_9/benchmark.yaml` in the [validated six-benchmark ZIP](https://github.com/vanderpol/scap-ng/actions/runs/37813594321), excerpted without changing the shown fields:

```yaml
benchmark:
  id: benchmark.rhel_9
  title:
    - text: Red Hat Enterprise Linux 9 STIG SCAP Benchmark - NIWC Enhanced with Manual Questions
      language: null
  version:
    value: '002.009.013'
    time: null
    update: null
  metadata:
    creator: [DISA]
    publisher: [DISA]
    contributor: [DISA]
    source: [STIG.DOD.MIL]
  default_selection: true
  groups: []
  rules:
    - SV-257777
    - SV-257778
    - SV-257779
    # ... 442 more Rule IDs in this Benchmark
```

The real converted Benchmark has **445 Rules**. It also carries description, product applicability, references, scoring, and publisher Profiles; the excerpt omits those fields for readability. Its `groups: []` is genuinely empty: the converter has **not invented group assignments**. Meaningful groups can be authored, but must not be presented as converted source when they are absent.

## A real Rule — the human-readable requirement

**RHEL 9 SV-257851** requires the `nosuid` mount option for the `/home` filesystem. A Rule preserves the STIG title, discussion, identifiers, severity, and fix **without burying the requirement inside test logic**.

From `authoring/rhel_9/rules/SV-257851.rule.yaml` in the same ZIP (the discussion below is abridged; all shown values originate in the actual Rule):

```yaml
rule:
  id: SV-257851
  version: r1044932
  title: RHEL 9 must prevent files with the setuid and setgid bit set from
    being executed on file systems that contain user home directories.
  severity: medium
  discussion: >-
    The "nosuid" mount option causes the system to not execute "setuid"
    and "setgid" files with owner privileges.
  remediation:
    guidance: Modify "/etc/fstab" to use the "nosuid" option on the "/home" directory.
  identifiers:
    - scheme: stig
      value: RHEL-09-231050
    - scheme: vulnerability
      value: V-257851
    - scheme: cci
      value: CCI-001764
```

The full source retains additional Rule fields, including references, applicability, choice bindings, and empty-but-explicit supported policy sections. The **fix** is represented under `remediation.guidance`; it is not discarded during conversion.

## A second policy example — Windows Server 2025

The actual converted **Windows Server 2025 SV-278001** Rule has the title *“Windows Server 2025 default permissions for the HKEY_LOCAL_MACHINE registry hive must be maintained.”* Its medium-severity policy discussion explains that unauthorized Registry permission changes can compromise system security and stability. The Rule also retains the lengthy DISA remediation guidance, including distinct defaults for domain controllers and other servers.

The **Rule owns the requirement and fix**; its [automated Assessment](assessments.md#explicit-evaluation-logic) separately represents the Boolean technical checks. Its existing `all/any/not` structure must not be advertised as an automatically converted `if/then/else` branch, because unknown-value outcomes may differ.

## How the Rule selects an Assessment

This actual Rule offers `default`, `automated`, and `manual` choices. The automated choice refers to a reusable Assessment checking the `/home` mount, while the manual choice preserves the STIG check procedure.

**Agreed 0.3 authoring target:** references will use stable **logical IDs**, so authors can rearrange files without updating `../` paths. The following is **illustrative target syntax, not the converter's current output**:

```yaml
rule:
  id: SV-257851
  assessment_choices:
    automated:
      assessment: rhel9.sv-257851.automated
    manual:
      assessment: rhel9.sv-257851.manual
```

The compiler must discover IDs in a declared scope, reject missing or ambiguous references, and package immutable resolved identities. **Implementation is not yet complete** ([#199](https://github.com/vanderpol/scap-ng/issues/199)); the real transitional source-path form is documented [below](#cross-file-reference-implementation-status).

## Publisher Profiles — use real selections

The RHEL 9 Benchmark defines **11 publisher Profiles**. For example, its actual `CAT_I_Only` Profile is:

```yaml
profiles:
  - id: CAT_I_Only
    title: CAT I Only
    description: null
    disabled_rules:
      - SV-257778
      - SV-257779
      - SV-257781
      # ... 414 more disabled Rule IDs
```

This excerpt shows the first three of **417 disabled Rules** from that Profile. `default_selection: true` means Rules are selected by default, with Profiles expressing deliberate exceptions. Publisher Profiles and **external Tailoring** are different: see the [worked tailoring fixture](../../research/iterations/003/examples/tailoring-all-options/tailoring/rhel9-example.tailoring.yaml), which explicitly labels fictional local policy values.

## Explicit applicability

An ordinary Rule may apply only when a package or system feature is present. The converted RHEL 9 `applicability.yaml` includes an explicit condition `benchmark.rhel_9.condition.gnome-shell-package`, linked to an Assessment that checks installation. SCAP-NG uses technical checks for applicability rather than treating CPE text as a magical scanner predicate.

Details: [real applicability Assessment example](assessments.md#applicability-assessment-technical-example).

## Readable Benchmark and Rule results

A Benchmark Result answers **how many Rules passed, failed, or could not be evaluated**. A Rule Result gives a concise outcome/reason and refers to the detailed Assessment Result. This replaces the need to manually correlate several layers of an ARF report for an initial diagnosis.

The [0.3 Benchmark Result example](0.3.0/results/benchmark-result.json) demonstrates these fields with **synthetic conformance data, not a live scan**. For root-cause Test/State/Item evidence, see the [Assessment Result example](assessments.md#assessment-results-that-explain-the-root-cause).

## What comes next?

Read the [Assessment examples](assessments.md) to see how that Rule is evaluated, including automated and manual checks, `for_each`, static values, direct Variable evaluation, conditional branches, Organization Input and bounded evidence. The [0.3 result fixture catalog](0.3.0/results/README.md) separately shows Scan, Benchmark, Automated Assessment and Manual Assessment results.

The six-benchmark set passed conversion, schema/semantics, normalization and compilation in [run 37819025184](https://github.com/vanderpol/scap-ng/actions/runs/37819025184); the **full 65-source active-0.3 release gate remains open** after additional semantic-validation failures ([#202](https://github.com/vanderpol/scap-ng/issues/202)). Neither static validation nor synthetic results establish scanner-runtime equivalence.

## Technical reference (optional)

This material is not needed to understand the policy examples.

### Cross-file reference implementation status

**Transitional converter output (real SV-257851):**

```yaml
assessment_choices:
  default:
    assessment: ../../shared/assessments/home-is-mounted-with-the-nosuid-option.assessment.yaml
  automated:
    assessment: ../../shared/assessments/home-is-mounted-with-the-nosuid-option.assessment.yaml
  manual:
    assessment: ../assessments/manual/SV-257851.manual.yaml
```

The existing compiler resolves these authoring **paths** into Assessment IDs inside the compiled package. It does **not yet** accept the logical IDs shown in the earlier *target* example. The approved direction applies uniformly to Benchmark-to-Rule, Rule-to-Assessment, dependencies, and other inter-file authored links; follow [#199](https://github.com/vanderpol/scap-ng/issues/199) for implementation, relocation, and ambiguity tests.

For measured assessment reductions, the exact `for_each:` search index, source provenance and broader census, see the [Assessment page's detailed evidence](assessments.md#detailed-reference-and-evidence). Historical 0.2 examples remain [archived here](../../board/review-content/0.2.0/README.md), not as current 0.3 authoring examples.
