# Datatype and comparison simplification — lossless-migration research

**Status:** research / candidate authoring grammar; **NOT** an adopted v0.3 schema change.  
**Issue:** [#200](https://github.com/vanderpol/scap-ng/issues/200). Owner requested impact research before adoption (2026-10-14).  
**Hard constraint:** SCAP 1.4/OVAL 5.12.3 technical truth, selection, typed conversions, errors, and SCAP policy meaning SHALL survive forward conversion. An intentionally deprecated/unsupported source construct is a visible blocker, never a silently altered Assessment.

## Evidence and reproducibility

Source: [owner-verified six-STIG authoring release](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-default-choice-af635ecf0255), ZIP `scap-ng-0.3-six-stig-authoring.zip`; SHA-256 `8dfbcf35d2fe61a370e6929d9a6399952e95150b0c37d7eaf7eef9e2a89cff3e`. Six NIWC-derived benchmarks: RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS, Apache HTTP Server 2.4 UNIX. The original NIWC pin is `8c8e5dff860af6b1290ee9273a282db24278f8d5`.

Run `python tools/research_datatype_operator_inventory.py scap-ng-0.3-six-stig-authoring.zip --report datatype-research.json` (PyYAML required). Counts include deeply nested inline Object/State predicates, shared Assessments, record fields, variable expression operands, and Variables. They are **authored occurrences**, not distinct Rules or independent checks.

| Classification | Occurrences | First-pass treatment |
| --- | ---: | --- |
| Native scalar `string` / `integer` / `boolean` literals with matching YAML type | 4,774 | Candidate to infer from explicit YAML scalar tag and compile to an explicitly typed canonical predicate |
| `version` scalar comparisons | 4 | Candidate typed comparison operators (including equality and ordering, not ordering alone) |
| Computed/derived Variable datatype declarations | 377 | Retain type contract until variable dataflow inference is proven |
| Referenced/computed `value:` objects | 64 | Resolve declared referenced Variable/Input type; do not infer from future runtime values |
| Literal value arrays | 48 | Analyze per-element types, cardinality, quantifiers, empty sets and mixed values before inferring |
| **Total** | **5,267** | **4,778 of 5,267 structurally rewritable in a conservative research trial; 489 held** |

Actual datatype counts: `string` 3,763, `integer` 919, `boolean` 581, `version` 4. In all 4,012 native YAML documents (2,433 Assessments, 1,567 Rules, six Benchmarks and six applicability catalogs), the 5,267 `datatype:` lines account for **152,041 bytes of 6,928,562 uncompressed YAML bytes (2.19%)**; ZIP savings cannot be inferred from that figure.

A **research-only in-memory** rewrite removed 4,774 literal declarations and represented four version comparisons with `version_greater_than_or_equal`; restoring those explicit types and original operations yielded **zero AST differences across all 4,012 source documents**. This proves a syntactic reversible mapping *for the classified fields only*, **NOT** JSON Schema validity of the proposed syntax, scanner behavior, OVAL runtime parity, target collector conformance, or support for every valid OVAL datatype.

There are **116 string-valued predicates with numeric- or Boolean-looking literals**. E.g. Windows 11 `SV-253255` compares record fields to the **strings** `'True'`; another applicability predicate compares domain role to **string** `'1'`. YAML source spelling and quoting must not be casually normalized into `true` or `1`.

## Source-backed examples and nonnegotiable behavior

### Ordinary numeric comparison

Windows 11 `SV-253264`, `windows-use-antivirus-program-test`, has `value: 4096`, `operation: bitwise_and`, `datatype: integer`. Candidate authoring removes the last field, relying on the native **integer** YAML value; compiler emits exactly the original typed bitmask predicate.

### A real version comparison

Apache `SV-214273`, `apache-usertrack-module-enabled-test`, compares `value: '2.4'`, `operation: greater_than_or_equal`, `datatype: version`. Candidate:

```yaml
value: '2.4'
operation: version_greater_than_or_equal
```

The compiler SHALL lower this to exactly the original OVAL-compatible version ordering. **Do not use SemVer ordering.** OVAL version supports arbitrary non-numeric single-character component separators and pads missing trailing numeric components with zero: `1.0` and `1.0.0` are *version-equal*, not string-equal. Version **equality and inequality** therefore also require typed semantics.

### The real counterexample to datatype-free runtime inference

Windows 11 `SV-253255` expects a cmdlet's `tpmpresent`, `tpmready`, and `tpmenabled` as strings `'True'`. Using the scanner's apparent Boolean interpretation changes content truth or may change casting errors. Explicit YAML string values can carry this intent, provided the authored grammar and compiler preserve the parsed scalar type.

OVAL System Characteristics `datatype` describes **collected storage**, whereas the authored OVAL State datatype determines **comparison interpretation**. An Item holding Registry `REG_SZ` text `"10"` can validly be tested by a State with integer `<= 10`; cast success is true, cast failure is **error**, not false. The authoring compiler must freeze the target comparison type; the scanner must not choose it based on runtime Item storage. See [existing parity issue #201](https://github.com/vanderpol/scap-ng/issues/201).

### Different valid OVAL datatypes require different algorithms

The six-STIG sample has **no** explicit `rpm_evr`, `debian_evr`, `ipv4`, `ipv6`, `binary`, `float`, `ios_version` or `fileset_revision` predicates. **Their absence here does not allow dropping them for SCAP 1.4 losslessness.**

- RPM `evr_string` and Debian `debian_evr_string` have distinct package-version orderings, not standard version or string ordering.
- OVAL IPv4/IPv6 comparisons operate on address/prefix pairs, not simple strings. A relational comparison where prefix lengths differ **must raise an error**; prefix subset/superset compares included address ranges. A typed operator such as `ipv4_subset_of` is not interchangeable with generic `subset_of` absent explicit type.
- Hex-encoded `binary` equality compares decoded bytes, not simply character text.
- OVAL `float` accepts lexical special values `INF`, `-INF` and `NaN`. Current native 0.3 finite JSON-number validation does **not** represent these directly: an **existing migration coverage gap** requiring a lossless special-value representation, or an explicit documented unsupported-source blocker, independent of this author's simplification. Arbitrary-precision OVAL integer and IEEE-32-bit OVAL float interpretation also warrant runtime range/precision tests.
- `record` has structured, repeatable, typed child-field semantics and only OVAL `equals` for the parent. The native record container can imply the parent type, but field types and duplicate-name aggregation cannot be discarded.

The six-STIG Variable census includes **377 type declarations on computed/typed Variables**, among them a shared Linux Audit Variable declared `datatype: string` whose expression uses `arithmetic.multiply`. This is an important **audit case**, not proof of a source defect: expression shape alone is not evidence of its declared output datatype or the source's effective cast semantics.

## Design options and impacts

1. **Ordinary operations + native YAML/capability type inference + specialized typed operators**. Proposed authoring grammar for typical literal predicates. Potentially eliminates 4,778 repeated datatype fields in these six STIGs. Typed operators must cover equality and ordering for all specialized OVAL comparison datatypes, not just `version_greater_than`; generated enum growth and mixed nested predicates need review.
2. **Ordinary operations + optional `compare_as` only for ambiguity or specialized types**. Fewer operation names and less operator-enumeration complexity, but reintroduces a separate field for the rare cases and still needs deterministic default rules.
3. **Retain explicit `datatype` in canonical compiled source and Scanner IR only**. Compatible with either authoring surface; keeps critical type semantics, deterministic validation, interop and lossless OVAL re-emission without forcing repetition on humans.

**Operator vocabulary scale:** OVAL's five version-like families (`version`, RPM EVR, Debian EVR, IOS version and fileset revision) each need up to six comparison forms (30); IPv4 and IPv6 each need up to eight including subset/superset (16); binary equality/inequality adds two. Naming every one as a distinct typed operator would introduce **up to 48 special forms** beyond ordinary operators, before float exceptional values or other future datatypes. This is a genuine authoring-versus-specification simplicity tradeoff. One alternative is `version_greater_than` for the common case and explicit `compare_as` for rarer families; another is a generic `compare` block with a typed operator modifier. **Do not select a hybrid merely from source frequency**; it must be deterministic, lossless and readable for unsupported/rare-but-valid OVAL constructs.

**Provisional synthesis, not an implementation decision:** Compiled canonical representation SHALL continue carrying explicit effective comparison types. For human authoring, basic YAML scalars can often make the type explicit without a redundant key; typed operations (or a narrowly scoped `compare_as`) are needed for specialized type interpretation. For untyped variable references, ambiguity, mixed/empty arrays, result-only Items, and function result types, explicit type contracts remain until a proven inference algorithm exists.

The **compiler**, not the eventual scanner, SHALL resolve all authored sugar to an unambiguous canonical typed predicate. Where inference cannot be proven unique, compilation fails with source location and expected/actual types. Never silently select the first eligible datatype; never automatically apply permissive runtime conversion to resolve authored ambiguity. Normal runtime Item-to-expected-State casts remain governed by the OVAL specification.

### Implementation surfaces affected *if accepted*

| Layer | Required change |
| --- | --- |
| Native authoring JSON Schema | Define scalar-inference grammar and small typed-operator enum; keep versioned source schema distinct from canonical compiled contract |
| Import/conversion (`native_capability_mapping.py`, `assessment_oval_vocabulary.py`) | Stage 1 retains exact legacy effective datatype, operation, defaults and lexical provenance; Stage 2 desugars to readable authoring only after equivalence is demonstrable |
| Static validator (`validate_generated_capability_semantics.py`) | Enforce typed operation applicability, fixed capability field types, Variable/Input identity/datatype matching, missing/ambiguous/mixed values and unknown operations |
| Compiler, signed bundle and manifest | Emit and bind explicit canonical datatype+operation, so scanners never infer from collected Items or filenames |
| Result interpreter/evaluator | OVAL-specific comparison and casting, error/unknown propagation, integer precision, float specials, version/package algorithms and CIDR prefix errors |
| Round-trip exporter and Self-Assertion | Reconstruct source-equivalent OVAL typed values/operations; prove true/false/error/unknown outcomes and item populations, not merely identical ASTs |
| Editor and docs | Show simple operators first; expose specialized comparisons and typed dynamic-input constraints where necessary |

**No native 0.3 schema, converter, compiler, benchmark or release asset is changed by this research.**

## Mandatory verification before any normative change

- Golden corpus: all non-deprecated OVAL 5.12.3 datatype/operator legal pairs and deliberately illegal pairs, extracted from *pinned* XSD/Schematron rather than guessed. Include all 13 native datatype categories, fixed capability field types, Object selectors, States, nested record fields, Variables, external Organizational Inputs and literal Components.
- Adversarial assertions: `'1'` vs `1`, `'True'` vs `true`, leading-zero strings, numeric strings collected by registry/cmdlet/shellcommand, `1.0` vs `1.0.0` version equality, mismatched CIDR prefix relational comparison → error, RPM/Debian epochs, bad package versions, bad numeric casts → error, binary hex equality, nonfinite floats and huge integers, empty/mixed multi-values and quantifiers.
- Dataflow: static source OVAL `var_ref` datatype equality constraint, runtime Item→State cast, literal/constant/local/external Variables, typed derived functions, `for_each`, filters, Set expressions, XPath/regex selectors and direct input bindings.
- **Proof gates in order:** (1) lossless SCAP 1.4 XML parsing/XSD/Schematron; (2) canonical IR; (3) readable authoring lowering; (4) reversible canonical desugaring; (5) exact migrated Assessment/Rule/Benchmark identity and source provenance; (6) full schema/semantic/package validation; (7) OVAL Self-Assertion expected evaluator outcomes and error statuses; (8) six-STIG conversion/compilation, then intentional **65-source** release gate; (9) independent actual-target scanner/collector conformance evidence. Keep stage verdicts separate.
- **Rollback policy:** Any non-bijective valid source construct stays in explicit canonical form or fails conversion visibly; never silently adjust source checks to force output. Existing non-convertible `independent.sqlext` and deprecated OVAL constructs remain independent tracked blockers, not implicit exceptions to the datatype preservation rule.

## Authorities

- [OVAL 5.12.3 common datatypes and operations](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-common-schema.html) (including version, package, float and CIDR rules).
- [OVAL 5.12.3 System Characteristics item types and casting](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-system-characteristics-schema.html).
- [OVAL 5.12.3 Definitions, Variables and expression semantics](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html).
- [Current SCAP-NG conversion crosswalk](../../../tools/scap_upconvert_v003/native_capability_mapping.py), [OVAL typed-variable conformance matrix](oval-variable-coverage.md), [OVAL 5.12.3 → NG](../../../specification/migration/oval-5.12.3-to-ng.md), and [SCAP-NG native capability predicates](../../../schema/v0.3.0/capability-common.schema.json).


## Reversible syntax prototype — 2026-10-14

**Correction to the initial inventory:** of the 4,774 ordinary-looking
typed scalars, 246 are typed values without a comparison operation. They
may be Variable or other noncomparison declarations; removing those types
without a separate proof risks changing source semantics. The first
prototype retains those 246 and all other noncomparison declarations.

- **[Research-only reversible codec](../../../tools/research_type_syntax_codec.py)**
- **[Focused expectations and negative tests](../../../tools/test_research_type_syntax_codec.py)**
- **[Six-STIG CI and attached reports](../../../.github/workflows/research-datatype-authoring-prototype.yml)**

### Implemented experimental choices

| Strategy | Ordinary YAML scalar | Version | RPM / IP / other specialized types |
| --- | --- | --- | --- |
| hybrid | infer native scalar value type | version_equals | compare_as: rpm_evr |
| typed-operators | infer native scalar value type | version_equals | rpm_evr_equals |
| compare-as | infer native scalar value type | compare_as: version | compare_as: rpm_evr |

The codec never decides comparison type from values collected by a scanner.
Every representation converts back to the same explicit canonical
typed comparisons. All options and their names are **research only**.

### Conservatively proved structural results

All three strategies reconstruct the canonical typed AST for the
identical pinned six-STIG ZIP (4,012 YAML documents) with **zero mismatches**.

- 4,528 ordinary typed scalar comparisons inferred unambiguously from
  the parsed YAML scalar type;
- four version comparisons expressed by specialized operation or
  optional comparison-type modifier;
- 623 noncomparison datatype declarations left explicit (377 without
  values plus 246 with values and no comparison);
- 112 dynamic-reference or array-valued declarations left explicit;
- 4,532/5,267 = **86.0%** of authored datatype declarations removed
  in this conservative research prototype, not the broader 90.7%
  theoretical figure.

The suite checks legal type/operator combinations across all 13 native
datatype families, explicit string versus integer/Boolean values,
integer-literal float comparisons, dynamically referenced values,
array/record constraints, unknown operations, and invalid comparison
types. This is **AST structural preservation**, not proven OVAL
expected-result equivalence, migration XML round-trip, or live scanner
evaluation. The current OVAL nonfinite float gap is explicitly
rejected and must be solved before claiming universal SCAP 1.4 losslessness.

Authoritative operation semantics are described in the
[OVAL 5.12.3 Core Common schema](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-common-schema.html).
Capability-specific constraints remain a separate required verification
beyond common datatype support. See the next-stage expected-result and
runtime test plan earlier in this report.
