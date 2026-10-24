# Issue #251: approved-require integration review packet

2026-10-24; [#251](https://github.com/vanderpol/scap-ng/issues/251),
[#248](https://github.com/vanderpol/scap-ng/issues/248).
Started from live main `5a43f45a972fb63526e71ac872b21d97a676044c`;
implementation checkpoint `97c5197f78c653165545e3277544e82bce88e62b`.
A follow-up commit contains the production CLI bridge and this packet.
**The three-case checkpoints pass. Issue #251 remains open for the source
`all_exist` population decision below. No schema, specification, result schema,
scanner, editor or 0.3 code was changed.** This is not 0.4.0 release completion.

## What changed

The existing `v04_field_requirement`, `build_v04_canonical_six_stigs`,
`scap_converter_core`, typed source IR, and native bundle compiler now connect
through the approved explicit `require` grammar. The shared OVAL parser and
mature semantic lowering remain the source authority. The CLI's three added
complex-source cases are gated by the original XML hashes, independently checked
OVAL semantic reconstruction, the existing reversible authoring passes, the
source-axis audit, exact schemas and compiler. This does not grant a new corpus-wide
support claim. Existing source-verified leaf/Variable adapters use the same
upgrader before compilation; their source-attestation and mutation tests remain.

All 20 source Test existence/check pairs, 20 field pairs and 20 record pairs
(including field/record `every`) retain separate axes. Distinct source States,
logical `one` versus `xor`, repeated field predicates, record members,
expected-value `value_match`, and explicit nearest field scopes survive.
Unrepresentable input errors rather than emitting a legacy State fallback.
Source-only tokens, omitted versus explicit XML attributes/defaults, graph IDs
and inverse ledgers remain in separate provenance, never compiler instructions
that secretly override the authored requirement.

The compiler consumes inline and shared/reference Objects, checks source DAGs
and capability agreement, keeps complete nested requirements in dispatch operands,
and independently revalidates compiled documents, manifest, IDs, hashes and
programs. Legacy State keys, invented keys and invalid count tokens are rejected.
No runtime Test evaluator was implemented or inferred from a textual rename.

Real Sets/Filters/Variables/for_each graphs are retained; only the existing
source-proven direct-filter projection is used for the Bluetooth leaf bridge.
No blanket flattening of single-operand Sets or permission bits was introduced.
This bounded work does not close the broader #248 occurrence-ledger audit.

## Actual generated outputs

Each row has one Assessment, its original OVAL graph/source mapping, exact
source hash, a YAML/JSON parsed-parity report and its compiled program. The test
also builds and verifies a complete three-document Benchmark/Rule/Assessment
bundle for each row; large bundles are not checked in. Each alternate Object
form is separately compiled and schema-validated without erasing sharing.

| Pinned source case | Test count | Generated YAML | Authoring JSON | Compiled JSON | Source graph and audits |
| --- | ---: | --- | --- | --- | --- |
| RHEL 9 SV-257889 | 2 | [YAML](SV-257889/authoring.yaml) | [JSON](SV-257889/authoring.json) | [program](SV-257889/compiled.json) | [provenance](SV-257889/provenance.json) |
| Windows Server 2025 SV-278001 | 5 | [YAML](SV-278001/authoring.yaml) | [JSON](SV-278001/authoring.json) | [program](SV-278001/compiled.json) | [provenance](SV-278001/provenance.json) |
| Windows Server DNS SV-259345 | 5 | [YAML](SV-259345/authoring.yaml) | [JSON](SV-259345/authoring.json) | [program](SV-259345/compiled.json) | [provenance](SV-259345/provenance.json) |

Definitions are respectively `oval:mil.disa.stig.defs:def:230325`,
`oval:navy.navwar.niwcatlantic.scc.windows:def:278001`, and
`oval:navy.navwar.niwcatlantic.scc.windows:def:259345`.
Their pre-existing original XML excerpts are under
`research/assessment-simplification/evidence/` (exact paths and SHA-256 in each
sidecar). They were neither downloaded from a new mirror nor rewritten.

Example source: Windows `...windows:tst:27800105` references
`...windows:obj:27800105` and `...windows:ste:27800105` / `...:ste:27800106`,
with `check="all"`, omitted `check_existence`, and `state_operator="OR"`.
Its WMI record `domainrole` fields contain source strings `4` and `5`.
The actual generated requirement is:

```yaml
require:
  items_found: one_or_more
  items_satisfying: every
  or:
  - fields:
      result:
        record:
          fields:
            domainrole:
              datatype: string
              equals: '4'
              values_found: one_or_more
              values_matching: every
          records_found: one_or_more
          records_matching: every
  - fields:
      result:
        record:
          fields:
            domainrole:
              datatype: string
              equals: '5'
              values_found: one_or_more
              values_matching: every
          records_found: one_or_more
          records_matching: every
```

Its compiled instruction has `opcode: CHECK_ITEM_CONDITION`,
`test_id: system-windows-domain-controller-test`, and the identical requirement
under `operands.require`; the linked JSON is the actual compiler output.
This preserves complete record alternatives instead of separating their members.
The source field's omitted datatype means string, so no integer coercion occurs.

Linux `oval:mil.disa.stig.unix:tst:23032500` uses `check_existence="any_exist"`
and `check="all"`. Its actual output uses `items_found: may_be_absent`,
`items_satisfying: every` and eight separate permission-bit conditions. For example,
the first condition is `fields: {setuid: {datatype: boolean, equals: false,
values_found: one_or_more, values_matching: every}}`. The full linked YAML retains
all eight bits, filtered passwd acquisition and dependent Variable graph.
Windows SV-278001 exercises explicit `var_check="at least one"`; Windows DNS
SV-259345 exercises omitted `var_check` (OVAL default `all`). XML attributes and
native expected-value quantifiers are separately retained in the sidecars.

## Checkpoints and commands

[Machine-readable results](test-results.json) records the exact focused command,
counts and overlapping denominators. Do not add overlapping suite totals as
independent coverage.

- Checkpoint A: real original OVAL -> maintained lowering -> reversible upgrader
  -> generated YAML/JSON -> exact version-local schemas and source audit: **3/3**.
- Checkpoint B: same generated files -> source IR -> compiler -> compiled bundle
  schema/manifest/content/program verification: **3/3 Assessments, 12/12 Tests**.
  The three synthetic policy wrappers have **9 documents** total; original and
  alternate Object forms both resolve and preserve Test counts/IDs.
- Focused schema/converter/upgrader/compiler/integration suite: **165 passed,
  0 failed, 0 skipped**. Includes one additional *negative* real-source case;
  the three positive-case denominator remains three.
- Existing converter bridge workflow's **21 external pinned XML inputs plus the four repository cases / 16 test modules**:
  **83 passed, 0 failed, 0 skipped**. See [input hashes](self-assertion-inputs.json)
  and `.github/workflows/v04-converter-core-bridge.yml` for exact paths, commands
  and environment bindings. These are focused Self-Assertion inputs, not 21 STIGs.
- Existing fast workflow's **31 test modules**: **197 passed,
  0 failed, 0 skipped**. The historical three ZIPs are no longer claimed valid
  under the revised schema; the lane now generates these fresh three cases.
- `python tools/test_v04_all_items_schema.py`: 3 positive/6 negative Test
  cardinality cases plus State-free presence, inheritance and legacy rejection.
- `PYTHONPATH=tools python tools/test_v04_canonical_authoring_guard.py`:
  6 rejection fixtures plus importer conflict guards passed.
- `git diff --check`: passed. The warning about duplicate `a1.yaml` is from the
  deliberate duplicate-ZIP-member rejection test.

Regenerate these samples from repository root with:

```sh
SCAP_NG_251_OUTPUT_DIR=/tmp/issue251-output PYTHONPATH=tools \
  python -m unittest tools.test_v04_approved_pipeline -v
```

The production CLI is also exercised in the converter bridge suite. For example:

```sh
python tools/scap_converter_core.py \
  --source-xml research/assessment-simplification/evidence/ms_windows_server_2025/SV-278001/source-oval.xml \
  --definition-id oval:navy.navwar.niwcatlantic.scc.windows:def:278001 \
  --assessment-id source-sv-278001-assessment \
  --output /tmp/windows-251.json --evidence /tmp/windows-251-provenance.json
```

The independent generic OVAL model compares **24,860 / 12,432 / 12,432**
scenarios per case. These are reused generic populations, not distinct native
capability executions. The Linux audit retains **4 unresolved empty-State
aggregate scenarios**; Windows audits retain zero. The separately maintained
boundary fixtures cover incomplete/error/unknown and exactly-one behavior.
Record acquisition, host execution and capability-specific scanner equivalence
remain unproved; source/schema/structural inversion is not runtime evidence.
No six-STIG regeneration or full 65-STIG run was performed locally.

## Source semantic blocker: owner decision required

The approved schema maps both OVAL Test `all_exist` and
`at_least_one_exists` to `items_found: one_or_more` and excludes synthetic
`does_not_exist` Items. Source provenance cannot act as a hidden executable
semantic override. The source result algebra distinguishes those OVAL tokens.

A minimal real declaration is RHEL 9 SV-258179:

```xml
<textfilecontent54_test id="oval:mil.disa.stig.ind:tst:23041300"
  version="1" check_existence="all_exist" check="all">
  <object object_ref="oval:mil.disa.stig.ind:obj:23041300"/>
</textfilecontent54_test>
```

Original source SHA-256:
`463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9`.
The Object acquires `/etc/audit/audit.rules` with the original setxattr regex
and `instance >= 1`; this Test has no State. The new real-source negative
regression lowers the unchanged Definition and confirms that `upgrade_v003`
fails the source-axis audit rather than certifying a source-exact compilation.

Controlled result boundary (not an observed host/scanner result): complete
source evidence with one existing and one `does_not_exist` Item yields
**false** for source `all_exist`, but **true** for source
`at_least_one_exists`. Both structurally map to `{items_found: one_or_more}`.
For incomplete State-bearing evidence, `all_exist` can also remain unknown
where an at-least-one match is decisive. Fields/records still retain `every`;
this Test-population issue is not used to collapse them.

The converter records `source_all_exist_requires_population_evidence` and exact
source tokens in its ledger; the strict source audit refuses to call this
collision equivalent. The three positive examples avoid this collision. No
source-exact fallback grammar, hidden field defaults, new schema enum, or
scanner behavior was invented to conceal it. Owner decision is required before
expanding source-exact acceptance: retain these inputs as blocked, or approve
an explicit representation/evidence contract that preserves their outcomes.
No broader acceptance or schema change is proposed as already approved.

## CI and remaining limits

At implementation commit `97c5197f78c653165545e3277544e82bce88e62b`:
[focused schema](https://github.com/vanderpol/scap-ng/actions/runs/40048569596)
and [canonical fast integration](https://github.com/vanderpol/scap-ng/actions/runs/40048569572)
passed. The follow-up repairs the converter bridge and retained source-oracle
fixtures exposed by live CI; final run/artifact links are posted in #251.

Several older preview/grammar/roundtrip workflows already failed at the approved
schema baseline (for example
[baseline six-STIG preview](https://github.com/vanderpol/scap-ng/actions/runs/40031013929)
and [baseline complete-logic preview](https://github.com/vanderpol/scap-ng/actions/runs/40031013983)).
Their immutable old artifacts remain historical. They were not silently
republished, relaxed, or treated as current-schema success. Focused passing
checkpoints do not close those broader migrations, the full #248 corpus audit,
the empty-aggregate boundary, source `all_exist`, or scanner conformance.
