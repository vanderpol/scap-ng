# Bounded independent source validation — 2026-10-30

Workstream [#251](https://github.com/vanderpol/scap-ng/issues/251), semantic review
[#255](https://github.com/vanderpol/scap-ng/issues/255). Baseline main:
`b450d150f25d92a9391b1fbb192e4c9f064f04dc` (maintained CI green).
This is independent validation, not authoring modernization or a new library.

## Scope and results

Eleven fixed Rule closures from six pinned NIWC-distributed archives at
`niwc-atlantic/scap-content-library@8c8e5dff860af6b1290ee9273a282db24278f8d5`.
Original OVAL node namespaces identify the reported namespace; the distributor and XCCDF
Rule namespace are not substitutes for that identity. Namespace attribution does
not independently authenticate who authored or modified the distributed node. All archive/member hashes
and every sliced dependency hash rejoin the pinned originals. Full original
component XSD/Schematron observations were replayed, then filtered to each exact
Rule closure, not inferred from a whole-file failure count.

| Rules | Capability coverage | Outcome |
| --- | --- | --- |
| SV-214228, SV-214251 | independent.shellcommand; nested concat/regex_capture/unique/merge and dependent Objects | Original valid; unchanged typed collection/comparison terms PROVED |
| SV-215838 | iosxe.global → count → integer Variable → variable.value; at least two NTP server values | Original valid; unchanged typed terms PROVED with new independent count reader |
| SV-257851 | linux.mount; field matching/cardinality and original mount regex | Existing frozen proof reproduced |
| SV-278021, SV-278023, SV-278101, SV-278131 | windows.wmi.query / windows.registry; mixed Test boundaries | Original valid; all_exist remains UNVERIFIABLE/UNSUPPORTED |
| SV-215833 | iosxe.global/line and Variable chain | EXCLUDED_SOURCE_INVALID (two NIWC Schematron failures) |
| SV-278143 | windows.wmi.query/registry and substring dependency | EXCLUDED_SOURCE_DEPRECATED (NIWC wmi_object); no proof bypass |
| SV-225230 | Windows .NET/WMI source | EXCLUDED_SOURCE_DEPRECATED (DISA wmi_object); not schema-invalid |

Accounting: **4 PROVED +4 unsupported +1 invalid +2 deprecated =11**.
Eight existing native Assessment bodies validate and compile to their frozen
program hashes; independent program operand checks pass. Three proof records
are outside the frozen 4,258-record floor (the two Apache Rules and IOS-XE NTP).
This is a separate evidence extension, not an assertion that published corpus
statuses changed. RHEL's proof is a retained control. The sample is diagnostic,
not representative of 100 capabilities or a basis for extrapolating corpus yield.

The new reader recognizes original `count` and the existing canonical native
`function: {name: count, arguments: ..., options: {}}`. It retains every component,
duplicates, order, Object/field projection and enclosing local Variable cast.
It never replaces count(values) with Item count, folds unknown to zero, or
executes a function. Extra options, empty arity, foreign namespace, unsupported
functions and changed operands/types/cardinality fail closed. Converter, compiler,
schema, result helper and scanner implementations are unchanged.

## DISA source findings

- `SV-225230`: `oval:mil.disa.fso.windows:obj:439702` is reported **deprecated** by
  pinned Schematron. XSD/required assertions are otherwise valid for the selected
  closure. This is a deprecation/policy exclusion, not proof of wrong runtime
  behavior or an invalid XML datatype. No DISA invalid assertion appears in this
  bounded sample; that is not a corpus-wide clean bill of health.

## NIWC source findings

- `SV-215833`: `oval:navy.navwar.niwcatlantic.scc.iosxe:var:21583306` is the owning
  local Variable of a concat input edge that fails the source string-Variable
  assertion. `...:var:21583307` owns the analogous regex_capture input-edge failure.
  Both messages and exact XPath locations are retained in fixtures/report.
  These concern declared types of referenced inputs, **not** a prohibition on an
  integer local Variable containing captured numeric text. Captured `"5"` can be
  cast to integer 5. Whole `exec-timeout 5 0` text cannot be cast to an integer.
  Preserve the original graph and strict validator exclusion; no source repair.
- `SV-278143`: `oval:navy.navwar.niwcatlantic.scc.windows:obj:27814302` is a
  deprecated wmi_object. A DISA-looking XCCDF Rule ID does not make this OVAL node
  DISA-authored. This sample does not establish that its substring computation
  is defective; that path remains unproved after the deprecation exclusion.

No inferred policy-intent defect was silently repaired. For example, the RHEL
mount regex remains source-identical; unanchored text alone does not establish
publisher intent. The earlier #265 source-intent question remains separate.

## Reference-model discrepancy requiring review (#255)

This is an **internal reference-model finding**, separate from both publisher
namespaces and the proposed #264/#265/#266 changes.

Pinned source Test: `oval:mil.disa.stig.win:tst:25327800`, reached from Server 2025
`SV-278021`; `check="all"`, `check_existence="all_exist"`.

```json
{"flag":"incomplete","check_existence":"all_exist","check":"all",
 "exists":1,"item_results":["false"]}
```

`oval-results-schema.xsd`, TestType documentation, incomplete exception 3a:

> 3a) If the check attribute evaluation results in "false", then the OVAL Test result must be "false";

The existing `evaluate_collected_object_test` helper returns **unknown** for this
vector because it stops at the all_exist/incomplete guard. A literal application
of 3a yields **false**. The paragraph orders existence before matching and also
contains exception 3b; the existing helper instead applies a conservative
future-population interpretation. This work records the conflicting result and
source-file hash without silently changing that interpretation, its old tests,
or any native result contract.

**Required decision:** resolve ordered existence versus incomplete exceptions
against the pinned OVAL documentation/conformance behavior, then approve the
reference-model correction/limits before using it as independent all_exist proof.
Do not infer a native schema change or scanner-runtime equivalence from either
model. Four valid Windows cases stay unproved. Complete collection with absent
expected populations and missing/error/unknown statuses remain independently
necessary boundaries; native scanners must not fabricate nonexistent Items.

## Reproduction, tests and preservation

```bash
python tools/audit_v04_bounded_source_validation.py --output NEW_REPORT.json
# Optional exact original replay (only these eleven Rules, six archives):
python tools/audit_v04_bounded_source_validation.py --originals PINNED_ZIP_DIR --output NEW_REPLAY.json
PYTHONPATH=.:tools python -m unittest -v tools.test_v04_bounded_source_validation
```

Fixtures/manifest: `tests/fixtures/v04-independent-validation/`. They are exact
original-node closure slices with retained full-component validation observations,
not complete signed originals. No converter is invoked. Without --originals,
validation observations are labeled retained; they are not called a fresh XSD run.
The CLI refuses to overwrite its report path. Model/table checks are reference
checks, not collection/scanner execution.

Focused integration: **59 selected /56 passed /3 skipped**, 10.357s, zero errors or
failures. The three skips require a test-local checkout location for OVAL XSDs;
a separate run explicitly bound the same operator fixture to vendored pinned
OVAL 5.12.3 schemas and passed **all four tests**, including both negative ANY
mutations, with zero skips. New suite has twelve tests with source/native count
mutants, fixed-denominator/hash checks, namespace attribution, zero-Variable
context, error/unknown propagation and 432 AND/OR six-state reversal checks.
ONE versus XOR with three true operands remains false versus true. These tests
also expose the unresolved reference-model discrepancy rather than treating its
current result as an accepted OVAL verdict.

All old 4,258 proof records, immutable ZIPs, authoring and compiled hashes remain
untouched. No 65-stream regeneration/rebaseline, final release/tag, pending
schema/authoring migration, automatic status promotion, or runtime claim.
Compact results are retained in [the JSON receipt](v04-independent-validation-20261030.json).
Complete proof terms belong in a separate evidence run; this source tree retains
bounded fixtures, executable checks and concise results/recovery notes.
