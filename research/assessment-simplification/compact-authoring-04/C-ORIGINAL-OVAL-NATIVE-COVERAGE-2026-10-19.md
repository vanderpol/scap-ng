# 0.4-C original OVAL native conversion: verified 36-Definition checkpoint

**19 October 2026 · Refs [#245](https://github.com/vanderpol/scap-ng/issues/245) · Research, not normative approval or scanner parity.**

The full pinned [OVAL Community SCAP-Self-Assertion Test Content](https://github.com/OVAL-Community/SCAP-Self-Assertion/tree/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content) contains **785 source Tests, 167 Definitions**; the maintained 0.3 source semantic round-trip accepts **162 Definitions**, with exactly five explicitly invalid/deprecated source exceptions. An independent 0.4-C authoring compile/reprojection now succeeds for **36 / 162**, with **126** remaining native-C unsupported. This is an original-source check, not 0.4-C scanner execution.

[**Successful full original-source C workflow / generated source-linked rejection report**](https://github.com/vanderpol/scap-ng/actions/runs/39344457603). The job's uploaded artifact contains `c-native/first-rejection-gap-report.md`, `c-native/conversion-manifest.json`, and all native C YAML, plus separate A fallback and hybrid proof packages. The workflow requires **at least 36** source-backed native C Definitions or fails. The [focused C source test workflow](https://github.com/vanderpol/scap-ng/actions/runs/39344255230) verified **372 unit tests passing** at the introduction of the independent selected-Object compiler, with structural failure cases for duplicate/omitted Tests, Set/Filter/Variable scope, value types and altered Test logic.

## Native C conversions by independently compiled route

| Original-source authoring path | Converted Definitions |
| --- | ---: |
| One Test compiled directly to `from` / `must` | **31** |
| Multi-Test, one explicitly objectless source | **3** |
| Multi-Test, separate source-selected Objects | **2** |
| **Total** | **36** |

The two new independently selected Object cases are real [Cisco IOS line Tests](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/ios/ios-def_line_test.xml) and [Cisco IOS-XE line Tests](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/iosxe/iosxe-def_line_test.xml). The new [bounded original OVAL multi-Test compiler](../../../tools/research_c_oval_multicheck.py) uses the existing **single** 0.4-C observations/checks/require compiler. It preserves each distinct source Object selector, typed State operator, original Test identity and top-level AND. Anything with unsupported Sets, Filters, Variables, sharing, missing/duplicate State or different logic fails explicitly rather than being counted as native C.

## Actual first-blocker accounting across the 126 unsupported source-compatible Definitions

| First rejected feature family | Definitions |
| --- | ---: |
| Source Variable dependency graph | **68** |
| Multi-Test structure beyond supported Object scopes | **44** |
| Source-supported C compiler/capability mismatch | 4 |
| State field cardinality | 4 |
| Selector typed/null structure | 2 |
| Other original-source edge cases | 4 |
| **Total** | **126** |

These are **first encountered blockers only**, not a comprehensive frequency count for every original XML construct. The same Definition can require several improvements. In particular, all **44** still-rejected multi-Test Definitions exceed the single-shared-selected-Object shape. Merely improving that specialized converter further is unlikely to move whole-corpus coverage. The next leverage is a general source-resolved multi-Object/Test graph compiler and the actual Variable dependency path—**not** another set of hand-picked simple `must` examples.

## Technical direction

Retain the established 0.3/0.4-A typed OVAL-compatible Objects, Sets, Filters, Variables and six-state logic as the execution semantics. Continue testing a much clearer C authoring vocabulary above it, preserving original documentation and separately managed source provenance. The already independently reconstructed [seven-Test original OVAL Set hybrid](C-OVAL-TYPED-SET-PROVENANCE-2026-10-19.md) and [five-Test, 19-Variable Apache hybrid](C-APACHE-FULL-HYBRID-2026-10-19.md) show that this architecture is feasible, but **those separate hybrid proofs are not included in the 36 native C count** until one consistent, source-tested C grammar accepts them.

Independent collector, Item/State, error/incomplete and full six-state scanner-result parity remains unproven. Organizational Input, version/IP comparison algorithms and true source-specific Variable functions remain on the 0.4-C roadmap, separate from the original corpus coverage metric. No 0.4-C language freeze or external SLANG comparative-review recommendation follows solely from the 36-Definition count.

This checkpoint is a reproducible GitHub source-conversion report and a bounded engineering plan, **not an automation that continues writing code after the chat ends**.
