# Explicit default equality on a nil UNIX filename

Continuation of [converter #251](https://github.com/vanderpol/scap-ng/issues/251)
from NTUSER integration `f141efb07603e72a3982ffda87489da8f0d5c74f`.
[Machine-readable receipt](v04-nil-filename-defaults-20261029.json).

## Original source and existing contract

NIWC `8c8e5dff860af6b1290ee9273a282db24278f8d5` supplies Solaris 11 SPARC
`SV-216418r959010` and x86 `SV-216181r959010`. Their original UNIX file Objects
select account home directories using an Object-derived path Variable and:

```xml
<filename operation="equals" xsi:nil="true"/>
```

OVAL 5.12.3 `unix-definitions-schema.xsd` file_object/filename documentation
states that a nil filename selects directory Items and that filename is not
used during collection. EntitySimpleBaseType defaults operation to `equals`.
The existing native Object already represents this with `name: null`.
The [compact original closures and provenance](../../tests/fixtures/v04-nil-filename-defaults/provenance.json)
retain every original dependency identity and the full source ZIP/blob pins.
They are extracted without source repair; original component whitespace remains.

Before: `filename: unsupported attributes ['operation']`.
After: the same native directory selection as the source with omitted default
operation. The correction accepts explicit or omitted `equals` only for a nil
`unix.file` filename. The independently maintained source reader separately
checks that exact operation. Source Variables, paths, ordered Filters, Set
boundaries, permission States and quantifiers remain unchanged.

This implements existing defaults, not new language meaning. Replacing nil
with `matches_regex: .*` would collect files under the directory and is rejected
by the independent mutation test. Ignoring arbitrary comparator attributes,
admitting other capability families, changing a schema, or relaxing source
validation are outside this bounded correction. All nondefault operations,
malformed nil values, wrong datatypes, text/children and unknown references
remain rejected. Compiler, mapping, scanner/editor and protected workflows
are unchanged. This is existing 0.4 UNIX file conversion, not 0.5 Windows work.

## Verification

- **52 focused/affected tests pass**, zero failures/errors/skips, including five
  new tests covering both originals, source validity/nondeprecation, default
  equivalence, scope restrictions, negative inputs and directory/file mutation.
- Both full original SCAP primary Rules pass the production selected-Rule
  acceptance path: source closure validity, schema, independent typed terms,
  compiled operands, bundle and independent package consumer. No full policy
  or scanner-runtime equivalence is claimed.
- All **523** preceding configured conformance Tests retain all four authoring,
  source-term, native-term and compiled-program hashes. Coverage stays 523/713
  configured, out of 803 original Tests; no new conformance proof is claimed.
- Both preceding NTUSER original primary proofs and exact program hashes remain
  unchanged under this correction. The six-source gate retains all 1,072 primary
  proofs and exact program hashes, with unchanged 324 blocked automated and
  171 manual/OCIL-only Rules. Together these retain all 1,074 preceding primary
  proofs across the six anchors and the two selected NTUSER Rules.
- The preceding NTUSER integration `f141efb07` finished all nine hosted gates
  successfully before this publication (3,279 maintained tests; zero failures,
  one existing skip). These base results are not full-suite verification of
  this new increment. All nine exact-commit workflows at `10f4e35b3` have now
  passed. [Maintained run 40867417638](https://github.com/vanderpol/scap-ng/actions/runs/40867417638):
  **3,284 run, 3,283 passed, zero failures/errors, one existing skip**,
  1143.910 seconds; job 123425584553, artifact 12895541852.
  [Six-source run 40867417851](https://github.com/vanderpol/scap-ng/actions/runs/40867417851),
  job 123425584157, artifact 12894249637, retains all 1,072 primary proofs.
  No duplicate full maintained suite was dispatched.

The original all-65 DRAFT archive is unchanged. Only the two selected Solaris
Rules were converted for new original-source evidence. Large outputs and logs
are outside source Git under `/workspace/recovery-20261029/`, including
`nil-six/`, `nil-conformance.json`, `nil-affected.log`,
`ntuser-retained-under-nil/` and `solaris-narrow-selected/`.
The conformance probe was paused to prioritize the NTUSER maintained suite;
its wall-clock elapsed field includes that pause and is not a performance result.

Reproduction:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_nil_filename_defaults test_v04_ntuser_empty_state \
  test_v04_direct_converter test_v04_expanded_source_proof \
  test_v04_direct_enum_variables test_v04_converter_contracts -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/verify_v04_direct_scope.py \
  --inputs PINNED_SIX_ZIP_DIRECTORY --output NEW_EVIDENCE_DIRECTORY
```

## Deferred source-valid cases

SPARC `SV-216301r959010` and x86 `SV-216066r959010` also have source-valid
explicit default attributes on a Variable-source `var_ref`. Isolated probing
past that guard exposes unsupported `split`, so admitting those attributes does
not unlock either Rule. That experimental admission is excluded from this diff.
Function grammar/evaluation and other normative contract dependencies remain
under [#255](https://github.com/vanderpol/scap-ng/issues/255); no hidden bypass.


A bounded original-source audit also checks the eight primary nil cmdlet datatype
cases in the published ledger. All eight closures are INVALID under the original
Schematron: nil `parameters` still requires explicit `datatype="record"`.
They remain rejected; this is not a request to fill missing original attributes.
The adjacent receipt identifies every Rule/source pin and actual source error.
No all-65 archive or historical ledger status is rewritten.

The two other acquisition-primary cases are VALID and nondeprecated, but remain
under the previously recorded acquisition-contract clarification:

- .NET `SV-225226r961041`, Object
  `oval:navy.navwar.niwcatlantic.scc.dotnet:obj:22522601`, has a `command`
  acquisition entity with `operation="case insensitive equals"` and a Variable
  reference. The native invocation parameter has no comparator. Do not drop it.
- Windows 10 `SV-220812r991589`, Object
  `oval:mil.disa.stig.windows:obj:22081200`, has
  `<module_version datatype="version">1.0.0.0</module_version>`.
  The native acquisition contract describes a version string, while the current
  scalar-parameter reader accepts string-typed originals only. Permitted source
  datatype projection must be explicit; do not apply a general acquisition cast.

Recommendation: retain both guards until the existing #255 coordination pins
per-parameter source-operation/datatype admission and independent proof
obligations. No new mapping or assessment meaning is inferred in this increment.
Population/all_exist, import/export, aggregation, unsupported functions and float
contracts likewise remain at their documented decision boundaries.


The JSON receipt includes actual generated Object/require excerpts for both
new original Rules, rather than relying only on descriptions of their output.
The exact implementation remains `10f4e35b331c622c14f6e3aa2bd4aa8981c810c1`;
subsequent receipt/checkpoint edits do not change converter or proof code.
