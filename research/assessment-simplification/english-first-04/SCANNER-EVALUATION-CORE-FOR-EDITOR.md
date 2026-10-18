# Evaluation-only SCAP-NG core for sample-data authoring

**18 October 2026 · Research / [#241](https://github.com/vanderpol/scap-ng/issues/241), [#229](https://github.com/vanderpol/scap-ng/issues/229), [#235](https://github.com/vanderpol/scap-ng/issues/235). Not a ratified scanner, compiler task or change to the 0.4 Assessment grammar.**

## Owner insight: collection and evaluation are separable

The editor does **not** need SSH, WinRM/WMI, shell, registry, process or filesystem collectors to test an author's observations. The editor needs to submit supplied *typed collected Items and source flags* to **the very same evaluator used by a tested scanner**.

A useful precedent is the official OVAL **5.12.3** `independent:variable_test`: a test compares the value(s) of a referenced variable against State criteria. It can exercise some comparison and result handling without inspecting operating-system artifacts. [Official OVAL Independent Definition element dictionary, `variable_test`](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/independent-definitions-schema.html#variable-test); [`variable_object`](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/independent-definitions-schema.html#variable-object) and [`variable_state`](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/independent-definitions-schema.html#variable-state).

**Important source precision:** This proves `variable_test` is a standard evaluation-only test mechanism; it does **not** prove any particular percentage of the SCAP 1.4 scanner validation-test corpus is made of variable tests. That share requires an actual census of a pinned official package. NIST's **SCAP Content Validation Tool** (checks conformance of data streams) and **scanner product evaluation semantics** are also distinct validation questions: [NIST SCAP 1.4](https://csrc.nist.gov/Projects/security-content-automation-protocol/scap-releases/scap-1-4).

## Proposed single-core architecture

```text
LIVE SCANNER                                AUTHORING EDITOR
native OS collectors                       user-entered typed Items
shell, filesystem, WMI, etc                imported/pasted sample evidence
                 \                         /
                  \                       /
                 ONE VERSIONED COLLECTED-DATA CONTRACT
                   typed Items + flag + status/provenance
                             |
                             v
                   SAME SCANNER EVALUATION CORE
                   object selection + Set/Filter handling
                   Variables / value expansion / for_each
                   field comparisons + record correlation
                   existence / check / match / entity/var_check
                   Test aggregation + six-state evaluate tree
                             |
                             v
                  six-state truth + reason / trace
                             |
                  scanner-backed sample result
                (when tested for that exact scope)
```

The **entry point changes**; the evaluator source and semantics do **not**. The live scanner owns collection and can optionally perform supported selector pushdown optimizations. The sample harness owns synthetic observations and must preserve **the equivalent canonical collected Item representation**, not invent values that a real collector could never return.

**Do not reduce this to “just call `variable_test` for every Test.”** OVAL `independent:variable_test` checks variable values; it does not itself reproduce a Windows `record` and correlated fields, Item-count existence, complex Object Sets, Filters, `for_each` over collected Items, or incomplete collected-object statuses. Those are common **evaluation-core** responsibilities even when all raw Items are supplied by an author.

## Two explicit injection levels for fixtures

| Injection point | Author supplies | Still evaluated by core | What is *not* tested |
| --- | --- | --- | --- |
| **A. Supplied variables**, analogous to OVAL `variable_test` | Named variable values and types, and status where allowed | Variable comparison, value-to-entity `var_check`/`entity_check`, tested logical Test/Assessment operations | Native data acquisition, Object discovery/selection, non-variable Item/record semantics |
| **B. Supplied collected Objects**, preferred general editor mode | Source Object IDs, flags `complete/incomplete/error/does_not_exist/not_collected/not_applicable`, zero/one/many typed Items with named fields, optional records and line provenance | State comparisons, field existence, Items and State check, record correlation, Set/Filter evaluation **if supplied at the prefilter boundary**, Variables derived from Items, `for_each`, six-state Test/`evaluate` | Native source collector implementation and its OS/provider fidelity |
| **C. Supplied *post-selection* Items** (optional, constrained) | Exactly the already-selected Items and declared status, with source Object selector path | Field/record/Item matching and six-state aggregate operations supported by the engine | Whether Object selector, Set/filter, variable-driven acquisition selects the right Items; must be labeled “selector not tested” |

**The chosen fixture boundary is part of the signed-off test record.** A result from level A or C must not be called a full native Assessment evaluation if that Assessment depends on skipped selectors/sources. Missing Test/Assessment dependencies fail closed or remain **UNSUPPORTED**, not made false, true, or empty.

## One conceptual synthetic sample fixture — *not an approved schema*

```json
{
  "research_fixture_version": "eval-only-concept-0.1",
  "assessment_id": "ng.shared.home-is-mounted-with-the-nosuid-option",
  "assessment_sha256": "<pinned Assessment SHA>",
  "injection_point": "pre_object_filter_collected_items",
  "sources": {
    "home-mount": {
      "collection_flag": "complete",
      "items": [
        {
          "id": "synthetic:mount-1",
          "fields": {
            "mount_point": "/home",
            "mount_options": ["rw", "nosuid"]
          }
        }
      ]
    }
  },
  "expected": {
    "test_result": "true",
    "assessment_result": "true",
    "oracle": "independently-reviewed source-backed fixture"
  }
}
```

**This is not a declared runtime fixture format.** Values must be checked against the exact capability's native Item type/multiplicity. `expected` is a separate independently authored prediction and **never** computed from the engine being tested. One matching option does not prove a pass if another selected mount lacks `nosuid`; one complete selected Item differs from an incomplete collection containing that same Item.

An **editor sample result** is a statement about the *provided synthetic evidence* at its declared injection point and version, **not a live-host compliance claim**. The Rule/Benchmark layer separately maps Assessment truth to XCCDF result/policy outcome.

## Reuse inventory — what we already have, and its limitations

| Existing Python source in this repository | Verified current slice | Missing before calling it the shared scanner core |
| --- | --- | --- |
| [`tools/oval_result_truth_tables.py`](../../../tools/oval_result_truth_tables.py) | OVAL 5.12.3 six-state Boolean/existence and `var_check` vs `entity_check` reference functions, record matching and incompleteness boundary helpers | Parsing actual arbitrary Assessment Test/State expressions and interpreting raw Items/values |
| [`tools/v04_a_truth_plan.py`](../../../tools/v04_a_truth_plan.py) | 0.4-A `evaluate` tree → source-positioned six-state result from **supplied Test truth leaves** | Field/Item/Test evaluation, Variables/Set/Filter collection graph |
| [`tools/v04_a_wmi_domainrole_source_fixture.py`](../../../tools/v04_a_wmi_domainrole_source_fixture.py) | Bounded WMI record `DomainRole` 0/1/2/3/4/5 source-exact role result simulation | Generic nested records and user-right Test evaluation; no live WMI |
| [`tools/prototype_a_linux_mount_scan.py`](../../../tools/prototype_a_linux_mount_scan.py) and [bridge](../../../tools/v04_a_linux_mount_expression_bridge.py) | One pinned Linux `/home` Item + Test + Assessment execution path | General capability comparisons/collections or OVAL parity |

These **reference research components are not an already-tested common scanner engine**; the owner-approved rule that AI is for authoring only, and tested scanner evaluation is authoritative, remains intact.

## Feasibility review — where the real work is

1. **Likely low-cost initial result evaluator:** literal scalar/multi-value comparisons; `equals`, anchored/nonanchored regex with the correct OVAL dialect, version/number/bitwise operations, Item and field existence versus matching, State aggregation, Test and `evaluate` truth tables. Use pinned independent 5.12.3 expected-result cases; no implicit defaults.
2. **Moderate complexity:** source Object selectors, nested Windows records and member correlation, `states_match`, expected-value `value_match` versus `entity_check`, `var_check`, reported elements; preserve collection status and source identity.
3. **Harder but still pure evaluation without OS access:** Object Sets/Filters including error/unknown membership, dynamic Variable references, `concat` cross-product versus `merge` join, `for_each` preserving per-Item lineage, conditional branch/unknown evaluation when semantics ratified.
4. **Not required for the sample harness:** implementing native collectors, credentials, remote orchestration, fast filesystem traversal, OS privilege elevation, SIEM transport, signed bundle distribution and host inventory.

**Complexity has been reduced substantially, but not eliminated.** The strongest risk is not parsing sample text; it is getting **result-status and cardinality semantics** exactly right on partial and correlated observations.

## Validation gates for an authoritative *evaluation-only* scanner mode

Before labeling a result **scanner-verified on supplied data**:

- Run **the exact same evaluator code/path** in the real scanner and the editor fixture mode (same semantic/version/capability registry), not parallel AI and Python guess implementations.
- Test output truth against independently transcribed OVAL 5.12.3 tables and source-backed snapshots for each supported capability/operation, including all six results, collected-object flags and positive/negative fixtures. Include missing versus empty Item/field, `only_one_exists` vs `only_one_matches`, zero/one/many value matching, incomplete decisive false vs unknown, status precedence, and same-record versus cross-record correlation.
- Check selection/Set/Filter/Variable dependency completeness, type and field multiplicity, provenance, status flags and exact lexical trace paths; reject unsupported operators/capabilities rather than assume common-language behavior.
- Pin scanner engine build ID, loaded Assessment/schema hashes, fixture hash, collection injection level, feature coverage and expected-versus-actual comparison. Ensure **fixture assertion passed** is distinct from **Assessment TRUE**.
- Use independent test implementations/oracles where possible; a second Python reference model can be useful to cross-check the scanner, but **cannot itself certify its own results**.
- **Human technical acceptance** via project review gate [#229](https://github.com/vanderpol/scap-ng/issues/229), with explicit supported surface and uncovered cases. Do not equate successful source conversion/compilation alone with semantic conformance.

**Result vocabulary:** `NOT SCANNER-VERIFIED / UNSUPPORTED` until that gate is met; afterward, `SCANNER-VERIFIED FOR SUPPLIED EVIDENCE` only for the tested evaluation slice, without claiming host collection was checked.

## Recommendation, scoped to the owner's current goal

**Prioritize an independently testable evaluation kernel and canonical collected-Item fixture contract, not the collection subsystem, as the first validation step for an AI-first authoring editor.** Use the existing Python OVAL reference calculations as conformance oracles, and `independent:variable_test` as the conceptual precedent for supply-values-first validation. Aim to make this kernel part of the scanner itself, so there is no later rewrite or two competing engines.

This is **architecture and acceptance research**, not a new compiler/scanner implementation authorization; it does not modify normative language semantics or assert that the current Python prototype passes full content validation.
