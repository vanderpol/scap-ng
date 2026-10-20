# 0.4-C Registry correction: preserve 0.4-A assessment mechanics

**20 October 2026 — research #245, not an accepted grammar change.**

## Verified actual source, not hypothetical Registry content

The pinned [original OVAL Self-Assertion Registry XML](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/windows/win-def_registry_test.xml), Definition `oval:org.mitre.oval.test:def:38`, contains **15 Registry Tests**, not one. One representative Test is `oval:org.mitre.oval.test:tst:1020`. Its exact source and independently converted A-compatible graph were checked against `c-review/adccc92797baef8bfea72399.review.json` in the pinned source-backed CI artifact.

| Aspect of that actual Test | Original OVAL 5.12.3 / A-compatible structure | C design implication |
| --- | --- | --- |
| Collection identity | ONE `registry_object` selecting `hive`, `key`, `name` | ONE collection with the same three selectors; order **hive → key → name** |
| Registry hive selector | `HKEY_LOCAL_MACHINE` (native 0.4-A capability enum: `local_machine`) | Use A's version-pinned enum crosswalk, **not** a second hive vocabulary |
| Key selector | `SOFTWARE\Microsoft\Windows NT\CurrentVersion`, equality | Same selector; no needless per-field `description` or `datatype: string` |
| Name selector | `CurrentVersion`, equality | Same selector, clearly named `name`; this identifies the Registry value entry |
| State | `hive` equals HKLM; `key` **case-insensitive equals** that path; `name` equals CurrentVersion | Retain all three State predicates, including different key comparison semantics |
| Test result | `check_existence="at_least_one_exists"`; `check="only one"` | Keep exact 0.4-A Test/existence/match semantics; no generic `must` substitution |
| Registry `value` | **Not checked** in this Test | Don't invent a `value` State predicate or conflate `name` and collected `value` |

[0.4-A README](../../../../schema/v0.4.0/README.md) already defines keyed Object comparison syntax, States, typed selectors, and Test `require`. [A Registry capability](../../../../schema/v0.4.0/capability-mappings/supported/windows.registry.json) declares `hive`, `key`, `name` as string-only State fields, while actual Registry **value** admits different datatypes; the old OVAL source and 0.4-A mapping must continue to control these semantics.

## Correction to misleading C sample

The prior [literal collection-input sample](c-original-windows-registry-typed-collection-inputs.research.yaml) showed three independently authored `input_name` / `input_hive` / `input_key` records, each redundantly carrying selector, description, datatype, and value. They came from **three different OVAL Variable-driven source Objects** in the same full Definition (hive-variable, key-variable, value-variable), whereas the simple `tst:1020` uses one Object with three literal selectors. The prior sample was source-projection *research*, **not** the authoring structure of a single Registry Test and **not** evidence of simpler C. It was misleading to show it as the ideal Registry example.

The linked sample is replaced by an **explicitly non-grammar comparative view** of `tst:1020`. The source-compatible tests and proof adapters may remain as migration/evidence research, but are no longer promoted as candidate C authoring syntax.

## Reset the comparison standard

**Do not redesign basic OVAL Object/State/Test declarations for C.** Adopt the 0.4-A implementation contract, with `object`→`collection` terminology if approved, logical display order (Collection → States → Test requirement), names and concise documentation. The user-facing editor may hide derivable string datatype and redundant legacy prose without changing the source/compiled representation. A presentation-only permutation is not counted as a language improvement.

**C requires a measured improvement over A on hard content, not new labels:**

1. Real Set/Filter example: preserve nesting, operand order, filter include/exclude and eight independent permissions bits, while demonstrating fewer and clearer *authored* operators.
2. Real Apache-derived-command DAG: reduce human-visible transformations or repeated collection requests without changing collection source, ordering, per-parent binding, regex/capture, missing/error propagation, or output identity.
3. Real foreach/conditional STIG: preserve per-parent correlation and full original AND/OR, with independent expected six-state results.
4. Compare side-by-side original OVAL, **existing 0.4-A**, proposed C and compiled-equivalence proofs. Measure total user-editable fields/lines, distinctive decisions, semantics and readability; don't count provenance moved to a separate file as removed execution complexity.

**Decision status:** proposed course correction in #245; no new normative grammar, no scanner parity, and no claim that C is substantially better yet. Avoid additional simple-Registry adapter churn. Focus only on actual complex-content gains before recommending C over A.
