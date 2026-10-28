# Maintaining the direct 0.4 experiment

This experiment inventories a complete Benchmark and emits a supported automated
subset, **not a production converter or complete Benchmark/policy migration**. Python 3.12 is used in CI. No model service is needed to run or edit
the code. The conversion and inventory modules are newly written; none imports the
previous prototype, a production renderer, a 0.3 module, or an intermediate IR.
The original signed fixture and unmodified public validators/compiler/proof
readers are reused as data and external gates, not as conversion algorithms.

## Files and contracts

| File | Responsibility / important entry points |
| --- | --- |
| [v04_direct_scap_source.py](../../tools/v04_direct_scap_source.py) | `SourceModel(path, expected_sha256)` verifies ZIP bytes/CRC, parses one complete XML member once, and indexes IDs/references per component. `automated_check` resolves checklist-local catalog references and rejects unsupported check choices. `rule_selected` projects ancestor/Profile selection. |
| [v04_direct_converter.py](../../tools/v04_direct_converter.py) | `AssessmentConverter.reference(id, kind)` is the single memoized recursive dependency visitor. `convert_object`, `set_expression`, `filter`, `convert_variable`, `predicate`, `convert_test`, and `criteria` produce current native dictionaries directly. `convert(source, rule_ids)` returns `(documents_by_relative_path, external_trace)` for a strict focused request. `convert_benchmark(source)` returns these plus complete coverage, isolating unsupported Rules. `main` emits JSON/YAML and metrics. |
| [v04_direct_inventory.py](../../tools/v04_direct_inventory.py) | `SourceInventory` indexes dependency edges once, follows unsupported closures too, discovers all checks/selections, and counts/digests original nodes. It does not lower content. |
| [v04_direct_scalar_behaviors.py](../../tools/v04_direct_scalar_behaviors.py) | Routes ordinary acquisition attributes from reviewed mappings; reads required/default/fixed attributes from original XSD once. Traversal and command errors retain separate shared handlers. |
| [verify_v04_direct_scope.py](../../tools/verify_v04_direct_scope.py) | `accept_source` is the shared verified-upgrade gate: original validity, source/native terms, compilation and independent package consumption. No lowering belongs here. |
| [audit_v04_direct_benchmark.py](../../tools/audit_v04_direct_benchmark.py) | Independently reconciles original checks/dependencies/Profiles, compares typed source terms, runs public package gates, verifies compiled operands and attaches proof levels. It cannot admit Rules. |
| [test_v04_direct_converter.py](../../tools/test_v04_direct_converter.py) | Eleven retained focused tests, controlled compositions, failures, public CLIs and compiled operands; imports independent `verify_original` from the audit module. |
| [test_v04_direct_benchmark.py](../../tools/test_v04_direct_benchmark.py) | Eight whole-inventory/admission/proof/public-gate regressions, including controlled faults and deterministic output. |

Flow: pinned ZIP → XML tree and scoped indexes → complete Rule inventory and
automatic admission (or strict focused selection) →
recursive OVAL references → native Assessments → labeled miniature Rule/Benchmark
wrapper and projected Profiles → external validation/compiler/consumer checks.
No source IDs control an algorithm branch; they locate input nodes or allocate
stable native names. Source IDs, hashes and omitted content live in the trace.

`UnsupportedSource` is a `ValueError` with a diagnostic. A failed dependency
aborts its Rule; a focused request fails entirely, while automatic admission
records the blocked Rule and continues. Discard a failed converter instance. Caches and
native declarations are explicit per-Assessment state; cached native values are
copied before use. Source trees are read-only after indexing in normal use.
Tests deliberately clone/mutate them for fault injection.

## Revised-schema integration (#251 / #255)

The committed schema baseline `d3132ae57` is authoritative. The converter enables
47 of the 51 mappings in the approved Independent/Linux/UNIX/Windows scope;
there are 100 mappings globally. Enabling a name does not mean every source
construct for that capability is implemented or executable.

`predicate` translates static enum collections value by value, preserving order,
duplicates and the consumer's `var_check` as `value_match`. Arrays and predicate
Variable references always emit their explicit source datatype, including the
implicit OVAL string type. `value_match`, observed `values_matching`, and Test
`items_satisfying` remain separate. Compact scalar strings retain their existing
form. A bare collector-parameter reference is typed by its parameter contract
and Variable declaration; it is not a comparison predicate.

`file.hash` uses the approved native `algorithm` Object selector and State field.
The complete domain is `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`.
Complement selection applies to that domain, rather than selecting one default
algorithm or generating extra Tests. One acquisition and its original Item
population remain intact. Static lists use the approved crosswalk; named runtime
Variables are supported when their dependency graph projects the same algorithm
domain, including Variable references and `unique` chains. The bijective rename
commutes with those operations. Arbitrary runtime strings/external inputs still
need an approved value-domain adapter; do not assume they already use native
spellings or invent a function to rewrite them.

The maintained `test_v04_filehash_acquisition_conflict` retains the schema-first
test identities and now verifies original Tests 305, 544 and 354, all six
algorithms/four quantifiers, duplicate values, original-source integrity, typed
runtime projection graphs, compilation, independent terms and negative mutations.
`test_v04_direct_typed_operands` revalidates all 39 Server 2025 user-rights Rules.
The [datatype correction receipt](../audit/v04-converter-explicit-datatype-corrections-20261027.json)
explains each of the 69 changed primary program hashes; all 1,010 proof identities
are retained. Values, quantifiers and dependency graphs are unchanged.

Use the read-only [acquisition review tool](../../tools/audit_v04_acquisition_parameters.py)
for the 15 Variable-capable parameters in shellcommand, SQL512, cmdlet and WMI:

```bash
PYTHONPATH=tools python tools/audit_v04_acquisition_parameters.py \
  --source-root ORIGINAL_OVAL_TEST_CONTENT --output /tmp/acquisition-review.json
```

