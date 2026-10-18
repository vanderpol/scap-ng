# Apache authorability challenge — trace sources, don't guess status

**18 October 2026 · Unscored research exercise for issues #235 and #227.** This is **not a blind A/B experiment**: the two linked full candidates are visibly identified. It is a focused *authoring drill* for the source-composition problem. No independent reviewer has completed it, and no 0.4 semantic contract is being changed.

## Read two complete renderings of the same check

- [Existing complete Apache English-first Assessment](FULL-05-apache.md) — 18 named Variables, four Tests.
- [Complete inline-command authoring candidate](FULL-05-apache-INLINE-COMMAND-CANDIDATE.md) — 14 named Variables, same four Tests; four exact single-use command expressions moved to their check.

**Use the full files**, not an edited three-line policy excerpt. Both contain the actual source definitions, shell literals, `regex_capture`, `merge`, flags, predicates and evaluation tree. The original source-backed current 0.4 YAML is also on the first linked page.

## Five questions an author must answer

1. **Dataflow.** Starting from the Apache process command source, name and trace the two **different** config-file populations: HTTPD_ROOT + main file + Include/IncludeOptional references, versus Apache's reported **actually loaded** config files. Which named Variables are *shared* by multiple checks? Which intermediate command-building names have only one consumer?
2. **One check.** Starting from the complete candidate's *main config/Include* `KeepAlive On` check, locate the exact source expression that builds the command, and follow its prerequisites back to the originating `ps` command. State the literal shell command components rather than substituting an imaginary built-in `apache-config` collector.
3. **Four checks.** Explain why `KeepAlive` and `MaxKeepAliveRequests` each have **two** Tests. What is mandatory in the base/Include path, and what does `when_present_...` govern in the actually loaded-files path? Separate a missing *field* from no collected command *Item*.
4. **Faults.** If an Include reference cannot be read, one upstream command has nonzero exit status, or a collector returns incomplete output, which exact result state follows? Identify the source's explicit flags, then identify **what must be looked up in the specification**. Claiming “it probably passes” does not count.
5. **Make a change.** In a *hypothetical lab-only variant*, add a `Timeout` directive check using both existing config populations. Show which sources you would reuse and identify the unresolved comparator, field cardinality and command construction details. You need not invent final executable YAML where the grammar is undocumented. Explain which version was less error-prone to author.

## Evaluation notes (facilitator only; withhold until response)

**Source facts:** Original Test `verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test` requires at least one Item and matching `stdout_line` `\\s*KeepAlive On`; the parallel loaded-file Test uses `when_present_matches_regex`. The `MaxKeepAliveRequests` pair uses `subexpression.at_least: 100` in the main/Include path and `when_present_at_least: 100` for loaded files. The top-level authored `evaluate.all_of` references **all four** Tests.

**Structural distinction:** The authored `all-loaded-configuration-filepaths-variable` is not the same as the base config plus Include/IncludeOptional references. Neither candidate merges them or invents a file walker. All shell flags, extraction patterns and sorts remain in place.

**Evidence boundary:** Zero/many stdout values, missing source paths, failures and incomplete collection need the source's actual result/collection contract; the current snippets alone cannot prove those semantics. Any reviewer who confidently asserts all missing/failed commands become passing checks has guessed. The hypothetical `Timeout` exercise is **not** a proposal to alter the Apache STIG.

## What to score

Record reviewer background, document, time spent, incorrect source connections, named-variable lookups, missing-provenance claims, errors confusing Item vs field presence, and hypothetical authoring changes that alter source population. Mark each response as *correct / partially correct / unsupported guess* with source paths as evidence.

The source edit eliminates **four one-hop command names and 25 non-comment YAML lines**, but still leaves **14 Variables**. If it does not improve actual answers or authoring accuracy, keep original source declarations and investigate an editor-side dependency graph instead. A new `pipe` or `derive` keyword does not solve this by itself.
