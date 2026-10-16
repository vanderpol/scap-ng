# SCAP-NG 0.4 — Assessment authoring technical review

**Pre-alpha Assessment authoring research for technical reviewers.** Start with the [short overview and three NG examples](ASSESSMENT-REVIEW-OVERVIEW.md). We welcome implementation counterexamples and semantic feedback, not approval of a finished standard.

**Downloads:** [10 original OVAL XML ↔ NG YAML/JSON comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015) · [complete corrected six-STIG r3 authoring source](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3). Review the former first; the latter is available for exhaustive inspection.

## The proposal in plain terms

One readable Assessment grammar uses observed **field names as keys** and meaningful operations (`equals`, `matches_regex`, `greater_than_or_equal`) instead of repeatedly spelling out an intermediate State wrapper. We still distinguish separate evaluation populations:

- **`collected_items_require`** — how collected Items must exist and match the Test; **not** a default for fields.
- **`state_fields_require`** — shared requirement for ordinary State fields at a Test or State-group scope, with explicit field-level overrides.
- **Field `require`** — the cardinality of a specific value/field, including a field that may be absent or must have exactly one matching value.
- **`result.record.require` versus `result.record.fields.<name>.require`** — independent nested-record and member quantifiers, without hidden inheritance from scalar fields.
- **`states_match` and `and`/`or`** — alternative States versus logical predicates inside a State; `value_match` remains independent for multiple expected operands.

All authoring keys above describe the **proposed 0.4 research candidate**, not ratified 0.4. Missing required semantics must fail validation rather than silently choose a default.

## Relation to the Slang feedback in Discussion #213

