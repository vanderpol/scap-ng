# SCAP-NG 0.4 — language derived from behavior, not chosen words

**Research working draft — October 16, 2026.** No vocabulary approved. No replacement 0.4 schema. The five cases below use original pinned Assessments, not invented examples. Read this before the [five complete before/after YAML comparisons](BEFORE-AFTER-REVIEW.md). We seek a *single executable, lossless human-authorable language*, not a pretty display layer.

**Vocabulary clarification:** Neither `where` nor `inspect` is disfavored or earmarked for deletion. They remain reasonable candidates if they clearly express distinct behaviors across real Assessments. We will not optimize for eliminating keywords, invent a new nesting scheme merely to replace familiar words, or select terminology before the full source-backed translation makes the need apparent.

## Describe what the Assessment does, without designing YAML

### 1. RHEL 9 — `/home` filesystem must have `nosuid` (SV-257851)

Read the effective Linux filesystem partition information. **Select** partitions whose mount point matches the original regular expression `.*\/home`. Require **at least one** selected partition. For **every** selected partition, require **at least one** mount-option value equal to `nosuid`. Include all elements in evidence.

*What remains explicit:* the source selection is **regex-based**, not exact `/home` matching; the two separate cardinalities (Items and option values) matter. The source permits a broader match than a new author might intend.

[Original and full English-first conversion](FULL-01-linux-home.md).

### 2. RHEL 9 — derive per-account initialization-file permissions (SV-257889)

Read Linux user accounts. Form one collection of non-system accounts and another of root accounts, using explicit collection difference and exclusion predicates. **For each** account in each relevant collection, derive the account's home directory and collect initialization files matching the source file-name pattern with the specified traversal rules. Exclude directory Items. Evaluate **all eight original permission requirements** for **every** selected file. Preserve the two populations' **different existence requirements**: no initialization files is allowed for the non-system-user check, but at least one is required for the root-user check. Both checks must pass.

*What remains explicit:* separate named populations, collection Set operations, per-user dependent collection, traversal and Item type exclusions, all eight permission predicates, population-specific cardinalities, and the final conjunction. The supplied source also includes a one-operand union, which an importer cannot silently delete without semantic evidence.

[Original and full English-first conversion](FULL-02-linux-files.md).

### 3. Windows 11 — domain role and deny-logon rights (SV-253495)

Read the computer's WMI `DomainRole` record(s). Select the appropriate security principal(s) assigned the **Deny log on through Remote Desktop Services** user right. The final Assessment permits **three distinct whole-check alternatives**: one applying to non-domain-controller domain-joined systems with several specified principals, one for standalone systems with the Guests principal, and one covering the separate Everyone-deny case. Keep every original existence/matching requirement on rights and WMI records.

*What remains explicit:* seven named Tests, three alternative branches, selection by the native Windows user right, per-Item/record/field quantifiers, and WMI role interpretation. Combining WMI alternatives into one per-record set-membership check is **not** equivalent when multiple records occur.

[Original and full English-first conversion](FULL-03-win11-rights.md).

### 4. Windows Server DNS — zones, signatures and validity bounds (SV-259345)

First obtain the DNS zone data used to construct three command-input Variables. Use the resulting PowerShell command(s) to check DNSSEC information and signature validity. Preserve the original **five** Tests and their final alternatives: a caching-only server, a qualifying Active Directory–integrated zone arrangement, **or** the conjunction of DNSSEC signed-zone and signature-validity checks. Preserve the lower and upper validity bounds rather than reducing them to one generic “valid” result.

*What remains explicit:* the zone discovery dependency, the three Variable definitions, command collection configuration, exact Test quantifiers, separate comparison predicates, and the original `any_of` / `all_of` topology. These command dependencies have not been proved replaceable by an automatic `for_each`.

[Original and full English-first conversion](FULL-04-dns.md).

### 5. Apache HTTP Server — discover configuration, then check directives (SV-214228)

Discover the Apache installation and effective configuration context, then follow loaded/included files according to the original commands. Using the **18 original Variables**, build commands to read the `KeepAlive` and `MaxKeepAliveRequests` settings. Enforce conditions on the required configuration locations and separately check conditions that apply only **when the optional directive exists**. Combine the original four Tests with AND.

