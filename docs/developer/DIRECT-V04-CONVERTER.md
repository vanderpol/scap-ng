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

## Run and inspect

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

Unsupported: other capabilities/functions, cross-datatype Variable casts,
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
220 converted + 71 blocked, all 220 source-proved. The earlier 84/207 and 81/3
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

All 18 supported original WMI closures prove and compile; eight remain blocked
by other unsupported capabilities or unapproved `all_exist` semantics. The
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
