# SCAP-NG 0.4.0 examples — Benchmarks and Rules

**Current authoring samples: 0.4.0 pre-alpha.** Start with the policy: a **Benchmark** identifies what is covered, a **Rule** says what is required, and an **Assessment** explains how to check it.

**Current all-65 source and smaller Assessment downloads:** [0.4.0 downloads and Assessment samples index](../../docs/releases/0.4.0-downloads-and-samples.md).

**Earlier canonical six-STIG YAML/JSON review ZIPs (historical):** [immutable October 21 source-only release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-canonical-flat-authoring-20261021) (includes independent validation reports and six unsigned source packages). The earlier [October 20 immutable YAML/JSON pre-release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) predates the approved flat-Object regeneration. [Assessment examples](assessments.md).

Those earlier six-STIG packages contain **4,001 authoring documents** for RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS, and Apache HTTP Server 2.4 UNIX. The directory structure separates Benchmarks, Rules, automated/manual Assessments and reusable shared Assessments. Both formats represent the same normalized source graph.

## Read a Benchmark, Rule and Assessment

A Benchmark's `rules` list refers to logical Rule IDs; a Rule's `assessment_choices` refers to logical Assessment IDs. Authors should not need to jump through filenames to understand the relationship.

In that earlier six-STIG 0.4.0 sample set, **all six Benchmarks declare the exact reachable automated Assessment specification at version 0.4.0**, rather than carrying obsolete 0.3.0 declarations. Original source files, version-declaration changes, hashes and reversible source transformations are preserved in the workflow evidence.

For the current normalized library, open the extracted `content/` tree as described in the [download index](../../docs/releases/0.4.0-downloads-and-samples.md). For historical six-STIG sample walkthroughs, start with `authoring/rhel_9/` or `authoring/ms_windows_server_2025/`, open a Rule under `rules/`, follow its `assessment_choices` logical ID to the matching Assessment, and then read its `tests` and `evaluate`.

An Assessment's **Test** owns the collection capability and expected outcomes. Inline `object` describes what to collect. `require` describes the expected Item population and matching values. More complex content retains Variables, Sets, Filters, nested record predicates and explicit logic.

**The full 0.4.0 example syntax is in [Assessments](assessments.md).**

## Status and historic results

The earlier six-STIG examples are **authoring samples**, not executable signed `.scapng` packages or live scan results. The later 0.4 candidate separately compiles 6,817 native candidates; those remain unsigned/unexecuted in an independent scanner. Source inversion, native JSON Schema validity, reference closure and generic OVAL result-model checks have passed for their documented scope; capability-specific scanner parity and final compiler output remain open. See the [0.4.0 finalization gates](../../review/current/0.4.0-FINALIZATION-GATES.md).

The previous **0.3.0** examples, original source, six historical compiled packages, and synthetic result fixtures remain in the [0.3.0 archive](../../archive/0.3.0/README.md). Those results have **not** been revalidated as 0.4.0 output.
