# English-first 0.4 Assessment authoring — source-compatibility research

**Pre-alpha experiment; NOT adopted grammar or scanner-conformance evidence.**
Tracking: [#235](https://github.com/vanderpol/scap-ng/issues/235) (research), [#227](https://github.com/vanderpol/scap-ng/issues/227) (vocabulary), [#229](https://github.com/vanderpol/scap-ng/issues/229) (semantics).

**Goal:** A security administrator understands an Assessment without knowing OVAL; an implementer derives exact semantics without guessing.

## October 16 corpus checkpoint — source-backed, fail-closed

- [Full six-STIG structural census](https://github.com/vanderpol/scap-ng/actions/runs/38908329365): **872 unique automated Assessments / 1,375 distinct named Tests**, from the SHA-256 pinned r3 authoring ZIP. **918** Tests use simple scalar State fields, **675** have native `collect` parameters, **387** have no States, **219** use State-level logical groups, **66** use records, **145** use Sets, **139** reference Variables inside their Object definitions, and **114** have **no explicit Object** (legitimate built-in collector capabilities, not necessarily broken content). These categories overlap.
- [Presence-only grammar proof](https://github.com/vanderpol/scap-ng/actions/runs/38909206051): **63/387** State-free Tests have exact source Test-node reconstruction using an explicit `require.collected_items: none | exactly_one | at_least_one | all_exist | may_be_absent` vocabulary plus their original `where`/`collect` definitions. **324** have more complex Object/Set/metadata structures and were rejected, not dropped. **126** negative validation guards passed.
- [DNS/Apache command Test proof](https://github.com/vanderpol/scap-ng/actions/runs/38908788030): **3** additional distinct Test nodes reconstructed exactly, keeping command/Variable references, Bash/PowerShell selection, original error flags and field/cardinality requirements. **12** mutation guards passed.
- [Previous full-corpus narrow grammar audit](https://github.com/vanderpol/scap-ng/actions/runs/38907185233): **39** source-exact field/selector Test nodes, with **1,336** unsupported by that initial translator. The 63 presence-only and 3 shell examples are disjoint from these 39.
- [Objectless native system-wide Test research](https://github.com/vanderpol/scap-ng/actions/runs/38909973142): **77/114** source-exact Test reconstructions across Windows audit policies, password/lockout policies and OS-family checks. An intuitive source-backed example is `inspect: windows.passwordpolicy` plus `require.min_passwd_len.at_least: 14`, without manufacturing an Object; **37** more-complex Tests reject fail-closed. **154** negative validation guards passed.
- **Combined research reach:** the disjoint experimental groups reconstruct **182/1,375 (13.2%) distinct Test nodes** exactly. These **are not yet one unified grammar** or full-Assessment / scanner semantic conformance.
- [Proven multi-Test Boolean-tree inversion](https://github.com/vanderpol/scap-ng/actions/runs/38907309219): four real RHEL, Win11, DNS and Apache Assessments retain their original named-Test `all_of`/`any_of` graphs. **A counterexample** shows why WMI alternative States cannot always be collapsed into per-record membership.

**New architectural consequence:** do not require a `where` or `collect` block for a built-in capability that has **no source Object**. For example, real Windows `passwordpolicy` Tests inspect the typed platform policy collector directly; inserting a fake Object or collector command to satisfy an authoring template would change meaning. Treat Objectless, selected, explicitly collected, Set-composed and Object-expanding paths as genuine acquisition cases of **one** future language.

**Next highest-value work:** a single human-readable AST that covers those five acquisition paths, both Test and field quantifiers without undocumented defaults, record-level constraints, and source-faithful derived commands. Do not equate a growing *Test-node* exact-inversion count with full Assessment conversion, six-state scanner/evidence parity or user comprehension. Current 0.4 base and released content remain unchanged.

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
