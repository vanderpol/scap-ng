# 0.4-C feasibility: new human authoring, shared A execution foundation

**19 October 2026 · initial architecture design, research only.**  
[Research issue #245](https://github.com/vanderpol/scap-ng/issues/245) · [A stabilization #239](https://github.com/vanderpol/scap-ng/issues/239) · [A dataflow/IR #240](https://github.com/vanderpol/scap-ng/issues/240) · [semantics #229](https://github.com/vanderpol/scap-ng/issues/229)

> **Proposed answer:** Yes, a **C** approach could deliver a substantially different human authoring language while leveraging 0.4-A's capability/collector contracts and SCAP 1.4 source-preservation work. We may also **redesign Variable syntax and execution**, but only if the resulting collected populations, typed values, dependencies, statuses and evidence are independently verified to be lossless. Do not restart the B provider rewrite. This is **not** a new normative grammar or a proven drop-in scanner.

## First executable feasibility checkpoint (19 October)

The first C prototype now has a [**one-page source-backed proof and negative-case report**](C-SHARED-ENGINE-PROOF-2026-10-19.md), with [8/8 focused tests PASS](https://github.com/vanderpol/scap-ng/actions/runs/39249073388). It consumes a **separately authored, research-only C YAML** for the original RHEL9 `/home` mount selector and reconstructs exactly the existing A collection/State/Item-requirement descriptor. An intuitive but source-changing `equals /home` rewrite fails closed. It also renders actual Apache **2- and 19-Variable** source dependency graphs as readable C steps and reconstructs the original A-indexed DAG and precollected-shell fixture values/statuses without new OS collectors. **Those Apache source specimens are 0.3-derived**, and the fixture outcomes use the existing research evaluator rather than an independent OVAL/scanner oracle. This validates a first **integration seam, not lossless rewritten Variable algorithms**. The C/A design remains non-normative; the exact next gate is source-pinned Windows typed Registry/records and a genuinely modified Variable operator with independent expected outcomes.

## Second executable checkpoint — common evaluation and actual Variable fusion (19 October)

The newer [**21-test focused CI gate PASS**](https://github.com/vanderpol/scap-ng/actions/runs/39251766907) covers [universal collection-empty/incomplete/error semantics and six-state Boolean evaluation](../../../tools/research_c_common_evaluation.py), the source-backed [Windows WDigest same-Item Registry bridge](../../../tools/research_c_registry_boundary.py), and a **separate fused Apache regex-capture + concat evaluator** over exactly the same precollected Items and pinned source graph ([implementation](../../../tools/research_c_fused_apache.py), [differential tests](../../../tools/test_research_c_fused_apache.py)). A pin mismatch or loss of source predicates fails closed; the fused evaluator agrees with independent expected outputs and a separate pre-existing source evaluator for the supported scenarios. The generic AND/OR/ONE/XOR lowering agrees with the previously audited independent six-state source oracle for the full six-by-six input pairs.

The results now establish **C architectural feasibility for focused source-backed Linux, Windows and Apache cases** without implementing another OS collector. They **do not** prove all six-STIG migration, original 1.4 XML parity, runtime scanner behavior or cross-OVAL regex identity. An explicit **complete/empty State-bearing Test whose existence passes** remains a semantic-review boundary. The [simple and complex examples review](C-AUTHORING-SAMPLE-REVIEW-2026-10-19.md) clearly distinguishes compiled research examples from narrative-only complex sketches. The separate repository-wide rebaseline smoke remains red in unrelated B source/crosswalk fixture tests; focused C pass is not a global-green claim.


## 19 October: source-backed shared-observation direction (research only)

The [Apache shared-observation research checkpoint](C-APACHE-SHARED-OBSERVATIONS-2026-10-19.md) identifies the more consequential readability opportunity: let several requirements consume a versioned, provenance-bearing **observation** instead of exposing every source Variable or repeating discovery. The pinned Apache SV-214268 source contains **19 Variables, five Tests, ten collection declarations and six Variables with multiple direct consumers**. The [read-only census](../../../tools/research_c_shared_observations.py) and [exact-scope evidence binding research](../../../tools/research_c_observation_bindings.py) distinguish a collection request, a collected observation, derived values and Test truth. Added focused tests cover source inventory, non-equivalent command/parameter coalescing, identity across target/snapshot/privilege/source Inputs, independently evaluated consumers and tamper detection. New tests are **not claimed CI-passing** until exact-head workflow verification.

**Do not equate** reusing the original source request/evidence with replacing four different Apache grep commands by a new typed directive reader. The latter could provide larger cross-Rule benefits but needs independently demonstrated Include semantics, file lineage, scope, errors and policy parity; until proved, it is **new native policy**, not lossless imported SCAP 1.4 semantics. A's source-preserving compatibility path remains mandatory.

## 1. Division of responsibility

```text
    One human-first C authoring language           SCAP 1.4 / source-exact 0.4-A input
                  |                                             |
          simple typed-requirement compiler          original-source compatibility compiler
                  +---------------------+-----------------------+
                                        |
                           ONE typed execution IR
                                        |
        +-------------------------------+-------------------------------+
        |                               |                               |
  A-derived ACQUISITION           TRANSFORM / DATAFLOW             EVALUATION
  capability mappings             typed derived values            typed field predicates
  Objects and selectors           Variables / expressions          Item/record cardinality
  platform collectors             Sets / filters / foreach         six-state logic
  typed Item/evidence IDs         scope / lineage / caching        completeness and result
        +-------------------------------+-------------------------------+
                                        |
                         one provenance and result format
```

**Preserve:** A's reviewed capability names and mappings, selector meanings, OS/API collection options, source identity, typed Items and records, completeness/error reporting, namespace/registry views, evidence provenance, and the potential for a shared collection cache. Collection and derived selectors must be separately traceable.

**Redesign:** The *auditor-facing* syntax, rule/condition vocabulary, natural named-resource/collection distinction, cardinality wording, and optionally the representation/implementation of Variables, Sets, filters and foreach. A new author need not write generic named Objects/Tests/States or chain temporary Variables when a typed requirement says the same thing.

**Protect:** Forward-import of SCAP 1.4 remains mandatory. Complex original mechanics can lower into **compiler-owned compatibility operations** in the same IR when they cannot be faithfully simplified. This must not become a second equally supported human-authoring YAML language or a hidden fallback that silently changes compliance results.

**Cost reality:** Existing scanners likely spend substantial engineering effort on platform acquisition, but we have not measured the proportion. More importantly, **there is currently no general-purpose executable 0.4-A scanner to drop into**. A's 4,001-document lossless *source envelope* and its verified 872 Assessment `evaluate` trees are still structural and result-only research, not completed collectors/Variable execution. Reuse A's *contracts and tested components* as the backend is built.

## 2. What "lossless" means for a Variable rewrite

**Losslessness applies to observable behavior, not text or identical intermediate Variable names.** A C compiler may inline, combine, or replace a source Variable with a typed transform pipeline only if it preserves:

- **Inputs and identity:** every source Object selector and option, typed Item/record population, namespaces, duplicate multiplicities, ordering where observable, empty vs absent vs null, and original source identity.
- **Computations:** typed concat, regex capture, merge, unique, split, count, arithmetic, Set union/difference and filters, with exactly the original operator/casting/regex semantics (do not assume similar-sounding operators are equivalent).
- **Dependencies:** original directed acyclic graph, dynamic selector calculations, collection timing, dependency errors, recomputation/cache scope and the origin of derived values.
- **Correlation:** foreach item aliases and lexical scoping; **per-parent collections must not silently become global unions**, and global-source requirements must not become per-parent requirements.
- **Outcomes:** complete vs incomplete reads; missing or inaccessible sources; duplicate/incorrect type; six-state Test/Assessment results; diagnostic and evidence lineage.

If proof fails, the importer retains the original operation through **versioned compatibility IR**, marks the simpler native rewrite unsupported, or classifies an explicitly different policy as a **new policy**, never as faithful conversion.

### Quantitative anchor (not execution proof)

The 0.4-A six-STIG [source-dataflow census](DATAFLOW-SIX-STIG-CENSUS.md) contains **377 named Variables**, **455 Variable references**, **91 shared Objects**, **162 Set sites**, **190 Filter sites** and **8 foreach sites**, with complete source-path indexing. The [lossless source envelope](LOSSLESS-IR-ENVELOPE.md) roundtrips 4,001 source documents and source graphs but **does not execute the Variables**. B's separate 0.3-corpus [Variable DAG census](../../requirements-first-language/contract-candidate/corpus/variable-dags.md) observes 376 source Variable declarations across 77 Assessments; those denominators are not interchangeable. A [six-state expression executor](EXPRESSION-RESULT-BOUNDARY.md) independently checks source Boolean trees only when **Test outcomes are supplied**.

## 3. Illustrative C authoring (NOT currently valid A or proven source-equivalent C)

These are **two short syntax sketches** to test the architectural benefit, not accepted SCAP-NG source or source-faithful conversions.

**Simple Linux requirement, native intent:**

```yaml
require:
  each: linux.mounts
  where:
    mount_point: {equals: /home}
  minimum_resources: 1
  must:
    mount_options: {contains: nosuid}
```

The A-derived collector would still acquire the filesystem/mount items with pinned selectors, statuses and source identity. **Do not silently replace the actual imported OVAL regex** `.*\\/home` with exact `/home`: native intent and source-converted behavior can differ.

**Windows Registry, native intent:**

```yaml
require:
  windows.registry_value:
    hive: local_machine
    key: 'SOFTWARE\\ExampleVendor\\Security'
    name: SecurityMode
    storage_type: dword
    value: 0
```

The A collector's view, type, absence, multiplicity, and coercion rules must be pinned before claiming equivalence to an original Registry Test. The friendly `storage_type` key is **only a sketch**; the canonical 0.4-A field is `type`, whose enum comes from the mapping. The typed `value` comparator remains an explicit concern.

## 4. Small technical proof before a decision

| Source-backed fixture | What must be demonstrated | Pass/fail boundary |
| --- | --- | --- |
| RHEL9 /home mount `nosuid` | C-friendly requirement compiles to **the same A-derived collection plan** and scoped comparison | Regex vs exact path, selected/matching Items, complete-empty and incomplete |
| Windows 11 Registry type/value | Native Registry selector and typed storage/value comparisons reuse A mapping | Registry view and datatype, missing/inaccessible, duplicates, type vs value |
| Apache with chained Variables | Rewrite typed concat, captures, merge, unique without replacing original command discovery | Actual dependency DAG, partial command output/errors and provenance |
| Linux root-account initialization files | Preserve global root-derived population and 0740 bit mask, not an unintended per-account requirement | Global/per-parent scope, all 4,096 POSIX mode cases, unknown/incomplete |
| Windows WMI or DNS correlated records | Preserve whole-State OR or zone/key parent identity | Mixed record values, missing relation, partial evidence and six-state result |

A focused experiment should produce **one paired collection/evaluation IR fixture** for a simple Linux case and one hard Variable case, with independent expected results and source provenance; only then expand. The [B research](../../requirements-first-language/GO-NO-GO-ARCHITECTURE-2026-10-17.md) contains useful readable grammar and evaluator fixture work, but its [conversion ledger](../../requirements-first-language/contract-candidate/corpus/conversion-progress.md) still reports zero scanner-verified source-equivalent Assessments. **Do not rebuild B platform providers to test C.**

## 5. Explicit decision gates

**GO for deeper C engineering** when: one pinned A capability collection request is reused **unchanged** by both source-compatible and C authors; typed Item/evidence contracts exist; a real source Variable graph is compiled to equivalent transform/evaluation instructions with independently expected outcomes; and C is clearly easier for first-time auditors to write/review.

**NO-GO for normative C promotion** until: full representative source migration (six reference STIGs), typed/evidence/error/six-state result correctness, source-compatibility handling, deterministic compiler and scanner integration, and independent authoring usability are validated. **No A-vs-C selection or weighted bake-off before comparable functional capability.** A remains the implementation/source-compatibility baseline; B remains historical research input.

**First architectural conclusion:** This is primarily a **new authoring/compiler frontend and a redesigned typed execution interface**, *not* another collection-engine project. The initial design is bounded here; the expensive part is verifying whether redesigned transforms really preserve source behavior, not deciding the layers.