It verifies the collection pin and records original declarations, Object IDs and
Variable edges. A one-value constant can become a single invocation input for
`all`, `at least one` or `only one`. Multiple constants and complement inputs
remain unsupported. Existing named runtime inputs retain their established
graph/operand proof scope; that is not independent proof of invocation
multiplicity or scanner behavior. Nondefault runtime quantifiers cannot be
silently discarded. Record members retain their existing `value_match` and
`selection_match`; original whole-record `var_ref` remains prohibited.

See the [integration handoff](../audit/v04-converter-revised-schemas-20261027.md)
for current coverage, remaining source/design obligations and exact verification.

## Shared specialized datatypes

[`v04_direct_datatypes.py`](../../tools/v04_direct_datatypes.py) owns supported
source/native type identities, lexical representation and comparison dispatch.
Special string-based datatypes retain their lexical text and select the existing
`version_*`, `rpm_evr_*`, `debian_evr_*`, binary/address and other approved typed
operators. Integer bitwise comparisons retain their distinct comparison semantics.
Do not infer package ordering from a capability name or use string ordering for
an explicitly typed version. Float conversion is still unsupported here.

The independent reader keeps its own frozen identities and rejects type/operator
conflicts without importing this conversion module. Run
`PYTHONPATH=tools python -m unittest test_v04_direct_special_datatypes -v` for
114 pinned original Tests, source/XSD checks, complete dependencies, native
validation, compilation, four-quantifier arrays/references and adversarial types.
The [current checkpoint](../audit/v04-converter-special-datatypes-20261028.md)
records 512 corpus term proofs and 1,012 primary Rule proofs. The preceding
schema integration section is its historical 438469880 checkpoint.

## Run and inspect

For fast cross-platform breadth measurement, use the
[complete pinned OVAL Test Content audit](../audit/v04-oval-test-corpus.md).
`audit_v04_oval_test_corpus.py` indexes standalone OVAL files and ZIP members,
follows each Test's complete dependency graph, and calls the existing visitor
for all approved non-macOS mappings as a diagnostic probe, alongside the unchanged
enabled-capability baseline. It does not add production support or admit Rules.
The full artifact separates conversion, schema, compiled operands and independent
source proof; unsupported platforms stay reference material. Run its twelve focused
tests with `PYTHONPATH=tools python -m unittest test_v04_oval_test_corpus -v`.

From repository root, in a disposable environment:

```bash
python -m venv /tmp/direct-v04-venv
/tmp/direct-v04-venv/bin/pip install PyYAML==6.0.3 jsonschema==4.25.1
source /tmp/direct-v04-venv/bin/activate
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
`--rule` may be repeated any positive number of times; one unsupported Rule fails
the focused request. There is no Rule-ID allowlist or two-Rule algorithm limit.
The tests invoke the unchanged public validator API for JSON (its directory CLI
discovers YAML only), assert six checked documents, use its CLI for YAML,
packs separate JSON/YAML ZIPs, runs the unchanged compiler CLI, and launches the
independent package consumer. It also checks exact program/source operands.

For a verified upgrade, add `--verify` to the focused command above, or use:

```bash
python tools/v04_direct_converter.py \
  tests/fixtures/v04-direct-prototype/server2025-signed.zip \
  --sha256 2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0 \
  --all-rules --verify --output /tmp/direct-verified-primary-subset
```

This is the existing converter's verified mode, not a production replacement or
complete policy migration. It validates original OVAL closure assertions and
deprecation, canonical authoring, independent typed terms, compiled operands and
the independent package consumer. Only `PROVED` closures enter
`primary-subset.scapng`; zero proved closures produce no package.
`acceptance.json` accounts for every original Rule, with checks, dependencies,
hashes and blockers (`NOT_SELECTED` for a focused request). `coverage.md` is its
human-readable view; `source-trace.json` retains provenance. Applicability remains
separately inventoried and unproved. Catalog failures are classified without
repair. `--verify` requires `--rule` or `--all-rules`. Source integrity, unknown
selections and existing output are fatal; blocked Rules remain isolated.

The fixture's [provenance](../../tests/fixtures/v04-direct-prototype/provenance.json)
pins the original repository/revision, ZIP and source Rule identities. The ZIP
is original data, not generated output; do not edit/re-sign it. Synthetic tests
are explicitly identified and do not increase original-source coverage.

## Safely change a conversion rule

The 2026-10-27 interim assignment separates converter work from the concurrent
capability-mapping/schema audit. Keep mappings, generated contracts, generators,
normative definitions, compiler/scanner implementations and 0.3 files unchanged.
The direct visitor now routes XML item-creation and traversal behaviors through
disjoint shared handlers. Independent proof reads file behaviors and nullable
filenames from frozen identity contracts; it does not call conversion helpers.

Unsupported cases are consolidated without admitting them:

```bash
PYTHONPATH=tools python tools/report_v04_conversion_gaps.py \
  --corpus /tmp/oval-corpus.json --original-root ORIGINAL_OVAL_TEST_CONTENT \
  --acceptance-root /tmp/direct-six --output /tmp/conversion-gaps.json
