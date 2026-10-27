# Generic capability batch and six-source acceptance — #251

Base: `b225b7eba0ab53d4722348bd77017c30efc9705d`. This batch enables
`unix.password`, `unix.sysctl`, `linux.partition`, `linux.systemdunitproperty`
and `independent.family` through existing generic conversion. The activation
list is now data, not a Python tuple. No new capability-specific conversion
algorithm, normative schema change or Rule-ID branch was needed.

The independent scalar reader uses frozen, hash-checked approved field identities,
not converter calls. Original XML supplies all predicates, quantifiers and
dependencies. Unknown fields, namespaces, mapping edits and system selectors fail
closed. Password fields come from the pinned original XSD. Primitive `int` /
`integer` labels are compared consistently without erasing Variable cast boundaries.
Enum regex operands remain patterns rather than being mistaken for literal enum
members; regex over renamed value domains remains blocked.

| Original source | Primary closures proved and compiled | Manual/OCIL | Blocked or unverified |
| --- | ---: | ---: | ---: |
| RHEL 9 | 176 | 27 | 242 |
| Oracle Linux 9 | 173 | 40 | 235 |
| Windows 11 | 218 | 11 | 28 |
| Windows Server 2025 | 249 | 30 | 12 |
| Windows Server DNS | 0 | 40 | 41 |
| Apache 2.4 UNIX | 0 | 23 | 22 |
| **Total** | **816** | **171** | **580** |

This covers 816/1,396 original OVAL-bearing Rules (58.45%) at the primary-OVAL
level. It is the first full primary-source acceptance measurement, not a claim that
all 816 cases were unlocked by these five capabilities. All prior 249 Server
2025 program hashes match exactly. Every accepted closure passes original
XSD/Schematron, current authoring validation, independent original-source terms,
native compilation and independently checked compiled operands. Only proved
closures enter the four generated subset packages. YAML and JSON are emitted
from the same native documents. Applicability/CPE remains separately inventoried
and unproved; these packages are **not complete policy equivalents**.

The configured 803-Test corpus now attempts 220 Tests, compiles 173 and proves
156 (previous 190 / 144 / 127). The wider diagnostic probe compiles 298 and proves
156 (previous 297 / 133). Its 131 unsupported proofs and 11 mismatches remain
visible; diagnostic compilation never admits unproved content. Twelve new focused
tests pass, including original-source, datatype/existence, namespace, selector,
mapping-contract, proof-retention and compiled-operand mutations. A pinned floor
fails CI if any of the 816 accepted proofs or programs is lost or altered;
additional proved Rules are permitted. At implementation `44254953b`, all ten
triggered hosted workflows pass. [Mandatory CI](https://github.com/vanderpol/scap-ng/actions/runs/40495471292)
passes **3,130 tests, zero failures/errors, one existing skip**. The local full
run passed 3,129 tests; three missing-XSD-link skips passed in a supplemental run,
as did the subsequently added retention test. Exact selection and both verified
artifact digests are in the [machine report](v04-direct-capability-batch.json).

DNS/Apache retain all 63 broken original catalog bindings. Source-invalid,
deprecated WMI and unresolved `all_exist` cases stay blocked. Three Windows 11
Registry closures require independent `xsi:nil` acquisition proof and are excluded.
No source repair, missing-condition suppression or new normalization is applied.

Reproduce with Python 3.12, PyYAML 6.0.3, jsonschema 4.25.1 and lxml 6.1.1:

```sh
PYTHONPATH=tools python -m unittest test_v04_direct_scalar_batch test_v04_direct_unix_password -v
python tools/verify_v04_direct_scope.py --inputs /path/to/pinned/Current --output /tmp/new-primary-proof
python tools/audit_v04_oval_test_corpus.py --source-root /path/to/OVAL_Test_Content --output /tmp/corpus.json
```

The converter itself grows by three nonblank/noncomment lines; the expanded
existing proof modules grow by 21 lines and the new shared independent scalar
reader has 93. Acceptance CLI/test code is recorded separately in machine evidence.
No specialized conversion branch was added for these five capabilities.

Source ZIP hashes are in the machine report and
[six-source lock](../../tests/fixtures/v04-direct-six-sources.json). Full Rule
outcomes, source validity, programs and generated packages are workflow artifacts.
[Actual UNIX password YAML/JSON](../examples/direct-unix-password/README.md) and
[six original Rule fixtures](v04-unix-password.md) make the new behavior browsable.
Next: shared file acquisition/traversal and RPM metadata, followed by complete
original applicability proof. This checkpoint does not certify scanner behavior
or a production release.
