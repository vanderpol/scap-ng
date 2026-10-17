# Complex Assessments: scale test and redesign iterations

**Research checkpoint — October 16, 2026 · not approved v0.4 grammar or scanner evidence.**
Tracking [#235](https://github.com/vanderpol/scap-ng/issues/235), [#227](https://github.com/vanderpol/scap-ng/issues/227), and [#229](https://github.com/vanderpol/scap-ng/issues/229).

**Question:** Can a security auditor understand and author a genuinely complex Assessment more easily, **without** hiding source behavior behind attractive YAML? The comparison is against the [five complete, real before-and-after Assessments](BEFORE-AFTER-REVIEW.md). This document is an *additional design experiment*, not a replacement for those source-reversible files.

## Baseline: what the current experiment actually proves

- The pinned six-STIG corpus has **872 distinct automated Assessments / 1,375 named Tests**. The existing English-first experiment structurally reconstructs **871 / 872 Assessments**, but this is *not* scanner/OVAL execution or evidence parity.
- The verified compact layout reduces YAML character count **5.21%** across reconstructed content. That is useful, but *not* a convincing reduction in conceptual complexity.
- The Apache [SV-214228](FULL-05-apache.md) Assessment has **18 local Variables**, four Tests, and a discovered dependency chain of up to **10 edges**. The Windows [SV-253495](FULL-03-win11-rights.md) Assessment has seven Tests and an OR of three compliance alternatives. Linux [SV-257889](FULL-02-linux-files.md) combines named account Sets, dependent file acquisition and eight permission predicates. DNS [SV-259345](FULL-04-dns.md) builds three commands from discovered zone names.
- One bootloader Assessment combines a `none_exist` Test with an attached State; it is **excluded**, not silently transformed. See the [boundary report](reports/english-first-04-none-exist-state-boundary.md).

**Success criterion is not minimum line count.** An auditor should be able to identify, from a complete Assessment: (a) provenance of data, (b) where selection and collection happen, (c) dependence between data sources, (d) precise existence and match quantifiers, (e) alternatives that produce a pass, and (f) missing/error/unknown behavior.

## Iteration 1 — translate vocabulary (necessary, insufficient)

Keep `inspect`, `where`, `collect`, `from`, `require`, `evaluate` and a reader-first order. This is the [current reversible auditor-first candidate](AUDITOR-FIRST-CANDIDATE.md).

**Keep:** explicit Item vs field-value cardinality, clear separation of object selection (`where`) and post-collection filtering (`exclude_if`), and explicit whole-check Boolean alternatives.

**Reject as final answer:** Apache's 18 Variable definitions are still an 18-node maze. `check: ...` prose does not make the referenced command's provenance self-explanatory.

## Iteration 2 — remove duplication and make acquisition a typed, navigable graph

**New design hypothesis (NOT validated by the 871/872 compiler):** In any check, use **either** an inline `inspect` to declare collection **or** `from` to reference a named source, **never both**. A `from` check inherits the source's capability *type* at compilation, not its English name or unstated defaults. Compose complicated collections as **named sources**, so checks do not nest the entire acquisition graph.

This is an actual structural improvement over the present research format, where `inspect` is sometimes repeated at both the source and referring check. It is still **one** authoring grammar, not a pretty view over a second authoring language. It requires new schema/type-checking and lossless-lowering proof before adoption.

**Small source-backed proof:** In the full [Windows 11 seven-Test experiment](experiments/windows-wmi-rights-typed-source.research.yaml), all **seven** referring checks inherited their capability from **two** named sources. The seven repeated `check.inspect` lines (217 YAML characters) were removed; source-type agreement was checked for each reference and reinserting those exact seven fields reconstructed the [original auditor-first YAML](auditor-candidate/windows-wmi-rights.auditor.research.yaml) **byte-for-byte**. This proves this narrow presentation change for *that file only*. Of the other four complete gallery files, none has a direct check-level named `from` to simplify. Do not extrapolate this into a major corpus-wide gain or scanner parity.

**Second improvement to that experiment:** [The fail-closed typed-source probe](../../../tools/research_english_first_04_inherited_capability.py) now resolves a **homogeneous Set source** by deriving its capability from each operand, including a one-operand `union`. It rejects missing names, mixed capability operands and cyclic references. [Nine targeted unit cases](../../../tools/test_research_english_first_04_inherited_capability.py) passed locally and the five complete gallery files are included as a repeatable GitHub Actions check. This is a *type-inference proof for the supported shapes*, not a verified full-corpus conversion, collection semantics or a license to drop Set operators.

### Linux: source graph, then two distinctly quantified checks

The following is a **design fragment** grounded in [SV-257889's complete source](FULL-02-linux-files.md); it is not an executable whole Assessment. The non-system account source below retains the real *separate exclusions* and the one-operand Set union. In the real Assessment the root-account source is another `difference` of the same accounts, excluding IDs **greater than 0** and home directory `/`.

```yaml
sources:
  all-users:
    inspect: unix.password
    where:
      username: {matches_regex: '[\w]+'}

  non-system-users:
    inspect: unix.password
    difference:
      - from: all-users
        exclude_if:
          - user_id: {less_than: 1000}
          - home_dir: {is: /}

  non-system-init-files:
    # Set itself is a typed composed source; operands declare acquisition.
    union:
      - inspect: unix.file
        for_each_source:
          item: user
          in: non-system-users
        where:
          directory: {from: user.home_dir}
          name: {matches_regex: '^\.[^\s\.]+'}
        filesystem: all
        traversal: {max_depth: 1, recurse: symlinks}
        exclude_if:
          - type: {is: directory}

checks:
  non-system-file-permissions:
    from: non-system-init-files
    require:
      items: may_be_absent
      every_item:
        all_of:
          - setuid: {is: false}
          - setgid: {is: false}
          - sticky: {is: false}
          - group_write: {is: false}
          - group_execute: {is: false}
          - other_read: {is: false}
          - other_write: {is: false}
          - other_execute: {is: false}
        all_fields_must_exist: true
```

The **second** root check is not optional and requires `items: at_least_one`. Its independent source, second check, original metadata, and `evaluate.all_of` are omitted *only to isolate the source-graph design*. A full candidate must include them. Do **not** simplify the two exclusion filters to `uid >= 1000` without proving missing/error semantics, or remove the unary `union` just because it looks redundant.

**Readability gain:** the auditor sees `from: non-system-init-files` once and can follow named prerequisites upward. **Remaining cost:** the source graph is still complex; this does not reduce the filesystem work or demonstrate a lossless transform.

### Windows: make decision branches explicit, preserve whole-record States

The seven checks can be displayed as **named predicates** with the original final logical form:

```yaml
evaluate:
  any_of:
    - all_of:
        - test: domain-joined-non-dc
        - test: denied-local-account
        - test: denied-guests
        - test: denied-domain-admins
        - test: denied-enterprise-admins
    - all_of:
        - test: standalone
        - test: denied-guests
    - test: denied-everyone
```

These are **editorial aliases**, not the original Test IDs; an exact converter must retain a bijective mapping to all seven IDs. Importantly, the real WMI `domainrole=1` and `domainrole=3` alternatives each apply to the **entire record-State comparison**. A source containing two records (roles 1 and 3) is a counterexample to flattening this into `domainrole in [1, 3]`. **Do not turn this OR graph into procedural `if/else`**: six-state results can differ. See [SV-253495](FULL-03-win11-rights.md) and [conditional research](../conditional-10/README.md).

**Readability gain:** auditors can see the three independent pass routes. **No semantic reduction** in seven original Tests; that's appropriate until equivalence is proved.

## Iteration 3 — replace *accidental* complexity with domain collection contracts

The largest opportunity is **not** shorter field names: it is changing the primitive **collection capability** while preserving all visible requirements. The same `sources → checks → evaluate` language can use generic shell collection or purpose-built native collectors. That is **one grammar with typed capabilities**, not two DSLs.

### Apache: typed loaded-configuration source, but ONLY after a capability contract

```yaml
# CONCEPTUAL DESIGN ONLY. NOT a lossless conversion of SV-214228.
sources:
  keepalive-occurrences:
    inspect: apache.configuration
    collect:
      discovery: installed_servers
      include_files: true
      representation: raw_occurrences
    where:
      directive: {equals_ignoring_case: KeepAlive}

checks:
  keepalive-across-loaded-files:
    from: keepalive-occurrences
    require:
      items: at_least_one
      every_item:
        value: {is: "On"}
```

This is intentionally **not presented as the four-Test original**. In particular, it might differ from the source's `grep` regular expressions, separate main/included-file predicates, *when-present* fields, exit/stderr flags, repeated directive handling and exact files considered loaded. Nor may `apache.configuration` assume effective rather than raw directive values.

Before this is admissible, a capability contract must define: Apache executable/install discovery; main file and `HTTPD_ROOT` resolution; `Include` vs `IncludeOptional`; recursive include order/globs/cycles; raw occurrences **with filename, line and include ancestry**; duplicates; casing and quoting; conditional sections; unavailable files; partial/error status; and evidence returned. Only then may we test whether **18 Variable nodes and their command graph** can be replaced by one semantic collection unit **without changing observed outcomes**. If not, preserve the proven generic-command route.

### DNS: zone-to-result correlation, not a magic shell-command replacement

A native `windows.dns.zone` capability could expose zone name, signing status and key validity as typed per-zone data, making the intended iteration apparent. But the existing five Tests build **three PowerShell commands from a collected zone-name source**, use specific error suppression/output conditions, and combine caching-only, all-AD-integrated and signed/key-bounds alternatives.

A proposed per-zone foreach is **not equivalent by assertion**: empty zone sets, duplicated names, partial collection, command failure and mixed per-zone outcomes must be compared against actual [SV-259345](FULL-04-dns.md). The proof must preserve each original 48/168-hour bound and its two separate key classes. Until then, reuse a *named zone source* but preserve the original command Variable graph.

## Iteration 4 — improve the proposal again: semantic cost and provenance, not just YAML size

A new native capability is only better if it moves real, **well-specified** complexity into a reusable audited implementation. The collection implementation must expose what was discovered, where it came from, why it was skipped, and partial/error flags. A short authoring file with an opaque collector is not a success.

**Proposed winning direction for further prototyping:** In particular, a named `from` check must not introduce a competing `where` or `collect`; any selection belongs in the defining source, where its collection stage and type can be checked. This fixes an ambiguity caught while reviewing the initial Apache sketch.

1. **One grammar:** `sources` define typed acquisition (native, selected, Set-composed or dependent); `checks` reference sources or inspect inline; `require` declares explicit cardinality; `evaluate` joins named checks in six-state logic. No duplicated `inspect` at a `from` call site and no redundant `combine → union` wrapper.
2. **One dependency model:** named sources are lexical, cycle-checked and type-checked. Dependencies appear *before* consumers in canonical authoring order. Names are identifiers, **never executable descriptions**. Use precise original Test/Item/provenance mappings during import.
3. **Two proof gates:** (A) exact source-graph round trips for syntax-only changes, including metadata and original Test IDs; (B) independent execution and collected-evidence parity for changed capabilities. A source-only round trip does *not* prove the Apache or DNS redesign.
4. **A useful audit explanation:** generated from the same source graph—not a second input language—show *acquisition → selection/filter → quantifier → final decision*, with a trace to each named source and original ID. Let an auditor expand a complex source DAG without making every ordinary check verbose.
5. **Cost accounting:** count source nodes/edges, maximum dependency depth, duplicated collections, shell commands, scanner traversal count, human reference hops, and exceptions. A 5% reduction in serialized text is not a proxy for success. Do not claim numerical gains without running the candidate and auditing evidence.

### Counterexamples that must remain failing guards

| Test case | Incorrect shortcut to reject |
| --- | --- |
| RHEL no non-system dotfiles, versus no root dotfiles | Treat both as mandatory, or both as optional |
| Missing/error-valued Linux filter fields | Rewrite Set differences as simple positive predicates without parity |
| Windows WMI records for roles 1 **and** 3 | Convert whole-State OR to one field-membership predicate |
| Windows unknown/error role | Replace whole-result Boolean OR with procedural `if/else` |
| Apache directive present in one loaded include but absent in another | Conflate raw occurrences, optional fields and effective value |
| Apache missing optional include, invalid glob, or recursive include | Return a clean pass without preserving native collection/evidence semantics |
| DNS two zones with different signing/key outcomes | Flatten to one scalar and lose per-zone or command failure behavior |
| `none_exist` with attached State | Drop the State or assume `no_item` equivalence |
| Undeclared `from`, mixed-capability union, cycle, or `from` plus `inspect` | Infer a source or pick one interpretation silently |

## Decision now

**Keep the proven English-first candidate as the reference; do not promote the new fragments to 0.4.** First prototype and mechanically check the `from`-without-`inspect` typed-source rule on all 871 admitted Assessments. In parallel, specify **one** native collector end-to-end, preferably Apache loaded configuration, and independently test source/evidence parity before crediting any complexity reduction.

**A more honest measure of success:** if an auditor can understand a complete Windows decision without reconstructing the Boolean graph, and an Apache author can follow *and modify* all actual discovery steps without decoding 18 Variables, the design is improving. If the only win is shorter YAML, iterate again.

**Source-backed examples:** [Linux account/files](FULL-02-linux-files.md) · [Windows WMI/user-rights](FULL-03-win11-rights.md) · [Windows DNS](FULL-04-dns.md) · [Apache includes](FULL-05-apache.md). The exact results baseline is [GitHub-hosted six-STIG research reports](reports/README.md).
