# 0.4-C roadmap — constants, Organizational Input, and specialized comparisons

**19 October 2026 · [research #245](https://github.com/vanderpol/scap-ng/issues/245). Tracked research/acceptance gates, not newly accepted normative 0.4-C syntax.** Only 0.4-C is active; do not resume 0.4-A/B, editor or unrelated tasks from this page.

## Priority and separation of concerns

1. **P0 — OVAL 5.12.3 Self-Assertion import parity and source accounting.** Recover a reproducible pinned conversion pipeline. Every original Test/Definition must have a converted artifact or an explicit unsupported reason; preserve meaningful descriptions, dataflow, Tests and provenance. Sets, Filters, Variables/functions and six-state source semantics come before new convenience syntax. The earlier local 291/785 Test, 51/167 complete Definition and 18 packaged C Assessment figures are historical **unreproduced** prototype observations, not current verified coverage.
2. **P0 — Inline fixed constants without adding needless authored Variables.** A literal/scalar/list belongs at its consumer when source types, multiplicity, value quantifier, consumer identity and provenance survive. Compiler-owned source mappings may retain former OVAL constant-Variable identity for diagnostics/re-export. A true computed or reused runtime value may still be a named derived value. **Never** collapse a multi-value constant into one value or turn source `var_check="only one"` into `any`.
3. **P1 — Typed comparisons, integrated into the same C source-parity gate.** The [0.3 owner-approved research direction](../../iterations/003/design/CURRENT-DESIGN.md) already omits provably redundant common scalar datatypes and uses descriptive typed operators, never authored `compare_as`. This is **not** a reason to assume the scanner's actual datatype algorithms are complete. Preserve canonical effective datatype plus OVAL base operation and compare against independently authored expected results.
4. **P1 after the OVAL corpus core — Organizational Input as a distinct 0.4-C requirement.** This is **not part of OVAL Self-Assertion coverage** and must not delay the P0 conversion package. Retain the accepted existing policy/input machinery; provide an author-facing way to bind approved organization values directly to an expected State without creating pass-through Variables.

## Datatype vs operator: defend the distinction

- Ordinary scalar equality and ordering: source datatype inferred **only where unambiguous** from typed YAML values and capability field contracts. The compiled IR remains explicitly typed and checked.
- **Version is an algorithm, not string spelling.** e.g. `version_equals: '1.0'` must compare equal to observed `1.0.0`; `version_greater_than: '2.9'` must compare true to observed `2.10`. These differ from lexical string ordering and from SemVer. Distinct OVAL package families (RPM EVR, Debian EVR, IOS and fileset) need distinct algorithms and are not covered by this dotted-version sample.
- **IP subsets are address-family-specific containment comparisons**, not a generic string `subset_of`. Example: observed `192.0.2.128/25` is `ipv4_subset_of: '192.0.2.0/24'`. Compare **observed network as left operand** with expected network as right operand; `ipv4_superset_of` is a different condition. IPv6 is distinct. OVAL ordered IPv4/IPv6 comparisons with unlike prefixes yield **error**, not false or an automatic subnet comparison. Prefix equality/inequality also remains typed. Preserve the effective prefix and family.
- `version_*` and `ipv4_*`/ `ipv6_*` names are a **provisional C authoring spelling** matching established 0.3 direction, not a new user vote or hidden `compare_as`. More specialized families, nonfinite float, multi-value type ambiguity and invalid Item→State casts require their own explicit conformance gates.
- The [pinned datatype × operation matrix](../../iterations/003/design/datatype-operation-conformance-matrix.md) covers 13 datatype families. Existing [13 independent expected-result cases](../../../tests/datatype-operator-evaluation-0.3/expected-cases.json) and [bounded test runner](../../../tools/test_research_type_evaluation_fixtures.py) exercise a **limited** string/int/bool/dotted-version/IPv4/IPv6 subset. Include these in focused **C CI** as regression dependencies, then expand against true pinned OVAL Self-Assertion and native compiler outputs. Passing these 13 cases is **not** full OVAL evaluator parity.
- Historical six-STIG research found **4,532/5,267 (~86%) authored datatype declarations** structurally removable while preserving typed canonical source AST. Those are a syntax-reduction baseline, **not** a justification to drop comparison datatypes from the internal representation. [Evidence](../../iterations/003/design/datatype-operator-lossless-review.md) and [#200](https://github.com/vanderpol/scap-ng/issues/200).

## Real constant Variable example — source evidence

[OVAL 5.12.3 extracted Board test](../../../board/review-content/0.2.0/sources/filter.xml), from the pinned OVAL Self-Assertion source, uses `oval:org.mitre.oval.test:var:134` with **two string values** `/opt/support/txt/txtfile` and `/opt/support/txt/txtfile/subtxtfile`. A `file_state/path` uses that Variable with **`var_check="only one"`**. A future C authoring form should be able to express the values **inline at that comparison** and preserve the *exactly one expected value matches* contract. This reference has a source OVAL `filter` in a `set`; **do not change Set membership when replacing the constant**.

For illustration only (not currently accepted C syntax):

```yaml
path:
  equals:
    - /opt/support/txt/txtfile
    - /opt/support/txt/txtfile/subtxtfile
  value_match: one  # source OVAL var_check=only one; explicit, not inferred
```

The precise C predicate nesting must follow the final single frontend, and source-native IDs/comments belong in conversion provenance rather than meaningless author-facing Variable names. Need independent source-equivalent comparison results under multi-value and zero-value evidence before automatic migration.

## Organizational Input scope (separate from source constants)

- Use publisher-defined typed Parameter → Rule Assessment-choice input binding → **direct State expected value** → explicit bound organizational Input Set / Assessment Request. Do not require a pass-through Variable or separate Tailoring artifact. Reuse [direct State input research #193](https://github.com/vanderpol/scap-ng/issues/193), [intuitive membership operators #195](https://github.com/vanderpol/scap-ng/issues/195), [publisher-generated fill-in template #196](https://github.com/vanderpol/scap-ng/issues/196), [instance scoping #175](https://github.com/vanderpol/scap-ng/issues/175), and [existing policy contract](../../../specification/policy/parameters-and-organizational-input.md).
- Distinguish organization-delegated expected policy data from a publisher-defined value (which cannot be overridden as Organizational Input), from OVAL external Variables (legacy conversion concern), and from data observed on the assessed host.
- Require typed constraints, cardinality and membership semantics, explicit target/instance binding **without automatic inference from filenames or host attributes**, authorization/supplier/provenance, validity windows and immutable run-frozen values; conflicting input sets must not silently override one another.
- Missing required input → `not_evaluated` with a structured `missing_organizational_input` reason, **never** pass/fail/NA or an invented default. Supplied values must **not** select or modify commands, collectors, privileges, or Test implementations. Address redaction in results.
- Acceptance test: one real STIG Rule genuinely requiring an organization-selected expected value, valid/missing/invalid/expired/conflicting inputs, source-correct State comparison for scalar and multi-value values, provenance and result reasoning. Do not claim OVAL corpus parity from this non-OVAL feature.

## Implementation sequence

1. Publish tested, pinned Self-Assertion conversion program and per-Test/Definition supported/unsupported manifest to GitHub; run source-parity gates.
2. Remove eligible constant-Variable *authoring* wrappers via source-conserving inline literals and explicit multi-value quantifiers, with original source mapping retained.
3. Demonstrate typed operators on source-backed OVAL version/IP comparisons (not just synthetic strings), extend comparator error/unknown tests, and fix actual discovered parity gaps rather than reopening settled naming.
4. After independent Self-Assertion progress is reviewable, add an integrated 0.4-C Organizational Input Assessment and policy/input-binding regression built from already accepted 0.3 contracts.
5. Only promote language semantics through the project's human decision/review process. No normative schema or runtime behavior changed by this roadmap.