[David Solin's Slang recollection](https://github.com/vanderpol/scap-ng/discussions/213#discussioncomment-18935232) describes **schema-constrained resources**, local discovery/existence/comparison, and AND/OR/XOR composition. Our [one-page before/after](ASSESSMENT-REVIEW-OVERVIEW.md#what-became-more-like-resource-oriented-checks) shows where 0.4 follows those ideas. This is convergence on the **authoring experience**, not an assertion that Slang is the SCAP-NG grammar or that Slang's historic conversions were universally lossless.

The deliberate differences are important:

| Slang-inspired principle | Current native 0.4 candidate | Why it is not yet shorter |
| --- | --- | --- |
| Select a typed resource once | Test `capability`, local Object `capability` and selector | The Test and Object are individually typed. Dropping repeated type information would need a strict compiler/schema rule, not an implicit authoring default. |
| Define discovery and checking together | Test-local `object` and named `states` field predicates | Selection and expectation stay distinct but adjacent; shared Objects can be referenced. |
| State presence and matching simply | `collected_items_require`, `state_fields_require`, leaf `require` | Collection and nested-record/field populations differ, including empty/incomplete/error cases. |
| Compose checks using Boolean logic | `evaluate: {all/any/one/odd}` over named Tests | OVAL's six technical results, dependencies and evidence cannot be replaced with untested Boolean shortcuts. |

A historic example resembling `suid: false` **is not a proven replacement** for `linux.partition.mount_options: {equals: nosuid}`. The real source must remain faithful; adding derived fields requires its own collector and six-state proof ([Slang research](../slang-feedback-04/README.md)).

## Title guidance: identify the check, not every intermediate node

- **Test `test_title`:** summarize what the full Test verifies, including its expected outcome. A Test should make sense to a reviewer without reopening the Object.
- **Private inline Object `object_title`:** **optional** in the current draft; omit when it merely repeats the Test title. A description may still help with non-obvious collection.
- **Shared named Object `object_title`:** valuable because multiple Tests can reuse its collection independently; use a distinct description of **what is collected**, not the pass/fail conclusion.

This reflects recommended **authoring style**, not a new normative rule. The present [draft schema](../../../schema/v0.4.0/assessment.schema.json) requires the `object_title` **property** for named shared Objects but permits a null value; [inline Objects](../../../schema/v0.4.0/capability-common.schema.json) do not require that property. Whether shared titles should be non-null is tracked in [#234](https://github.com/vanderpol/scap-ng/issues/234). The [simple Linux Test example](ASSESSMENT-REVIEW-OVERVIEW.md#three-ng-examples-from-the-actual-six-stig-r3-content) omits a redundant null display-only, leaving published content unchanged.

## Three deeper NG examples — directly from r3 source

The short examples on the [overview](ASSESSMENT-REVIEW-OVERVIEW.md) show Linux mount selection, Windows State alternatives, and user-right assignment. These additional clips are **unchanged excerpts from actual linked Assessments**, not complete, standalone Assessments.

### 1. Windows WMI: a record is not its field

Windows 11 [SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml) has five `windows.userright` and two `windows.wmi.query` Tests. This WMI State has *two* requirements: one for the record and one for its `domainrole` member. The next State permits another `domainrole`.

```yaml
      states:
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '1'
            require: at_least_one_exists_and_all_match
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '3'
            require: at_least_one_exists_and_all_match
```

The [Guests user-right Test in the short overview](ASSESSMENT-REVIEW-OVERVIEW.md#three-ng-examples-from-the-actual-six-stig-r3-content) makes the contrast: `at_least_one_exists_and_some_match` applies to collected **Items**; its `trustee_name.require: at_least_one_exists_and_all_match` applies to the **field's values**. They cannot be merged.

### Composing checks without a separate Boolean language

The same Windows 11 [SV-253495 Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml) contains this **verbatim** `evaluate` expression. It combines role-specific groups and a separate acceptable `Everyone` branch while retaining the named Tests:

```yaml
  evaluate:
    any:
    - all:
      - test: system-non-dc-domain-joined-windows-server-or-workstation-test
      - test: deny-log-on-through-remote-desktop-services-local-account-test
      - test: deny-log-on-through-remote-desktop-services-guests-test
      - test: deny-log-on-through-remote-desktop-services-domain-admins-test
      - test: deny-log-on-through-remote-desktop-services-enterprise-admins-test
    - all:
      - test: system-standalone-windows-server-or-workstation-test
      - test: deny-log-on-through-remote-desktop-services-guests-test
    - test: deny-log-on-through-remote-desktop-services-everyone-test
```

This is the parallel to Slang's **AND/OR** composition. The draft also supports `one` and `odd` combination modes, but the excerpt **does not demonstrate those modes**, nor does it justify rewriting this tree as procedural `if/else`. It is especially important not to confuse `one` (exactly one matching branch) with `odd` (an odd number of matching branches).

### 2. DNS: “only one and it matches”

Windows Server DNS [SV-259345](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml) retains a precise field-level `only_one_exists_and_matches` rule:

```yaml
      states:
      - stdout_line:
          require: only_one_exists_and_matches
          equals: 'True'
```

The Test also declares `collected_items_require: at_least_one_exists_and_all_match` for collected Items. “Exactly one field value matches” and “all collected Items match” are **different scopes**, even when the author sees only one `stdout_line` in practice.

### 3. Apache: preserve actual runtime dataflow

Apache [SV-214228](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml) still needs dynamic Variables because a config path is assembled from detected paths. The converter **does not** replace this with an invented literal or claim a universal lossless `for_each` rewrite. Typed literal components in this particular dynamic expression are still present in the r3 source; datatype simplification is not universal.

```yaml
    filepath-http-conf-file-variable:
      title: Filepath to http conf file
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-httpd-root-variable
        - literal:
            value: /
            datatype: string
        - variable: relative-server-config-file-variable
```

Another Test in this Assessment permits a missing optional directive while requiring matching values if present:

```yaml
      states:
      - stdout_line:
          require: may_be_absent_and_all_match
          matches_regex: \s*KeepAlive On
```

The full file contains more collection and Variable dependencies; these excerpts are for comprehension, not a replacement for the authoring archive.

## The semantic questions we need answered

1. **Absent versus incomplete:** Does the proposed combination of collected-Item, ordinary field and record requirements retain OVAL `true`, `false`, `unknown`, `error`, `not_evaluated` and `not_applicable` outcomes when Items are missing, partial or failed? [Boundary review](INCOMPLETE-ITEM-SEMANTICS-REVIEW.md).
2. **Conditional expressions:** Source OVAL `OR(AND(G,P),AND(NOT G,Q))` and procedural `if G then P else Q` disagree in **81/216** generic six-state cases. We must preserve source-faithful `evaluate` trees unless a particular rewrite is proven, including skipped-branch evidence. [Detailed questions](../conditional-10/CONDITIONAL-REVIEW-QUESTIONS.md).
3. **Iteration and Variables:** A source-backed `for_each` illustration can be authored and tested, but that does **not** prove universal automatic rewriting of dynamic ObjectComponent graphs. Preserve Sets, Filters and runtime provenance until equivalence is established.
4. **Evidence:** Should a source→NG correspondence table include exact Item counts, missing/error markers, Object/Variable provenance, and decisive reason codes for scanner auditability?

## Evidence and remaining gates

| Independently supported | What it does **not** establish |
| --- | --- |
| [Six real STIGs converted/validated/compiled with 0.3](https://github.com/vanderpol/scap-ng/actions/runs/38829943744) | That 0.4 research files compile or that two scanners agree |
| [r3 YAML/JSON source proof](https://github.com/vanderpol/scap-ng/issues/228) + [4,001 JSON documents statically validated](https://github.com/vanderpol/scap-ng/actions/runs/38830995691) | Native 0.4 JSON-to-signed-bundle compilation |
| **872 unique automated Assessments / 1,375 native Tests** in the deduplicated r3 archive | **1,396 Assessment / 2,144 Test appearances** counted across six Benchmarks are not unique files |
| **2,958/2,958 Rule choice links resolved**, no duplicate Assessment IDs | Semantic runtime parity of referenced Assessments |
| **1,106 fewer explicit field requirement declarations out of 2,550 (43.4%)** in the scope research | Fewer runtime tests or less collected data |

Schema/source/identity checks are promising, but **no SCAP-NG 0.4 scanner is yet validated**. Independent native YAML and JSON compilation is tracked in [#232](https://github.com/vanderpol/scap-ng/issues/232); evaluator conformance in [#229](https://github.com/vanderpol/scap-ng/issues/229). The separate [0.3 source-converter release gate #226](https://github.com/vanderpol/scap-ng/issues/226) covers the broader input corpus. Published 0.3 and immutable preview releases are unchanged.

**Please send feedback as a concrete source node → observed Item/field population → expected six-state result → candidate NG expression.** That gives us a reusable conformance test, not just a vocabulary preference. [Assessment grammar decisions #227](https://github.com/vanderpol/scap-ng/issues/227) · [semantics #229](https://github.com/vanderpol/scap-ng/issues/229) · [capability schemas #228](https://github.com/vanderpol/scap-ng/issues/228).
