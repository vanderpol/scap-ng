# OVAL 5.12.3 datatype × operation conformance matrix — research checkpoint

**Status:** normative OVAL source matrix / proposed SCAP-NG conformance fixture plan, **not an adopted new authoring syntax**.  
**Issue:** [#200](https://github.com/vanderpol/scap-ng/issues/200)  
**Pinned reference:** [OVAL 5.12.3 common schema](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-common-schema.html), SimpleDatatypeEnumeration and ComplexDatatypeEnumeration. This is a supported-operation matrix from authoritative datatype prose, **not** a claim that the dynamic evaluator currently passes each case. Verify any differences with pinned XSD/Schematron and capability-specific fixed datatypes before coding.

Abbreviations: `eq` equals; `ne` not equal; `gt/ge/lt/le` ordered comparisons; `ci_eq/ci_ne` case-insensitive; `regex` pattern match; `band/bor` bitwise operations; `subset/superset` IP inclusion.

| Native datatype | Source OVAL datatype | Allowed operations | Required implementation behavior |
| --- | --- | --- | --- |
| string | string | eq, ne, ci_eq, ci_ne, regex | Keep lexical type, regex implementation and flags |
| boolean | boolean | eq, ne | OVAL lexical boolean spellings are imported into native booleans, not string truth |
| integer | int | eq, ne, gt, ge, lt, le, band, bor | Arbitrary mathematical integers; never treat bool as int |
| float | float | eq, ne, gt, ge, lt, le | IEEE-754 single-precision interpretation; preserve INF, -INF, NaN source semantics |
| binary | binary | eq, ne | Hex-encoded lexical content represents decoded bytes |
| version | version | eq, ne, gt, ge, lt, le | Numeric components, separators, zero-pad trailing components |
| ipv4 | ipv4_address | eq, ne, gt, ge, lt, le, subset, superset | Compare masked address+prefix; relational prefix mismatch → error |
| ipv6 | ipv6_address | eq, ne, gt, ge, lt, le, subset, superset | Same prefix semantics and mismatch error as IPv4, 128 bits |
| rpm_evr | evr_string | eq, ne, gt, ge, lt, le | RPM epoch/version/release comparator; NOT decimal or SemVer |
| debian_evr | debian_evr_string | eq, ne, gt, ge, lt, le | Debian package-version comparator, including tilde and epoch |
| fileset_revision | fileset_revision | eq, ne, gt, ge, lt, le | Fileset version ordering; native execution parity needs proof |
| ios_version | ios_version | eq, ne, gt, ge, lt, le | Cisco IOS train version semantics; native parity needs proof |
| record | record | eq | Typed record fields, repeated fields and cardinality; variables may not use record as source OVAL datatype |

**Important:** This table is the COMMON datatype/operation upper bound. An individual OVAL entity may narrow allowed datatypes/operations further. Object selectors, State predicates and record children have distinct contracts, and the pinned OVAL Schematron additionally constrains `var_ref` source effective datatype. Do not turn this table into a blanket permission for arbitrary capability fields.

## Minimal proof fixtures to implement next

Each fixture must record **source OVAL XML/typed IR**, expected effective datatype, authored candidate YAML, canonical compiler output, and independently justified expected evaluator result. Both positive and negative source cases are necessary. The scanner test suite must not compute its expected outcome using the function under test.

| Case | Authored candidate | Canonical OVAL meaning | Expected result or gate |
| --- | --- | --- | --- |
| Textual string `'01'` vs `'1'` | `value: '01'; operation: equals` | `string / equals` | false against collected `'1'` |
| Numeric `1` vs collected text `'01'` | `value: 1; operation: equals` | `integer / equals` | true when OVAL Item→State cast succeeds |
| Invalid numeric cast | `value: 1; operation: equals` | `integer / equals` | error for collected `'abc'`, not false |
| Version equality | `value: '1.0'; operation: version_equals` | `version / equals` | true against `1.0.0` |
| Version ordering | `value: '2.9'; operation: version_greater_than` | `version / greater than` | true against `2.10` where observed comes first |
| RPM epoch | `value: '0:99.0-1'; operation: greater_than; compare_as: rpm_evr` | `evr_string / greater than` | observed `1:2.0-1` compares greater |
| Debian tilde | `value: '1.0~rc1'; operation: less_than; compare_as: debian_evr` | `debian_evr_string / less than` | source/target orientation must be asserted |
| IPv4 relational bad prefixes | `value: '192.0.2.0/25'; operation: greater_than; compare_as: ipv4` | `ipv4_address / greater than` | ERROR against observed `192.0.2.0/24`, not false |
| IPv4 inclusion | `value: '192.0.2.0/24'; operation: subset_of; compare_as: ipv4` | `ipv4_address / subset of` | verify observed-vs-expected direction |
| Typed Variable binding | `value: {variable: v}` with resolved type | OVAL `var_ref` with matching datatype | mismatch rejected at compile/migration validation |
| Empty/mixed array | typed explicit list | OVAL `var_check` + State `entity_check` | preserve original cardinality, errors and quantifiers |
| Nonfinite float | source `INF/-INF/NaN` | OVAL `float` special lexical values | **Known native representation gap. No silent coercion or successful parity claim** |

## Design checkpoint

**Do not add 48 new operators to normative syntax simply to avoid optional type metadata.** In the research prototype, test minimal `version_*` operators plus `compare_as` for specialized families against an entirely optional `compare_as` design; measure authoring footprint, encoder/decoder complexity, and exact canonical round-trip. Compare both against the supported-operation matrix above. Keep the canonical compiled form explicitly typed regardless of human-friendly syntax.

No 0.3 production converter/schema change until all 13 families can be represented losslessly and invalid combinations fail closed; then run Self-Assertion, representative six STIGs and, at deliberate release checkpoint only, the 65-source corpus. A green structural round-trip does **not** prove collected-Item evaluator behavior.
