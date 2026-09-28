# OVAL -> SCAP-NG Assessment Design Review Samples

These five samples are intentionally **provisional**. They are derived from real
RHEL 9 V2R9 STIG OVAL and exist to expose design problems before the Assessment
schema is stabilized.

The goal is not to transliterate OVAL XML. The goal is to preserve OVAL's
semantics while replacing its Definition/Test/Object/State/Variable authoring
graph with explicit, readable collection, derivation, assertion, and result
semantics.

## Samples

| Sample | RHEL 9 Rule | OVAL closure | Design pressure |
| --- | --- | --- | --- |
| 01 | RHEL-09-253070 | 2 defs, 1 test, 1 object, 1 state | simple scalar comparison; expose formerly hidden existence/check behavior |
| 02 | RHEL-09-215020 | 2 defs, 1 test, 1 object | pure absence/existence assertion |
| 03 | RHEL-09-232190 | 1 def, 1 test, 1 object, 3 filter states, 1 variable | multi-item universal assertion; bounded failure evidence |
| 04 | RHEL-09-653030 | 2 defs, 2 tests, 3 objects, 1 state, 2 variables | named intermediate data and derived values |
| 05 | RHEL-09-654025 | 7 defs, 24 tests, 24 objects, 17 variables | large repeated logic; candidate structured capability + Cartesian assertion matrix |


## Formal Stage-1 / Stage-2 paired sample

RHEL-09-654025 is now the first explicit paired conversion example.

**Rule policy and traditional Check Text**

- Rule policy:
  `../../policy/RHEL-09-654025.policy.yaml`
- Manual Assessment preserving the source STIG Check Text:
  `../manual/RHEL-09-654025.manual.assessment.yaml`

**Automated Assessment variants**

- **Stage 1 lossless baseline**:
  `../automated/RHEL-09-654025.lossless.automated.assessment.yaml`
- **Stage 2 aggressive/native candidate**:
  `05-audit-syscall-matrix-native-candidate.assessment.yaml`

The Stage-1 file preserves all 24 OVAL tests, exact regular expressions,
explicit OVAL existence/check behavior, the defaulted
`at_least_one_exists` cases, and both source anomalies in which the nominal
64-bit root case actually resolves to a duplicated `b32` regular expression.

The Stage-2 candidate intentionally does not preserve that implementation
shape. It demonstrates the possible future `linux.audit_rule` capability and
a Cartesian assertion model.

Review the Stage-1 file when evaluating conversion fidelity. Review Stage 2
when evaluating whether native SCAP-NG authoring is substantially easier.

## Working principles exercised

- No hidden authoring defaults for existence/cardinality or comparison quantifiers.
- Collection semantics and assertion semantics are separate and visible.
- Named intermediate data replaces opaque variable/object reference chains.
- Result evidence limits do not change compliance truth.
- The content author can request bounded concrete failure examples.
- A scanner may optimize execution internally without forcing authors to model the engine's execution graph.
- Lossless source conversion and semantic/native refactoring are separate concerns.

## Important finding from sample 05

The source OVAL for RHEL-09-654025 appears to contain duplicated 32-bit root
patterns for the \`lsetxattr\` and \`removexattr\` cases where the surrounding
structure suggests corresponding 64-bit cases may have been intended.

That is exactly why an aggressive converter must not silently infer and
"repair" intent.

A conservative conversion SHALL preserve the source behavior. A later semantic
refactoring pass MAY propose a cleaner structured form, but any behavior change
requires explicit review/provenance.

## Questions these samples intentionally leave open

- Whether \`fields\` belongs under collection, results, or both.
- Final vocabulary for explicit existence/cardinality.
- Final expression syntax for named derived data.
- Whether common derived properties such as partition \`total_bytes\` belong in the capability data model.
- Whether SCAP-NG should add structured domain capabilities such as \`linux.audit_rule\` rather than requiring regex parsing of configuration text.
- Final syntax for a Cartesian assertion matrix such as sample 05.

Do not treat these files as final schema fixtures.


## Simulated result fixtures

The \`results/\` directory contains three provisional result fixtures for each
Assessment sample. These are intentionally not a finalized result schema; they
exist to stress the relationship between Assessment semantics and operational
reporting.

| Assessment | Result fixtures |
| --- | --- |
| 01 sysctl scalar | pass, wrong-value fail, missing-required-item fail |
| 02 package absent | pass, prohibited-package fail, collection error |
| 03 command ownership | pass, complete fail, short-circuit fail |
| 04 derived audit storage | pass, size fail, source collection error |
| 05 audit syscall matrix | pass, missing-required-combination fail, collection error |

The fixtures test:

- concise deterministic \`message\` values suitable for SIEM/log consumers;
- exact versus unknown total failure counts;
- short-circuit evaluation;
- item-level concrete evidence;
- missing-item/missing-match evidence;
- rich \`error\` outcomes instead of flattening collection failures into
  compliance failure;
- derived/intermediate evidence;
- aggregate matrix/completeness summaries.

### Important result-model finding

Not every compliance failure has a concrete "bad object."

Two distinct evidence shapes are already necessary:

1. **offending collected item**, for example a file whose owner is not root;
2. **missing required condition**, for example no audit rule exists for a
   required syscall/architecture/identity combination.

The final result model SHOULD represent both without pretending that a missing
required object was itself collected.

The result payload boundary—how much Rule policy metadata, Assessment metadata,
source lineage, and evidence belongs in each result versus a surrounding run
package—remains intentionally open pending review of real operational
consumers such as Splunk/Elastic JSONL output.
