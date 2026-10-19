# C permission shorthand: filters and missing fields safety review

**19 October 2026 · #245 · research only — NOT an approved C language change, accepted source converter rewrite, or scanner-semantic proof.**

## Source-backed distinction

The inherited RHEL9 **SV-257889** has a shared `state-mode-0740-or-less-permissive` State containing **eight separate Boolean checks** (`suid`, `sgid`, `sticky`, `gwrite`, `gexec`, `oread`, `owrite`, `oexec`) with **AND** grouping, each requiring its observed field to exist and equal false. Both original `unix.file` Tests reference the same State but apply different Item-existence requirements.

**The RHEL9 source does contain Filters and Sets**, but these reference **other** States: UID/home selection and directory exclusion before the two Test populations are evaluated. The eight-bit permission State is a **Test State** in this particular graph, **not a Set/Filter State**. This is confirmed by [the original authored graph](../samples/rhel_9/assessments/automated/niwc.rhel_9.SV-257889.automated.assessment.yaml) and [typed source-edge evidence](../evidence/rhel_9/SV-257889/graph.json). This distinction is material: a State used to exclude Items cannot be replaced by an unchecked Test result without changing which Items exist for subsequent existence/matching rules.

## Safe scope of the candidate shorthand

```yaml
must:
  every_item:
    permission_bits:
      no_more_permissive_than: '0740'
```

For the **exact proven State shape only**, the research compiler **expands** this authoring shortcut back to the same eight A-mapped `unix.file` Boolean State predicates (with their individual field-presence requirements), rather than replacing them with a new scanner-side numeric mode comparator. The 4,096-mode numerical test proves equivalence **only for fully observed, valid twelve-bit POSIX modes**, not collection, Set/Filter selection, absent Item fields, ACLs, symlink resolution, errors, or provenance. The source Test existence requirements and two dynamic home-directory populations remain unaltered.

**Explicit rejection rule:** A faithful-source permission-State rewrite is **ineligible** if that State is referenced by *any Object Filter or nested Set Filter*, if its eight Boolean terms are missing, duplicated, non-AND, not strictly false/equality, have different entity existence/check requirements, or if its Test uses a more complicated State composition. It is not enough that the eight bit values look equivalent. A future generalized filter-aware rewrite would require a distinct, independently checked six-state filter-selection and propagation proof; **no such rewrite is approved**.

## Executable source-guard and adversarial tests

- [`prove_legacy_source_permission_state_context`](../../../tools/research_c_permissions_macro.py) reads the **complete original Assessment** with its Objects, Filters, Sets, Variables, States and Tests, and permits the exact State **only for AND Test-State use**. It carries the source graph fingerprint and returns **unchanged** Objects, Variables, Test existence/matching contexts; it explicitly declares `filters_rewritten: false` and `runtime_parity_verified: false`.
- [Negative tests](../../../tools/test_research_c_permissions_macro.py) inject the same permission State as a direct Object exclude Filter **or inside a Set operand Filter**, remove/duplicate a required permission term, change a term from false to true, weaken its field presence/check requirement, change AND to OR, or change a consuming Test's matching requirement. Each must fail rather than claim lossless substitution.
- No default source-converter or scanner change is made. The standalone C macro is still a **research-only authoring mechanism**. New native authoring of other policies is a separate use from automatic rewriting of existing SCAP 1.4 source.

## Cross-Rule and global-State reference limitation

The checks above inspect the **one source Assessment closure** supplied to the guard. The original OVAL State may be shared by other Rules or references in the same source datastream, including Filters outside this closure. Therefore local structural eligibility is **not global conversion eligibility**. The research guard now reports `LOCAL_STATE_PATTERN_ONLY_GLOBAL_USES_UNAUDITED`, with `global_source_consumers_audited: false` and `source_conversion_authorized: false`. A complete datastream/benchmark-wide reverse-reference audit (including object filter uses) is a separate prerequisite before any source-converter rewrite. The authoring shortcut can still compile to eight native conditions for a newly authored check, without claiming a source migration.

## Decision

**Conditional GO for researching a visible authoring alias over this exact local Test-State pattern; NO-GO for automatic source rewriting until benchmark-wide consumers and filter semantics are independently checked, and NO-GO for changing collector behavior.** Retain all eight native bit predicates in the compiled evaluation contract. Do not promote the alias or its present English spelling before the other C semantic and first-read authoring gates pass.

This is one bounded case study and cannot authorize substituting an octal-mask comparator for arbitrary `unix.file` States, changing `SV-257889`'s account populations, or extending the shortcut to other source States.
