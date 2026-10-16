# English-first 0.4 Assessment authoring — source-compatibility research

**Pre-alpha experiment; NOT adopted grammar or scanner-conformance evidence.**
Tracking: [#235](https://github.com/vanderpol/scap-ng/issues/235) (research), [#227](https://github.com/vanderpol/scap-ng/issues/227) (vocabulary), [#229](https://github.com/vanderpol/scap-ng/issues/229) (semantics).

**Goal:** A security administrator understands an Assessment without knowing OVAL; an implementer derives exact semantics without guessing.

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

The fixture repository is pinned to commit 99cbceae8d594c44cb509df95975ac1676a2b44a. The fail-closed compiler lowers only **two exact typed macros**, then requires the generated Test semantic shape to match the real source verbatim except the irrelevant Object-title presentation field. It checks collection selector, State operation and value, independent field and Item quantifiers, reported elements, and Test title. Shared named Objects are resolved before comparison.

It also tests rejection of mutated source cardinalities and unknown operator/extra keys, and runs bounded six-outcome checks against the project's pinned OVAL reference model. It explicitly checks the multi-value counterexample [true, false], where all vs some differ.

| Real source | Status / boundary |
| --- | --- |
| RHEL9 SV-257851 Linux mount_options includes nosuid | Narrow exact Test inversion attempted; repeated values require State some-match but collected partitions require all-match |
| Windows 11 SV-253495 Guests right | Narrow exact Test inversion attempted; optional-singleton trustee_name and some-collected-Item match must stay distinct |
| Windows 11 SV-253254 registry EditionId alternatives | Not yet supported |
| Windows 11 SV-253495 WMI records / full 7-Test tree | Not yet supported |
| RHEL9 SV-257889 account-derived dotfiles and for_each | Not yet supported |
| DNS SV-259345 dynamic Variables + evaluation alternatives | Not yet supported |
| Apache SV-214228 multi-file configuration and optional fields | Not yet supported |

**The two favorable cases are NOT a claim about full source Assessment parity.** A green structural inversion is necessary, not sufficient, for complete six-state runtime/evidence parity. No SCAP-NG 0.4 scanner exists yet.

## Required research gates before a decision

1. Prove one readable, structured native YAML grammar over **all** needed original collection, Test, State, record, Variable, and Boolean-graph semantic concepts. Avoid a simple-case dialect plus a separate OVAL-like fallback.
2. Exhaustively retain OVAL 5.12.3 Test/field existence and aggregation (including uncommon combinations), collection incomplete/error/not-collected status, six technical outcomes, operand value_match, record-member errors, Object Set filters, and evidence/source Item identity.
3. Measure **whole-six-STIG** source coverage with exact vs unsupported vs changed semantics labels; distinguish unique Assessment nodes from per-benchmark occurrences. Include source IDs and decisive counterexamples.
4. If six-STIG coverage is compelling, repeat across all 65 STIGs and account for all unsupported outliers. Do not silently fall back to manual/shellcommand without reporting and review.
5. Test human comprehension of **complete checks** without explanation, including small screens, missing data, exactly-one checks and nested/composed assessments.
6. Promote vocabulary only when it is both intuitive and source-semantic-equivalent with a reproducible acceptance gate. Until then leave 0.3, the published 0.4 prerelease and editor plans unchanged.

The [complex source research](../compact-authoring-04/ENGLISH-FIRST-COMPLEX-SOURCE-AUDIT.md) documents where the same conceptual ordering helps and where collection/semantic graphs do not yet compress.

**Meeting guidance:** narrow cases may be an interesting direction, but are not yet sufficient to advocate a new 0.4 grammar. The strongest topic for a vendor discussion remains precise preservation of source semantics.
