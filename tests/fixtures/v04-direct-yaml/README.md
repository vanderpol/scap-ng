# Original YAML acquisition conversion evidence

These are byte-exact public fixtures from
[OpenSCAP/openscap](https://github.com/OpenSCAP/openscap/tree/099cd84a0fa23c0e5d748e4e577c900c9b280623/tests/probes/yamlfilecontent),
pinned at `099cd84a0fa23c0e5d748e4e577c900c9b280623`.
[Provenance](provenance.json) records upstream Git blob and SHA-256 identities.
The shell scripts and YAML inputs are retained as original evidence; converter
tests never execute those scripts or collect data from the host.

All five original OVAL documents, containing 51 Tests, pass the vendored OVAL
5.12.3 XSD and embedded Schematron without repair or deprecation diagnostics.
Their generator's historical `schema_version` is preserved unchanged.

| Original document | Tests | Converted, compiled and typed-term proved | Unsupported |
| --- | --- | --- | --- |
| key | 10 | 10 | 0 |
| array | 5 | 2 | 3: deferred `split` function |
| content | 4 | 1 | 3: record-member Variable projection |
| offline_mode | 3 | 3 | 0 |
| types | 29 | 29 | 0 |
| Total | 51 | 45 | 6 |

[Conversion receipts](conversion-evidence.json) bind each original document/Test
to the native program and independent source/native semantic term hashes.
The regression reruns conversion and compares those receipts, source validity,
complete dependencies and source preservation. Native authoring validation,
dataflow/field-requirement validation, compilation and operand verification
are separate checks. The source proof reader imports no converter helpers.
Every converted Assessment also passes compiled-bundle schema, graph, integrity
and exact program verification in an explicitly constructed packaging wrapper.
That wrapper is not counted as an original Benchmark or production Rule.

These are **typed semantic terms and compiled operands**, not independently
executed YAML parsers or scanner results. In particular, the types fixture's
YAML 1.2 typing, nonfinite floats, malformed casts, null handling, platform
file access and offline roots still require runtime conformance work. The
non-scalar and missing-key query examples retain their original acquisitions;
conversion never precomputes them into false, empty Items or successful absence.

These 51 additional public probe Tests have their own denominator. They are
not added to the 803-Test Self-Assertion corpus or counted as published NIWC
production Rules. Capability admission remains bounded by proved constructs.

The converter uses the committed `independent.yamlfilecontent` mapping:
file path or directory/name plus YAML Path, or inline content plus YAML Path.
File acquisition reuses shared traversal lowering; inline content has no
filesystem or traversal parameters. Content and query require equality.
Unsupported/deprecated behaviors and ambiguous input combinations fail closed.

OVAL's record transport names are decoded into actual YAML key identity:
`my^camel^case^^^key` becomes `myCamelCase^Key`. Scalar/list marker `#` remains
`#`. This decoding applies only to YAML record fields, once; it does not change
other capabilities' record contracts or expected values. Native/OVAL readers
decode independently. Record lookup, outer record matching, field matching and
Variable `var_check` keep their separate scopes.

The array Tests 2/4/5 remain blocked by the grouped function contract in
[#255](https://github.com/vanderpol/scap-ng/issues/255). Content Tests 2/3/4
depend on local Variable `oval:0:var:1`, which projects Object 1's `value`
record member `yaml` via `object_component/@record_field`. This is distinct
from a Variable reference **inside a State record field**, which is already
supported and tested. A string Variable cannot receive the entire record;
guessing a dotted field path would introduce an unapproved projection contract.
The consolidated dependency report records these three cases as a Variable/
collection representation limitation. No source rewrite or fallback is used.

Run the bounded regression with:

```bash
PYTHONPATH=tools python -m unittest test_v04_direct_yaml_records
```
