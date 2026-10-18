# 0.4 command composition: acceptance contract before choosing syntax

**18 October 2026 · Research #235 / #227. Not an accepted or normative specification.** Use alongside the two complete [DNS](FULL-04-dns-INLINE-COMMAND-CANDIDATE.md) and [Apache](FULL-05-apache-INLINE-COMMAND-CANDIDATE.md) direct-command candidates and the unchanged [before/after baseline](BEFORE-AFTER-REVIEW.md). No compiler, scanner, new execution primitive or source modification is implied by this review.

## What was really removed

Both experiments eliminate **single-use command-expression *names***, not collection operations, shell commands, dependency edges or Test outcomes.

| Source | Prior English-first | Direct-command candidate | Verified construction | Unverified |
| --- | --- | --- | --- | --- |
| DNS `SV-259345` | 3 Variables, 184 non-comment lines | 0 Variables, 163 lines | 3 `collect.command.variable` references replaced by their exact original `concat` expression subtree, one each; reversible when original declarations are retained | Standalone recovery of Variable title, `kind`, datatype and runtime typing / provenance |
| Apache `SV-214228` | 18 Variables, 335 lines | 14 Variables, 310 lines | 4 leaf `collect.command.variable` references replaced with exact original `concat` expression, one each; 14 upstream Variables untouched | 14-step graph still burdens author; how a scanner maps nested expression into a shell command |

**Important:** These are line counts from the *prior research after* YAML, **not** the source 0.4 normative schema. Reversibility of a text edit *with an edit recipe* is not proof that an author can produce a complete self-describing native 0.4 Assessment or recover omitted source metadata.

## Official OVAL 5.12.3 clarification: vector `concat` versus scalar `merge`

The [5.12.3 Core Definition](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#concatfunctiontype) explicitly says a multi-valued concat component yields **a collection of constructed strings**, using a Cartesian product when several components are multi-valued; [merge](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#mergefunctiontype) yields **one string** from a collection. See the [source-backed DNS/Apache distinction](OVAL-5123-CONCAT-MERGE-READABILITY.md). **This settles the original OVAL function-level meaning, NOT the native 0.4 Value→Object→collection instance correspondence, upstream failure behavior, or scanner parity.** Do not replace one by the other for authoring convenience.

## Semantic contract a viable *single authoring language* must expose

Before choosing `collect.command: concat`, `derive`, `pipeline` or any other syntax, an implementer should be able to answer every cell without an undocumented default.

| Boundary | What must remain explicit | Failure mode to test |
| --- | --- | --- |
| Source reference | Which named collection and which element (`stdout_line`) supplies each command input | Missing source ID; wrong capability/field type; unrelated scope |
| Value cardinality | Whether `values.object.field` means zero/one/many values and how `concat` consumes their **ordered** population | Zero values, two different zone names, duplicate values, missing field, error Item |
| Command rendering | Literal fragments, type conversion, separators, quoting/escaping, environment and shell | Silent join of many zones, command text changed by trimming/quoting, shell injection risk; do **not** change the original commands merely to improve style |
| Runtime acquisition | Whether dependent collection waits for upstream source; whether source results are cached/shared | An incomplete/error upstream collection treated as successful empty string; redundant collector execution |
| Result completeness | Preserve complete/incomplete/error/not-collected/not-applicable flags and who produced them | Assumed `true` or `false` for an unresolved command |
| Assessment checks | Preserve **Item count**, stdout field presence, value matching, optional-vs-required predicates and exact six-state `evaluate` | `no_values_exist` misread as `no command Item exists`; optional Apache directive treated as unconditional |
| Provenance & authorship | Original source ID, Variable title/kind/datatype where semantically relevant, source graph and evidence/sample hashes | Standalone inline authoring drops legacy metadata with no recovery policy |

**Stop condition:** If any such question requires a newly invented runtime rule, the candidate may still be reviewed for human comprehension but **must not** be promoted as equivalent.

## Explicit counterexample: DNS multi-zone concatenation

The DNS source command is built from **literal + `values.object: list-all-forward-lookup-zones-object`, `field: stdout_line` + literal**. The source does **not** declare a `for_each` over each zone in the existing English-first command definition. It would be unsafe to tell auditors that the candidate “runs one command per zone” merely because the source variable is plural. The multi-zone command-building semantics, including original shell interpretation, require a real provenance-aware differential proof.

**Separate case:** The DNS caching-only Test has `at_least_one_item_exists: true`, but its **`stdout_line` field** requires `no_values_exist`. Removing those apparently contradictory words would actually erase a distinction between successful command execution with zero output lines and no collected command Item.

## Explicit counterexample: Apache two configuration-file sources

The Apache source has **two independent discovery paths**: reading the root config plus Include/IncludeOptional references, and querying actually loaded configuration files. Their membership and error behavior may differ. A new single `all_config_files` source or one short “check across all Apache configuration” action would be an **unproved semantic rewrite**. Both must remain distinct unless equivalence holds for zero/one/many files, missing references, dynamic includes, stderr/exit statuses, and partial output.

Four final command-expression Variables can be inlined safely as a **source edit** only because each has one check use; that does **not** justify collapsing those two upstream sources.

## Vocabulary choices now grounded in the two real source operations

The [operator language comparison](VALUE-OPERATOR-AUTHORING-BAKEOFF.md) sets a **V1** control (the existing `concat` / `merge` function meanings) against **V2** (`build_each_combination` / `join_values`) and rejects **V3** (a raw string-template interpolation layer) for now. The [neutral micro-comprehension packet](VALUE-OPERATOR-BLIND-PACKET.md) must be completed before reviewers read the expected answers. Neither changing terms nor inline placement is approved; collection and result-status rules stay separate from the OVAL value-function output.

## Decision hypothesis to test with authors

- **H1 (minimum intervention):** Permit an *explicitly typed* inline command expression at a check's collection boundary for a **single-use** derived command. Keep reused named sources and Variables when they genuinely serve more than one consumer. Requires a canonical typed expression contract, explicit provenance/metadata handling and no hidden defaults.
- **H2 (editor-only navigation):** Keep the existing source graph, but show a one-line expanded command preview and a “go to original definition” link for each variable use. Requires no new authoring syntax; may be preferable if inline expressions bloat checks.
- **H3 (new composition operator):** Defer. Do not add `pipe`, `derive`, `gather`, `where` or a new implicit per-zone loop just because Apache still has 14 upstream Variables. First show H1 or H2 fails on a complete high-complexity check with independent auditor evidence.

**Preferred *next experiment*, not an adoption:** Compare H1 and H2 with one **blind** complete DNS Assessment, then repeat for the full Apache Assessment if H1 helps. Score accurate inference about multi-value inputs and incomplete/error separately from superficial YAML aesthetics. If authors cannot explain these semantics, “shorter” loses.

## Rejected assumptions and next gates

Reject “command interpolation always loops over all values,” “single-use means safe to delete metadata,” “no stdout means no Item,” “case-insensitive pattern equivalence can be guessed,” and “Apache's two file populations can be merged.” For every accepted candidate, source AST roundtrip and independent result-status/evidence tests remain future gates. There are **no new independent reviewer scores or verified scanner results** in this file.

Dated recommendation for this iteration: keep the inline-command candidate **under study**, retain the current grammar as authoritative, and prioritize collection/Variable composition and transparent source cardinality over choosing English synonyms.
