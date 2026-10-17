# Typed evidence providers — decision gate for auditor-first syntax

**17 October 2026. Research #235 (authoring), #229 (source semantics). Not normative 0.4, a scanner, or a verified SCAP 1.4 conversion.**

The fresh-start language succeeds only if native typed resources are **not opaque compliance functions** concealing OVAL under friendly vocabulary. What must the auditor write, and what obligations belong in reusable, inspectable providers?

## Two genuinely different authoring shapes

**Collection policy** — at least one selected mount must exist, and EVERY selected mount must comply:

~~~yaml
require:
  each: linux.mounts
  where:
    mount_point: {equals: /home}
  minimum_resources: 1
  must:
    mount_options: {contains: nosuid}
~~~

**Optional population** — any existing guest account must be disabled, but no guest accounts is acceptable:

~~~yaml
require:
  each: windows.accounts
  where:
    category: {equals: guest}
  must:
    enabled: {equals: false}
~~~

The new candidate each/minimum_resources is not yet accepted by the original grammar validator. Unlike if_empty: fail, the author states **that selected resources are required to exist**. A known-complete zero selected population fails only when a positive minimum is declared. A collection with zero observed because collection was incomplete is never confirmed empty.

**Named resource policy**, a distinct candidate:

~~~yaml
require:
  resource: windows.registry_value
  using:
    hive: HKLM
    key: 'SOFTWARE\Policies\Microsoft\Windows\Installer'
    name: AlwaysInstallElevated
  must:
    value: {equals: 0}
~~~

This is natural when the provider contract establishes a unique logical resource (including registry view and namespaces). If a provider promised uniqueness but returns two matching records, this is a **provider identity error**, not permission to choose a passing item. Two compliant /home mounts may satisfy the first collection policy but fail the unique-resource contract. Named resources must not silently change cardinality.

## Required versioned provider manifest

| Contract | Minimum content and falsifying counterexample |
| --- | --- |
| Provider ID + version | Stable OS/capability, typed input and output schema, supported operations; apache.loaded_directives is not implemented merely because the name is intuitive |
| Item identity and namespaces | What each record denotes, mount namespaces / registry views / duplicates; separate Item identity from field values |
| Selector and acquisition distinction | where filters selected Items; using configures the provider; missing or unreadable selector fields must not silently become nonmatches |
| Field schema | Typed scalar/list/record values, field presence, absent/read error and operator cardinality; repeated DNS stdout_line is NOT one number |
| Related resources | Lexically scoped user-to-home-to-file association, shared homes, traversal and symlink rules, stable parent/child identity |
| Collection completion | complete/incomplete/error/not collected/not applicable, zero AFTER selection vs raw zero; status and missing-element reasons |
| Evidence provenance | Source file and line, raw command flags, collected Item IDs, timestamps, capped samples and counts |
| Performance/safety | Timeouts, max items, truncation, recursive traversal limits, dedup and cache keys, least-privilege data access |
| Migration contract | Source-specific six-state fixtures and exception paths before declaring a native check equal to source OVAL |

Each provider must be broadly reusable across multiple rules, not one opaque "passes STIG SV-..." function.

## Four source-backed blockers

**RHEL home mount.** A new policy selecting exact /home is distinct from original source regex .*\/home. Both can be authored natively, but one cannot be silently substituted for the other. Count the selected population, not raw mounts. A missing mount_point field can conceal an applicable mount.

**Windows 11 SV-253495.** Source WMI DomainRole logic is OR of two WHOLE State alternatives: all nested records must equal 1, OR all must equal 3. Complete records [1] and [3] satisfy a State. Complete [1,3] satisfies neither. Rewriting this as membership in [1,3] changes the result. A typed computer-role provider must define record grouping, partial/error behavior, and source-parity tests before converting original checks.

**Apache SV-214228.** Four original command checks and derived Variable graph cannot automatically become just two properties, KeepAlive On and MaxKeepAliveRequests >=100. A provider returning only (directive,value) loses which included file or config supplied a directive, discovery/command flags and optional fields. The new concise rule is a greenfield policy unless a real provider preserving source distinctions is proven.

**Windows DNS SV-259345.** Source has five checks, command-derived values, conditional alternatives, two whole threshold States and possibly repeated stdout_line values. A single validity_hours between [48,168] on a scalar is not defined for a multi-valued field. Preserve zone/key parent correlation, output typing and original source aggregation when asserting migration.

## Synthetic counterexamples (not actual scanner runs)

[Reference experiment](../../tools/research_requirements_first_evidence.py) and [regression tests](../../tools/test_research_requirements_first_evidence.py) distinguish:

- Required complete zero -> Fail, optional complete zero -> Pass.
- Nonempty raw population with zero selected -> presence still fails; two selected with one violation -> Fail.
- Incomplete zero -> Unknown, but an already observed violation of an every requirement -> Fail.
- Unreadable/missing selection or required-property fields -> unresolved/Error, never silently excluded.
- Exactly one SELECTED resource vs exactly one compliant among several; singleton promise vs duplicate evidence error.
- Original WMI complete [1,3] whole-State comparison vs naive one-of membership.
- Apache projection to only (directive,value) loses source-file evidence.
- DNS multi-valued numeric field cannot silently evaluate as scalar between.

The experiment deliberately implements only a **limited four-status model** plus an explicit not-applicable observation. It does not implement the complete OVAL six-state standard, actual typed provider collection, original SCAP 1.4 migration parity, or the SCAP-NG scanner. The existing [OVAL 5.12.3 reference tables](../../tools/oval_result_truth_tables.py) are a separate compatibility research source.

## Internal adversarial rereads (same assistant, not independent reviewer)

1. Novice: affirmative minimum is clearer than if_empty: fail; but minimum_resources is still query vocabulary and named resource is more sentence-like.
2. Security auditor: the named-resource form hides identity assumptions; editor must show intended population and whether multiple matches are possible.
3. Source auditor: normalized roles and flattened Apache/DNS fields lose distinctions that source tests use. Lossless conversion must fail closed, or retain a separate compatible execution representation.
4. Implementer: typed reusable capabilities are a substantial engineering investment; per-STIG custom verdict probes would recreate OVAL as a hidden proprietary engine.
5. Results auditor: every evaluated requirement must explain coverage, status, source evidence and why the available evidence is decisive. More readable YAML alone does not satisfy this.

## Next decision gate

- Prove one real provider, preferably Linux mounts, with typed identity, scoped data and complete/incomplete/error statuses.
- Test required vs optional vs singleton against synthetic and then real collected data, including duplicates, unknown selectors and partial data.
- Independently prove one genuinely complex source conversion: first mixed WMI records, then Apache command group and DNS repeated values.
- Run a cold authoring test with unlabeled examples and an actual new requirement, not only comprehension questions.
- Keep the candidate out of normative schema/v0.4.0, and do not start an opinionated editor implementation yet.

**Current judgment:** the requirements-first direction remains promising for **native authoring**, but whether to use a named single resource or an explicitly counted population depends on real identity contracts. Neither should be chosen just to reduce line count.
