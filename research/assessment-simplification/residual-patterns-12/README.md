# Residual complex-pattern census

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> This directory records recurring complexity patterns that remain after the
> already-known simplification opportunities (locality, foreach, and strict
> conditional shapes) are separated out. It does not authorize new schema or
> converter behavior.

## Question

After removing the common/simple cases, are the remaining complex Assessments
mostly one-off OVAL graphs, or do they fall into a small number of recurring
semantic patterns that could justify additional modernization?

## Production basis

Pinned NIWC revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

Fresh current conversions were generated for:

- RHEL 9 V2R9;
- Windows Server 2025 V1R1.

Successful census:

https://github.com/vanderpol/scap-ng/actions/runs/37549807776

Tool:

`tools/measure_residual_complexity_patterns.py`

The census is descriptive only. It does not modify source or assume that two
similar graphs are semantically interchangeable.

## Overall result

Across **703 automated Assessments**:

- **119 (16.93%)** were classified as residual-complex by the conservative
  research criteria;
- RHEL 9: **93 / 435 = 21.38%**;
- Windows Server 2025: **26 / 268 = 9.70%**.

Residual feature counts overlap:

| Residual signal | Assessments |
| --- | ---: |
| Filters | 65 |
| Multi-Test composition | 65 |
| Sets | 53 |
| Non-direct Variable dataflow | 46 |
| Nested evaluation not already an exact complementary conditional | 29 |
| Variable functions | 25 |

Variable-function occurrences in the residual population:

| Function | Occurrences |
| --- | ---: |
| concat | 23 |
| regex_capture | 8 |
| split | 5 |
| count | 5 |
| unique | 3 |
| arithmetic | 1 |

The important result is that **the residual population is not uniformly
complicated**. Coarser clustering exposes several repeated families.

## Largest recurring families

### 1. Layered text configuration using Set/Filter machinery — 30 Rules

The largest coarse family contains **30 RHEL 9 Assessments** using
`independent.textfilecontent54`, one Set, two Filters, one Test, and no
Variable functions.

Representative Rules include:

- SV-257784 — systemd Ctrl-Alt-Delete burst configuration;
- SV-257982 — SSH logging;
- SV-257984 — SSH blank-password policy;
- SV-257985 — SSH root login;
- SV-257986 — SSH PAM;
- SV-258068 — shell inactivity timeout;
- SV-258084 — sudo reauthentication;
- multiple password-complexity and authentication settings.

This family deserves a dedicated semantic review. The likely author intent is
often "evaluate a setting across the applicable base configuration and drop-in
configuration sources," while OVAL expresses the acquisition using generic Set
and Filter graphs.

**Do not yet replace this with a new construct.** Configuration precedence,
duplicate definitions, include/drop-in semantics, and effective-versus-present
configuration must be proven for each domain. A typed effective-configuration
collector may be a better solution than another general-purpose language
feature.

### 2. Alternative compliance/configuration paths — 10 Rules

Ten RHEL Rules share a three-to-five-Test `all/any` family, including the
kernel-module disable checks.

These are not ordinary if/else. They describe multiple acceptable evidence
paths/configuration locations. The conditional research already uses these as a
negative control.

Preliminary direction: keep ordinary `any/all` unless a higher-level typed
capability makes the alternatives disappear naturally.

### 3. Constant-list selector + filtered file search — 6 Rules

Exactly six closely related RHEL Rules cover system command/library
files/directories and ownership/group ownership:

- SV-257918 through SV-257923.

The current graph uses a constant Variable containing a list of directories,
feeds that Variable into a file selector, excludes out-of-scope or already-good
Items with Filters, and asserts that no violating Items remain.

This is a strong candidate for a **small authoring/normalization improvement**,
not a general computation feature. Questions to test:

1. Can a private constant-list Variable be safely inlined into the selector?
2. Can the same semantics be expressed more directly as "for all in these
   directories, after excluding symlinks/directories as appropriate, expect
   owner/group X" instead of "collect violations then assert none exist"?