```

The report verifies the complete original collection pin, validates original
closures, and distinguishes implementation gaps, reviewed schema limitations,
Variable/collection limitations, unsupported operations, invalid/deprecated
original source, and external infrastructure failures. Schema rejection alone
does not establish a schema defect. Diagnostic-only conversions remain separate
from enabled capabilities and verified primary packages. Optional
`--external-failures` accepts an explicit JSON list of failures with `source`,
`message` and `evidence_url`; infrastructure failures never become source failures.

The [dependency register](../../tests/fixtures/v04-converter-schema-dependencies.json)
pins specific source counterexamples and the remaining integration queue. A
schema-dependent case is recorded and skipped while independent work continues.
Once the schema owner's new baseline is published, review its changed contracts
before implementing the follow-up assignment or refreshing proof fingerprints.

Ordinary capability activation lives in
[`v04_direct_capabilities.json`](../../tools/v04_direct_capabilities.json).
The generic visitor reads the existing version-local mapping; adding a capability
does not require adding a dispatch function. Admission still requires original
fixtures, independent source proof, current validation and compiled-operand checks.
The [scalar proof contracts](../../tests/fixtures/v04-scalar-proof-contracts.json)
freeze reviewed source/native field identities and mapping hashes independently of
conversion. A mapping change must be reviewed against original XSD/XML before
refreshing this evidence; do not automatically bless a changed hash.

For example, to extend an ordinary scalar capability, add its approved mapping
identity to activation data and its independently reviewed identity recipe to
the proof contracts. Pin original Self-Assertion XML and positive/negative cases
as in `test_v04_direct_scalar_batch.py`. If existing generic handlers cannot
preserve the source construct, leave it blocked and implement a shared handler
with source-backed boundary tests. No Rule-ID branch is appropriate.

`verify_v04_direct_scope.py` runs all six pinned original primary closures,
records every unsupported Rule, and packages only independently proved output.
Its [proof floor](../../tests/fixtures/v04-six-primary-proof-floor.json) retains
1,012 Rule proofs and exact compiled-program hashes; losing a proof or changing
a program fails the workflow. Additional proved Rules are allowed. Update this
fixture only after examining an independently verified intentional change.
Applicability remains a separately recorded obligation, not implied by this floor.
Run `PYTHONPATH=tools python -m unittest test_v04_direct_scalar_batch
test_v04_direct_unix_password test_v04_direct_scope -v` for the small batch checks;
the six-source workflow retains complete generated evidence and packages.

The next ordinary batch adds Linux listening servers, SELinux Boolean/status,
systemd dependencies, UNIX interface/shadow/symlink/uname and Windows group/user
SID acquisitions through activation/proof data only. Its ten original files are
under `tests/fixtures/v04-direct-scalars-expanded`; `provenance.json` records the
upstream paths, revision and checksums. The files are unchanged source inputs.
Run `PYTHONPATH=tools python -m unittest test_v04_direct_scalar_expansion -v`
for original-XSD/Schematron validation, 46 source-Test conversions, compiled
operands, independent terms and negative mutations. Additional UNIX fixtures
in other upstream platform directories remain in the complete corpus audit;
this does not add a macOS capability or execute a collector.

First read the existing 0.4 mapping and pinned OVAL 5.12.3 declaration for the
affected entity. `tools/v04_direct_capabilities.json` selects the supported catalog;
`load_mappings` reads its **0.4** files. Selector/State field names, enum
crosswalks and acquisition defaults come from these mappings. Capability
additions require proof of their missing datatype/acquisition behavior; merely
adding a name to the activation data is not sufficient. Do not edit normative schemas or
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
- Variable Test sources and multivalue function operands keep constants as named
  typed collections. `named_variable` materializes the existing constant grammar;
  `variable.value` removes only an unmodified `variable_object/var_ref` indirection.
  Text references participate in inventory, cycle detection and independent
  original-source closure. Separate State identity predicates and Variable-source
  Sets/Filters remain blocked. No values or status outcomes are evaluated.
- Single-collection `merge` and `unique` preserve their operand graph; merge
  delimiter/sort/order defaults are explicit. Multiple components remain blocked
  rather than inventing a collection-union expression. Run
  `PYTHONPATH=tools python -m unittest test_v04_direct_variables -v` for 21
  original cases plus controlled negative/aggregation boundaries. The nine
  original files and hashes live in `tests/fixtures/v04-direct-variables`.
- UNIX file acquisition preserves nil filenames as `name: null`, filesystem scope,
  permission-field identities and downward recursion. FileBehaviors default
  recursion to none; depth/direction apply only to equality directory selectors,
  per the original XSD. Full filepath and non-equality path acquisition retain
  provenance without invented recursion. Upward recursion stays blocked. Run
  `test_v04_direct_file_traversal` for 16 original file/Set Tests plus controlled
  projection/recursion mutants.
- Ordinary scalar behaviors use mapping routes and original XSD defaults. RPM
  `filepaths=false` becomes `include_file_paths: false`, separately from matching.
  The independent scalar contract freezes this identity/default. Run
  `test_v04_direct_scalar_behaviors` for three original RPM Tests and negative
  Boolean, namespace, duplicate and unknown-attribute boundaries.
- Comparator-free absence requires the exact source absence form. Empty string
  equality is not removed. `all_exist` remains blocked.
- Shared Objects preserve source identity, not payload deduplication. Set
  operand order and nesting are retained. OVAL Set Filters apply in order to
  each referenced operand **before** the operator. Direct leaf Filters stay on
  that acquisition. `filter_condition` renders the approved Filter leaf syntax;
  it does not traverse arbitrary records. Non-Boolean/collection evidence is
  never evaluated, erased or defaulted by the converter.

Unsupported: other capabilities/functions, cross-datatype Variable casts,
nested records and record-level Variables, unimplemented acquisition
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
`compile.json` for that focused measurement; the actual generated bundle is under `compiled/`. Timings are
observations, not golden expectations. The engineering report distinguishes
these fresh measurements from the previous prototype's preserved evidence.

## Complete inventory and automatic admission

Use the same pinned source/SHA above with **one** mode instead of `--rule`:

```bash
python tools/v04_direct_converter.py SOURCE.zip --sha256 SHA256 \
  --inventory-only --output /tmp/direct-inventory
python tools/v04_direct_converter.py SOURCE.zip --sha256 SHA256 \
  --all-rules --output /tmp/direct-supported-subset
