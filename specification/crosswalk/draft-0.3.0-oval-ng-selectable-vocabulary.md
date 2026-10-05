# Draft 0.3.0 OVAL → SCAP-NG selectable-vocabulary crosswalk

**Status:** 0.3.0 design/reference draft; intentionally not linked from the main specification navigation yet.

## Purpose

This document reviews author-visible vocabularies where a content author selects one value from a defined list.

The design rule for SCAP-NG is:

> When SCAP-NG represents the same semantic concept as OVAL, retain OVAL terminology unless SCAP-NG is more internally consistent or provides a meaningful usability/semantic improvement.

Shorter spelling alone is not a sufficient reason to rename an established OVAL concept.

This crosswalk separates:

- **retain** — NG already matches OVAL closely enough;
- **consistent improvement** — NG deliberately uses a more consistent machine-friendly spelling without changing meaning;
- **meaningful improvement** — NG uses a different term because it communicates the semantics more accurately;
- **0.3.0 review/change** — current NG terminology is not clearly better and should be corrected or explicitly justified;
- **NG-only** — no direct OVAL authoring enum exists;
- **coverage gap** — conversion may preserve the choice, but the native schema/reference does not yet expose a settled first-class vocabulary.

The OVAL baseline is the pinned OVAL 5.12.3 schema under
`third_party/scap-1.4-schemas/oval_5.12.3/`.

## 1. Definition / Assessment class

| OVAL | NG 0.2.0 | Disposition |
|---|---|---|
| `compliance` | `compliance` | retain |
| `inventory` | `inventory` | retain |
| `miscellaneous` | `miscellaneous` | retain |
| `patch` | `patch` | retain |
| `vulnerability` | `vulnerability` | retain |

This is an exact semantic vocabulary carryover. NG Assessment `purpose`
(`assessment` / `applicability`) is a separate NG concept and SHALL NOT be
used as a replacement for class.

## 2. Check / match quantifier

OVAL `CheckEnumeration` is used for Test `check`, State/entity
`entity_check`, and variable `var_check`.

| OVAL 5.12.3 | NG 0.2.0 match vocabulary | Current interpretation | Disposition |
|---|---|---|---|
| `all` | `all` | all individual results satisfy | retain |
| `at least one` | `any` | one or more satisfy | **0.3.0 review/change** |
| `none satisfy` | `none` | zero satisfy | consistent simplification; review with full family |
| `only one` | `one` | exactly one satisfies | consistent simplification |
| `none exist` | none | deprecated OVAL value | do not restore |

The questionable term is `any`: it is shorter but can mean “an arbitrary
member” in ordinary English. It is not obviously better than OVAL's established
“at least one” concept or the repository's existing `one_or_more` spelling.

## 3. Existence requirement

OVAL `ExistenceEnumeration` and NG existence are semantically separate from
the check/match quantifier above.

| OVAL 5.12.3 | Meaning | NG 0.2.0 | Disposition |
|---|---|---|---|
| `all_exist` | all relevant entities exist | `all` | consistent simplification |
| `any_exist` | zero or more may exist | `optional` | **meaningful improvement**: communicates optionality better |
| `at_least_one_exists` | one or more exist | `some` | **0.3.0 change**; prefer canonical `one_or_more` unless review finds a better reason |
| `none_exist` | zero exist | `none` | consistent simplification |
| `only_one_exists` | exactly one exists | `one` | consistent simplification |

Important OVAL nuance: for Test `check_existence`, OVAL documents
`all_exist` as equivalent to `at_least_one_exists` because non-existent Items
do not affect Test evaluation. For State entity existence, the distinction can
still matter. NG SHALL preserve the semantic scope rather than treating the
words as interchangeable globally.

## 4. Logical operators

OVAL `OperatorEnumeration` combines criteria or State results.

