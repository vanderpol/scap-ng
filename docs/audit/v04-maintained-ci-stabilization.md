# Maintained regression CI stabilization — #251 / #248

Base: `1db46495fd166a384ed76ec98e18b89b658bbc23` on `main`.
The [complete occurrence inventory](v04-maintained-regression-inventory.json)
classifies every baseline failure/error, retains its exact test/subtest identity
and initial error, and marks resolved versus remaining. No test module, subtest,
assertion or CI filter was silently removed or demoted.

## Results

| Run | Tests | Failures | Errors | Skips |
| --- | ---: | ---: | ---: | ---: |
| Historical pre-registry baseline | 3031 | 19 | 142 | 26 |
| Actual starting main, including registry regressions | 3036 | 19 | 142 | 26 |
| Repaired maintained runner | 3037 | 2 | 127 | 26 |
| Focused production/schema/compiler/repair suites | 191 | 0 | 0 | 0 |

**32 baseline failure/error occurrences resolved; zero new; 129 remain visible.**
The extra test is a generated/base-schema contract and reference-resolution
regression. The earlier positive fixtures were migrated to the approved grammar;
legacy spellings now appear as explicit negative cases. Their coverage was not
removed. Existing source/compiler positives and negatives remain passing.

## Repairs

1. `generate_capability_schema_v04.py`: generated-local references resolve against
   the generated schema ID, while normative relative document references resolve
   against the version root. Apply the qualification to fixed-result schemas too,
   which previously returned early. `independent.unknown` uses the same mandatory
   structured Test.require contract as the approved schema. Generated contracts
   no longer advertise deprecated Test State properties or old Boolean aliases.
   The new regression compares generated validation to the approved Test
   validator, including invalid metadata, missing require, scalar require and
   legacy States. No network resolution or validation bypass is used.
2. `test_generate_capability_schema_v04.py`: migrate maintained positive inputs
   to explicit Item/field counts, structured require and `exactly_one` expected
   value cardinality. Preserve bad-field, missing-count, malformed-Object,
   Filter-position, dynamic-selector and enum negatives. Explicitly reject old
   `all`/`any`/`odd` authoring aliases and deprecated Test State properties.
3. `test_v04_fixed_unknown_minimal.py`: replace obsolete positive assumptions
   with the approved uniform grammar. Missing/scalar require are negative
   fixtures; structured require is positive. Invalid Object/result/State tests
   now start from an otherwise valid Test, so they cannot pass merely because
   require is missing. This changes authoring tests, not unknown-result semantics.
4. `validate_v04_fields_condition_preview.py`: in the explicit legacy-review
   validation bridge, flatten historical Object wrappers *before* strict Test
   promotion. Independently verify the Object inverse, then verify the Test
   source inverse. Raw archives and default strict compiler behavior stay intact.
   The Apache tests retain actual immutable source fixtures, exact regex and
   cardinality assertions, round-trip ledgers, source-archive mismatch rejection,
   shared Objects, dependency verification, idempotence and negative validation.
5. Apache fixture assertions now inspect the approved current `fields`/counts
   structure and use current `selection_match: every`. No automatic alias was
   added to any parser, compiler or normative schema.

No files under `schema/` or `specification/`, production OVAL converters,
`v04_field_requirement.py`, or native/typed-IR compilers changed. No editor,
scanner, source evaluation algebra, frozen 0.3 generator or 65-STIG corpus run.

## Remaining inventory and release-scope decisions

Initial classification: 18 obsolete maintained-fixture occurrences, 14 maintained
preview bridge/fixture occurrences, 126 historical research occurrences,
two historical research reference-scope errors, and one source-backed schema
representation boundary. The first two groups are repaired.

| Module | Remaining occurrences |
| --- | ---: |
| `test_research_c_composed_assessment` | 4 |
| `test_research_c_dns_shell` | 3 |
| `test_research_c_explicit_typed_field_roundtrip` | 9 |
| `test_research_c_external_observations` | 2 |
| `test_research_c_guided_projection` | 6 |
| `test_research_c_objectless` | 1 |
| `test_research_c_original_oval_to_authored_c` | 17 |
| `test_research_c_oval_multicheck` | 37 |
| `test_research_c_oval_singleton_source` | 5 |
| `test_research_c_permissions_macro` | 8 |
| `test_research_c_require_language` | 19 |
| `test_research_c_unified_compiler` | 10 |
| `test_research_c_unified_complex_windows` | 1 |
| `test_research_c_windows_shared_native` | 1 |
| `test_v04_field_requirement_schema_candidate` | 1 |
| `test_v04_scalar_none_exist_source` | 1 |
| `test_validate_v04_fields_condition_preview` | 4 |

