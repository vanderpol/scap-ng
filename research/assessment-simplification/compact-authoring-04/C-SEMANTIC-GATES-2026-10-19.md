# 0.4-C continuation: semantics-first acceptance gates

**19 October 2026 — research issue #245 — proposal and test design only; not normative and not owner-approved.** This checkpoint follows [C critical design review](C-CRITICAL-DESIGN-REVIEW-2026-10-19.md) and [source-backed sample review](C-AUTHORING-SAMPLE-REVIEW-2026-10-19.md). It does not change the pinned A schema, converters, collector contracts, editor or scanner.

## Recommendation

Continue C as an independent **authoring frontend** to a single A-compatible, typed execution representation. Do not freeze the C language, publish a parity claim, or accept a concise phrase on textual resemblance. A remains the source-preserving import fallback.

**Prefer explicit item quantifiers in the authoring surface** (`any_item` and `every_item`) until a blind first-read review proves that bare `must` reliably means *one or more observed Items exist, and at least one individual Item satisfies every listed condition*. That is not the default English reading of *must* for many auditors. The short-form cost is small; the implicit cardinality error is material. This is a research recommendation, not a grammar change.

## Four independent questions — never conflate

1. **Which Items are collected?** A version-pinned capability, Object selector, collection parameters, Sets and Filters determine the eligible population. A filter is not an assertion and an assertion cannot silently become a filter.
2. **Which field values match within one Item/record?** Preserve datatype, entity existence, value count, record identity and operator. `all` over fields is not `all` over Items.
3. **How many eligible Items exist, and how many must match?** Distinguish at least one matching, every matching, exactly one matching, exactly one existing, none matching, and absence. Preserve OVAL/A paired existence semantics, including successful-empty and incomplete acquisition.
4. **How do Test outcomes combine?** Named `and`/`or`/`not` trees evaluate over six-state outcomes, not Items, records or field values. Evaluate with source-backed tables, not programming-language Boolean shortcuts.

## Required adversarial counterexamples

| Gate | Observation | Unsafe shortcut | Required behavior |
| --- | --- | --- | --- |
| Multiple Items | Two Registry Items: DWORD 0 and DWORD 1 | Bare `must` silently means `every_item` | `any_item` can pass, `every_item` fails |
| Same Item | One Registry Item supplies `type: dword`, another supplies `value: 0`; neither has both | Match fields across different Items | Fail a requirement that demands both on the same Item |
| Empty collection | Successful complete read returns zero Items | Universal truth makes required `every_item` pass | Fail if one or more required; separately test source-specific absence requirements |
| Partial acquisition | One good Item, rest unknown | Return Pass for every-item check | Unknown unless a known bad Item makes Fail decisive |
| Error | Collector explicitly reports error | Interpret as successful empty population | Preserve Error and evidence |
| Record correlation | Record A has good first field; record B has good second field | Flatten both into an unrelated global field pool | Require same parent record when original source does |
| Per-parent scope | Parent A contributes all good paths; parent B contributes one bad path | Union all descendants and test only an arbitrary result | Retain original foreach scope, cardinality and lineage |
| Source filter | A shared State participates in Object Set/Filter and separately in a Test | Replace both consumers with a permission comparison alias | Refuse rewrite until the exact global consumer graph is independently accounted for |
| Permissions | Mode 0604 is numerically below 0740 | Compare octal values with `<=` | Fail 0604 under permission-bit-subset semantics |
| Source selector | RHEL `matches_regex: '.*\\/home'` | Rewrite to exact `/home` for elegance | Treat as a different native policy, never faithful source import |

## Permission shorthand: precise scope

The source-backed RHEL9 case has **eight separate forbidden permission booleans** in one State, but also two Tests with differing existence checks, separate Variables, Objects and Set/Filter construction. The tested `no_more_permissive_than: '0740'` macro is a compact *State predicate* over all 4,096 POSIX 12-bit modes. It is **not** a replacement for the full source Rule, a global shared State rewrite, an ACL policy, or a collector. Local dependency closure does not prove cross-Rule closure. The existing macro guard explicitly reports `source_conversion_authorized: false` and `global_source_consumers_audited: false`. Preserve both declarations unless a new independently reviewed end-to-end provenance proof exists.

For any attempted source migration, gather all consumers of the source State by immutable source ID across Rules and imported benchmarks, including references inside Objects/Sets/Filters, Test States and derived Objects/Variables. If the repository corpus cannot establish globally complete identities and references, report **UNKNOWN/NO-GO** rather than interpreting zero discovered references as zero real consumers.

## Next engineering sequence (focused, not the routine 65-STIG gate)

1. Implement a **read-only complete-consumer census** for one source State across the pinned source graph and cross-check independently against raw XML reference IDs. Include an adversarial fixture in which a second Rule uses that State as a Filter. Until then the bit macro stays an authoring-only display/expand shortcut.
2. Test `none_exist` and `any_exist` with State-bearing complete-empty and incomplete Item populations using actual pinned OVAL semantics. Do not invent a generic zero-item state aggregation. Keep uncommon cases through faithful A compatibility IR when unknown.
3. Add a complex C authored *Apache SV-214268* candidate covering five Tests and the actual 19-Variable graph, with source identity, per-operation provenance and independent output oracles. Record **operations genuinely eliminated by proven fusion**, not just renamed. If remaining steps are still required, expose them in an editor drilldown without pretending conceptual reduction.
4. Add a source-backed Windows correlated WMI/DNS or nested record case and an adversarial cross-parent record counterexample. Verify field/record/Item scopes separately.
5. Run a blinded novice authoring/readback exercise with source-check questions, especially `any_item` versus `every_item`, successful-empty, partial evidence, alternate values and shared source definitions.
6. Once a unified C compiler handles all supported source patterns or preserves explicit compatibility operations without loss, produce six-STIG conversion and a source/IR coverage ledger. **No A-versus-C selection** before these coverage and semantic gates.

## Stop/go and evidence vocabulary

- **GREEN — structural:** C lowers to identical pinned A selectors, predicates, requirement tokens and provenance identity. Does *not* imply runtime parity.
- **GREEN — fixture:** independently expected value/status/trace agrees on declared finite cases. Does *not* imply general-source semantics.
- **GREEN — source-runtime:** independently verified OVAL 5.12.3 expected execution outcome under identical collected evidence and error state.
- **GREEN — representative:** all six pinned STIG benchmarks accounted for, every unsupported path explicitly flagged and fallback measurable, with no silently altered policy.
- **GREEN — human:** blind reviewers accurately explain and edit both simple and complex requirements without the OVAL model.
- **NO-GO:** semantic ambiguity, source population mismatch, ungrounded global reuse, silent coercion, lost parent correlation, lost six-state/error distinction, or a shorter surface that cannot be reversed to a faithful policy/evidence trace.

**Overall status at this checkpoint:** architectural feasibility demonstrated in bounded fixtures; high-value semantic and human readability gates remain open. No new acceptance decision has been taken.