| OVAL 5.12.3 | NG 0.2.0 | Disposition |
|---|---|---|
| `AND` | `all` | consistent authoring vocabulary |
| `OR` | `any` | consistent authoring vocabulary, but coordinate with quantifier review |
| `ONE` | `one` | consistent authoring vocabulary |
| `XOR` | `odd` | **meaningful improvement** |

OVAL XOR has parity semantics: true when an odd number of operands are true,
not merely “exactly one”. NG `odd` states that behavior more accurately.

## 5. Comparison operations

| OVAL 5.12.3 | NG 0.2.0 |
|---|---|
| `equals` | `equal` |
| `not equal` | `not_equal` |
| `case insensitive equals` | `equal_ci` |
| `case insensitive not equal` | `not_equal_ci` |
| `greater than` | `greater_than` |
| `less than` | `less_than` |
| `greater than or equal` | `greater_or_equal` |
| `less than or equal` | `less_or_equal` |
| `bitwise and` | `bit_and` |
| `bitwise or` | `bit_or` |
| `pattern match` | `match` |
| `subset of` | `subset` |
| `superset of` | `superset` |

The shift from whitespace phrases to snake_case is a reasonable machine-authoring
consistency improvement. However, abbreviations such as `ci` and shortening
`equals` to `equal` are not automatically meaningful improvements. The
0.3.0 operation-vocabulary issue should decide the canonical spellings as one
family rather than one token at a time.

## 6. Datatypes

| OVAL 5.12.3 | NG 0.2.0 | Disposition |
|---|---|---|
| `binary` | `binary` | retain |
| `boolean` | `boolean` | retain |
| `evr_string` | `rpm_evr` | meaningful clarification |
| `debian_evr_string` | `debian_evr` | meaningful clarification |
| `fileset_revision` | `fileset_revision` | retain |
| `float` | `float` | retain |
| `ios_version` | `ios_version` | retain |
| `int` | `integer` | consistent/full-word improvement |
| `ipv4_address` | `ipv4` | concise native type; retain unless semantic ambiguity appears |
| `ipv6_address` | `ipv6` | concise native type; retain unless semantic ambiguity appears |
| `string` | `string` | retain |
| `version` | `version` | retain |
| `record` | `record` | retain |

The renamed package-version datatypes remove OVAL-specific historical wording
and identify the comparison domain more clearly.

## 7. Filter action

| OVAL 5.12.3 | NG 0.2.0 | Disposition |
|---|---|---|
| `include` | `include` | retain |
| `exclude` | `exclude` | retain |

No terminology divergence is needed.

## 8. Set operator

| OVAL 5.12.3 | NG 0.2.0 | Disposition |
|---|---|---|
| `UNION` | `union` | formatting consistency |
| `INTERSECTION` | `intersection` | formatting consistency |
| `COMPLEMENT` | `difference` | meaningful improvement |

NG uses lowercase source vocabulary consistently. `difference` is easier for
authors to understand as an ordered A-minus-B operation than OVAL's historical
`COMPLEMENT` spelling. NG must still preserve OVAL semantics, including
single-operand behavior and filtered operands.

## 9. File recursion target

Non-deprecated Unix/Independent OVAL file behavior uses:

| OVAL 5.12.3 | NG 0.2.0 | Disposition |
|---|---|---|
| `directories` | `directories` | retain |
| `symlinks` | `symlinks` | retain |
| `symlinks and directories` | `symlinks_and_directories` | formatting consistency |

Windows retains the corresponding `junctions` terminology rather than
pretending junctions are Unix symlinks.

Deprecated OVAL values such as `files`, `files and directories`, and
`none` SHALL NOT be reintroduced into native NG merely for compatibility.

## 10. File recursion direction

OVAL historically exposed `up`, `down`, and `none`.
The current NG traversal construct represents only supported downward traversal;
direction is structural rather than a selectable vocabulary.

Disposition: **meaningful simplification**. Deprecated/unsupported upward
recursion does not justify retaining a three-value direction switch.

## 11. Filesystem traversal scope