The 126 historical research occurrences include research C implementations that
read removed scalar enum catalogs (`KeyError: 'enum'`), old export expectations,
and proposal builders that require removed `inherited_field_predicate` or
`all_items_requirement` definitions. Two further C test validators lack a
resource registry (`Unresolvable: reported-elements.schema.json`); merely fixing
that lookup would still leave their legacy native-A output incompatible with
current schema and enum assertions. These are not newly introduced production
converter failures, and reviving them would exceed the approved current-grammar
scope. Every test continues to run in the existing maintained gate.

**Proposal, not implemented:** Jack should decide whether to retain these as
current release requirements (and authorize migration) or preserve their original
research dialect against an immutable historical toolchain in an explicitly
separate research job. A split would change release gating and must be reviewed;
there are no new exclusions, expected-failure markers, skips or conditional
assertions in this change. The current gate is intentionally still red.

### Smallest source-backed representation boundary

Pinned source: `OVAL-Community/SCAP-Self-Assertion`, revision
`e3538595c5083b9c34d937a81d319234df9bbfaa`,
`SCAP_1.4/OVAL_Test_Content/macos/macos-def_gatekeeper_test.xml`,
SHA-256 `a76301de534a71f84fc498108c59b065551b9ec933db1b0a8e8582e835b2eebf`.
Test `oval:navy.navwar.niwcatlantic.scc:tst:1` references State
`oval:navy.navwar.niwcatlantic.scc:ste:1`, whose conditions include:

```xml
<enabled datatype="boolean">1</enabled>
<unlabeled check_existence="none_exist" />
```

The unlabeled condition asserts absence; it supplies no comparison value. In the
OVAL reference existence algebra it is true with no existing unlabeled entities
and false with one existing entity. These are source-algebra observations, not
host scanner results. Inventing an `equals` operand is not a lossless repair.

The maintained source proof still emits the old dialect. Its explicit current
promotion also fails: canonical scalar predicates require `values_found` and
`values_matching` plus a comparator. The retained old absence-only branch
requires `require: none_exist` with `maxProperties: 1`, but `require` is not an
allowed scalar property, and two current count properties are mandatory. An
inherited field predicate still requires a comparator. Thus simply migrating
this fixture cannot produce an approved comparator-free absence condition.

The original failing positive and its three passing negative tests are retained.
**Decision needed:** authorize a separately reviewed canonical absence-only
representation/schema correction, or explicitly classify this source shape as
unsupported at this version. This task does neither. The separate existing
Test-population `all_exist` boundary also remains unresolved and unchanged.

## Reproduction and validation

Python 3.12.14. Workflow pins: PyYAML 6.0.3, lxml 6.1.1, jsonschema 4.25.1.
`cryptography` is unpinned in the workflow; observed version was 50.0.2.
The four workflow source XML fixtures are downloaded at the exact Self-Assertion
revision above, with TLS verification, and supplied by their existing variable
bindings. The runner and workflow files are unchanged.

From `/workspace/scap-ng`, with `TASK_FIXTURES` set to the directory containing
the four downloaded XML basenames:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003 \
SCAP_NG_APPARMOR_SOURCE_XML="$TASK_FIXTURES/linux-def_apparmorstatus_test.xml" \
SCAP_NG_ENVIRONMENT58_SOURCE_XML="$TASK_FIXTURES/ind-def_environmentvariable58_test_linux.xml" \
SCAP_NG_UNAME_SOURCE_XML="$TASK_FIXTURES/unix-def_uname_test.xml" \
OVAL_GATEKEEPER_SOURCE="$TASK_FIXTURES/macos-def_gatekeeper_test.xml" \
python tools/run_current_tool_regressions.py
```

Inventory capture wrapped `unittest.TextTestRunner.run` to serialize its existing
failure/error records; it did not alter discovery, filtering, assertions, return
status or any test. Baseline and final inventory have zero newly failing IDs.

The focused invocation used the same Python/dependencies/PYTHONPATH, plus the
pinned `SCAP_NG_IOS_LINE_SOURCE_XML` and `SCAP_NG_IOSXE_LINE_SOURCE_XML` bindings:

```bash
python -m unittest -v \
  test_scap_converter_core test_scap_converter_core_object_presence \
  test_scap_converter_core_multistate test_scap_converter_core_apparmorstatus \
  test_scap_converter_core_environment_uname test_v04_approved_pipeline \
  test_v04_schema_draft test_v04_field_requirement_schema \
  test_v04_native_bundle_compiler test_oval_result_truth_tables \
  test_generate_capability_schema_v04 test_v04_fixed_unknown_minimal \
  test_v04_apache_preview_compatibility test_v04_field_requirement_conversion \
  test_v04_canonical_requirement_oracle test_v04_public_cli_smoke \
  test_v04_source_schema_registry
```

`python tools/audit_repository_layout.py --check` and `git diff --check` also
passed. Hosted CI and implementation commit SHAs are recorded below after push.

Related issues: [#251](https://github.com/vanderpol/scap-ng/issues/251),
[#248](https://github.com/vanderpol/scap-ng/issues/248). No scanner-runtime
conformance or equivalence claim is made.
