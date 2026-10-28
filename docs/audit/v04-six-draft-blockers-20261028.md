# Actual six-benchmark draft blockers — 2026-10-28

Issue: [#251](https://github.com/vanderpol/scap-ng/issues/251).
The [published DRAFT — NOT RUNTIME VERIFIED](https://github.com/vanderpol/scap-ng-evidence/tree/v04-six-source-draft-20261028-c65a134b5/runs/v04-converter/2026-10-28-six-source-draft-c65)
uses pristine toolchain `c65a134b539558609ccf3bdc0600f38e411bbb2e` and NIWC
`8c8e5dff860af6b1290ee9273a282db24278f8d5`. Analysis reads that actual Rule
ledger, not historical conversion estimates. [Machine-readable counts](v04-six-draft-blockers-20261028.json)
record its SHA-256 and evidence commit `150d57f14050954161e4515d49a637991740fe01`.

## Disjoint primary causes

Each of the 341 blocked automated Rules appears exactly once here. The 171
OCIL-only/manual Rules and 1,055 eligible compiled/unproved Rules are excluded.

| Primary cause | Rules | Responsibility / next action |
| --- | ---: | --- |
| `all_exist` | 232 | Largest population-contract dependency; coordinate #255. Production lowering remains explicitly unauthorized. |
| Unresolved checklist catalog bindings | 63 | Original packaging defect: 41 DNS, 22 Apache. Preserve source and report; do not guess aliases or coerce namespaces. |
| Acquisition parameter comparison/type | 17 | Bounded converter candidate: all involve an explicit shell-command pattern regex operation already supported by the committed mapping. Probe source/semantic preservation next. |
| Unsupported functions | 16 | Ten `split`, six `count` primary cases. Keep unsupported until coordinated function integration and error contracts are ready. |
| Invalid/deprecated original closures | 12 | Source remediation; do not relax validation. Includes two raw native candidates explicitly disqualified from eligible output. |
| Comparator-bearing absence | 1 | Preserve the source/absence proof boundary; no generalization of the pinned RHEL exception. |
| **Total** | **341** | Counts are current primary causes, not predicted successful unlocks. |

| Benchmark | Blocked automated |
| --- | ---: |
| RHEL 9 | 126 |
| Oracle Linux 9 | 122 |
| Windows 11 | 18 |
| Windows Server 2025 | 12 |
| Windows Server DNS | 41 |
| Apache 2.4 UNIX | 22 |

Server 2025 has 291 total Rules, 261 OVAL-bearing and 30 OCIL-only. Its current
draft has 249 eligible compiled/unproved and 12 blocked automated Rules.

## Capability and secondary counts overlap

Required capabilities are counted once per blocked Rule, not once per node.
Leading requirements are Textfilecontent54 (148 Rules), sysctl (52), partition
(22), shellcommand (21), registry (18), variable.value (18), WMI query (13),
rpminfo (10), and UNIX file (10). A Rule may need several capabilities. These
counts do not identify a unique failure or promise that enabling a capability
will unlock that many Rules. The 63 catalog-blocked closures have unresolved
capability requirements; do not infer their executable content from guessed
references. The JSON report retains the complete overlapping breakdown.

Secondary messages are deduplicated per Rule across source-node contexts.
They include all_exist on 232 Rules, acquisition-parameter guards on 21, split
on ten, count on six, and nil cmdlet input guards on three. The same primary
message can recur as a secondary node diagnostic; do not add those counts.
The original occurrence count for all_exist was 1,181 secondary entries, which
represents 232 affected Rules, not 1,181 Rules. Masked failures mean a primary
fix is only an upper bound on possible conversion gains.

## Two source-backed corrections to priority assumptions

DNS and Apache contain catalog `uri` elements in the SCAP data-stream namespace
instead of `urn:oasis:names:tc:entity:xmlns:xml:catalog`. Matching component-ref
names do not authorize silently repairing that source namespace error. The
strict converter's unresolved binding diagnostics are preserved.

The earlier zero-function Oracle research estimate is incomplete for extended
Definitions. Original Oracle Rule `SV-271653` selects
`oval:mil.disa.stig.ol9os:def:271653`, which contains:

```xml
<extend_definition definition_ref="oval:mil.disa.stig.defs:def:230511"/>
```

That Definition reaches local Variable
`oval:mil.disa.stig.linux:var:23051100`, containing `split delimiter=","` over
Object `oval:mil.disa.stig.ind:obj:23051102` / Item field `subexpression`.
The original ZIP SHA-256 is
`6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d`.
The ledger records additional split/count/arithmetic reachability through
resolved closures. Its function presence counts cover resolved bindings only;
they do not replace an independent census of the catalog-invalid sources.
Do not infer that substring is the sole remaining production function obligation
from a walk that omits `extend_definition` edges.

This corrects a factual reachability assumption; it does not approve any
function implementation, new syntax, schema change or evaluation semantics.

## Implementation priority

Investigate the existing shellcommand intrinsic regex route first. The mapping
already permits `pattern match` for its `pattern` parameter and describes
regex filtering; `AssessmentConverter.parameter` currently hardcodes equality.
Preserve the regex string, acquisition boundary, Variable/cardinality guards,
collection error controls and independent source proof. Do not admit unrelated
command/query comparison operations merely because their XSD permits them.
Measure actual newly proved Rules after the fix; 17 is a primary-case upper
bound, not an implementation result.

Continue the preserved enum-reference batch with focused tests and old-hash
retention. Keep #255 population/function dependencies separate from source
remediation. Existing exact-c65 maintained CI passed 3,264 tests with zero
failures/errors and one existing skip; no duplicate full suite was run for
publication or this data analysis. A later verified checkpoint still requires
its exact-SHA source validity, independent proof and six-benchmark gates.

To reproduce counts, read the published `ledger.json`, select rows with
`oval_bearing` and `draft_status != CONVERTED_COMPILED_UNPROVED`, assert 341
unique `(benchmark, source_rule)` identities, and count `primary_diagnostic`
once per Rule. For secondary/capability breakdowns, deduplicate each Rule's
messages or `needed_capabilities` before adding it to a counter. The JSON
report provides the exact ledger digest and original per-benchmark messages.
