# Converter integration with the revised 0.4 schemas

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) and
[#255](https://github.com/vanderpol/scap-ng/issues/255), from clean `main`
`2bd1bae6b6477a90ca706aa7353987e0a94ceb82`. Approved schema commit
`d3132ae57432924f21d01a9b6ca2689d70f1b2f2` is an ancestor. No schema, mapping,
generator, compiler, scanner, editor, original OVAL payload or 0.3 file changed.
Repository migration under #254 remains deferred.

## Implemented

The existing recursive visitor enables **47/51** mappings in the approved
Independent/Linux/UNIX/Windows scope (**47/100** globally). This adds `file.hash`,
not a second conversion engine. Its native Object `algorithm` selector retains
one acquisition over all six approved algorithms, including complement selection.
Source Variables become ordered static arrays without dropping duplicates;
`var_check` becomes the independent `value_match`. No synthetic Items, extra
Tests, implicit OR, guessed algorithm or collector default is introduced.

The pinned original UNIX cases have these meanings:

| Original Test | Object algorithms | State algorithm comparison |
| --- | --- | --- |
| 305 | MD5 and SHA-1 | None of SHA-224, SHA-256, SHA-384, SHA-512 |
| 544 | Complement of the four SHA-2 algorithms | At least one of MD5 and SHA-1 |
| 354 | The four SHA-2 algorithms | At least one of those same four algorithms |

Thus the earlier question about matching none of the Variable's values applies
to the comparison's own boundary: Test 544 uses it for acquisition, while Test
305 uses it in State comparison. It does not invert the overall Test result.
Error, unresolved Variable and incomplete acquisition dependencies are retained;
these conversions do not evaluate a collector or manufacture an empty success.

Named runtime algorithm Variables work when their graph projects the same
approved enum domain, through direct ObjectComponent, Variable references and
`unique`. The value rename is a bijection. Independent source proof retains the
source vocabulary until the enum consumer checks that correspondence. A cached
algorithm Variable cannot silently become an ordinary string in a digest,
command or other consumer. Arbitrary runtime strings/external bindings still
need a reviewed adapter; callers are not assumed to supply native spellings.
State equality and inequality retain their original Variable quantifiers;
lexical/regex enum operations without a proof remain unsupported.

All array and predicate Variable operands now emit explicit datatypes, including
OVAL's default string datatype. Values, Variable matching, State value matching
and collected-Item matching remain separate. All **39 original Server 2025
user-rights Rules** retain their original proofs and compile successfully.
Eight affected current converter documentation examples were regenerated and
proved with type annotations only; their manifests preserve the historical
generation evidence and record the correction separately.

## Evidence and retention

The [compact receipt](v04-converter-revised-schemas-20261027.json) records exact
commands, passing/failing/skipped counts and coverage. Exact published commit
and hosted CI results are recorded in the existing
[issue #251 handoff](https://github.com/vanderpol/scap-ng/issues/251).

- All 100 capability contracts regenerate: 141 selectors, 694 State entries,
  zero failed contracts and zero schema/mapping changes.
- The 803-Test original collection has 710 Tests in enabled capabilities:
  414 convert, validate and compile; 406 have independent typed-term proofs.
  Six original UNIX/Windows hash Tests are newly proved, including mandatory
  Tests 305, 544 and 354. Controlled mutations are not additional original proofs.
- Every preceding 400 original proof identity and source-term hash is retained.
  Program hashes are unchanged for 369; 31 changes add only explicit string
  datatypes. Compilation alone does not prove the other eight compiled cases.
- The six-source floor retains all 1,010 primary OVAL Rule identities. Its
  941 unchanged program hashes and 69 individually explained type-only changes
  are in the [correction receipt](v04-converter-explicit-datatype-corrections-20261027.json).
  The comparison checked every old/new Assessment property, not just selected
  hashes or schemas. Quantifiers, values and dependency graphs are unchanged.
- All eight original `unix.process58` Tests remain covered by the maintained
  original-source continuation tests and corpus audit. Their acquisition
  contract has not been changed.

Proof scope remains structural correspondence of typed acquisition/comparison
terms, complete dependency graphs, provenance and compiled operands. Native
schema validity, conversion, compilation, independently checked terms and scanner
execution are distinct states. Applicability/full policy migration, publisher
trust, scanner-runtime equivalence and release readiness are not established.

## Acquisition parameter review and remaining work

The [source-backed review](v04-converter-acquisition-parameters-20261027.json)
records all 15 Variable-capable parameters: shellcommand 3, SQL512 5, cmdlet 5,
WMI 2. It includes pinned original declarations and Variable edges. The
Self-Assertion collection's two parameter Variable edges use closed one-value
literal expressions; that collection has no SQL512 Test or original multivalue
command/query input example. This does not establish that production runtime
Variables always have one value. Existing production command graphs, including
SV-278139, retain their earlier graph/operand proof scope; invocation multiplicity
requires separate evidence.

One immutable constant can become one acquisition input for `all`, `at least
one` or `only one`. Multiple constants, complement inputs and nondefault runtime
quantifiers remain unsupported rather than becoming new invocations. Whole-record
`var_ref` remains prohibited by original OVAL. Individual record fields retain
the already proved `value_match` and `selection_match` boundaries.

Review the following as one cross-capability design packet, not one request per
capability, if broader runtime inputs are required:

1. A runtime enum adapter must define source/native vocabularies, valid and
   out-of-domain values, duplicate/zero-value behavior, cast failures and
   unknown/error/incomplete propagation. Direct same-domain projection support
   does not authorize arbitrary string rewriting or a new Variable function.
2. Acquisition inputs must distinguish identity selection from invocation data.
   SQL version/instance/database selection cannot be generalized from command,
   SQL statement or WQL text. For any multivalue expansion, specify independent
   versus correlated inputs, resulting Item identities, order, duplicates and
   result/completeness propagation. Schema reference acceptance is insufficient.
3. Reuse the existing record-field proofs. Do not replace record members with a
   whole-record Variable or turn collection parameters into selector predicates.

Four mappings in the approved platform scope remain inactive: `unix.sshd`
(three pinned nullable-path schema cases; another original uses invalid
`var_check="none exist"`), `linux.rpmverifyfile` (all three pinned examples use
deprecated `md5_differs`), SQL512 and YAML file content (no original Tests in this
pinned collection; source-backed acquisition proof still needed). The
[dependency register](../../tests/fixtures/v04-converter-schema-dependencies.json)
retains the resolved hash counterexamples and active SSH counterexamples.
Other unsupported constructs remain classified in consolidated diagnostics;
there is no fallback conversion to inflate coverage.

Converter predicate emission is ready for the owner's final explicit-datatype
schema restriction. This work deliberately leaves the permissive common schema
and its visible integration-gap regression unchanged. Historical/non-converter
content must be reviewed separately before a repository-wide restriction.