```

`SOURCE.zip` and `SHA256` stand for the exact fixture path/hash in the runnable
example above, not new source downloads. Inventory mode emits no authoring.
Automatic mode inventories every original Rule first, then uses the same generic
recursive visitor for every unambiguous automated closure. `CAPABILITIES` is an
implemented/tested support boundary; merely adding a mapping file never admits
its capability. The full mapping catalog only supplies descriptive inventory
names. Mixed-capability closures must satisfy every dependency.

`coverage.json` and `coverage.md` are separate from executable authoring. Each
original Rule has checks/selectors, source member/hash/fragment, all recursive
OVAL IDs/hashes/reference edges, needed capabilities/constructs, source default
and Profile selections, omissions, status, artifact paths and proof level.
`summary` conserves the source denominator. Only `converted` Rules have native
Rule/Assessment documents; `blocked` Rules have primary and contextual blockers.
A zero-conversion run emits coverage/trace only, not an invalid empty package.
All output titles identify a subset. Manual alternatives, platform execution,
policy metadata/scoring/remediation remain explicitly outside the claim.

Admission uses unchanged strict authoring/capability validation. A successful
conversion is **`authoring_validated`**, not source-proved. Expected per-Rule
failures are isolated; corrupt ZIP/hash/index/global invariants and unexpected
programming exceptions abort the run. Blocked closures get cached per-node
probes plus independent entity/function/filter/quantifier diagnostics; unknown
capability internals are not interpreted. A future implementation may expose
additional blockers, so the manifest does not claim an exhaustive unsupported
standards conformance diagnosis. There is no fallback or approximate lowering.

The independent audit (same minimal venv) measures three fresh public CLI runs
per mode and verifies serialized content/paired compilation/consumer/operands:

```bash
python tools/audit_v04_direct_benchmark.py \
  tests/fixtures/v04-direct-prototype/server2025-signed.zip \
  --sha256 2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0 \
  --rule xccdf_mil.disa.stig_rule_SV-278139r1182083_rule \
  --rule xccdf_mil.disa.stig_rule_SV-278080r1180946_rule \
  --output /tmp/direct-whole-benchmark-evidence
python tools/test_v04_direct_benchmark.py -v
```

The `--rule` arguments here select only the **focused comparison workload**;
automatic admission always discovers the whole Benchmark. Output `evidence.json`
contains timings, commands, hashes, public gate results and individual proofs.
The audit's separate root `coverage.json/md` attaches `source_proved` only after
original typed-term and exact compiled-operand checks; `compiled_unproved` retains
explicit unsupported proof obligations. Producer coverage remains unchanged.
Current architecture-acceptance checkpoint for this pin: 291 original Rules =
249 converted + 42 blocked, all 249 source-proved. The earlier 84/207 and 81/3
results, plus the 87/204 architecture and 130/161 authoring checkpoints, remain preserved in their dated
audit packets. Generic common Set proof
now covers the three original Registry Set cases; integer ordered comparisons
admit three additional Rules. These are not updates to the packaged
883-Assessment ledger. Example coverage row (abridged):

```json
{"source_rule":"xccdf_mil.disa.stig_rule_SV-278139r1182083_rule",
 "status":"converted", "proof_level":"source_proved",
 "needed_capabilities":["independent.shellcommand","windows.registry"],
 "blockers":[]}
```

To add a capability in a separately authorized phase: identify exact blocked
source obligations; inspect the version-local mapping and original OVAL source;
implement only missing generic behavior, with negative tests and independent
operand proofs; then extend `CAPABILITIES` and rerun admission/audit. Never add a
Rule ID or source hash branch. The small comparator example above is the current
safe extension exercise; this phase adds no capability family or normalization.
Generated coverage/evidence is regenerated by this audit command; do not edit
proof counts by hand. `test_v04_direct_benchmark.py` also covers complete original
inventory, deterministic runs, controlled zero/one/many/mixed admission,
missing/cyclic references, Profile/semantic failures and manifest/program mutants.

## Engineering execution and validation profiling

[Owner execution directive](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
authorizes bounded, source-verified increments within the approved grammar;
production promotion remains separate. The tracked engineering ledger records
base/result SHAs, exact proof/compiled/blocked counts, tests, CI and next work.
The new ordered-comparison extension admits only explicit OVAL `datatype="int"`
for greater-than, greater-or-equal and less-or-equal; string/Boolean ordering is
not inferred. Original-source parity and inclusive-boundary mutants are in
`test_v04_direct_acceptance.py`.

The common Set reader now uses the same typed Set traversal for every known
collector family, with family checks and source operator/default/operand order
retained. Tests read all 108 collected-object flag combinations directly from
the pinned OVAL 5.12.3 XSD charts and compare the existing reference combiner.
This is source/contract verification, not scanner implementation or execution.

To reproduce profiling after a public `--all-rules` emission:

```bash
python tools/profile_v04_direct_validation.py \
  /tmp/direct-supported-subset/authoring --samples 1 \
  --output /tmp/direct-validation-profile.json
