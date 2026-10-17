# English-first 0.4 Assessment authoring — source-compatibility research

**Pre-alpha experiment; NOT adopted grammar or scanner-conformance evidence.**

**[FINAL GROUND-UP ALTERNATIVE: evidence → atomic claims → passing cases](PROOF-FIRST-GROUND-UP-ALTERNATIVE.md).** Instead of further renaming `require`, this research reorganizes an Assessment around what is collected, what precisely must be true, and which named combinations establish compliance. Demonstrates original RHEL `nosuid`, complete Windows WMI record-State alternatives, dependent Linux files, DNS and Apache, including unresolved source-only cardinality/missing-field semantics. **The simple RHEL case is longer and the replacement has NOT been source-lowered or six-state verified. This is a product-design experiment, NOT the new leading approved YAML grammar.** The most promising idea is a source-derived auditor proof sheet with named passing routes and a guided editor, even if the current split-requirement grammar wins as the underlying standard.


**CURRENT CANDIDATE — [canonical SCAP-NG comparison operators + consistent Item/record/State grammar](canonical-operators/report.md).** Pinned six-STIG conversion preserves **871/872 full automated Assessments (1,374/1,375 Tests)** and removes **1,494** experimental field comparison aliases (`is` → `equals`, `equals_ignoring_case` → `case_insensitive_equals`, `at_least` → `greater_than_or_equal`, etc.). It retains the verified simplifications: no `condition`/`scope` wrappers, no `some` synonym, explicit `states.and/or` and `fields.and/or`, and redundant record existence Boolean flags removed. The **[updated six-pattern auditor gallery](AUDITOR-SAMPLE-GALLERY.md)** links to complete on-GitHub Assessments: [RHEL nosuid](canonical-operators/linux-home.canonical.research.yaml), [Windows 11 seven-Test WMI/rights](canonical-operators/windows-wmi-rights.canonical.research.yaml), [nested Linux files](canonical-operators/linux-files.canonical.research.yaml), [DNS](canonical-operators/dns.canonical.research.yaml), and [Apache](canonical-operators/apache.canonical.research.yaml). The one known contradictory bootloader source Assessment remains rejected; independent scanner/evidence parity is still unproven. **Research only, not normative v0.4.**

**Predecessor:** [consistent quantifiers + structural `states`/`fields` grouping](consistent-quantifiers/report.md) — same 871/872 source coverage, but examples still use now-discarded field comparison aliases.

**[Item-versus-field combined-scope audit](scope-targets/scope-target-audit.md)** — tests whether a future `scope: items_and_fields` shorthand earns its place in v0.4. Pinned source shows **922** Tests with ordinary scalar fields: **567** have matching *named* Item/field requirements (**323** one-field, **244** multi-field or multi-State) and **355** have at least one different field requirement. These are raw source-mode counts, not lossless compiler validation of a new shorthand. Prior State/Test field-scoping proof already removed **1,106/2,550** redundant declarations. Do **not** merge Item and field populations or allow scalar field policies to cascade into records. The current grammar and release are unchanged.

**Earlier intermediate proof:** [flat `require` without `condition`](flat-require-experiment/report.md) — includes the now superseded `scope:` and `match: some` authoring presentation.

**[NEW — merged vs split requirement proof](require-presentation-comparison/report.md):** both presentations reconstruct 871/872 full automated Assessments (1,374/1,375 Tests) from the pinned six STIGs; 1,742 invalid-input mutations rejected. Compare [RHEL split](require-presentation-comparison/linux-home.split.research.yaml) / [merged](require-presentation-comparison/linux-home.merged.research.yaml), [Windows WMI split](require-presentation-comparison/windows-wmi-rights.split.research.yaml) / [merged](require-presentation-comparison/windows-wmi-rights.merged.research.yaml), and [Apache split](require-presentation-comparison/apache.split.research.yaml) / [merged](require-presentation-comparison/apache.merged.research.yaml). **Neither author-facing grammar is approved**, and the 201 `all_exist` source Test distinctions are preserved (not normalized) pending six-state runtime/evidence proof.

