# Current 0.4 converter and compiler developer runbook

**Scope: October 23, 2026 pre-alpha integration checkpoint.** The supported
paths below are a bounded subset. No published full OVAL coverage or scanner
conformance is claimed.

## One source tree; historical releases are immutable

- Develop on `main`. Keep one current converter/upgrade path and one current
  native compiler. Isolated research branches are temporary; merge reviewed
  changes back to `main`. Never maintain a parallel live 0.3 source tree.
- Use [versioned source snapshots](../releases/TOOLCHAIN-RELEASES.md) from the
  exact release tag to reproduce an older output, including its specification,
  schemas, guides and test fixtures. A developer source snapshot is **not** a
  release declaration or an executable scanner-conformance certificate.
- Do not modify the normative release specification to make a conversion test
  pass. Capture genuinely ambiguous semantics for human review.

## Converter: preserved 0.3 functionality in a 0.4 entry point

From a repository checkout with Python 3.12 and pinned test dependencies
`lxml==6.1.1`, `PyYAML==6.0.3`, `jsonschema==4.25.1`:

```bash
python tools/scap_converter_core.py \
  --source-xml /path/to/original-oval-definitions.xml \
  --definition-id oval:example:def:1 \
  --output /tmp/assessment-0.4.json \
  --evidence /tmp/assessment-conversion-evidence.json

python tools/test_scap_converter_core.py -v
python tools/test_scap_converter_core_object_presence.py -v
python tools/test_scap_converter_core_multitest.py -v
SCAP_NG_IOS_LINE_SOURCE_XML=/path/to/ios-def_line_test.xml \
SCAP_NG_IOSXE_LINE_SOURCE_XML=/path/to/iosxe-def_line_test.xml \
  python tools/test_scap_converter_core_multistate.py -v
SCAP_NG_FILEVAULT_SOURCE_XML=/path/to/macos-def_filevault_test.xml \
SCAP_NG_FIRMWAREPASSWORD_SOURCE_XML=/path/to/macos-def_firmwarepassword_test.xml \
SCAP_NG_PROFILES_SOURCE_XML=/path/to/macos-def_profiles_test.xml \
  python tools/test_scap_converter_core_singleton_presence.py -v
SCAP_NG_APPARMOR_SOURCE_XML=/path/to/linux-def_apparmorstatus_test.xml \
  python tools/test_scap_converter_core_apparmorstatus.py -v
python tools/test_v04_public_cli_smoke.py -v
SCAP_NG_CONSTANT_VARIABLE_SOURCE_XML=/path/to/oval-def_constant_variable.xml \
SCAP_NG_CHECK_ENUMERATION_SOURCE_XML=/path/to/oval_check_enumeration_variable_values.xml \
  python tools/test_scap_converter_core_constant_matrix.py -v
SCAP_NG_BOOLEAN_DATATYPE_SOURCE_XML=/path/to/oval_boolean_datatype.xml \
SCAP_NG_STRING_DATATYPE_SOURCE_XML=/path/to/oval_string_datatype.xml \
SCAP_NG_INT_DATATYPE_SOURCE_XML=/path/to/oval_int_datatype.xml \
  python tools/test_v04_source_verified_constant_datatypes.py -v
python tools/test_oval_semantic_core_preservation.py -v
# With the pinned source available (see below):
SCAP_NG_VARIABLE_SOURCE_XML=/path/to/ind-def_variable_test.xml \
  python tools/test_scap_converter_core_variable.py -v
SCAP_NG_FAMILY_SOURCE_XML=/path/to/ind-def_family_test.xml \
  python tools/test_scap_converter_core_family.py -v
```

