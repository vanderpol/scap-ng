# SCAP-NG 0.3 examples — Benchmark and Rules

**SCAP-NG 0.3.0 is pre-alpha.** Begin with the **policy**, not the machinery: a Benchmark says *what is covered*; a Rule says *what is required and why*; an Assessment says *how to check it*.

This page illustrates real converted **Red Hat Enterprise Linux 9 STIG** content. Continue to [Assessment examples](assessments.md) for automatic checks, manual procedures, `for_each`, Variables, and other technical features. For the complete current review, see [review/current](../../review/current/README.md).

## Benchmark → Rule → Assessment

**SCAP 1.4:** Benchmark and Rule material is largely combined in one XCCDF document, with checks elsewhere. **SCAP-NG:** A Benchmark references independent Rules; each Rule retains readable policy prose and chooses an Assessment. There is **no extra Policy file** between Rule and Assessment.

## RHEL 9 Benchmark

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

The converted Benchmark contains **445 Rules**, along with description, applicability, references, scoring, and publisher Profiles. Its `groups: []` indicates that no groups are defined in this converted source.

## RHEL 9 Rule — the requirement

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

## Windows Server 2025 Rule

The actual converted **Windows Server 2025 SV-278001** Rule has the title *“Windows Server 2025 default permissions for the HKEY_LOCAL_MACHINE registry hive must be maintained.”* Its medium-severity policy discussion explains that unauthorized Registry permission changes can compromise system security and stability. The Rule also retains the lengthy DISA remediation guidance, including distinct defaults for domain controllers and other servers.

The **Rule owns the requirement and fix**; its [automated Assessment](assessments.md#explicit-evaluation-logic) separately represents the Boolean technical checks. The converted Assessment retains `all/any/not` evaluation; changing it to `if/then/else` could change outcomes when values are unknown.

## How the Rule selects an Assessment

**RHEL 9 SV-257851** offers an automated check for `/home` mount options and a manual check procedure. The Rule retains the requirement; the chosen Assessment contains the actual Test.

**See the [complete worked Rule → Assessment example](assessments.md#start-here-the-rule-and-its-automated-assessment)**, with both the real Rule's `assessment_choices` and the inline `object`, `states`, and `evaluate` YAML. Those examples are deliberately kept together on the Assessment page so a reader can follow the relationship without jumping back and forth.

The **agreed 0.3 authoring contract** uses stable Assessment IDs instead of relative file paths. The remaining compiler/converter migration is tracked in [#199](https://github.com/vanderpol/scap-ng/issues/199); the linked walkthrough clearly labels its ID-based sample as the intended format.

## Publisher Profiles

The RHEL 9 Benchmark defines **11 publisher Profiles**. The `CAT_I_Only` Profile includes:

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

Details: [applicability Assessment example](assessments.md#applicability-first-check-whether-a-rule-applies).

## Readable Benchmark and Rule results

A Benchmark Result answers **how many Rules passed, failed, or could not be evaluated**, then gives a readable finding for each evaluated Rule. The detailed technical evidence is kept in a referenced Assessment Result.

The current [0.3 Benchmark Result fixture](0.3.0/results/benchmark-result.json) is **synthetic, not a live scan**. It contains two illustrative failed Rules; the excerpt below shows its policy summary and one finding:

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
  "rule_results": [{
    "rule_id": "rule-file-owner",
    "outcome": "fail",
    "message": "Observed UID 1001; expected UID 0.",
    "reason": {
      "code": "value_mismatch",
      "message": "The collected file owner did not match the required owner."
    },
    "evidence_refs": ["config-file-1"]
  }]
}
```

The full fixture also shows the Rule title, severity, check selection, applicability, execution instances, and references to supporting Assessment Results. For the decisive Test/State/Item comparisons, see [Assessment Results that explain the root cause](assessments.md#after-scanning-assessment-results-that-explain-why).

### How Scan, Benchmark, and Assessment Results fit together

**SCAP 1.4** commonly packages several result layers together in ARF XML. **SCAP-NG** gives each layer a distinct role:

- [Scan Result](0.3.0/results/scan-result.json) identifies the scanner run and targets, and indexes Benchmark and Assessment Results.
- [Benchmark Result](0.3.0/results/benchmark-result.json) summarizes compliance and reports Rule outcomes and readable findings.
- [Automated Assessment Result](0.3.0/results/assessment-result.json) and [Manual Assessment Result](0.3.0/results/manual-assessment-result.json) preserve underlying technical evidence and assessor provenance. Their examples are explained on the [Assessment page](assessments.md).

All linked files are [0.3 synthetic result fixtures](0.3.0/results/README.md), not observed host assessments.

## Active Directory Forest — a complete manual STIG example

The **Active Directory Forest V3R2 STIG** provides a smaller example of the same architecture: **7 Rules** from the DISA manual become a SCAP-NG Benchmark, 7 standalone Rules, and 7 Manual Assessments retaining the check procedure and remediation. The converter also records a source-to-native conversion audit.

Two optional presentations are rendered **from the native SCAP-NG content**, not from a separate XCCDF reader:

- **HTML review:** browse Rule titles, severity, discussion, check procedure, and fix text.
- **Excel audit checklist:** the same policy and check text, with controlled results, evidence/notes, evaluator, and review-date fields.

[Download the verified Active Directory Forest pilot artifact](https://github.com/vanderpol/scap-ng/actions/runs/37821933656/artifacts/11570215522) from the [successful validation run](https://github.com/vanderpol/scap-ng/actions/runs/37821933656). It contains native YAML, `active-directory-forest-audit.html`, and `active-directory-forest-audit.xlsx`. The [workflow](https://github.com/vanderpol/scap-ng/actions/workflows/stig-manual-audit-outputs.yml) regenerates these files from its pinned DISA manual when the artifact expires.

That run passed the conversion audit, optional-output checks, and validation of the Benchmark, Rule, and Manual Assessment documents against **both 0.2 and 0.3 schemas**. Source authoring is still path-based; the separate logical-ID migration remains unfinished ([#199](https://github.com/vanderpol/scap-ng/issues/199)). This example demonstrates the manual-audit path; the RHEL 9 example above demonstrates automated checking.

## What comes next?

Read the [Assessment examples](assessments.md) to see how that Rule is evaluated, including automated and manual checks, `for_each`, static values, direct Variable evaluation, conditional branches, Organization Input and bounded evidence. The [0.3 result fixture catalog](0.3.0/results/README.md) separately shows Scan, Benchmark, Automated Assessment and Manual Assessment results.

The six-benchmark set passed conversion, schema/semantics, normalization and compilation in [run 37819025184](https://github.com/vanderpol/scap-ng/actions/runs/37819025184); the **full 65-source active-0.3 release gate remains open** after additional semantic-validation failures ([#202](https://github.com/vanderpol/scap-ng/issues/202)). Neither static validation nor synthetic results establish scanner-runtime equivalence.

## Technical reference (optional)

This material is not needed to understand the policy examples.

### Cross-file reference implementation status

The [worked RHEL 9 example](assessments.md#1-the-rule-chooses-how-to-check-the-requirement) shows the agreed **logical-ID** authoring notation. At this pre-alpha checkpoint, the current compiler still resolves legacy source-path references; migration to native logical-ID lookup is tracked in [#199](https://github.com/vanderpol/scap-ng/issues/199).

For measured authoring reductions, source provenance and the broader census, see the [Assessment page's optional evidence](assessments.md#evidence-and-further-reading-optional). Historical 0.2 examples remain [archived here](../../board/review-content/0.2.0/README.md), not as current 0.3 authoring examples.
