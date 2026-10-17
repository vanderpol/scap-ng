# OVAL `only_one_exists`: truth table, actual uses, and simplification options

**17 October 2026 — source-backed research only, not adopted SCAP-NG YAML. Issues #235 and #229.**

## Exact meaning

OVAL 5.12.3 `check_existence="only_one_exists"` requires **one and only one observed Item** with root status `exists`. It is entirely distinct from `check="only one"`, which asks that exactly one **existing collected Item satisfy the State**. Likewise, State entity and record-field cardinality are different scopes.

References:
- [OVAL Core Common 5.12.3, ExistenceEnumeration](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html#existenceenumeration)
- [OVAL Core Results 5.12.3](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-results-schema.html)
- [OVAL Core System Characteristics, collection flags](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-system-characteristics-schema.html)

### Complete collection: OVAL existence result only

| Existing Items | Missing/does-not-exist Item statuses | Error Item statuses | Not-collected Item statuses | Result |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0+ | 0 | 0 | **false** |
| 1 | 0+ | 0 | 0 | **true** |
| 2+ | 0+ | 0+ | 0+ | **false** |
| 0–1 | 0+ | 1+ | 0+ | **error** |
| 0–1 | 0+ | 0 | 1+ | **unknown** |

A missing Item does not count as existing. Two confirmed existing Items produce **false**, even if other Items have `error` or `not_collected` statuses. The separate OVAL Test **only evaluates its State comparison if the existence requirement evaluates true**.

### Collected-object status overrides and incomplete

| Collected-object flag | Existing Items | Test result, without any State |
| --- | ---: | --- |
| `complete` | 0 | **false** |
| `complete` | 1 | **true** |
| `complete` | 2+ | **false** |
| `incomplete` | 0 | **unknown** |
| `incomplete` | 1 | **unknown** |
| `incomplete` | 2+ | **false** |
| `error` | any | **error** |
| `not collected` | any | **unknown** |
| `not applicable` | any | **not applicable** |
| `does not exist` | any | **false** |

With a State attached, an `incomplete` collection of exactly one Item can also be decisively **false** if the observed Item fails the relevant comparison. The reference implementation documents additional specifics; do not use the existence-only table as a complete State-result evaluator.

## Not the same as “only one Item matches”

| Collected Items | State comparison results | `only_one_exists` + `all` | `at_least_one_exists` + `only one` |
| --- | --- | --- | --- |
| 0 | (none) | false | false |
| 1 | true | true | true |
| 1 | false | false | false |
| 2 | true, false | **false** | **true** |
| 2 | true, true | false | false |

The fourth row is the counterexample that forbids merging these into a single vague label.

## Every selected native Test, with original OVAL source selector evidence

The pinned six-STIG native preview contains **seven** Tests with `only_one_exists`, and the original six source STIG XML packages contain eight DISA and four NIWC occurrences (the source population is larger, and cross-benchmark reuse exists). The following native-source mapping uses **OVAL Test-comment + existence-mode candidates**, not converter-retained original Test-ID provenance.

| Native content | Original author candidate | Source selector | Retention concern |
| --- | --- | --- | --- |
| Windows 11 `SV-253266` | NIWC | `bcdedit /enum`, `^description` | May match multiple boot entries; exactly-one is **not obviously redundant**, though policy intent needs review |
| Windows 11 `SV-253296` | NIWC | `W32tm /query /configuration`, `^Type:` | May reflect a single setting; prove collector command cardinality before removing |
| Linux shared `Defaults timestamp_timeout` | DISA | OVAL `textfilecontent54` Object **set** with two referenced Objects | Multiple definitions/lines may be found; no safe shortcut |
| Linux shared `pam_unix.so sha512` | DISA | `/etc/pam.d/password-auth`, regex, `instance >= 1` | Duplicate matching directives **can** affect exactly-one outcome |
| Linux shared DoD notice/banner | NIWC | One literal `/etc/issue` file, regex, **`instance = 1`** | **Potentially redundant cardinality:** Object only selects the first match in the named file; no second Item should satisfy that Object if collector honors identity and instance selection |
| Linux `/sys/fs/selinux/enforce` | DISA | Fixed literal filepath, regex, `instance >= 1` | Generally one-line pseudo-file, but no source-level max-one constraint |
| Linux `/etc/selinux/config` | DISA | Fixed filepath, `^SELINUX=(.*)`, `instance >= 1` | Multiple setting lines possible; exactly-one may prevent ambiguous configuration |

The `textfilecontent54` `instance` entity identifies a particular occurrence of a pattern in a file; equality to 1 selects the first such occurrence, whereas `>= 1` can select every occurrence. See [OVAL 5.12.3 Independent Definition textfilecontent54_object](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/independent-definitions-schema.html).

**The DoD banner is a strong candidate for redundant `only_one_exists` (because `instance = 1` already constrains Item selection), but it is not a proven lossless OVAL conversion until we also check incomplete/status behavior and the original Item-identity contract.** In particular, a configured `instance = 1` limits selected matches; it does not prove the full collector result model has no error or incomplete states.

## Alternative authoring approaches

### Option A — one controlled Item dropdown (preferred candidate)

```yaml
require:
  items: exactly_one
  condition: {value: {equals: 1}}
```

Same structure as other proposed requirements. The dropdown value determines the Item population, and `condition` describes a predicate on the one Item. For a presence-only requirement, omit `condition`. This is **proposed syntax**, not a published schema.

### Option B — a generic typed count expression

```yaml
require:
  item_count: {equals: 1}
  condition: {value: {equals: 1}}
```

The comparison is intuitive, but **evaluating a count of a partially collected or errored population is not ordinary integer arithmetic**. To be faithful, the count needs collection completeness/error semantics and must count existing root Items, **not matching Items or field values**. A new `item_count` keyword may therefore make the grammar bigger rather than smaller.

### Option C — one-or-more plus at-most-one

Logically `count(exists) >= 1` AND `count(exists) <= 1`; as Boolean arithmetic it equals exactly one. Two author-facing clauses are longer, harder to scan and require careful six-state combination rules. **Not recommended as the normal syntax**.

### Option D — prove that the selected resource identity has maximum cardinality one

An exact `filepath`, registry value, WMI singleton, or `instance = 1` can sometimes guarantee that no second matching Item can be collected. In those cases an exactly-one requirement **may be replaceable by required presence**, or even by an underlying capability's unique identity contract. Only do this when the cap/collector and all incomplete/error cases are independently proven; a filename alone is not proof.

### A proved reduction in the current source vocabulary

The native corpus currently uses both:

- `only_one_exists_and_only_one_matches` (2 Tests)
- `only_one_exists_and_matches` (3 State-bearing Tests), plus 2 State-free `only_one_exists`.

For exactly one existing Item, OVAL `check=all` and `check=only one` are redundant. The scoped [exhaustive generic regression](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_exactly_one_equivalence.py) checks **12,432 combinations** of collection flag, 0–3 existing Items, optional missing/error/not-collected Item statuses, and six possible State results. They agree.

Thus one `items: exactly_one` can replace **multiple redundant combined-quantifier labels**, without removing exactly-one semantics. Note that a source `check="none satisfy"` is different and must be retained as a negated condition if present.

## Recommendation

**Keep exactly-one Item existence as one clearly scoped native dropdown option for now**, but **remove redundant compound spellings** after review. Unlike old Test-level `all_exist`, exactly-one detects genuine duplicates. Perform source-specific proof before simplifying the DoD banner or other apparent singleton checks. Preserve legacy OVAL import and all result/evidence outcomes; do not turn source Test duplicates into compliant results.