3. Would a typed file-scope/list selector make the Variable disappear without
   changing collection completeness or filesystem traversal behavior?

### 4. Parsed fstab mount-option lists — 5 Rules

Five RHEL Rules share the same structure:

- SV-257866;
- SV-257870;
- SV-257871;
- SV-257872;
- SV-257873.

They parse an `/etc/fstab` row using textfilecontent54, extract the comma-
separated mount options, `split` the string, and then test the derived list
while separately testing the active mount.

This looks more like a **missing typed configuration capability** than a need
for richer expression syntax.

Research candidate: model configured mount entries directly (for example a
future typed mount/fstab configuration collector) so authors can compare
configured and active mount options without regex + split plumbing.

No capability name is proposed or accepted here.

### 5. Derived configuration path via concat — 3 Rules

SV-258013, SV-258020, and SV-258026 form a repeated RHEL family. A value is
extracted from configuration content and then concatenated with fixed path
segments to locate another configuration resource.

This resembles the already-proven foreach/direct-projection pattern but adds a
simple transformation/template step.

Research questions:

- Is a bounded `for_each` projection with an explicit path template sufficient?
- Is a local derived selector expression clearer than a global Variable?
- Do these examples justify a general transform feature, or are they better
  handled by typed domain collectors such as dconf-aware acquisition?

Do not broaden foreach v1 until the semantic mapping is proven.

## Windows recurring families

### Event-log path resolution — 3 Rules

SV-278043, SV-278044, and SV-278045 form one repeated family involving:

- Registry-derived event-log path;
- `%SystemRoot%`/absolute path handling;
- concat/regex_capture Variables;
- file-effective-rights evaluation;
- conditional Boolean structure.

The conditional modernizer successfully detects and rewrites the branch shape,
but the remaining dataflow is still complex. The current production regression
also exposes pre-existing 0.3 Windows mapping/alignment gaps in these Assessments
(registry predicate vocabulary and existence vocabulary); those failures are
not caused by the conditional expression itself.

This family is a good candidate for a typed Windows event-log/file-location
abstraction after the 0.3 mapping issues are corrected.

### Domain/role-sensitive user-right checks — repeated family

Several Windows Server 2025 Rules use target-role/domain state to select the
relevant user-right requirement. These are being handled by the separate
pattern-based conditional modernization research.

No STIG IDs are encoded in the matcher. Production Rules are regression
fixtures only.

### Other Windows dataflow families

The residual census also retains:

- registry-derived AD data-file paths and file-effective-rights checks;
- FTP/site configuration path construction;
- certificate/key discovery patterns;
- other small Variable families.

These should be reviewed after the higher-frequency RHEL families because they
may be better solved with typed Windows collectors rather than new generic
expression features.

## Working prioritization

The current evidence suggests this order for further research:

1. **Finish conditional pattern proof classes** already underway.
2. **Review the 30-rule layered configuration Set/Filter family** for effective
   configuration semantics.
3. **Prototype constant-list Variable inlining / direct all-item expectation**
   on SV-257918–SV-257923.
4. **Model the five fstab split cases as a typed configuration collector** and
   compare complexity/evidence semantics.
5. **Test bounded transformed foreach/local-selector syntax** on the three
   concat/path cases.
6. Then inspect the smaller one-off function families (count/unique,
   regex_capture, arithmetic) and decide whether they justify language features.

The goal is not to eliminate every OVAL feature. The goal is to determine which
recurring production patterns can become smaller and clearer **without losing
typed acquisition, evidence, error, cardinality, or six-state semantics**.

## Relationship to modernization stats

Modernization/normalization effectiveness should be measurable on every run.

Current modernization output now includes per-Assessment stats and aggregated
`modernization-stats.json` / `evidence.json` totals for foreach and
conditional passes. The repository normalizer also emits a structured
`stats` section while retaining its historical `summary` block.

The stats are evidence, not acceptance criteria: a higher rewrite percentage is
not desirable if it weakens semantic guarantees.
