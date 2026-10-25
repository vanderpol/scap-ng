# Maintaining the direct 0.4 experiment

This is a two-Rule experiment, **not a production converter or full Benchmark
migration**. Python 3.12 is used in CI. No model service is needed to run or edit
the code. The two conversion modules are newly written; neither imports the
previous prototype, a production renderer, a 0.3 module, or an intermediate IR.
The original signed fixture and unmodified public validators/compiler/proof
readers are reused as data and external gates, not as conversion algorithms.

## Files and contracts

| File | Responsibility / important entry points |
| --- | --- |
| [v04_direct_scap_source.py](../../tools/v04_direct_scap_source.py) | `SourceModel(path, expected_sha256)` verifies ZIP bytes/CRC, parses one complete XML member once, and indexes IDs/references per component. `automated_check` resolves checklist-local catalog references and rejects unsupported check choices. `rule_selected` projects ancestor/Profile selection. |
| [v04_direct_converter.py](../../tools/v04_direct_converter.py) | `AssessmentConverter.reference(id, kind)` is the single memoized recursive dependency visitor. `convert_object`, `set_expression`, `filter`, `convert_variable`, `predicate`, `convert_test`, and `criteria` produce current native dictionaries directly. `convert(source, two_rule_ids)` returns `(documents_by_relative_path, external_trace)` without writing files. `main` emits JSON/YAML and metrics. |
| [test_v04_direct_converter.py](../../tools/test_v04_direct_converter.py) | `verify_original` independently resolves original XCCDF/OVAL, then uses existing independent operand readers. Unit tests cover published dependencies, controlled compositions, failures, public CLIs, and compiled operands. Measurement mode runs the same gates. |

Flow: pinned ZIP → XML tree and scoped indexes → selected source Rules →
recursive OVAL references → native Assessments → labeled miniature Rule/Benchmark
wrapper and projected Profiles → external validation/compiler/consumer checks.
No source IDs control an algorithm branch; they locate input nodes or allocate
stable native names. Source IDs, hashes and omitted content live in the trace.

`UnsupportedSource` is a `ValueError` with a diagnostic. A failed dependency
aborts the entire conversion. Discard a failed converter instance. Caches and
native declarations are explicit per-Assessment state; cached native values are
copied before use. Source trees are read-only after indexing in normal use.
Tests deliberately clone/mutate them for fault injection.

## Run and inspect

From repository root, in a disposable environment:

```bash
python -m venv /tmp/direct-v04-venv
/tmp/direct-v04-venv/bin/pip install PyYAML==6.0.3 jsonschema==4.25.1
export PYTHONPATH=tools
/tmp/direct-v04-venv/bin/python tools/v04_direct_converter.py \
  tests/fixtures/v04-direct-prototype/server2025-signed.zip \
  --sha256 2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0 \
  --rule xccdf_mil.disa.stig_rule_SV-278139r1182083_rule \
  --rule xccdf_mil.disa.stig_rule_SV-278080r1180946_rule \
  --output /tmp/direct-v04-output
/tmp/direct-v04-venv/bin/python tools/test_v04_direct_converter.py -v
```

Use a new output directory: existing output is never overwritten. Inspect
`authoring/direct-slice/assessments/*.yaml` beside `source-trace.json`.
JSON and YAML serialize the same native dictionaries; metrics are separate.
The subprocess test invokes the unchanged public validator on **each format**,
packs separate JSON/YAML ZIPs, runs the unchanged compiler CLI, and launches the
independent package consumer. It also checks exact program/source operands.

The fixture's [provenance](../../tests/fixtures/v04-direct-prototype/provenance.json)
pins the original repository/revision, ZIP and source Rule identities. The ZIP
is original data, not generated output; do not edit/re-sign it. Synthetic tests
are explicitly identified and do not increase original-source coverage.

## Safely change a conversion rule

First read the existing 0.4 mapping and pinned OVAL 5.12.3 declaration for the
affected entity. `CAPABILITIES` selects the small supported catalog;
`load_mappings` reads its **0.4** files. Selector/State field names, enum
crosswalks and acquisition defaults come from these mappings. Capability
additions require proof of their missing datatype/acquisition behavior; merely
adding a name to the tuple is not sufficient. Do not edit normative schemas or
production mappings as part of this spike.

**Worked change included in this implementation:** supporting integer OVAL
`operation="less than"` uses the already approved native `less_than` comparator.

1. Add `'less than': 'less_than'` to `COMPARISONS` (the resulting line is present).
2. In `test_documented_integer_comparator_extension_is_source_verified`, a
   controlled copy of the pinned Registry State compares integer 2 with this
   operation. The test requires independent original/native terms to agree and
   the unchanged compiler to accept the output. An unreviewed operation must fail.
3. Run the focused test, then the whole prototype module:

```bash
PYTHONPATH=tools python -m unittest \
  test_v04_direct_converter.DirectConverterAcceptance.test_documented_integer_comparator_extension_is_source_verified
PYTHONPATH=tools python tools/test_v04_direct_converter.py -v
```

Do not replace a failed comparison with schema-only acceptance. A new semantic
choice needs owner review. Existing tests deliberately retain incorrect
quantifiers, altered selectors/Variables, broken references and legacy grammar
as negative cases. The maintained regression command is
`python tools/run_current_tool_regressions.py`; its existing CI workflow supplies
the pinned Self-Assertion bindings/XSD link. Do not run the 65-source corpus.

## Semantics worth preserving

- Only an unambiguous default OVAL check, optionally duplicated as `automated`,
  is admitted. Named OCIL `manual` choices are recorded as omitted; they are
  **not** full Rule equivalence. Other selectors/systems and Profile refinements
  fail instead of being silently ignored.
- Constants become typed arrays; `var_check` remains at the consumer. Item,
  observed-field and expected-value quantifiers are separate.
- Comparator-free absence requires the exact source absence form. Empty string
  equality is not removed. `all_exist` remains blocked.
- Shared Objects preserve source identity, not payload deduplication. Set
  operand order and nesting are retained. OVAL Set Filters apply in order to
  each referenced operand **before** the operator. Direct leaf Filters stay on
  that acquisition. `filter_condition` renders the approved Filter leaf syntax;
  it does not traverse arbitrary records. Non-Boolean/collection evidence is
  never evaluated, erased or defaulted by the converter.

Unsupported: other Rules/capabilities/functions, cross-datatype Variable casts,
records, explicit acquisition
behaviors, Profile inheritance/refinement, CPE/platform execution, manual
execution, full policy metadata/scoring/remediation. This is not source-wide
XSD validation, signature verification, scanner acceptance, or a new
normalization admission. The source Set unit is an actual pinned Object subtree;
its added Filter/operator variants are controlled unit compositions, not extra
published Rule conversions.

Generated authoring/trace/metrics are regenerated by the CLI. Reproduce the
three cold/fifteen warm samples, three CLI emissions, public validation, paired
compilation and independent consumer evidence in a new directory:

```bash
PYTHONPATH=tools python tools/test_v04_direct_converter.py --measure /tmp/direct-v04-evidence
```

Read `results.json`, `json-validation.json`, `yaml-validation.json` and
`compile.json`; the actual generated bundle is under `compiled/`. Timings are
observations, not golden expectations. The engineering report distinguishes
these fresh measurements from the previous prototype's preserved evidence.
