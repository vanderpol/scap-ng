# SCAP-NG English-first Assessment research — quick external review

**Not approved v0.4 syntax. Not a scanner.** A research comparison, not a standards vote.

## The question

Can a security administrator understand a complete Assessment without knowing OVAL, **while a scanner implementer can reproduce the original SCAP 1.4/OVAL semantics without guessing**?

## Four real source-backed examples

[View the short YAML excerpts and their limitations](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md) · [Download four complete research YAMLs (GitHub Actions artifact)](https://github.com/vanderpol/scap-ng/actions/runs/38913249970/artifacts/12051575856).

| Source example | Why it is hard | Where the experimental grammar helps |
| --- | --- | --- |
| **RHEL 9 SV-257889** | User-password inventory → nested file collection, Set union/difference, filters, eight permission fields | explicit Set/iteration scope and `every_item_must_match`; source one-operand union still needs a simpler proven form |
| **Windows 11 SV-253495** | Domain role from WMI records plus seven user-right Tests and three OR alternatives | Named `sources` + check-level `from`, nested `every_record`, `at_least_one_item_matches`, `any_of`/`all_of` |
| **Windows Server DNS SV-259345** | Dynamically generated zone commands, exact-one stdout, five Tests/three alternatives | Check-level `collect`, `exactly_one_is`, named `all_of`/`any_of`; command-building Variables preserved |
| **Apache 2.4 SV-214228** | Discover installation and included config; four required/optional directive Tests, 18 local Variables | `when_present_matches_regex` vs required values, preserved source command Variables and error handling |

**Source verification:** [CI](https://github.com/vanderpol/scap-ng/actions/runs/38913249970) reconstructed all **four entire source-Assessment dictionaries exactly** (not just excerpts). The expanded [six-STIG census](https://github.com/vanderpol/scap-ng/actions/runs/38921900743) now reconstructs **871/872 complete automated Assessments (99.9%)**, with one source shape still rejected. A separate compact-layout experiment removes redundant collection syntax without changing the original Assessment dictionaries. These are **structural round trips of the existing 0.4 preview**, not independent six-state scanner/OVAL runtime proofs.

## Three questions for technical reviewers

1. **Readable enough?** After seeing a complete file, which elements are still unclear without OVAL experience? In particular, can the reader distinguish collection expansion (`for_each_source`) from evaluating collected items (`every_item_must_match`)?
2. **Semantically safe?** How should a compact typed field operator preserve Item-vs-field cardinality, missing/unknown/incomplete collection, and record-level checks? The mixed WMI `domainrole=[1,3]` population is an explicit counterexample to rewriting two whole-State alternatives as a single per-record membership check.
3. **What must remain explicit?** Is there a genuinely readable way to show DNS/Apache derived command graphs and filesystem Set/filter provenance without rewriting how data is gathered?

**Draft consistency rule:** Ordinary `inspect` implicitly gathers; put `where`/`collect` beside it, use `from` for named sources, and reserve `gather` for complex Sets/iteration. The `gather.union` shorthand (without `combine`) in the [examples page](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md) is a proposed illustration, **not yet source-verified**.

**Boundary:** We are **not** asking for approval of `check`, `inspect`, `gather`, or `require` names. The work is pre-alpha research toward *one* human-readable, source-faithful authoring grammar. Existing v0.3 and pinned v0.4 review artifacts are unchanged.

Tracking: [research #235](https://github.com/vanderpol/scap-ng/issues/235) · [semantic proof #229](https://github.com/vanderpol/scap-ng/issues/229).
