# Residual production-complexity pattern research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> This study does not change the 0.3.0 schema, converter contract, capability
> semantics, or Board-review baseline. It identifies recurring semantic shapes
> in the remaining complex production content so future modernization work is
> driven by measured reuse rather than isolated examples.

## Question

After accounting for the simpler/local Assessment population and the already
studied foreach and conditional patterns, is the remaining real-world
complexity:

1. a small number of recurring semantic patterns that deserve clearer native
   representation; or
2. mostly irreducible one-off OVAL graphs?

## Corpus

Pinned NIWC revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

Platforms:

- RHEL 9;
- Windows Server 2025.

Successful coarse-family census:

https://github.com/vanderpol/scap-ng/actions/runs/37550318735

Tool:

`tools/measure_residual_complexity_patterns.py`

## First result

Across **703 automated Assessments**:

| Platform | Automated | Residual complex | Percent |
| --- | ---: | ---: | ---: |
| RHEL 9 | 435 | 93 | 21.38% |
| Windows Server 2025 | 268 | 26 | 9.70% |
| **Total** | **703** | **119** | **16.93%** |

The first exact structural fingerprint was intentionally too strict and yielded
one exact shape per residual Assessment. A second coarse fingerprint abstracts
IDs, titles, literals and exact cardinalities while retaining capabilities,
Variable-function families, Set/Filter presence, Test-count bands and
evaluation structure. That exposes recurring families.

The residual population is therefore **not** a random long tail.

## Aggregate residual signals

These categories overlap:

| Signal | Assessments |
| --- | ---: |
| Filters | 23 |
| Multi-Test composition | 65 |
| Sets | 53 |
| Non-direct Variable dataflow | 46 |
| Nested evaluation not covered by exact-complement conditional recognition | 29 |
| Variable functions | 25 |

Observed Variable-function occurrences include:

| Function | Occurrences |
| --- | ---: |
| values/object-derived values | 48 |
| concat | 23 |
| regex_capture | 8 |
| split | 5 |
| count | 5 |
| unique | 3 |
| arithmetic | 1 |

The largest reason combinations after counting only substantive Filter entries are:

- **30**: Sets only;
- **20**: multi-Test + nested evaluation;
- **14**: multi-Test + non-direct dataflow + Variable functions;
- **10**: multi-Test + Sets;
- **6**: Filters + non-direct dataflow.

An earlier census incorrectly counted empty/presentation `filters` keys as
actual Filters. The corrected run reduces substantive Filter use from 65 to 23
without changing the 30-rule Set family.

## Highest-value recurring families

### 1. Text setting from primary file + drop-in files — 30 RHEL Assessments

Census shape:

- capability: `independent.textfilecontent54`;
- one Test;
- one Set collection structure;
- no substantive Filters;
- no Variable functions;
- no nested evaluation.

This family alone is **25.2% of the entire two-platform residual population**
and **32.3% of the RHEL residual**.

Examples include:

- SV-257784 — `CtrlAltDelBurstAction` from `system.conf` plus
  `system.conf.d/*.conf`;
- SV-257982 — SSH `LogLevel` from `sshd_config` plus
  `sshd_config.d/*`;
- SV-258005 — SSH `IgnoreRhosts` from the primary config plus drop-ins.

The older maintained converted views make the underlying intent especially
clear: collect the same setting from a primary file and a drop-in directory,
union the observations, then apply one State expectation.

**Research hypothesis:** this may deserve a first-class configuration-source or
"primary + drop-ins" collection idiom rather than requiring authors to express
ordinary configuration scope through generic Set machinery.

The corrected census shows this family has **no substantive Filters**, which
makes the repeated pattern cleaner than first measured. A topology pass over
the exact 30-rule family found **30/30 identical Set topology**:

- operator: `union`;
- exactly two operands;
- both operands are Object references;
- neither operand has a Filter.

That makes recursive locality a concrete first experiment: inline each private
leaf Object into the Set operand, then inline the private Set Object into its
Test. This preserves native Set semantics and may eliminate the remaining
pointer chain without adding a new authoring construct.

Only if that remains materially hard to read should a new "primary + drop-ins"
or effective-configuration abstraction be considered. Separately, we still
need to determine whether these Sets merely union source locations or whether
the security requirement really depends on configuration precedence/effective
value rules that the source OVAL does not itself model.

### 2. Alternative compliance paths — 10 RHEL Assessments

Census shape:

- `independent.textfilecontent54`;
- 3–5 Tests;
- nested `all` + `any`;
- no Sets, Filters or Variables.

Examples include SV-257804, SV-257806, SV-257807, SV-257880, SV-257983,
SV-257994, SV-258003, SV-258006, SV-258009 and SV-258232.

Some are already known **not** to be if/else. For example the kernel-module
cases represent multiple acceptable configuration paths and correctly remain
ordinary `any`.

**Research direction:** classify these as explicit alternatives rather than
trying to eliminate Boolean composition indiscriminately.

### 3. Enumerate files/directories and report only violations — 6 RHEL Assessments

Examples SV-257918 through SV-257923 use `unix.file` with a constant list of
directories, recursion and exclusion filters. Representative intent:

