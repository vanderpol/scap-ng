# SCAP-NG 0.4 — technical review overview

**Suggested 20-minute technical review, not a request for approval.** We want to learn where a simpler Assessment authoring format could change OVAL 5.12.3 meaning, especially with incomplete collection and non-Boolean results. **0.4 is pre-alpha research; 0.3 is unchanged.**

## Read or download first

- **[Ten real OVAL XML → SCAP-NG comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015)** — best short pre-read. Includes source-backed YAML/JSON and a `SHOWCASE-START-HERE.md` guide. Additional `for_each` and `if/else` illustrations are separately labeled research, **not automatically emitted lossless conversions**.
- **[Six complete STIGs: YAML and JSON authoring, corrected r3](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3)** — optional deeper inspection. Includes RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, DNS and Apache. All 2,958 Rule Assessment-choice links resolve.

## Three NG examples from the actual six-STIG r3 content

These are source-backed excerpts inside automated Tests, not standalone Assessments. **The Linux sample omits only `object_title: null` for readability**; the linked published source is unchanged. Other excerpts are verbatim.

**1. Linux — `/home` must use `nosuid`** ([RHEL 9 shared Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml)). The Test title explains the assertion. A private Object selects the mount, and the State checks its options. There is no need to repeat the Test title on the private Object.

```yaml
    home-mounted-nosuid-option-test:
      test_title: /home is mounted with the nosuid option.
      capability: linux.partition
      object:
        capability: linux.partition
        select:
          mount_point:
            matches_regex: .*\/home
      states:
      - mount_options:
          require: at_least_one_exists_and_some_match
          equals: nosuid
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
```

**2. Windows 11 — EditionId may be Enterprise *or* EnterpriseS** ([SV-253254](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253254.automated.yaml)). One Test expresses two allowed State alternatives. Item and State-field requirements are explicit and separate.

```yaml
      states:
      - and:
        - type:
            equals: string
        - value:
            equals: Enterprise
      - and:
        - type:
            equals: string
        - value:
            equals: EnterpriseS
      reported_elements: all
      states_match: any
      state_fields_require: at_least_one_exists_and_all_match
      collected_items_require: at_least_one_exists_and_all_match
```

**3. Windows 11 — deny Remote Desktop access to Guests** ([SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml)). Here the Test asks for *some matching collected Item*, while the `trustee_name` field has its own requirement. These quantifiers are **not interchangeable**.

```yaml
    deny-log-on-through-remote-desktop-services-guests-test:
      test_title: Deny log on through Remote Desktop Services - Guests
      capability: windows.userright
      object: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          case_insensitive_equals: Guests
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
```

That same [SV-253495 file](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml) also contains nested WMI records with separate **record and record-field requirements**. See the [technical examples](ASSESSMENT-REVIEW-TECHNICAL.md) for that excerpt.

## Suggested review flow (20 minutes)

| Time | Focus | Question for reviewers |
| --- | --- | --- |
| **0–5 min** | Examples above | Are collection, State-field and nested-record requirement scopes clear and distinct? |
| **5–10 min** | Windows registry/user-right/WMI records | Which missing, duplicate, error, unknown, or incomplete Item scenarios break these quantifiers? |
| **10–15 min** | RHEL `for_each` and Windows conditional source | When is conversion demonstrably equivalent, and when must we preserve the OVAL graph? |
| **15–20 min** | Counterexamples and next tests | Can we capture 1–3 source-backed cases with expected six-state results? |

**Important conditional warning:** `OR(AND(G,P),AND(NOT G,Q))` is **not generally equivalent** to a procedural `if G then P else Q`; [81 of 216 generic six-state combinations differ](../conditional-10/CONDITIONAL-REVIEW-QUESTIONS.md). The converter does not silently replace that OVAL Boolean graph.

## What has — and has not — been demonstrated

- **Passed:** current-main 0.3 conversion and compilation for the six representative STIGs ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38829943744)); r3 independent **JSON schema + reference** check on **4,001 documents** with **2,958 resolved Rule choices** ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38830995691)).
- **Not yet proven:** independent **0.4 native YAML/JSON-to-`.scapng` builds** ([#232](https://github.com/vanderpol/scap-ng/issues/232)), live scanner parity, and universal lossless `for_each` or `if/else` rewrites ([#229](https://github.com/vanderpol/scap-ng/issues/229)). Research vocabulary is **not ratified**.

## What feedback would help most

Useful feedback is a concrete **OVAL expression / collected Item set / expected six-state result**, or a source case that may require distinct Test, State, record or field requirements. We will add semantic cases to [#229](https://github.com/vanderpol/scap-ng/issues/229) and vocabulary questions to [#227](https://github.com/vanderpol/scap-ng/issues/227). See the [technical preview](ASSESSMENT-REVIEW-TECHNICAL.md) for further examples and evidence; feedback is not Board approval or implementation authorization.
