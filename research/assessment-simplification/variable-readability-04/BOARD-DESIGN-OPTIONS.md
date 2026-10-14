# 0.4 research proposal: explain and reuse complex Variable graphs

**Status: research proposal for OVAL Board discussion, not accepted syntax or a vote.** This is deliberately separate from the frozen 0.3 specification.

## Problem and measured evidence

The six-STIG census found **407** Variable uses; Apache alone contains **282**. Complex derivations require following intermediate Object collections, multiple Variables and function chains to understand a failed check. Fully inlining definitions is not an adequate general answer: **113 of 137** tested independent inlinings increased line count, while **97** increased nesting.

The published 0.3 Apache corpus retained a common **11-Variable** derivation in **15 Assessments**. A prototype extracted it into **one authoring-only module**, preserving two typed public outputs and binding the source collection Object separately in each Assessment. All **15/15** imported sources independently expand back into the **exact original parsed 0.3 Assessment**. This removes **154** repeated declarations from the source authoring corpus without modifying compiled Assessment data.

The experiment has no new runtime semantics; structural compilation is not proof of OVAL/scanner execution equivalence when future changes introduce different operators.

## Two complementary but independent reuse questions

Apache highlights **three** problems, and one design need not solve all of them:

- **Authoring maintenance:** when a common discovery algorithm has a bug, fixing 15 independently maintained copies is error-prone. Build-time source reuse permits one correction, with each consumer rebuilding and validating against the updated, explicitly pinned source. The research prototype demonstrates independent expansion of 15/15 consumers, but does not establish a general version-upgrade workflow.
- **Runtime efficiency:** executing equivalent system discovery commands 15 times may waste substantial time. A scanner could collect once *per compatible target and evaluation context*, retain the Items and their status/provenance, then supply those same observations to 15 separate checks. The source-only proof **does not** measure real command executions or prove safe runtime deduplication.
- **Diagnosability:** independent of either reuse mechanism, explain which collection or transformation failed and which assessments depend on it. A shared acquisition failure must not be transformed into an invented pass or an incomplete result presented as complete.

The options are **orthogonal**: source-only reuse, runtime-only collection deduplication, **both**, or neither. Do not assume the Board must choose exactly one. Runtime sharing can be implemented either through an explicit testless typed Observation/knowledge provider, or through a scanner optimization that transparently deduplicates safely equivalent collections in separately compiled Assessments. These paths have different interoperability implications.

A runtime equivalence key must consider at least: target/session/snapshot, collector capability/version, normalized command and parameters, environment/working directory, privilege/security context, organizational input binding, requested evidence, and time/freshness requirements. The implementation must handle simultaneous consumers with one in-flight collection; independent consumers must receive the original status, completeness, errors, value cardinality, lineage and redaction constraints. Do not equate matching YAML text with safe command reuse. A target's configuration may change between checks, and some commands have side effects or context-sensitive output.

**What has been proven:** 15/15 exact canonical build-time expansions and 154 duplicate declarations removed from experimental authoring.

**Not yet proven:** actual number of duplicate process executions, time savings, safe runtime sharing, target-scoped cache invalidation, and equivalence of error/evidence behavior. Quantify these separately before estimating performance benefits.

## Proposal A — visible derived-value flow

Generate a non-executable reader/debugger view from the canonical graph: input Objects → intermediate Variables and operations → typed outputs → consuming Test/State. Keep the actual YAML and standalone OVAL available beside the view.

An opt-in scanner diagnostic mode could attach bounded per-stage information: input collection status/completeness, number of input Items, number of derived values, whether a transform failed, redacted sample values, source Item lineage and downstream dependencies. It MUST NOT alter Test verdicts, silently change empty/error/unknown behavior, or claim completeness from sampled evidence. Its schema and security requirements would need a separate results discussion.

**Can be developed without an Assessment language change.** Static `VARIABLE-DEBUG-PLAN.yaml` examples in the evidence ZIP are placeholders for the trace layout, *not scanner results*.

## Proposal B — reusable authoring-only derived-value module

The prototype retains original Object/Variable definitions, exact names and provenance inside a source module. An Assessment imports it with explicit identity, version, export contract and content digest. The compiler lowers the import to precisely the original standalone Assessment before schema validation and packaging.

Illustrative **research syntax** (not yet normative):

```yaml
source_module:
  id: research.apache.httpd.discovery.source
  version: 1
  requires:
    objects:
      - gather-unique-apache-http-installation-paths-object
  variables:
    # 11 original typed Variable definitions, unchanged
  exports:
    httpd_executable:
      type: variable
      name: apache-path-httpd-or-apache2-variable
      datatype: string
    primary_and_included_configs:
      type: variable
      name: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
      datatype: string
```

```yaml
assessment:
  imports:
    apache_discovery:
      source: shared/source-modules/apache-httpd-discovery.module.yaml
      id: research.apache.httpd.discovery.source
      version: 1
      sha256: <verified-source-digest>
      exports: [httpd_executable, primary_and_included_configs]
```

The compiler SHALL fail on unknown source IDs, source digest/version mismatch, missing required Object bindings, private-component references, conflicting IDs, mismatched types, or unresolvable dependencies. General implementation must also reject import cycles and define namespace behavior. The current research prototype handles one pinned import; it **does not prove** arbitrary nested imports, imports from all platforms, or a standardized authoring schema.

**Authoring reuse is not runtime sharing.** No scanner caching, shared collected Items, new Observation result, or cross-Assessment status scheduling is implied. Source-bound collections remain in their original Assessments.

## Proposal C — keep genuinely dynamic or multi-source Variables named

Do not obscure chained calculations when multiple value streams combine, regex capture can fail, filters alter membership, or a derived value fans out to independent consumers. Retain typed names and expose the stage-level graph for debugging. Avoid importing generic script or expression language semantics without complete truth/error/cardinality analysis.

## Board questions (feedback, not a vote)

1. Should source-only modules be standardized as optional authoring syntax, or left to publisher/editor tooling that emits canonical Assessments?
2. Should reusable runtime observations be explicit testless providers in the specification, a scanner optimization over independently authored Objects, or both?
3. Is a generated Variable dependency view sufficient, or should a portable **optional diagnostic trace** with per-stage status, counts, provenance and redaction be standardized?
4. Which real OVAL examples demonstrate when repeated collection is safe to share versus when evaluation context or freshness requires independent acquisition?

## Evidence and next acceptance gates

See [research issue #223](https://github.com/vanderpol/scap-ng/issues/223) and the matching release's `BOARD-RESEARCH-PREVIEW.md`, `BUILD-TIME-IMPORT/` and source-paired examples. Each import consumer example contains an original standalone `oval.xml`, current 0.3 Assessment, imported research authoring, and compiler-expanded 0.3 Assessment.

Before ratification: general parser/schema and namespace design, adversarial input and import-cycle tests, checks for variable datatype/cardinality/provenance and organizational-input boundary, independent implementation review, and measured readability/debugging outcomes. Do not reopen the 0.3 release.