*What remains explicit:* the installation/configuration discovery dependency graph, required versus when-present tests, command/error handling, four complete Tests and their final conjunction. A narrative “check Apache config” must not silently replace those dependencies or the effective-config semantics.

[Original and full English-first conversion](FULL-05-apache.md).

## Concepts that recur — independently of terminology

| Distinct concept | Why the author must be able to express it | Candidate words to evaluate later |
| --- | --- | --- |
| Intent / human title | Explains the security condition; does not define executable semantics | `check`, title |
| Native data kind | Selects a collector contract such as `linux.partition` or `windows.userright` | `inspect`, `capability`, `assess` (no winner) |
| **Object selection** | Narrows the objects before conditions are evaluated; not a compliance predicate | `where`, `select`, or nested field (open) |
| Collection procedure | Commands, query arguments, traversal, or source-specific collection parameters | `collect`, procedural source |
| Reusable/derived collection | Named collection reference and Set/iteration operations, possibly with filters | `from`, named source, direct Set operation |
| Filter of collected Items | Include/exclude elements using an already-collected State; distinct from selecting a native Object | `include_if`, `exclude_if` |
| Required observation | States, explicit value/Item/record cardinality and exception behavior | `require`, `expect` (open) |
| Results composition | Boolean combination of distinct named Tests, including conditional/alternative paths | `evaluate`, `all_of`, `any_of` (open) |
| Reporting | Elements returned and redaction/results behavior | explicit report control |

The rows are **semantic roles**, not a proposed dictionary. One row may not require a separate keyword if a simpler structure can express it *without hiding meaning*. Conversely removing a keyword while adding inconsistent nested forms is not progress.

## How to select a grammar

Judge a whole Assessment, not isolated snippets:

1. **Semantic fidelity (gate):** each admissible original must reconstruct exactly, with no hidden zero/one/all defaults, changed variable source, filter order, or report metadata. Independently test six-state collection/error/evidence parity separately.
2. **Author comprehension:** can a reviewer identify the collection, selection, predicate, cardinality, missing-data behavior, and final decision without following opaque variable names?
3. **Authoring from a blank page:** can a novice write the check from capability definitions and a short grammar reference, without copying an enormous sample?
4. **Consistency:** one role should have one construction across objectless collectors, nested Linux iteration, Windows records, derived Variables and reusable Sets.
5. **Simplicity:** measure nesting and optional special cases before counting or renaming keywords. Never treat a shorter file as proof of an easier language.

### What the structural word-removal experiment actually showed

The [passing six-STIG exploratory comparison](https://github.com/vanderpol/scap-ng/actions/runs/38988669776) reversibly represented **871 of 872** complete source Assessments with a trial structure that folds ordinary `inspect` + `where` into a polymorphic `capability` field. The only rejection remained the original Linux bootloader source exception.

This is **not** a recommendation for the word `capability` and **not** a recommendation to eliminate `where`. In fact, the trial **increased rendered YAML character count by 0.79%** (1,593,224 → 1,605,776), even before accounting for authors learning a string-or-mapping field. **Six complete Assessments retained other nested `where` usage**, demonstrating that not every occurrence means the same sort of top-level native Object selection. Literal word removal and semantic simplification are different goals. The experiment showed that a systematic rename/re-nest is feasible for admitted source structures, **not** that it makes them clearer or easier to author.

### Current evidence (not a final choice)

The [six-STIG structural census](reports/README.md) has exact reconstructed source structures for **871 of 872** automated Assessments. The bootloader Test combining `none_exist` and an attached State remains a fail-closed exception. The four complex full comparisons pass a source inversion, and the [Markdown consistency test](../../../tools/test_english_first_full_markdown_examples.py) checks all five inline “after” examples. These are **not** independent SCAP 1.4 runtime/evidence conformance or author usability results.

The candidate **minimal hybrid** deliberately collapses `inspect` plus `where` into one polymorphic `capability` mapping. Its experiment must preserve other nested `where` uses, metadata and Variable graphs. That experiment helps test whether removing `where` actually simplifies complex authoring; it is **not** evidence that `capability` is a preferred word.

**Provisional research principle:** favor a predictable, source-first progression — identify source → select/collect/derive Items → state precise requirements → combine results. Do not freeze `inspect`, `capability`, `where`, `require`, or `evaluate` until the roles and source exactness are understood.
