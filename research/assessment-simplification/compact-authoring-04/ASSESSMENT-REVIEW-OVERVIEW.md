# SCAP-NG 0.4 — technical review overview

**Suggested 20-minute technical review, not a request for approval.** We want to learn where a simpler Assessment authoring format could change OVAL 5.12.3 meaning, especially with incomplete collection and non-Boolean results. **0.4 is pre-alpha research; 0.3 is unchanged.**

## Read or download first

- **[Ten real OVAL XML → SCAP-NG comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015)** — best short pre-read. Includes source-backed YAML/JSON and a `SHOWCASE-START-HERE.md` guide. Additional `for_each` and `if/else` illustrations are separately labeled research, **not automatically emitted lossless conversions**.
- **[Six complete STIGs: YAML and JSON authoring, corrected r3](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3)** — optional deeper inspection. Includes RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, DNS and Apache. All 2,958 Rule Assessment-choice links resolve.

## What became more like resource-oriented checks

A reviewer in [Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213#discussioncomment-18935232) recalled **Slang**: select a schema-defined resource, state what must exist and match, then compose checks with AND/OR/XOR. **SCAP-NG 0.4 moves in that direction, but does not claim to implement Slang.**

- **Collect/select:** a native capability and Object selector identify the system facts to inspect.
- **Expect:** observed field names and comparisons sit beside collection in the same Test, not in a distant named State registry.
- **Require:** explicit human-readable cardinality names distinguish *collected Items* from *field values*, so a shorter check does not silently change an OVAL verdict.
- **Compose:** `evaluate` combines named Tests with `all`/`any`/`one`/`odd`; retaining it permits reusable and complex source-faithful logic.

This is still more explicit than Slang's sketch: a Test and its private Object may both declare a capability, cardinality phrases are longer, and the compiler cannot assume a `suid: false` field means exactly the same as the real `mount_options: nosuid` check. Those differences are deliberate until equivalence can be proven. See the [precise source comparison and limits](../slang-feedback-04/README.md).

## Three NG examples from the actual six-STIG r3 content

These are source-backed excerpts inside automated Tests, not standalone Assessments. **The Linux sample omits only `object_title: null` for readability**; the linked published source is unchanged. Other excerpts are verbatim.

**1. Linux — `/home` must use `nosuid`** ([RHEL 9 shared Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml)). The Test title explains the assertion. A private Object selects the mount, and the State checks its options. There is no need to repeat the Test title on the private Object.

**Compared with 0.3,** the same real State and Test requirements previously appeared as:

```yaml
# Source-derived 0.3 State + Test requirements (surrounding fields omitted)
states:
  - field: mount_options
    value: nosuid
    operation: equals
    existence: one_or_more
    match: one_or_more
existence: one_or_more
match: all
```

In 0.4, `mount_options` and `equals` are directly readable, and the two `require` keys keep the **different scopes** intact. This is a readability change, not a claim that every mount option must be `nosuid`. [0.3 source-derived comparison](BOARD-PREVIEW.md#same-check-rhel-9-sv-257851-home-nosuid).

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

**Why `some` for the State, but `all` for the Test?**

- **Inside each filesystem Item:** `mount_options` may include `rw`, `nodev`, and `nosuid`. At least **one option** must exist and equal `nosuid`; requiring every option to equal `nosuid` would be wrong.
- **Across collected filesystem Items:** at least **one filesystem** must be selected, and **every selected filesystem** must satisfy that mount-option check. If the selector finds two mounts and just one has `nosuid`, the Test fails.

In plain English: **“Find at least one matching filesystem; every filesystem found must include `nosuid` among its mount options.”** These are two independent collections and two independent quantifiers, not a contradiction.

**Selector caveat:** the current source-derived `matches_regex: .*\\/home` can select more than just an exact `/home` mount. This is why the Test-level `all` matters. Tightening that regex may be desirable for new content, but must **not** be silently done during source-faithful conversion.

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

## Need more than single-Test examples?

The [three complex source-backed Assessments](COMPLEX-REAL-WORLD-EXAMPLES.md) show the **full multi-Test logic** for Windows role-dependent user rights, DNS zone/Variable processing and Apache configuration discovery. This is where the Slang-inspired readability goals meet actual OVAL complexity. The short samples above are deliberately the entry point, not the completeness argument.

## Suggested review flow (20 minutes)

| Time | Open this sample or evidence | Question for reviewers |
| --- | --- | --- |
| **0–5 min** | [Three embedded NG examples](#three-ng-examples-from-the-actual-six-stig-r3-content) | Are the Object, Item and field requirements clear? |
| **5–10 min** | [Win11 SV-253254 registry source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253254.automated.yaml) and [SV-253495 WMI record excerpt](ASSESSMENT-REVIEW-TECHNICAL.md#1-windows-wmi-a-record-is-not-its-field) | Do missing/duplicate record fields, errors or incomplete Items change the intended result? |
| **10–15 min** | [RHEL9 SV-257889 faithful vs `for_each` example](../foreach-07/REVIEW.md#production-example-rhel-9-sv-257889) and [Windows Server 2025 SV-278001 conditional sketch](../conditional-10/EXAMPLES.md#windows-server-2025-sv-278001) | Which rewrites preserve OVAL semantics? **Both are research illustrations; the conditional sketch is not a proven rewrite.** |
| **15–20 min** | [Incomplete-Item result table](INCOMPLETE-ITEM-SEMANTICS-REVIEW.md#the-bug-the-added-tests-caught) and [machine-readable six-state boundary cases](../../../tests/v04-semantic-boundaries/cases.json) | Which outcomes or collection scenarios need new counterexample tests? |

**Important conditional warning:** `OR(AND(G,P),AND(NOT G,Q))` is **not generally equivalent** to a procedural `if G then P else Q`; [81 of 216 generic six-state combinations differ](../conditional-10/CONDITIONAL-REVIEW-QUESTIONS.md). The converter does not silently replace that OVAL Boolean graph.

## What has — and has not — been demonstrated

- **Passed:** current-main 0.3 conversion and compilation for the six representative STIGs ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38829943744)); r3 independent **JSON schema + reference** check on **4,001 documents** with **2,958 resolved Rule choices** ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38830995691)).
- **Not yet proven:** independent **0.4 native YAML/JSON-to-`.scapng` builds** ([#232](https://github.com/vanderpol/scap-ng/issues/232)), live scanner parity, and universal lossless `for_each` or `if/else` rewrites ([#229](https://github.com/vanderpol/scap-ng/issues/229)). Research vocabulary is **not ratified**.

## What feedback would help most

Useful feedback is a concrete **OVAL expression / collected Item set / expected six-state result**, or a source case that may require distinct Test, State, record or field requirements. We will add semantic cases to [#229](https://github.com/vanderpol/scap-ng/issues/229) and vocabulary questions to [#227](https://github.com/vanderpol/scap-ng/issues/227). See the [technical preview](ASSESSMENT-REVIEW-TECHNICAL.md) for further examples and evidence; feedback is not Board approval or implementation authorization.