python tools/test_v04_direct_acceptance.py -v
```

Profiled and unprofiled timings are separated. Complete public schema/Object
capability validation runs on every pass. No schema pruning, assumed-family fast
path, validation bypass or claimed performance optimization was introduced.
The measured hotspot is repeated JSON-Schema branching/`unevaluatedProperties`,
not source parsing or mapping IO. Keep future optimization proposals distinct
from proof/admission changes and require unchanged positive/negative outcomes.

## Singleton-system capability sources

The audit-policy increment uses the existing 0.4 contract
`native.test_source.kind: none`. Its original OVAL Objects have no acquisition
entities: the source is the current system, not a parameterized resource.
`convert_object` requires the source Object to be empty; `convert_test` omits
native `object` entirely. Source Object IDs/versions/hashes remain in the
external dependency trace. Source selectors, Sets, Filters and Variable
`object_component` acquisition are rejected for this source kind; no placeholder
Object or new native acquisition syntax is invented.

The first singleton increment enabled `windows.auditeventpolicysubcategories`. Its 43 complete
original closures are independently verified. The independent reader obtains
field/value/deprecation boundaries from the original pinned Windows OVAL XSD,
not the converter's mapping. Literal enum constraints are checked after any
approved value crosswalk; dynamic enum computations outside this tested bound
remain unsupported. Unknown/deprecated fields, invalid original enums/types,
changed native operands and meaningless native Objects are negative regressions.

```bash
python tools/test_v04_direct_audit_policy.py -v
```

This authorizes neither other singleton families nor production promotion.
The evidence-ranked engineering ledger names the next bounded source census;
whole dependency closure admission and independent proof remain required.

## Local Objects and readable YAML

`SourceModel.object_uses(component, root_id, kind)` walks one Assessment's actual
dependency graph before conversion. Each reachable Test, Object, State or Variable
is visited once; its outgoing acquisition edges are counted, including Set operands,
Filter-State Variables and Variable Object extractions. Repeated references to one
Test/Variable do not duplicate its acquisition. A source Object identity used once
is private/inline; multiple uses share a named Object. Counts elsewhere in the
Benchmark do not participate. Equal selector values never merge distinct source
IDs. Cycles and unsupported dependencies still fail closed. Original IDs, hashes
and scoped reference edges remain in the external trace/coverage, not native IDs.

Private Test Objects inherit capability and omit redundant capability/title.
Variable Objects retain their required capability. Shared Objects retain stable
IDs, capability and a meaningful source comment; if the comment is generic, a
title describes literal source selector facts rather than guessing purpose.
System-source `kind: none` still omits Object and blocks invented acquisition.

[v04_direct_yaml.py](../../tools/v04_direct_yaml.py) is the small presentation
layer, separate from source conversion. It builds serialization-only flow-mapping
hints and uses PyYAML's safe scalar handling. Simple flat Registry selector Objects
are single-line; Sets, Filters, computed selectors and traversal remain multiline.
`require` stays block-style and Boolean sequences retain their complete subtrees.
JSON uses the ordinary native dictionary. No YAML text rewriting is performed.

To change formatting, edit `compact_registry_object`/`presentation`, then run the
style tests: node flow-style and line-boundary checks establish presentation,
while parsed YAML/JSON equality checks structure and ambiguous strings/paths/regex
scalar types. Do not change `predicate` or remove quantifiers to shorten YAML.
Capability changes still follow the source/mapping/independent-proof procedure
above; presentation policy cannot authorize a new acquisition or semantic default.

```bash
PYTHONPATH=tools python tools/test_v04_direct_authoring_style.py -v
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --output /tmp/direct-authoring-examples
```

The second command regenerates six small actual output examples and their JSON
peers/trace manifest, after proving and compiling the supported subset and the
selected wrapper. Use a new output directory. The tracked
[example navigation](../examples/direct-v04/README.md) is generated with that
command, not maintained by hand. For a practical presentation-only edit, exclude
regex selectors from `compact_registry_object`, add a source-backed regex case to
the style test and verify it becomes multiline while parsed structure and original
proof remain unchanged. Whole-subset original/compiled negative mutations remain
in `test_v04_direct_benchmark`, `test_v04_direct_acceptance` and the audit-policy tests.

## Closed Registry hive selector relation

The bounded hive increment admits literal Registry acquisition selectors using
original `case insensitive equals`. The Object and Item domains in original OVAL
5.12.3 contain six canonical hives plus an empty Variable/error placeholder.
Across all 49 pairs, equality and case-insensitive equality have the same relation;
the six real hives map one-to-one to the approved native enum. The producer uses
the versioned capability crosswalk and checks domain case distinction. The
independent reader separately reads/hashes the original Object/Item XSD domains,
checks every pair, and derives native hive names from original tokens.

Only nonempty literal acquisition operands are admitted. Empty/unknown/lowercase
source tokens, dynamic hive operands, non-string datatypes, pattern selectors and
State-level enum comparator changes remain blocked. Other string selector
comparators (for example, Registry keys) retain their original operation. Source
Object IDs, original selector attributes/value and the reason remain in external
`selector_equivalences`; they are also independently recorded in each proof.
No Test matching, error/incomplete/unknown evidence, Variable expansion or
`all_exist` behavior changes. Native output equals the equivalent original
`equals` spelling, including all collection and evaluation boundaries.

```bash
PYTHONPATH=tools python tools/test_v04_direct_registry_hive.py -v
```

Its five tests cover all 19 newly supported original Rules, all six controlled
literal hives, the 49-pair domain proof, exact compilation and negative mutants.
The browsable authoring examples remain pinned to their manifest's converter
commit; run regeneration from that commit to reproduce their historical 130-Rule
snapshot. Current `main` regeneration reports the larger supported subset.

## Windows user-rights capability

`windows.userright` uses the existing generic selector, field, constant-Variable,
Filter and Set visitors. Known enum selectors retain `equals` and explicit
`value_match` for arrays; computed enum values without proved membership remain
unsupported. Original trustee names/SIDs retain their string comparators and
field quantifiers. The independent reader derives allowed fields and rights from
original OVAL XSD, without importing the producer's capability mapping.

The first user-rights checkpoint independently proved/compiled 34 of 39 original
candidate closures. Five stayed atomically blocked by WMI records. The next
WMI increment discharges those dependencies, so all 39 now prove/compile. The
restricted-catalog regression still demonstrates that removing WMI support
blocks every mixed closure instead of publishing an incomplete substitute.

The original orphaned-SID check uses 45 constant rights, an include Filter and
`none_exist`. Its omitted `var_check` means **all**, preserved as `value_match:
every`; changing it to `one_or_more` fails source proof. This may differ from the
source author's apparent intent: one scalar right cannot equal all 45 distinct
values under complete evidence. Preserve the source, flag the concern and obtain
explicit owner authorization before any source-specific repair. Error/incomplete
evidence must not be described as successful complete collection.

```bash
PYTHONPATH=tools python tools/test_v04_direct_userright.py -v
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability windows.userright --output /tmp/direct-userright-examples
```

The example selection controls inspection only. Whole-source admission still
walks every dependency and runs strict validation. Old example packets retain
their pinned converter SHA; new generation records the current SHA and counts.

## WMI records and named acquisition parameters

`record_predicate` maps original `EntityStateRecordType` to the approved nested
`record` wrapper: per-field comparisons stay inside one record, then
`records_matching` combines records, and Test `items_satisfying` combines Items.
It preserves original field names and explicit/implicit datatypes. Numeric-looking
source strings remain strings; source integers become explicit `integer` values.
Missing required record members remain errors under the existing record contract.
Record comparators other than equality, duplicate/invalid source field names,
record-level Variables, unsupported record absence and masking stay blocked.

The original OVAL field-name restriction applies to imported XML only. The
converter does not lowercase or rename an invalid source field to make it pass,
and does not impose that restriction on native human authoring.

WMI namespace/WQL are acquisition parameters, not comparison selectors. They
use the existing parameter visitor. When an acquisition is genuinely shared,
`object_title` now also describes source acquisition-parameter facts, giving an
otherwise untitled shared query a meaningful title and stable native reference.
It never invents a query purpose or adds a title to a private Object.

```bash
PYTHONPATH=tools python tools/test_v04_direct_wmi.py -v
```

The first WMI increment proves/compiles 18 original closures. Cmdlet support
adds two complete mixed closures, bringing current WMI coverage to 20/26; six
still require unsupported legacy behavior or unapproved `all_exist`. The
five WMI-dependent user-rights closures are included in the 18. These counts
overlap by capability and are not added to each other as independent Rules.


## Password and lockout policies

The two versioned mappings authorize `test_source.kind: none`; original OVAL
Objects likewise describe the system as a whole and have no acquisition fields.
`v04_direct_system_policy.policy_entity` checks the approved typed field contract
and requires the original explicit `datatype` attributes: `EntityStateIntType`
and `EntityStateBoolType` declare `use="required"` with fixed values, not omission
defaults. It never edits original source nodes or guesses types from spelling. The independent proof reader separately derives
field types and literal restrictions from original OVAL XSD, not this helper or
the native mapping. Omitted `var_check` remains `all`/`value_match: every`.

Literal `max_passwd_age`, `force_logoff` and `lockout_duration` must be nonnegative,
as required by the original embedded Schematron. Variable-supplied values retain
their Variable and comparison semantics; conversion does not evaluate them or
turn unknown/error evidence into complete success. No additional range or unit
normalization is invented. Unknown fields/types, invented selectors/Sets/Filters,
Variable acquisitions from a singleton and dummy native Objects fail closed.
Comparator-bearing or typed field absence remains outside this bounded proof.

```bash
PYTHONPATH=tools python tools/test_v04_direct_system_policy.py -v
```

All seven original password-policy and three lockout-policy closures prove and
compile. Controlled source derivatives additionally exercise
constant-Variable quantifiers and rejected datatype omissions; they are regression evidence, not extra coverage.
To extend these contracts, inspect the original typed field and any Schematron
restriction, update the small source adapter, and add both a source-derived
positive and an independently rejected operand/quantifier mutation. Do not
broaden `kind: none` to capabilities whose approved contract requires an Object.


## Windows services

`windows.service` reuses the generic selector, State, Variable, Set and Filter
visitors. The two original Rules retain different service-name comparisons:
`equals` and `case_insensitive_equals` are never merged. Start/current-state
constants retain their exact original API names, without an enum crosswalk.
The independent reader obtains service fields and enum domains directly from
original OVAL XSD and checks native flat acquisition/require terms separately.
Unknown or computed enum membership remains blocked; typed non-string fields
need their required explicit original datatype attributes.

```bash
PYTHONPATH=tools python tools/test_v04_direct_service.py -v
```

Four focused tests cover both actual closures, exact public validation and
compilation, selector/enum/quantifier mutants, invalid source fields and a
controlled relative-COMPLEMENT Set whose include Filter applies to each operand
before the operator. Repeated acquisition identity remains genuinely shared.
Controlled derivatives establish reusable construct behavior, not extra original
Rule coverage. Source proof and compilation do not establish scanner execution.


## Independent text-file acquisition

`independent.textfilecontent54` reuses generic flat selectors, field requirements
and dependency visitors. `v04_direct_file_behaviors.file_behaviors` converts the
bounded nonrecursive acquisition parameters independently of State comparisons:
original optional defaults are `ignore_case: false`, `multiline: true`,
`singleline: false`, `item_creation: all_object_elements_fullfilled` and
filesystem scope `all`. Explicit flags override defaults. Original `defined`
filesystem scope maps to the approved native `same`; other scopes retain their
names. Item creation remains a collection boundary, never a field comparison.

Unknown, duplicate or nonempty behaviors, explicit Windows-view behavior and
traversal attributes fail closed. Do not silently discard them or widen this
module's contract without original-source positives and negative mutations.
The independent reader separately checks original attributes/defaults and typed
terms; it does not import the new helper. Original patterns, backslashes,
instances, capture datatypes and State Boolean structure remain exact.

```bash
PYTHONPATH=tools python tools/test_v04_direct_textfile.py -v
```

Five tests cover all seven actual OpenSSH closures, YAML/JSON structure equality,
all eight Boolean-flag combinations, both item-creation modes, three filesystem
scopes, invalid attributes and semantic mutations. Controlled derivatives add no
original Rule coverage. The compiler preserves patterns and parameters; scanner
execution or regex-engine conformance is not claimed. Follow the public pipeline
above to regenerate the complete supported subset; authoring remains inline by
default and complex patterns remain readable multiline Objects.


## Windows file effective rights

`windows.fileeffectiverights53` uses the existing selector, State, Variable, Set
and Filter visitors. Leaf file acquisitions materialize original filesystem scope
`all`, including full paths; Set wrappers leave scope on each operand. The bounded
source contract supports full-path/SID and directory/name/SID acquisition. Names
and path comparisons retain their source operations. Nilled selectors, traversal
and explicit group/view behaviors remain unsupported rather than discarded.

Original omitted group-selection behavior includes the selected group SID and
does not expand its members (`include_group=true`, `resolve_group=false`). This
matches the approved native direct-SID acquisition contract; no implicit group
membership traversal is invented. The independent reader derives source State
fields/types and group defaults from original XSD without importing producer
mappings. Boolean State fields require explicit original `datatype="boolean"`;
omission is rejected, never inferred from spelling or silently defaulted.

```bash
PYTHONPATH=tools python tools/test_v04_direct_file_rights.py -v
```

Five tests cover all eight actual closures, both path forms, positive/negative
permission values, schema and YAML/JSON checks, default-exclude SID Filters,
Variable matching, original Item cardinalities, invalid source types and group
expansion, and a controlled two-path relative complement with ordered Filters on
each operand. Swapping complement operands fails independent proof. Controlled
derivatives are not extra original coverage. These are graph/operand/contract
proofs, not Windows access-check execution or scanner parity.


## Shell collection error controls

`v04_direct_command_behaviors.command_behaviors` preserves the approved Boolean
acquisition parameters `error_if_exit_status_not_0` and `error_if_stderr_exists`.
Original `ShellCommandBehaviors` declares both optional with default false.
Explicit true requests collection-error evidence, not a failed ordinary matching
condition. Each acquisition keeps its own flags; a neighboring default command
must not inherit true. Script/shell/pattern strings remain unchanged and are never
executed by conversion or these tests.

The common Object visitor calls the helper for inline, shared, Variable and Set
acquisitions. Unknown, duplicate, foreign or nonempty behavior nodes and invalid
Boolean lexical values fail closed. The independent reader separately reads the
original attributes; it neither imports the helper nor changes the original XML.
Existing error/incomplete/not-collected evidence cannot become complete success.

```bash
PYTHONPATH=tools python tools/test_v04_direct_command_behaviors.py -v
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability independent.shellcommand --output /tmp/direct-command-examples
```

Four tests cover ten actual closures, required native parameters, original
optional/default declarations, all four flag combinations, changed/deleted flags,
incorrect matching substitutions, collection evidence guards and invalid XML.
The sample helper also selects an actual true-error-flag Assessment by emitted
structure. Example selection never controls Rule admission. This preserves a
collection contract; it is not a shell runner or scanner implementation.


## Cmdlet invocation records and null constraints

`v04_direct_cmdlet_inputs.cmdlet_input` translates the approved collection inputs.
Source `xsi:nil=true` becomes native null only for a nullable parameter, preserving
unconstrained module identity/version and absent invocation/select records. It
never turns null into an empty string or an invented Object. Scalar collector
inputs remain equality parameters. Read-only verb enums must be known literals;
computed enum membership remains blocked.

Input records use `fields` with explicit `selection_match`, separately from
expected-value `value_match` and Test/State `values_found`/`values_matching`.
Source entity_check/var_check defaults remain all/every in their separate scopes.
Numeric-looking strings such as Select-Object first `"100"` stay strings. Original
nil/record/type/operator/name constraints, field uniqueness and lowercase source
names are checked without restricting native human authoring to lowercase.
Unsupported wildcard selection, masks, parent record Variables and malformed
inputs fail closed. Record result requirements reuse the existing structured
record visitor; acquisition records are never flattened into strings.

```bash
PYTHONPATH=tools python tools/test_v04_direct_cmdlet.py -v
```

Six of seven actual cmdlet closures prove and compile, including two WMI-dependent
Rules. Five tests cover actual input/result graphs, nulls, YAML/JSON, independent
selection/value matching, invalid input records, wildcard/name/type errors and
native operand mutations. The WMI suite retains its original 18/8 restricted-
catalog boundary; the cmdlet and full-benchmark suites verify current expansion.

The capability-specific Object `select` parameter is an approved input record,
not the forbidden generic select wrapper. Authoring statistics now recognize it
at typed cmdlet Object sites, consistent with the unchanged canonical Object
validator. A legacy selector-wrapper shape still fails schema validation and is
reported as obsolete. No validator or approved grammar is weakened. Cmdlets are
represented and compiled; no PowerShell command is executed by these tests.


## Remaining approved Windows primitives

The current catalog includes `windows.ntuser`, `windows.appcmd`,
`windows.appcmdlistconfig` and `independent.environmentvariable58`. They use the
same recursive Object/Variable/Set/Filter visitor; no Rule-ID switches exist.
NTUSER materializes original `include_default=false` and
`item_creation=key_and_name_exist`, preserving ordered exclusions. Source registry
type labels retain their approved native crosswalk. IIS result `"false"` remains
a string, not an inferred Boolean.

Nullable selectors follow the versioned mapping. The original environment PID
`xsi:nil=true` becomes native null selecting the Assessment tool's running process,
not PID zero or an unscoped system environment. Source variable components with
exactly one complete string constant can be folded into a typed scalar literal;
multi-valued constants and cross-datatype cases still fail closed. Original
constants and their identities remain in dependency provenance. Shell acquisition
Filters remain on the original collected-object boundary, including Variable
acquisitions; none are pushed into Test matching or reordered.

Case-insensitive inequality retains the approved `case_insensitive_not_equal`
operator and original strings. It is neither rewritten as case-sensitive inequality
nor implemented by changing string case. Non-string source operands fail closed.

```bash
PYTHONPATH=tools python tools/test_v04_direct_remaining_primitives.py -v
```

Seven tests cover five actual complete closures, source optional defaults,
current-process null PID, singleton/multi-value boundaries, NTUSER types/exclusions,
IIS Filters/function order and case-insensitive inequality. A separate original
source counterexample (SV-278008) combines pattern-matched paths with recursion
attributes forbidden by original OVAL Schematron. It remains blocked; removing
those attributes or weakening the native traversal guard is not an implementation
fix. Explicit source normalization needs owner approval.

Nil input types retain original source requirements: integer PID and module version
require explicit datatypes; nil cmdlet records require `datatype: record` under
original Schematron. SV-278031 omits that record attribute and is now blocked,
correcting the earlier seven-candidate admission. A controlled explicitly typed
derivative is tested but does not count as original coverage. See the
[source counterexample](../audit/v04-source-invalid-cmdlet-nil.json).

### Original check denominators

All 30 Rules reported as competing check selections in this pin are OCIL-only;
they contain no original automated OVAL check. There are 261 OVAL-bearing Rules,
of which 249 currently prove. The 291-Rule denominator still matters for total
Benchmark coverage. Neither denominator establishes full policy equivalence.
Reproduce the original-source census independently of the converter:

```bash
python - <<'PY'
import xml.etree.ElementTree as ET
from zipfile import ZipFile
with ZipFile('tests/fixtures/v04-direct-prototype/server2025-signed.zip') as source:
    member, = (name for name in source.namelist() if name.endswith('.xml'))
    root = ET.fromstring(source.read(member))