- enumerate files in known system-command/library directories;
- exclude objects that already satisfy the requirement;
- exclude non-target types such as directories/symlinks;
- assert that no violating Items remain.

This is a common **violation-query** idiom.

Example SV-257918 effectively says:

> From system command directories, find ordinary files not owned by root; there
> SHALL be none.

**Research hypothesis:** a positive authoring form such as "all matching files
must satisfy State X" may be much clearer than expressing compliance as
"collect failures by excluding good Items, then require none." The semantic
proof must include incomplete/error collection and Filter behavior before any
automatic rewrite.

### 4. Mounted state + persistent fstab option — 5 RHEL Assessments

Examples:

- SV-257866
- SV-257870
- SV-257871
- SV-257872
- SV-257873

Each repeats the same basic graph:

1. verify an active `linux.partition` mount has an option;
2. parse the corresponding `/etc/fstab` row;
3. extract the comma-delimited option string;
4. `split` it into values;
5. verify the desired option is present; and
6. separately prove the mount exists in `/etc/fstab`.

This is not primarily a general Variable-language problem. It is a recurring
**persistent mount configuration** domain concept.

**Follow-up result:** [fstab-13](../fstab-13/README.md) found 23 RHEL
Assessments that read `/etc/fstab`, not just these five. OVAL 5.12.3 keeps
mounted `linux.partition` facts distinct from persistent configuration, so a
sibling typed record capability such as `linux.fstab` is the cleaner native
authoring direction.

The five split-Variable Rules **cannot** be automatically collapsed to one
ordinary typed Test without changing six-state behavior: incomplete source
collection drives the source `split`/Variable path to `error`, while an
ordinary typed Test yields `unknown` or a decisive `false`. Treat the typed
collector as a native-authoring opportunity, not a proven lossless migration
rewrite.

### 5. Dconf database-name -> locks-directory derivation — at least 3 RHEL Assessments

Examples SV-258013, SV-258020 and SV-258026 use the same graph:

1. parse `/etc/dconf/profile/user` for `system-db:<name>`;
2. derive `/etc/dconf/db/<name>.d/locks` with `concat`;
3. search the derived directory for a required locked key;
4. require both the database declaration and the lock.

This is another domain concept hidden behind generic Variable operations.

**Follow-up result:** the broader RHEL 9 converted corpus contains 14 automated
Assessments touching `/etc/dconf/db` and 7 reading
`/etc/dconf/profile/user`, but only these three use this exact
profile-value -> derived-lock-directory graph. That is too narrow, by itself,
to justify a new dconf-specific capability.

The graph fits a more general bounded `foreach` proof class instead:
one ObjectComponent projection, only singleton literal prefix/suffix operands,
and one target Object selector with `var_check: at least one`. See
[foreach-07](../foreach-07/README.md).

General `concat` remains review-required because two collection-valued
operands can form a Cartesian product. The AIDE path construction in SV-258134
is a concrete counterexample.

### 6. Windows event-log path derivation — 3 Server 2025 Assessments

SV-278043, SV-278044 and SV-278045 form a repeated family using:

- Windows registry;
- Windows file effective rights;
- Sets/Filters;
- `concat + regex_capture + values`;
- a role/path conditional.

The conditional branch itself is now recognized by the generic conditional
modernizer. The remaining complexity is path derivation from registry data and
permission assessment.

The current 0.3 conversion of these Rules also exposes a separate known
`windows.registry` post-alignment mapping gap. That gap must not be confused
with conditional-recognition correctness.

### 7. Windows role/domain user-right branches — recurring family

Several Server 2025 Rules combine `windows.wmi.query` role/domain facts with
`windows.userright` expectations. Some now match the generic mutually
exclusive-enum conditional proof; others remain unproven and correctly stay in
review.

Continue improving the proof classes generically. Rule IDs are fixtures only;
the modernizer SHALL NOT contain product or Rule allowlists.

## Important design lesson

The recurring families suggest at least three different kinds of
"modernization":

1. **presentation/locality modernization** — inline private Objects/States;
2. **evaluation modernization** — turn proven environment branches into native
   conditionals while leaving alternatives as `any`;
3. **domain modernization** — replace generic regex/Variable/Set plumbing with a
   typed concept such as persistent mount configuration, dconf locks, or
   configuration files with drop-ins.

These should not be collapsed into one generic graph simplifier.

A domain-specific modernization may yield a much larger readability improvement
than adding another generic expression operator.

## Priority order

Next deep dives should be:

1. the 30-rule text-setting/drop-in Set family;
2. the 5-rule persistent mount option family;
3. the dconf path-derivation family;
4. the 6-rule file violation-query family;
5. remaining Windows role/domain conditional guards;
6. Windows event-log path derivation after the registry mapping boundary is
   clean.

For each family:

- read the STIG requirement/check text;
- inspect the exact OVAL graph;
- identify the security-domain concept;
- propose a simpler native representation only if it is materially clearer;
- prove conversion conditions and counterexamples;
- measure how many production Assessments match;
- add run statistics to the modernizer;
- fail closed outside the proof class.

## Status

**Research only; pattern census complete, family semantic review in progress.**