Tracking: [#235](https://github.com/vanderpol/scap-ng/issues/235) (research), [#227](https://github.com/vanderpol/scap-ng/issues/227) (vocabulary), [#229](https://github.com/vanderpol/scap-ng/issues/229) (semantics).

**[Earlier scoped `and` / `or` authoring + editor proof](SCOPED-AND-OR-EDITOR-PILOT.md)** — real Windows WMI, Linux permissions and six-STIG source-exact examples. Sibling `scope: states|fields` with `and|or`, validated autocomplete for four native capabilities; 871/872 source-exact Assessments, 3,484 malformed-input guards, and original NIWC bootloader violation identified. [CI proof](https://github.com/vanderpol/scap-ng/actions/runs/39034513658).

**[Exactly-one existence: official truth tables, seven source selectors, and elimination of redundant combined quantifiers](EXACTLY-ONE-EXISTS-TRUTH-TABLE.md)** — source and 12,432-case regression evidence. Proposes one clearly scoped `items: exactly_one` choice rather than several special labels; **no normative changes**. [Passing test CI](https://github.com/vanderpol/scap-ng/actions/runs/39031176661).

**[OVAL exceptional-feature retention gate](OVAL-EDGE-FEATURE-RETENTION-GATE.md)** — source-backed criteria for core, advanced, importer-only compatibility and potential deprecation. Rare usage triggers semantic review; no unsupported source behavior is silently removed. [Rare operator guards passed](https://github.com/vanderpol/scap-ng/actions/runs/39030549202).

**[Original OVAL Test author/source census](reports/source-oval-author-edge-census.md)** — 2,140 original six-STIG OVAL Tests (1,818 DISA, 322 NIWC/NAVWAR), stratified by original Test IDs and contrasted with 1,375 native Tests; 201 native all-exist cases have 198 DISA and three NIWC *comment+mode source-ID candidates*, not confirmed converter lineage. [Passing CI](https://github.com/vanderpol/scap-ng/actions/runs/39030379635).

**[Original OVAL State/Set/Variable/operator edge census](reports/source-oval-semantic-edges.md)** — exact-one Test matching, State-field cardinality, Object Set difference, nested Variable functions and logical operations separately inventoried by source author. [Passing CI](https://github.com/vanderpol/scap-ng/actions/runs/39030633098).

**[DISA SCAP 1.3 versus NIWC SCAP 1.4 OVAL source provenance](OVAL-SOURCE-PROVENANCE-BOUNDARY.md)** — original Definition/Test/Object/State/Variable IDs verified for both source organizations; inherited DISA checks are not a valid sample for interpreting use of new NIWC OVAL 5.12.3 authoring options. The mixed 201-Test Item-creation census must be joined back to original OVAL IDs before reporting author-specific behavior. [Passing source-ID CI](https://github.com/vanderpol/scap-ng/actions/runs/39029699446).

**[201-Test all-exist equivalence](reports/all-exist-native-equivalence.md)** — source-Test classification: 127 State-free and 74 State-bearing. All agree with at-least-one on complete, existing-only Item populations; incomplete State-bearing and mixed Item-status differences remain explicit. [CI proof](https://github.com/vanderpol/scap-ng/actions/runs/39029016539).

**[Item creation settings in all 201 cases](reports/all-exist-item-creation.md)** — 132 textfilecontent54 Tests use `all_object_elements_fullfilled`; three NTUSER use `key_and_name_exist`. [CI census](https://github.com/vanderpol/scap-ng/actions/runs/39029190471).

**[Experimental real-Item validation schema](native-existing-item.profile.schema.json)** — enforces root `exists` for confirmed real native Items and retains missing/error field/collection status; [nine research regression tests](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_native_existing_item_profile.py) [passed in CI](https://github.com/vanderpol/scap-ng/actions/runs/39029351309). This is **not** the normative 0.4 result schema.

**[Existing-resource-only native Items — proposal](NATIVE-ITEM-EXISTENCE-POLICY.md)** — prohibits fabricated absent root Items in native results, preserves missing field/resource and failure evidence, and explains why Test `all_exist` still needs separate error/incomplete review. [Executable boundary guards](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_nonexistent_items_policy.py) passed in [GitHub CI](https://github.com/vanderpol/scap-ng/actions/runs/39028682792). Research only; the 0.4 normative schemas were not modified.

**[All 201 `all_exist` Tests — source-selection and reuse forensics](reports/all-exist-source-forensics.md)** — examines open-ended pattern searches, fixed and multi-value selectors, dynamic discovery, State-free versus State-bearing checks, and reused Objects. Original OVAL 5.12.3 documentation conflicts on Test-level equivalence under mixed Item statuses, and partly missing Items may be reported optionally. Source choices remain unchanged pending semantic and provenance proof.

**[New: fixed `items` + `condition` requirement-choice coverage, six-STIG audit](reports/fixed-requirements-six-stig.md)** — counts precisely which existing Item/field existence-and-matching modes a small dropdown vocabulary covers and links individual residual Tests. Two focused scoped choices raise source-annotated requirement coverage above 98% of unique automated Assessments; three choices raise it above 99%. This is **not complete grammar, Rule coverage, usability, or scanner semantic parity**. Remaining source cases are reviewed individually before any rewrite or language extension.

**Goal:** A security administrator understands an Assessment without knowing OVAL; an implementer derives exact semantics without guessing.

**[Browse six graded auditor-friendly examples](AUDITOR-SAMPLE-GALLERY.md)** — simple Linux/Windows checks through Windows WMI records, DNS, Apache, and dependent Linux file collection; each links to complete YAML on GitHub.com.

**[Complexity stress test and redesign iterations](COMPLEXITY-STRESS-TEST-ITERATIONS.md)** — the difficult Linux, Windows, DNS and Apache cases; one grammar, typed source dependencies, explicit semantic hazards, and a seven-Test Windows proof of removing duplicate `inspect` at named `from` references. Native Apache/DNS redesign is still unproven research.

**[Apache 18-variable dependency map](APACHE-DEPENDENCY-REDESIGN.md)** — six human-understandable stages, two distinct file-discovery branches, four preserved checks, and the contract needed before a native collector can replace shell commands.

**[Read the check-level existence audit](TEST-ITEM-EXISTENCE-REVIEW.md)** — 1,375 source Tests, including why `none` needs no State and why `all_exist` is still unsettled in OVAL's own documentation.\n\n**[Review the auditor-first candidate](AUDITOR-FIRST-CANDIDATE.md)** — a complete, source-reversible language proposal emphasizing security-auditor reading order and explicit Item existence versus matching. Research only; original OVAL runtime/evidence parity remains unproven.

**[Review the before-and-after examples](BEFORE-AFTER-REVIEW.md)** — five complete real 0.4 vs experimental English-first Assessments, each with a short excerpt, direct GitHub links and focused questions for author feedback. **This is the practical decision review.**

**[Start here: decision brief](DECISION-BRIEF.md)** — what is proved, what remains unproved, and what evidence would justify adopting (or rejecting) the English-first grammar. The detailed report statistics below are supporting evidence, not the adoption decision.

**[Authoring consistency working draft](AUTHORING-CONSISTENCY-WORKING-DRAFT.md)** — one proposed location for each collection operation, set-composition vocabulary, named-source resolution, and acceptance gates. This is research guidance, **not an approved schema**. The [source-backed examples](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md) now show the Linux referenced collection in the same English-first style rather than switching back to the 0.4 source vocabulary.

## Six-STIG reports you can read on github.com

**[Open the GitHub-hosted six-STIG research reports](reports/README.md)** — the preferred entry point on restricted networks and phones. This folder contains a readable summary of the last independently verified results and is configured to receive each new report as ordinary Markdown and, where practical, JSON files in the repository. **No Actions artifact download is required to read this page.**

The [six-STIG workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-english-first-census-04.yml) still creates optional ZIP artifacts, but those may use non-github.com download domains and are not a viable primary distribution method. New reports must be confirmed as successfully published before being described as verified. The [reference graph audit source](https://github.com/vanderpol/scap-ng/blob/main/tools/research_english_first_04_references.py) and [GitHub publication source](https://github.com/vanderpol/scap-ng/blob/main/tools/research_english_first_04_publish.py) are also available directly.

## Six-state research checkpoint — 125,268 matched generic cases

The [passing six-STIG and six-state workflow](https://github.com/vanderpol/scap-ng/actions/runs/38921900743) adds two independent implementations of **generic OVAL 5.12.3 Item outcome aggregation**, cross-checking **all 10 currently mapped existence × Item-match combinations plus five State-free presence modes** over complete/incomplete/not-collected/error/not-applicable/does-not-exist flags and six individual result statuses. **125,268 generic cases agreed**. **12 empty-population cases remain undefined by our generic reference helper** and are explicitly excluded, never treated as passes.

The **single remaining source-shape exception** is the real Linux bootloader Assessment that requires `none_exist` but includes a State comparison. A [pinned-source boundary matrix](https://github.com/vanderpol/scap-ng/blob/main/tools/research_english_first_04_none_exist_state_boundary.py) verifies outcomes when Items exist or collection is incomplete/error/not collected, but does **not** settle the `complete + 0 Items + attached State` corner case. In that scenario the current generic reference raises because it cannot aggregate an empty State-result set. Do **not** silently drop the State or convert `none_exist` to `none_match`; independent interpretation and original XML evidence are required.

The full source-structure census now stands at **871/872 complete unique automated Assessments**, representing **1,374/1,375 named Tests**. The *earlier* research-only compact presentation of these 871 Assessments removed roughly **4.5% of YAML characters** without altering their original Assessment dictionaries. A **new direct-Set-operation change** (eliminating `combine` before `union`/`difference` and preserving one-operand Sets) has been committed with regression guards, but its six-STIG CI result must be reviewed before updating that figure. The human-readability judgment still requires actual reviewers and more work on complex Sets, WMI records, and Variable command graphs.

**What passed:** reference-model equality of generic result aggregations and source-structure inversion. **What has not passed:** independent end-to-end OVAL XML → native collections → scanner/evidence parity, including real multi-valued States and missing data. The exact wording of the 0.4 normative authoring grammar remains open.

## Human reading order (research presentation rule)

Assessment authors should encounter **source data before assertions**. We found that the early experimental translator emitted `require` (State) above its corresponding `gather`/`where`/`collect` (Object); this is confusing even though YAML mapping order does not affect the scanner's evaluation semantics. Both [the base research translator](../../../tools/research_english_first_04_complex.py) and [compact research renderer](../../../tools/research_english_first_04_compact_layout.py) now emit a canonical display order:

```yaml
check: /home is mounted with the nosuid option
inspect: linux.partition
where:
  mount_point:
    matches_regex: '.*\\/home'
require:
  mount_options:
    includes_value: nosuid
```

For more advanced Assessments, put named `sources` **before** `checks`; within each check use `check` → `inspect` → `from` / `gather` / `where` / `collect` → `input_from` → `require` → `report_elements`; finally put the whole-Assessment `evaluate` tree after the checks. This is one YAML grammar with a consistent display order, **not procedural ordering or a second syntax**. The complete six-STIG CI asserts this order while also proving exact source round-trip. Vocabulary is still experimental, and shortening a requirement must separately preserve native cardinality/error semantics.

## Start with four diverse, complete research Assessments

**[Concise external reviewer one-pager](RESEARCH-REVIEW-ONE-PAGER.md)** · **[Read the four-source example review](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md)** and [download all four complete candidate YAML Assessments](https://github.com/vanderpol/scap-ng/actions/runs/38913249970/artifacts/12051575856) (RHEL user→file collection with Sets/`for_each`, Windows role-dependent user-rights + WMI records, DNS zone-signing Variables, and Apache multi-file configuration). **All four complete Assessment source dictionaries reconstruct exactly** under the research lowerer, with source-backed CI. Neither a normative 0.4 grammar nor an independent scanner/OVAL semantic-equivalence proof.

## Latest full-Assessment source inversion — 871 of 872

[PASS: six-STIG source-structure CI](https://github.com/vanderpol/scap-ng/actions/runs/38921900743): **871/872 distinct automated Assessments (99.9%)** reconstruct their **entire original 0.4 r3 Assessment dictionaries exactly**, encompassing **1,374 named Tests**. The fixed six-STIG release ZIP has an enforced SHA-256, and **871 mutation guards** reject unexpected authoring requirements rather than hiding unsupported constructs. **One source Assessment remains rejected** (none_exist with an attached State). This is **not** original SCAP 1.4 scanner parity, independent six-state execution/evidence conformance or a readability-user-study result.

The progression from 39 Test-only cases → 800 whole Assessments → 826 → 837 → 848 → 865 → 868 → 871 reflects real additions to the reversible experimental grammar, including typed value comparison metadata, full collection graph preservation, direct Test input Variables, Windows record scopes and explicit local field overrides. None of these authoring research additions changes the 0.4 normative draft or immutable six-STIG r3 preview.

**Human factors gate remains open.** Some unusual forms are still wordy: exact source inversion demonstrates no structural information was lost, **not** that the YAML is already as clear as plain English. Compare the [source-backed readable examples](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md) and the [external one-page review](RESEARCH-REVIEW-ONE-PAGER.md) before choosing a vocabulary.

## October 16 corpus checkpoint — source-backed, fail-closed

- [Full six-STIG structural census](https://github.com/vanderpol/scap-ng/actions/runs/38908329365): **872 unique automated Assessments / 1,375 distinct named Tests**, from the SHA-256 pinned r3 authoring ZIP. **918** Tests use simple scalar State fields, **675** have native `collect` parameters, **387** have no States, **219** use State-level logical groups, **66** use records, **145** use Sets, **139** reference Variables inside their Object definitions, and **114** have **no explicit Object** (legitimate built-in collector capabilities, not necessarily broken content). These categories overlap.
- [Presence-only grammar proof](https://github.com/vanderpol/scap-ng/actions/runs/38909206051): **63/387** State-free Tests have exact source Test-node reconstruction using an explicit `require.collected_items: none | exactly_one | at_least_one | all_exist | may_be_absent` vocabulary plus their original `where`/`collect` definitions. **324** have more complex Object/Set/metadata structures and were rejected, not dropped. **126** negative validation guards passed.
- [DNS/Apache command Test proof](https://github.com/vanderpol/scap-ng/actions/runs/38908788030): **3** additional distinct Test nodes reconstructed exactly, keeping command/Variable references, Bash/PowerShell selection, original error flags and field/cardinality requirements. **12** mutation guards passed.
- [Previous full-corpus narrow grammar audit](https://github.com/vanderpol/scap-ng/actions/runs/38907185233): **39** source-exact field/selector Test nodes, with **1,336** unsupported by that initial translator. The 63 presence-only and 3 shell examples are disjoint from these 39.
- [Objectless native system-wide Test research](https://github.com/vanderpol/scap-ng/actions/runs/38909973142): **77/114** source-exact Test reconstructions across Windows audit policies, password/lockout policies and OS-family checks. An intuitive source-backed example is `inspect: windows.passwordpolicy` plus `require.min_passwd_len.at_least: 14`, without manufacturing an Object; **37** more-complex Tests reject fail-closed. **154** negative validation guards passed.
- [Generic common-scalar grammar, extended native acquisition](https://github.com/vanderpol/scap-ng/actions/runs/38911089510): **189** source-exact Tests across 13 capabilities, preserving original selectors, collectors, `filesystem` and `traversal` options, and independently reproducing source Test/field one-or-more/all requirements. **75** are textfilecontent54 and **35** unix.file Tests. The natural-language predicates are structurally proven *macro contracts*, not approved abbreviations. The generic group overlaps with exactly **one** of the three separate DNS/Apache command specimens (Apache required KeepAlive); the other narrow groups have different State/Item requirements or no State/Object.
- **Combined research reach:** **370/1,375 (26.9%) distinct Test nodes** reconstructed exactly across complementary research prototypes. These **are not yet one unified grammar** or full-Assessment / scanner semantic conformance. Of those rejected by the generic scalar proof, **519** had different Item cardinality/reporting, **150** had Object/Set patterns outside the current acquisition shape, **152** had grouped/multiple fields, and **96** had extra Test-level/scoped State keys. Categories reflect first fail-closed rejection and are not independently measured blockers.
- [Proven multi-Test Boolean-tree inversion](https://github.com/vanderpol/scap-ng/actions/runs/38907309219): four real RHEL, Win11, DNS and Apache Assessments retain their original named-Test `all_of`/`any_of` graphs. **A counterexample** shows why WMI alternative States cannot always be collapsed into per-record membership.

**New architectural consequence:** do not require a `where` or `collect` block for a built-in capability that has **no source Object**. For example, real Windows `passwordpolicy` Tests inspect the typed platform policy collector directly; inserting a fake Object or collector command to satisfy an authoring template would change meaning. Treat Objectless, selected, explicitly collected, Set-composed and Object-expanding paths as genuine acquisition cases of **one** future language.

**Next highest-value work:** verify the direct-Set change against the pinned six-STIG archive; resolve the **one remaining source-shape exception**; then test whether someone can author the full shared-collection, command/Variable, WMI-record and conditional examples using one consistent vocabulary. Verify nested named-source references, `for_each_source.in` resolution and cycles before declaring the grammar authorable. The 871-document structural round trip does **not** establish six-state scanner/evidence parity or user comprehension. Current 0.4 base and released content remain unchanged.

## Leading readability sketch, not yet legal 0.4

~~~yaml
check: Guests must be denied Remote Desktop logon
inspect: windows.userright
where:
  userright:
    equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
require:
  trustee_name:
    includes_ignoring_case: Guests
~~~

Collection and selector are deliberately present. This is structured, indented YAML, not an expression string or a second micro-language.

## Important source-discovered constraint

- [OVAL 5.12.3 Windows userright_item](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/windows-system-characteristics-schema.html#userright-item): trustee_name occurs **0..1 times within each Item**.
- [OVAL 5.12.3 Linux partition_item](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/linux-system-characteristics-schema.html#partition-item): mount_options occurs **0..unbounded times within each Item**.

A typed shorthand could hide a redundant one-value OVAL quantifier for the Windows field, but the Linux case must retain its actual multi-value semantics. The source Item collection has an independent existence and match requirement in each case. No silent defaults or general-purpose substring interpretations are allowed.

## Reproducible source-inversion experiment

[Experimental lowerer / test](../../../tools/research_english_first_04.py) · [CI and artifacts](https://github.com/vanderpol/scap-ng/actions/workflows/research-english-first-04.yml) · [pinned real six-STIG fixture manifest](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/manifests/pinned-real-stig-fixtures.json).

The fixture repository is pinned to commit 99cbceae8d594c44cb509df95975ac1676a2b44a. The initial fail-closed lowerer began with **two typed field macros** and has since added a narrowly patterned registry alternative and Windows user-right regex. Separate command and State-free presence experiments are reported in the checkpoint above. Each supported candidate must reconstruct the real Test shape exactly, except the nonsemantic Object-title presentation field. It checks collection selector, State operation and value, independent field and Item quantifiers, reported elements, and Test title. Shared named Objects are resolved before comparison.

It also tests rejection of mutated source cardinalities and unknown operator/extra keys, and runs bounded six-outcome checks against the project's pinned OVAL reference model. It explicitly checks the multi-value counterexample [true, false], where all vs some differ.

| Real source | Status / boundary |
| --- | --- |
| RHEL9 SV-257851 Linux mount_options includes nosuid | Narrow exact Test inversion attempted; repeated values require State some-match but collected partitions require all-match |
| Windows 11 SV-253495 Guests right | Narrow exact Test inversion attempted; optional-singleton trustee_name and some-collected-Item match must stay distinct |
| Windows 11 SV-253254 registry EditionId alternatives | Exact source Test inversion passed in the narrow lowerer; not scanner parity |
| Windows 11 SV-253495 WMI records / full 7-Test tree | Entire named-Test evaluation graph round-trips; WMI record fields are **not** yet lowered from English-first syntax |
| RHEL9 SV-257889 account-derived dotfiles and for_each | Named-Test evaluation graph round-trips; account→file collection expansion remains unsupported by the English-first lowerer |
| DNS SV-259345 dynamic Variables + evaluation alternatives | DNSSEC signed command Test inversion passed and evaluation graph round-trips; Variable synthesis and entire Assessment still unproven |
| Apache SV-214228 multi-file configuration and optional fields | Two KeepAlive command Test inversions passed, preserving optional field semantics; all four Tests and the discovery Variable graph not yet modeled |

**The two favorable cases are NOT a claim about full source Assessment parity.** A green structural inversion is necessary, not sufficient, for complete six-state runtime/evidence parity. No SCAP-NG 0.4 scanner exists yet.

## Acquisition finding: preserve collection scope instead of hiding it

The full [source shape audit](https://github.com/vanderpol/scap-ng/actions/runs/38910857006) found **463** real Test Objects with a `filesystem` acquisition option, **145** using Set composition, **13** with explicit traversal and **5** with a direct Object-level `for_each`. Adding explicit, unmodified `filesystem`/`traversal` fields to the typed English-first source template raised generic scalar source-exact coverage from 78 to **189**. These are **not** equivalent to Set union/difference or `for_each` expansion; each of those needs a separately proved readable representation. Merely dropping acquisition flags to shorten a snippet is forbidden.

## Key readability lesson from the new objectless cases

The English-first format cannot mandate `where` or `collect` for every Test. For real Windows password-policy content, the typed capability **is** the system-data acquisition contract. This complete **research-only** Test-node illustration is sourced from Windows 11 SV-253303:

~~~yaml
check: "'Minimum password length' is set to at least '14' characters"
inspect: windows.passwordpolicy
require:
  min_passwd_len:
    at_least: 14
report_elements: all
~~~

The operator has a narrowly verified source expansion: Test **one-or-more Items, all match**, field **one-or-more values, all match**, source greater-than-or-equal comparator, and original reporting policy. This is an explicit operator contract, **not** permission to infer those quantifiers for every field/capability. Research approval and independent six-state runtime proof remain open.

## Required research gates before a decision

1. Prove one readable, structured native YAML grammar over **all** needed original collection, Test, State, record, Variable, and Boolean-graph semantic concepts. Avoid a simple-case dialect plus a separate OVAL-like fallback.
2. Exhaustively retain OVAL 5.12.3 Test/field existence and aggregation (including uncommon combinations), collection incomplete/error/not-collected status, six technical outcomes, operand value_match, record-member errors, Object Set filters, and evidence/source Item identity.
3. Measure **whole-six-STIG** source coverage with exact vs unsupported vs changed semantics labels; distinguish unique Assessment nodes from per-benchmark occurrences. Include source IDs and decisive counterexamples.
4. If six-STIG coverage is compelling, repeat across all 65 STIGs and account for all unsupported outliers. Do not silently fall back to manual/shellcommand without reporting and review.
5. Test human comprehension of **complete checks** without explanation, including small screens, missing data, exactly-one checks and nested/composed assessments.
6. Promote vocabulary only when it is both intuitive and source-semantic-equivalent with a reproducible acceptance gate. Until then leave 0.3, the published 0.4 prerelease and editor plans unchanged.

The [complex source research](../compact-authoring-04/ENGLISH-FIRST-COMPLEX-SOURCE-AUDIT.md) documents where the same conceptual ordering helps and where collection/semantic graphs do not yet compress.

**Meeting guidance:** narrow cases may be an interesting direction, but are not yet sufficient to advocate a new 0.4 grammar. The strongest topic for a vendor discussion remains precise preservation of source semantics.