x = '{http://checklists.nist.gov/xccdf/1.2}'
benchmark, = (b for b in root.iter(x + 'Benchmark')
              if b.get('id') == 'xccdf_mil.disa.stig_benchmark_MS_Windows_Server_2025_STIG')
rules = list(benchmark.iter(x + 'Rule'))
oval = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
automated = sum(any(c.get('system') == oval for c in r.findall(x + 'check')) for r in rules)
print({'rules': len(rules), 'oval_bearing': automated, 'no_oval': len(rules) - automated})
PY
```

The example publisher's `--capability` filter selects consuming Test capabilities.
It does not select capabilities acquired only inside Variables. The IIS appcmd
Variable closure is proved and compiled in the audit evidence; use
`windows.appcmdlistconfig` for the published IIS configuration representative.
This selection limitation changes no converter admission or dependency processing.

## Schema changes and converter maintenance

The approved 0.4 native schemas define the output contract. Reviewed source
mappings define correspondence; original OVAL XSD and embedded Schematron define
the input contract. A missing converter feature or mapping is not permission to
alter the native language or invent a source normalization.

Ordinary field changes should update schema/mapping data and fixtures, not add a
capability-specific Python branch. The generic converter already reads selector
and State-field maps at runtime; State fields become structured inline `require`.
New datatypes, operators or acquisition semantics still require a shared handler
and independent source proof before admission.

The [schema/converter synchronization workflow](../../.github/workflows/v04-converter-schema-sync.yml)
runs for 0.4 schema/mapping changes, original pinned OVAL schema changes and changes
to its generator/checker. It refreshes **data**, validates canonical target paths,
tests an ordinary field refresh, and runs pinned cmdlet/IIS/NTUSER source checks.
Its `scap-ng-040-converter-contracts` artifact contains the current normative and
generated schemas, field descriptors, fingerprints and unresolved source routes:

```bash
PYTHONPATH=tools python tools/v04_converter_contracts.py --output /tmp/v04-converter-contracts.json
PYTHONPATH=tools python -m unittest -v test_v04_converter_contracts test_v04_direct_cmdlet test_v04_direct_remaining_primitives
```

`v04_converter_contracts.contract` validates one mapping against the maintained
public native generator. `snapshot` assembles deterministic data for the current
catalog. No generated Python, new conversion IR, bot branch or automatic semantic
decision is involved. A bad target or obsolete wrapper path fails the check and
retains a review artifact. Missing correspondence is reported, not guessed: the
schema owner added the `file.hash` acquisition selector route in `d3132ae`;
[its source-backed review packet](../audit/v04-filehash-acquisition-conflict.md)
records the correction. Converter integration remains deferred to the follow-up
assignment; a mapping refresh does not automatically enable support.
This process does not enable additional capabilities or replace the full
mandatory/source-proof gates. It does not regenerate the six-STIG corpus.

Current metadata paths refer to flat Objects, such as `object.command` and
`object.name`. The genuine cmdlet input is `object.select`, a nullable structured
record; it must remain supported. Generic acquisition wrappers remain invalid.
Regression tests validate both sides of this distinction.

The public 0.4 schema generator still adapts the preceding generator internally;
that legacy dependency is recorded technical debt, not a new direct-conversion
stage. Removing it requires contract-parity verification, not another overlay or
wholesale converter rewrite. Prefer shared XSD/Schematron validation and small
construct handlers over additional capability-name branches. Profile validation
before optimizing source parsing: the recorded 249-Rule checkpoint spent 0.16 s
lowering versus 28.85 s validating, excluding authoring serialization. That single
workload does not establish asymptotic scalability or a production speedup.

## Native contract generation

Current generation uses version-neutral `v04_capability_source.py`, direct native
`v04_capability_native.py` and `generate_capability_schema_v04.py`. It constructs
no older grammar and performs no wrapper flattening or version-string rewriting.
The [native generator report](../audit/v04-native-generator.md) documents field
refresh, source kinds, the full parity fixture and focused tests. Genuine cmdlet
`select` remains metadata-defined; generic acquisition wrappers remain invalid.
