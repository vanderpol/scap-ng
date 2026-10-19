# 0.4-C: shared observations versus Apache's 19-Variable graph

**19 October 2026 · [research #245](https://github.com/vanderpol/scap-ng/issues/245) · proposal and bounded source census, NOT accepted grammar or scanner.**

## Why change direction within C?

The source-preserving 0.4-A/B approach exposes a long chain of named commands, regex captures, concatenations and merges. The [real Apache SV-214268 source](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml) has **19 Variables, five Tests and 10 source acquisition declarations**. Six named Variables have two direct consumers. A source-backed [read-only observation census](../../../tools/research_c_shared_observations.py) now measures *collection-request identity* separately from Variable fan-out; [negative tests](../../../tools/test_research_c_shared_observations.py) forbid coalescing different commands, patterns, flags, scopes, filters or dynamic command bindings. A bounded CI assertion expects **10 distinct acquisition contracts** here. Verify against the exact-head Actions run before treating the code result as independently CI-confirmed.

The critical design insight: **the author cares about observed facts, not the variable names required to assemble shell commands**. The collection and transformation details remain essential to scanner correctness and forensic evidence, but should not dominate the primary auditing view.

## Three things we must not confuse

| Construct | What it means | Sharing |
| --- | --- | --- |
| **Collection recipe** (A Object / capability + exact parameters) | How to request Items | Identical, supported plans can potentially share a collection execution inside the same bounded target/snapshot context; an identical request is **not** proof of identical behavior across time, privilege, versions or targets |
| **Observation** (proposed first-class read-only evidence) | A typed Item/record population **and** its completeness/error/provenance/identity, produced by a collection or derived step | Multiple checks or Rules can reference the *same observed evidence* without inventing new existence/matching rules; preserve each consumer's original population and scope |
| **Requirement / Test outcome** | How a particular policy judges observed evidence | May be referenced separately, but is **not** interchangeable with a shared observation; different Rules can impose different requirements on identical facts |

A source Variable might construct a command string, a list of filepaths or a predicate input. None is automatically equivalent to a reusable observed Item collection. C must make these categories explicit and give each one a clear authored role.

## Exact source-backed Apache decomposition

The real five Tests check **Session**, **SessionCookieName (HttpOnly and Secure)** in two *different* configuration populations, and whether the Apache session-cookie module is enabled.

| Candidate named fact | Actual source lineage | Consumers / constraints |
| --- | --- | --- |
| Apache process/executable discovery | Existing shared shell command `ps -e -o command ...` and two different regex captures | Installation base for apachectl commands; executable path for module and loaded-file commands; do not assume one Apache instance |
| Main configuration filepath | HTTPD_ROOT and SERVER_CONFIG_FILE acquired from separate original commands, then combined | Used for Include discovery and the main + included-files population |
| **Main + referenced Include files** | Main filepath + shell grep of Include/IncludeOptional + extracted path merge | Session and SessionCookieName **mandatory-main** checks |
| **Actually loaded configuration files** | Apache `-t -D DUMP_INCLUDES` output, regex capture → unique → merge | Session and SessionCookieName **other-loaded** checks; not automatically equal to main + Include |
| Loaded modules | Original executable-derived `-M` command | Session-cookie module Test |
| Session and SessionCookieName lines | **Four distinct** downstream shell command/pattern requests across the two file populations | Source Item selection, when-present versus mandatory field existence, same-Item semantics and per-Test provenance must remain visible |

The two file populations are **not** interchangeable. A single convenient `apache.config_files` label would be ambiguous unless it names a precise population. The source also uses distinct existence/matching semantics between main and other-loaded checks; using one generic `must` to conceal those distinctions risks false Pass or Fail results.

The prior [Apache second-pass review](../english-first-04/APACHE-SECOND-PASS-READABILITY.md) independently found 18 Variables and five reused nodes in a *different* Apache SV-214228 Assessment. Aggressively inlining seven single-use operations there **increased** indentation and source lines over a more modest four-name reduction. This is evidence against “inline all Variables”; it is not evidence against explicit shared observations.

## Candidate C authoring model: facts once, requirements separately

**Non-executable semantic sketch; syntax, names and provider support are not approved.** The references below denote existing source lineages, not newly implemented `apache.*` collectors.

```yaml
observations:
  apache_processes:
    acquire: existing-source-process-collection
  main_and_included_files:
    derive_from: existing-source-main-plus-include-lineage
  loaded_configuration_files:
    derive_from: existing-source-DUMP_INCLUDES-lineage
  session_lines_main:
    acquire: existing-source-main-session-command
  session_lines_loaded:
    acquire: existing-source-loaded-session-command
  cookie_lines_main:
    acquire: existing-source-main-cookie-command
  cookie_lines_loaded:
    acquire: existing-source-loaded-cookie-command
  enabled_modules:
    acquire: existing-source-apache-M-command

requirements:
  - check: existing-source-required-main-session-test
    on: session_lines_main
  - check: existing-source-optional-other-loaded-session-test
    on: session_lines_loaded
  - check: existing-source-required-main-cookie-test
    on: cookie_lines_main
  - check: existing-source-optional-other-loaded-cookie-test
    on: cookie_lines_loaded
  - check: existing-source-cookie-module-test
    on: enabled_modules
combine: existing-source-five-Test-AND
```

This shows **comprehension architecture**, not a new source-equivalent authoring program. It intentionally does *not* imply the hidden source graph has disappeared; with only present A collectors, the full Variable graph and distinct collection contracts must still exist in compiler-owned compatibility IR. A short alias list alone is a *presentation* win, not proven reduction in runtime commands or source complexity.

**Second, more valuable but harder experiment:** permit one reusable *typed configuration-content observation* to expose Directive Items with file identity to several Rules (Session, SessionCookieName, KeepAlive, MaxKeepAliveRequests, etc.). Acquire file contents using reviewed A-derived capabilities if possible, transform into provenance-preserving typed directive observations, and evaluate each requirement separately. This may genuinely shrink repeated collector calls and source-specific command-building. It is **new native policy** unless we independently prove equivalence of Apache config parsing, Include/IncludeOptional, runtime overrides, glob/relative-path rules, quoting, symlinks, duplicates, module context, ordering, empty/partial/error behavior, regex selection and scope to the legacy shell commands. Do not quietly claim a faithful SCAP 1.4 conversion.

## Observation contract required before implementation

Every observation must explicitly carry:
- **Identity & scope:** source/observation ID, provider/capability version, host, scan snapshot, environment/privilege, caller input bindings, namespace/registry view where relevant, and parent/foreach correlation keys.
- **Typed evidence:** collection request fingerprint, Item/field/record types and IDs, duplicate and order semantics when observable, source file/command location, path/line provenance, and derived-value origin.
- **Completeness:** complete success vs complete-empty, incomplete, missing/not-collected, error and not-applicable. Reusing an observation must never upgrade unknown to complete or launder errors into absence.
- **Consumer independence:** an observation contains data, not the policy's `any_item` / `every_item` / optional/existence decisions. Different consumers can judge the same evidence differently and retain separate Test results.
- **Cache boundary:** only share an execution where acquisition requests **and execution scope/snapshot** agree, without timing- or privilege-dependent side effects. Never coalesce distinct shell commands solely because they concern the same Apache file.
- **Traceability:** two-way edges from each Rule/Test to the shared observation and all original source Variables, Objects, Item IDs and transformations; failures explain which evidence was missing or invalid.

## Next decision gate — a measured improvement, not shorter prose

1. **Exact-source track:** show full SV-214268 source → shared-observation view → exact pinned A/source reconstruction, and verify five Test outcomes against independently expected complete/empty/incomplete/error evidence. Prove that reused observed Items preserve each Test's cardinality and parent scope.
2. **New native observation track:** implement a small typed Apache directive observation over *precollected files*, with two checks reading one observation and independent expected outcomes. Do **not** add an unreviewed OS collector. Verify duplicate directives, contradictory lines, absent files, failed reads, cross-file contamination and relative Include paths.
3. **Measure across Rules:** count reused source acquisition contracts, repeated derived values, and potentially shared typed facts in the reference Apache STIG. Distinguish author-visible expressions eliminated, runtime calls reduced, source identity retained and unproven parser semantics.
4. **First-read human review:** can an auditor correctly explain the two different file populations, conditional checks and absent/incomplete results using only the observation-oriented C view? Do not accept a shorter source if those distinctions disappear.

**Recommendation:** promote shared observations to a **primary C research hypothesis**, but not yet to normative syntax or an optimization requiring a new scanner implementation. This is likely to achieve larger gains than renaming OVAL operators, especially when observations are reused across many Rules. A-compatible import remains the safety baseline.

## Executable native-observation micro-probe (not legacy source conversion)

A separate [precollected Apache directive observation](../../../tools/research_c_apache_directive_observations.py) and [adversarial tests](../../../tools/test_research_c_apache_directive_observations.py) now test the architectural *value* of actual shared facts, not just shortening a source Variable graph:

- One explicitly named file population of precollected typed `{file_id, path, line, text}` records is read **once** by the prototype; two independent consumers select `Session` and `SessionCookieName` directive Items without executing additional commands.
- Items preserve parent file identity and line number. A `SessionCookieName` missing `Secure` in one source file cannot borrow `Secure` from a directive in another file merely because the fields were extracted from a shared source.
- A complete-empty population stays distinct from incomplete/error/not-collected; a partial collection retains the `incomplete` status and observed lines, **without assigning Pass**. Unsupported file identities/line ordering and terminal errors carrying trusted Items are rejected.
- Shared observations carry facts and provenance; they do **not** impose the existence or all/some comparison semantics for any consuming Rule. A consumer may judge two `Session` lines differently depending on its explicit policy.

**Hard limitation:** this reads already-acquired lines; it does not resolve Include/IncludeOptional, Apache quoting or effective configuration contexts, and it does not replace the legacy source's four distinct grep commands. It is not a new OS collector and is **not** an OVAL 5.12.3 execution oracle. The focused GitHub Actions regression now includes the probe, but its latest exact-head result must be inspected before saying CI passed.

The benefit to measure next is whether a reviewed **existing A-derived file collection** can supply these shared typed lines for many Rules. If that proof fails, maintain the original shell-based source-compatible plan and keep the typed observation approach explicitly native.