| OVAL 5.12.3 | Meaning | NG 0.2.0 |
|---|---|---|
| `all` | all available filesystems | `any` |
| `local` | local filesystems only | `local` |
| `defined` | remain on the filesystem containing the explicitly defined path | `same` |

This is a 0.3.0 terminology review item. `same` may be clearer than
`defined`, but `any` is not obviously clearer than OVAL `all`. The family
should be reviewed together.

## 12. Variable/input cardinality

NG uses:

- `one`;
- `zero_or_one`;
- `one_or_more`;
- `zero_or_more`.

This is an NG authoring vocabulary derived from cardinality, not a direct OVAL
enum. It is explicit and internally regular. It is also one reason that
`one_or_more` is preferable to introducing a separate `some` synonym for the
same count concept.

## 13. OVAL variable-function selectable vocabularies

Pinned OVAL 5.12.3 defines these additional author choices:

### ArithmeticEnumeration

- `add`
- `multiply`
- `divide`
- `subtract`

### SortEnumeration

- `document`
- `lexical`
- `numeric`
- `natural`

### OrderEnumeration

- `ascending`
- `descending`

### DateTimeFormatEnumeration

- `year_month_day`
- `month_day_year`
- `day_month_year`
- `win_filetime`
- `seconds_since_epoch`
- `cim_datetime`

Current conversion/round-trip tooling recognizes OVAL variable-function
constructs, including arithmetic. These selectable vocabularies are not yet
presented as one clearly versioned native 0.2.0 schema/reference family.

Disposition: **0.3.0 coverage gap**. Preserve OVAL names by default unless a
native representation has a documented meaningful improvement.

## 14. OVAL family vocabulary

OVAL has a central `FamilyEnumeration` such as `unix`, `windows`,
`macos`, `ios`, etc.

NG does not expose this as one author-selected family enum. Instead, the
capability namespace carries the relevant domain (for example `unix.file`,
`windows.registry`, `linux.rpminfo`).

Disposition: **meaningful architectural improvement**. Capability identity is
more precise than asking an author to separately select a broad family.

## 15. OVAL message level

OVAL `MessageLevelEnumeration` contains:

- `debug`
- `error`
- `fatal`
- `info`
- `warning`

This is not currently a first-class native Assessment-authoring selector.
Migration/conversion diagnostics and runtime result diagnostics are separate NG
concerns. Do not introduce this vocabulary into native source solely because it
exists in OVAL.

## 16. NG-only selectable vocabularies

These have no direct OVAL enum equivalent and therefore are not candidates for
lexical compatibility:

- Assessment `mode`: `manual` / `automated`;
- Assessment `purpose`: `assessment` / `applicability`;
- input cardinality;
- reported-elements projection;
- result/evidence materialization controls;
- package/signature choices defined outside OVAL Assessment semantics.

Each NG-only vocabulary still needs internal naming consistency.

## 17. 0.3.0 decision rule

For every vocabulary reviewed in 0.3.0:

1. identify the exact OVAL lexical values and semantics;
2. identify the current NG lexical values and scopes;
3. prefer the OVAL concept when semantics are the same;
4. normalize spelling only when it makes NG internally consistent;
5. rename only when the new term communicates semantics more accurately or removes a real historical ambiguity;
6. never introduce a synonym merely because it is shorter;
7. preserve explicit migration aliases only when needed for 0.2.0 compatibility;
8. add a focused regression whenever a vocabulary change could affect conversion or truth semantics.

## 18. Current 0.3.0 issue tracking

Concrete changes are tracked independently from this crosswalk. This document is
the comparison/reference surface, not the implementation backlog.

At minimum:

- existence `some` vs `one_or_more`;
- check/match `any` vs OVAL `at least one`;
- comparison-operation naming family;
- filesystem-scope naming family;
- explicit native coverage for OVAL variable-function choice vocabularies.

The crosswalk SHALL be updated when those issues are resolved.

