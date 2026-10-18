# 0.4 Assessment editor — sample-data test bench (research)

**18 October 2026 · [Issue #241](https://github.com/vanderpol/scap-ng/issues/241) · NON-NORMATIVE UX/authoring research.** Owner request: a regex101-style space where a content author supplies system evidence and immediately sees true/false, explanation and test cases. **Not a request to implement a compiler, scanner or alternate 0.4 authoring grammar.** See current language issues [#227](https://github.com/vanderpol/scap-ng/issues/227) and [#235](https://github.com/vanderpol/scap-ng/issues/235), and independent semantics [#229](https://github.com/vanderpol/scap-ng/issues/229).

## The primary experience

A content author edits a real Assessment while exercising it on **simulated collected system evidence**. The editor does **not** connect to a real host, execute shell commands, query WMI, or need production credentials for this workflow. Its feedback must make the distinction among these layers obvious:

1. **Source collection:** which Object/capability produced the Item(s), and its `complete/incomplete/error/not_collected/not_applicable/does_not_exist` flag.
2. **Item existence:** none, one, more than one; these are collected Items, **not fields or expected literals**.
3. **State/field matching:** presence, type, and zero/one/many values on **each Item**; `require` at the applicable scope, `states_match`, record-member requirements, `value_match` on expected arrays.
4. **Test results:** individually evaluated against each selected Item with the six states, reason and source predicate path.
5. **Assessment result:** the exact authored `evaluate` tree applied to actual Test outcomes; *not* a generalized Rule compliance mapping.

The result should be **true, false, error, unknown, not_evaluated, or not_applicable**, not a red/green-only verdict. The summary can say *Assessment true → likely passing a positive compliance requirement* where appropriate, but the Rule/Benchmark layer determines **pass/fail**; do not assume all Assessments are positive-polarity or that not_applicable means passing.

## Relevant existing tools — patterns to reuse, not runtimes to copy

- [regex101 documentation: saved unit tests](https://support.regex101.com/editor/unit-tests/) explicitly distinguishes interactive sample strings from repeatable **expected-result assertions**. Its [accepted/rejected cases guide](https://docs.regex101.com/guides/test-several-cases/) shows that a negative input is a test that **passes** when correctly rejected. That maps directly to Assessment test cases where an expected `false` should produce a green *fixture regression* result.
- [regex101 privacy documentation](https://docs.regex101.com/) describes matching/testing locally; for SCAP-NG, synthetic data should be the default and browser-local operation preferable where the capability and semantics can be safely implemented. We must **not** assume source OVAL regex dialect equals the browser's JavaScript regexp.
- The [Open Policy Agent Rego Playground](https://play.openpolicyagent.org/) demonstrates a compact **policy / input JSON / output** loop with an explicit Evaluate operation and examples; it also provides a **coverage view**. For SCAP-NG, the equivalent is Assessment source / typed collected Items & statuses / six-state Test and Assessment trace, including where a predicate was not evaluated.
- **Differentiator:** Neither a generic regex matcher nor a generic JSON input pane by itself models SCAP-NG's Item completeness, variable expansion, correlated records, `collected_items_require` vs nested State-field `require`, and unknown/error/not-applicable propagation. These cannot be replaced with a generic green/red “matches” indicator.

## First screen: one file, one scenario, three meaningful areas

```text
Assessment: home-mounted-nosuid-option        Scenario: [Complete, compliant ▼] [Run]
--------------------------------------------------------------------------------------
AUTHORING SOURCE            SAMPLE COLLECTED DATA             RESULT AND EXPLANATION
  linux.partition             Source: home-mount               Assessment: TRUE
  where mount_point           Status: [complete ▼]              Test: TRUE
  matches /home               Items: 1                          Item 1: TRUE
  mount_options equals          mount_point: /home                 mount_options: TRUE
  nosuid                       mount_options: [rw,nosuid]          - rw: nonmatch
  collected_items_require                                          - nosuid: match
    at_least_one_exists                                         Why: one Item exists;
    and_all_match                                               every selected Item has
                                                                at least one nosuid option
--------------------------------------------------------------------------------------
[+ Add Item] [Remove Item] [Missing field] [Incomplete] [Error] [+ Save case]
Expected: TRUE              Actual: TRUE             [Matches expectation]
```

The display is an **interaction mock**, not the real current GUI or a working general-purpose evaluator. Source and evidence appear side by side to minimize reference hopping. Click a field or Test result to jump to its **exact authored predicate** and source Item. The UI should highlight what was **decisive** versus what was never evaluated or remained unknown. Avoid stack-like panels with empty wrapper levels; present nested records only when the data is actually a record.

### Three information views; one underlying semantics

The owner's existence/matching decision is **not a blocker** for this UX. The editor can offer **two *presentations*** of the same typed Item/field requirement, without persisting two different Assessment YAML grammars:

- **Structured view**: “Item existence = one or more; Matching Items = all”. For a `mount_options` field: “Value existence = one or more; Matching values = at least one”.
- **Merged-label view**: show `at_least_one_exists_and_all_match` (at Item scope) or `at_least_one_exists_and_some_match` (at field scope), alongside a plain-English explanation.

Both views must reference **the same single canonical requirement**, versioned AST node, input Items, and result. Switching views must not change source meaning or execution, and should flag any ambiguous “only one matches” versus “only one exists” label. **Do not implement alternate YAML dialects merely to A/B test the editor.** Record which view produces fewer wrong predictions on real source-backed examples before choosing the normative grammar.

## Minimum authored scenario: independent expected vs actual

Store two conceptually different pieces:

- **Input evidence**: explicitly selected Assessment/Source revision, collection flag, typed Item entities/record subfields, original/reference provenance, exact editable bytes and synthetic-data label. The user may provide partial observations.
- **Expected outcome**: independently authored expected six-state Test/Assessment result, optional expected per-Item/per-field results, and the specific normative chart/source reason. It must **not** be autogenerated by the implementation being tested.

The editor computes a third **Actual result** only if its implementation supports **the complete required evaluation slice**. A scenario has statuses **PASS (actual equals expected)**, **FAIL (mismatch)**, **UNSUPPORTED (needed source feature not implemented)**, **INVALID SAMPLE (type/shape/status conflict)**, or **NOT RUN**. A fixture assertion PASS is not synonymous with compliance TRUE. A deliberate expected FALSE with actual FALSE **passes the regression test**.

Samples should be reusable:
- authors can save **multiple cases per Assessment** and rerun them automatically after each edit;
- each sample has an explicit expected outcome and immutable source revision/hash in the test report; stale source hashes are visible instead of silently comparing against changed semantics;
- “show why” includes collection flags, selected Item counts, Test IDs, `states[index]`/record/field paths, decisive match/absence and six-state outcome, with clickable links to evidence;
- export the **fixture and report** into GitHub for reviewer reproducibility; keep fixtures **separate from compiled/signed scan-content bundles**.

## Four real source-backed initial cases

These are design exercises, not assertions of general runtime support.

| Case | User edits in sample pane | Expected research boundary |
| --- | --- | --- |
| [Linux `/home` nosuid](FULL-01-linux-home.md) | One `linux.partition` Item with `mount_options: [rw,nosuid]`, then omit `nosuid` or remove all Items; toggle complete/incomplete | Complete one match → true; complete one nonmatch → false; complete zero Item → false; incomplete one matching Item → unknown, not an unconditional pass |
| [Windows WMI domain role](FULL-03-win11-rights.md) | `win32_computersystem.DomainRole` record values `1`/`3`, `0`/`2`, or missing `domainrole`; change record count | Distinct roles match their corresponding Test; **missing record member is not a missing collected Item** and may be error; original [pinned WMI record reference fixture](../../../tools/v04_a_wmi_domainrole_source_fixture.py) supplies expected boundaries |
| [Windows 11 seven-Test `evaluate` tree](FULL-03-win11-rights.md) | Feed **explicit Test outcomes** for the role and trustee checks before full collector implementation | Three OR alternatives, including independent Everyone path; visually show **true/false/error/unknown** Test leaves and exact six-state aggregation. This tests the result graph, **not** WMI or userright collection |
| [Linux derived account dotfiles](FULL-02-linux-files.md) | Users → `home_dir` projection → `for_each` directory Items → files, including absent root/non-system files and incomplete source | Show selected source lineage and different `may_be_absent_and_all_match` vs `at_least_one_exists_and_all_match` policies; mark **UNSUPPORTED** for runtime slices not yet proved |

Use the [independently pinned existence/record/Set/partial fixtures](../../../tests/v04-semantic-boundaries/cases.json), [0.4 semantic boundary tests](../../../tools/test_v04_semantic_boundary_cases.py), and [bounded Linux Test-to-expression pilot](../../../tools/v04_a_linux_mount_expression_bridge.py) as **sources for acceptance expectations**, not as evidence that all Assessments currently execute. The current research Boolean result executor accepts **already supplied Test values only**: [expression boundary](../compact-authoring-04/EXPRESSION-RESULT-BOUNDARY.md). For unsupported Test/collector features it must say so.

## Essential negative and security cases

1. **Zero Items versus missing field**: `items: []` with `complete` ≠ one Item missing `mount_options` or Windows `result.record.fields.domainrole` ≠ field value `""`.
2. **Partial stream**: one currently matching Item in an incomplete “all match” collection is **unknown**; one decisive nonmatching Item may already establish **false**. Do not replace unknown with false by convenience.
3. **Multiple Items versus multiple values on an Item**: `nosuid` in one field array is not an existence guarantee about other matching mount Items; `value_match` over expected values is yet another quantifier domain.
4. **Record correlation**: a required Windows record must not be satisfied by pieces of two different records.
5. **Selector/Filter status**: a Set filter that sees error/unknown or an incomplete source cannot be assumed to include/exclude by a Boolean shortcut.
6. **Unsupported operator**: conditional `if/then/else` with an unsettled six-state contract must be marked unsupported until approved, not assigned an intuitive Boolean `else`.
7. **Regex dialect**: display a regex match preview only using a declared standards-compatible engine; if browser regex behavior differs, label it a **non-authoritative preview**. No user-provided regex or input may execute shell, external scripts, WMI or provider commands.
8. **Evidence privacy**: synthetic samples default; imported scan evidence may contain usernames, paths and secrets. Require opt-in, redaction and explicit “will be saved to repository” notice; no uploading identifiable/sensitive system evidence by default.
9. **No fabricated provenance**: authored sample evidence may cite `synthetic:user-authored`; it is not permitted to masquerade as a real host or original DISA/Joval/OpenSCAP result.

## Incremental engineering boundary — do not hijack 0.4 readability work

| Phase | What the author gets | Prerequisite / honest limitation |
| --- | --- | --- |
| **Design + static sample pane** | Typed Item/field sample entry, preloaded cases, navigable source links, text-only explanations for documented examples, **expected-only** display | Possible without an Assessment evaluator; label “not run” rather than fake actual outcomes |
| **MVP 1: supported local Test slices** | Six-state live result for scoped field comparisons, Item existence and one/none/many under complete/incomplete/error; explicit “unsupported” for everything else | Independent result oracle [#229](https://github.com/vanderpol/scap-ng/issues/229); strict capability/type checks |
| **MVP 2: Assessment `evaluate`** | Named Test result simulation and expression-tree trace, even before real collectors for each Test | Existing [supplied-leaf expression research](../compact-authoring-04/EXPRESSION-RESULT-BOUNDARY.md); show supplied versus observed |
| **MVP 3: complex evidence** | Correlated records, Set/Filter and `for_each`, named source lineage, variable/value expansion and command-result Items | Every enabled slice needs source-backed oracle tests; no blanket “supports all 872 Assessments” claim |
| **Later:** authenticated real evidence | Import well-defined collected Items, compare sandbox vs real scan, test actual provider parity | Scanner/evidence backend, security review and versioned provenance; **not required** for editor's first mock |

Prefer **structured capability-generated forms plus optional raw YAML/JSON**, rather than asking authors to learn every field. Example values should be clearly synthetic, fast to duplicate/mutate, and side-by-side with live source. Avoid storing test data in signed scan distribution.

## The readability experiment this unlocks

Give unprimed authors the same policy and four example observations: complete/true, complete/false, zero Item, incomplete/unknown. Randomize **UI presentation**, not the underlying authored requirement. Compare:
- whether they correctly predict outcomes *before* pressing Run;
- how often they confuse **Item**, **field**, **record** or **expected-value array** quantifiers;
- successful creation of a fifth scenario and its expected result;
- number of clicks/reference hops, time and unsupported confident assumptions.

Test three views: **merged requirement label**, **separate existence + match controls**, and **merged label with immediate expanded explanation**. Determine whether editor affordances make the grammar naming dispute insignificant. **No usability result or preferred winner is claimed before actual review.**

## Decisions deferred deliberately

**Do not decide yet** merged vs separate canonical source fields, `states` vs `expect`, conditional six-state behavior or scope inheritance for Windows records. The editor should render the currently pinned semantics, expose unresolved mappings and collect evidence for a subsequent owner decision. The first usable milestone is a **truthful, reproducible sample-data sandbox with a visible result trace**, not a general-purpose scanner or a new source language.