The current implementation calls the established semantic IR parser and
`scap_upconvert_v003` source/language lowering plus its 0.3 capability
alignment. A distinct 0.4 projection reuses the verified flat-Object and
requirement transformations, validates the Test through the native 0.4
compiler. For the original two leaf shapes it checks agreement with the
independently developed OVAL importer (normalized to flat-Object syntax).
For direct Object-only cases it instead compares the mature 0.3 graph field
by field to the original OVAL Test and Object before emitting native syntax.
The pinned AppArmor singleton Definition `oval:com.jovalcm.test:def:967` is
also supported through this same 0.3 lowering and direct State projection.
Only the original Self-Assertion file at revision
`e3538595c5083b9c34d937a81d319234df9bbfaa`, SHA-256
`1e9b6d6bab5a40226db960cebf08c8124282b86e8b0c52316027d48b2c97a5d6`,
is admitted. Its empty Object becomes an implicit singleton; the original
Test existence/check quantifiers and integer `loaded_profiles_count >= 0`
State remain explicit. The raw mature lowering graph is fingerprinted with
only the caller-selected Assessment identity excluded, then each aligned
Test/State binding and operand is checked against the original graph.
The independent AppArmor oracle is used only by differential tests, never
to supply converter output. This does not admit other integer/singleton shapes
or establish live AppArmor scanner behavior (Refs #232 #248).

The checkout must contain both `schema/v0.3.0/capability-mappings/supported/`
and `schema/v0.4.0/capability-mappings/supported/`. In particular the mature
0.3 mapper represents a direct shell Filter using an intermediate single
UNION Set operand; the 0.4 adapter admits that exact source-proven shape,
while real original OVAL Sets remain unsupported. Missing 0.3 mappings are
an error, never an implied conversion fallback.

**Supported in this checkpoint:** a source-verified single direct Object-only
Test with mapped string selectors and an explicit OVAL existence requirement
(`any_exist`, `at_least_one_exists`, `none_exist` or `only_one_exists`), with
no State, Variable, Set, Filter or nested Boolean criteria. The current core
reuses the mature 0.3 lowering, verifies every Test/Object/selector binding
against the original OVAL, and compiles a native 0.4 presence instruction.
The immutable ASA line and IOS BGP-neighbor/section examples exercise this path.
These checks do **not** establish scanner-result parity.

Also admitted in the same source-attested direct-Test bridge: precisely one
scalar State, with literal string equality or regex, default State field
existence/check semantics, one direct Object, and the original Test `all` or
`at least one` check. It emits the explicit source-exact 0.4 Test/State
fallback, preserving quantifier boundaries. The immutable AIX fileset
Self-Assertion source exercises this case. Variables, multiple State fields,
nondefault field checks, Sets and Filters still fail closed. No live scanner
evaluation or full six-state equivalence is claimed.

An explicitly mapped singleton capability may omit its otherwise empty
source Object in native 0.4; it must declare `test_source.kind=none` and the
original OVAL singleton-object migration crosswalk. The immutable ASA version
case verifies this optimization, including a `version` comparison and a
negative test that rejects nonempty singleton Objects.

This same source-attested singleton path admits *absence of a State* when the
original OVAL Test uses only an existence requirement. Pinned macOS FileVault,
firmware-password and profiles checks verify the genuinely empty OVAL Objects,
explicit capability crosswalks and compiled 0.4 presence checks. An unlisted
singleton capability or extra original Object field still fails closed.

A flat original OVAL `AND` over 2–15 distinct direct no-State Object Tests
also reuses the mature 0.3 lowering. Each Test's capability, source reference,
check/existence, Object selector, operation and order are independently
attested; the native result has explicit `and` semantics and compiles every
Test. The pinned IOS global example has two direct Test/Object branches.
Original `OR`, negation, shared Objects and missing provenance fail closed;
the no-State variant separately rejects State-bearing branches.

The multi-Test path also composes the **existing single-Test direct-State
proof** when a flat original OVAL AND contains two or more distinct Test
branches with at most one literal scalar State each. Source Test/collection/
State identity closure, original source operations, quantifiers and ordering
must still match the mature 0.3 graph. The immutable IOS and IOS XE line
Self-Assertions exercise two regex State branches each. Arbitrary nested
criteria, Object sharing, multi-field States and Variable-backed predicates
are not admitted through this path.

Previously admitted are one direct
`independent.shellcommand` PowerShell presence Test with a single `include`
Filter, or one direct `windows.registry` value-equality Test with its
original `only one` item quantifier; **also** one pinned
`independent.variable_test` four-way source Definition
`oval:org.mitre.oval.test:def:538`. It contains four distinct AND-ed Test
bindings across two constant string Variables and preserves State `var_check`
separately from Test item quantifiers. The shared core uses the mature 0.3
graph as its executable source, checks it against the independently audited
native 0.4 implementation and regenerates OVAL for semantic comparison.
Also admitted: pinned `independent.family_test` Definition
`oval:org.mitre.oval.test:def:95`, which uses one regex constant Variable,
preserves State `var_check=all` and the Test `at least one` check, and has
independent 0.4 import/export and semantic round-trip proof.

The shared converter additionally imports two existing independent pinned
integer-constant-Variable matrix cases (`oval:org.mitre.oval.test:def:92`
and `def:170`). These cover one/multiple literal values, `equals`, integer
less/greater comparisons, all four original `var_check` quantifiers and
negated AND criteria across two and ten Tests. Their **executable output**
comes from the mature 0.3 lowered Variable/Test/State graph; a separate
source-pinned OVAL importer supplies a whole-Assessment differential oracle.
Original SHA drift, lost source references and changed 0.3 predicates cause
hard errors. This is two reviewed source files, not general Variable coverage.

The already implemented source-pinned OVAL datatype importer supplies an
independent comparator for **three more 0.3-backed typed constant-Variable
suites** (Boolean, string and integer; 8, 10 and 20 original Tests).
The mature 0.3 graph retains Test quantifiers, nested AND/NOT branches and
typed comparisons, while the source attestations check literal lexemes and
every original Variable, Test and State binding. The shared core emits the
native version only if its complete Assessment matches that prior importer.
Other typed suites remain separately reviewed, not yet core-integrated.

For source regressions, retrieve only the immutable
[`e3538595` Self-Assertion source](https://github.com/OVAL-Community/SCAP-Self-Assertion/commit/e3538595c5083b9c34d937a81d319234df9bbfaa)
at `SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_variable_test.xml` and
`SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_family_test.xml`, plus
`agnostic/oval-def_constant_variable.xml`,
`agnostic/oval_check_enumeration_variable_values.xml`,
`agnostic/oval_boolean_datatype.xml`, `agnostic/oval_string_datatype.xml`,
`agnostic/oval_int_datatype.xml`,
`aix/aix-def_fileset_test.xml`, `asa/asa-def_line_test.xml`,
`asa/asa-def_version_test.xml`,
`ios/ios-def_global_test.xml`,
`ios/ios-def_line_test.xml`, `iosxe/iosxe-def_line_test.xml`,
`macos/macos-def_filevault_test.xml`,
`macos/macos-def_firmwarepassword_test.xml`,
`macos/macos-def_profiles_test.xml`,
`ios/ios-def_bgpneighbor_test.xml`, and
`ios/ios-def_section_test.xml` files
under the same `SCAP_1.4/OVAL_Test_Content/` prefix. The Variable and Family
regressions check their SHA256, and the Object-only regression independently
checks OVAL source Test/Object/selector details. Sources are fetched by the maintained
GitHub Actions test, not copied into the repository.

These source-bound subsets are **not** a general language-coverage claim;
both Variable cases already had independent 0.4 coverage prior to integration.
Other shapes must error, including genuine Sets, arbitrary Variable
references/function chains, arbitrary nested criteria, unsupported Filters
and unmatched Test/State semantics. The legacy broad 0.3 importer
remains available to avoid destroying existing source support while verified
0.4 adapters are added.

The CLI writes a single standalone Assessment authoring document. It **does
not** create a full Benchmark/Rule graph or an executable `.scapng` bundle.
The public compiler independently accepts a complete Benchmark/Rule/Assessment
authoring source package or JSON/YAML archives. The public CLI smoke regression
uses a schema-valid minimal graph to verify both compilation forms yield
identical native `.scapng` bytes. A converter output Assessment must be
combined with its originating Benchmark/Rule and any dependent content before
bundle compilation; there is **not yet** one public raw OVAL-to-bundle command.
Run source-to-native differential tests and versioned compiler checks before
raising coverage claims. The evidence JSON explicitly marks `scanner_parity`
and `full_oval_coverage` false.

## Count source coverage before choosing the next construct

Run the public read-only source audit against a pinned original OVAL corpus,
or a single original XML file:

```bash
python tools/audit_scap_converter_core_coverage.py \
  --source /path/to/original-oval-corpus \
  --report /tmp/oval-core-coverage.json
python tools/test_audit_scap_converter_core_coverage.py -v
```

The report contains every Definition's source hash and status, plus separate
counts for mature **0.3 source lowering** and **current source-proven 0.4
output**, including 0.3-lowerable cases blocked in the current core. Native
0.4 acceptance also requires schema validation and compiler program acceptance.
Malformed files and deprecated Definitions are counted separately; they are
never removed silently from the denominator. This is a converter coverage
inventory only, **not** a scanner parity or STIG benchmark completion report.
The dedicated CI converter regression tests the two pinned external Variable
Definitions through this reporting path as well as the direct conversion path.
For the full 167-Definition Self-Assertion source audit, manually trigger
`0.4 original OVAL core conversion coverage` in GitHub Actions. It
checks out the original repository at its immutable revision and uploads the
complete per-Definition report. The audit also runs when its own script,
converter code or workflow changes, but deliberately does not run on
unrelated pushes.

## Compiler: canonical 0.4 graph only

For a complete, closed native 0.4 authoring archive, compile independently
parsed JSON and YAML and require byte-for-byte native-bundle equality:

```bash
python tools/v04_native_bundle_compiler.py \
  --json-archive /path/to/canonical-authoring-json.zip \
  --yaml-archive /path/to/canonical-authoring-yaml.zip \
  --output-dir /tmp/compiled-scapng \
  --report /tmp/compiled-scapng-report.json
```

The compiler verifies native source graphs and compiled Test/result programs.
It does not execute a live scan; signing and publisher trust are separately
specified. Consult the [tool index](../../tools/HUMAN-RUNNABLE-SCRIPTS.md)
for source package and single-serialization development modes.

## Coverage evidence required before retiring 0.3 modules

For each newly supported construct, pin original OVAL and XCCDF sources;
assert exact field operations, existential/value quantifiers, criteria and
Filter/Set sequencing; test negative cases; compare source→0.4 and 0.4→OVAL;
run schema and native compiler checks. Record coverage numerator,
denominator, blocked cases and scanner-unproved cases separately. Retain the
old source-lowering path until its replacement demonstrably covers it.
