# Native 0.4 contract generation — #251

Base: `c1c124f58a45981a7cfe5678eb4206afd6baf75c`.
The current generator now constructs native Item/Test/flat-Object contracts
from version-local mappings and original XSD metadata directly. It no longer
constructs a 0.3 schema, rewrites version strings, or flattens an older Object
wrapper. The current public validator loads older generators only for older
specification versions. Fresh-process tests block both historical generator
imports while generating all contracts, validating real original-source output
and compiling a native package.

**Parity:** all 100 complete generated-schema fingerprints match the preceding
implementation, including annotations, constraints and reference targets. All
803 pinned corpus cases, source/dependency hashes, authoring/program hashes and
outcomes are unchanged. No capability is enabled or normative schema modified.
Thirty-three focused tests and eight schema-promotion audit tests pass locally;
at implementation `b225b7eba0ab53d4722348bd77017c30efc9705d`, all 31 triggered
hosted workflows pass. The downloaded mandatory result confirms **3,118 tests,
zero failures/errors and one existing skip**. Exact runs and verified artifact
digest are in the [machine report](v04-native-generator.json), including
[mandatory CI](https://github.com/vanderpol/scap-ng/actions/runs/40489065483).

The active generation dependency path falls from **1,188 to 487 nonblank,
noncomment lines**, counting the complete modules needed for generation.
Historical files remain for their existing callers. In the same environment,
100 generations took 2.18 s on the old path and 1.00 s on the native path on the
first pass; three repeated passes were 2.17–2.41 s versus 1.03–1.05 s. This is
schema-generation timing, not whole-converter or scanner performance. Ordinary
capabilities now parse their Definitions XSD once and Item XSD once; fixed-result
contracts need one source parse. Metadata/source-field mutation tests prove that
new fields and changed types refresh without new Python branches or stale caches.

Responsibilities:

- `v04_capability_source.py`: reviewed version-neutral XSD field/type extraction;
  no NG authoring grammar. These individual helpers match the new design.
- `v04_capability_native.py`: direct Item, Test-source and flat Object construction.
- `generate_capability_schema_v04.py`: current typed selectors, inline conditions,
  recursive Sets/Filters and qualified current-version references.

For an already approved new source field, update its declarative field mapping
and any necessary datatype override, regenerate contracts with
`python tools/v04_converter_contracts.py --output /tmp/contracts.json`, and run
`PYTHONPATH=tools python -m unittest test_v04_native_schema_generation
 test_v04_converter_contracts -v`. The controlled field-addition/type-change test
shows this workflow without modifying a real normative schema. Review legitimate
contract changes before updating the fingerprint fixture. Capability algorithms
and generated Python are not created by this process.

The existing inert old-property rejection guard is retained solely for exact
contract parity; those properties are not in the allowed Test surface and do not
introduce authoring aliases or a native State layer. Real cmdlet `select` remains
a declared acquisition parameter. Native generation never creates generic
`select`/`collect` wrappers. Older-version validation and explicit historical
migration retain their own dependencies; this is not a wholesale history cleanup.

Nineteen current workflow path filters now include the two generator helpers,
so future helper edits retain the existing source-proof/contract checks. No
historical job was modernized or acceptance assertion weakened.
