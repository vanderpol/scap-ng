# RPM file-verification converter checkpoint

Tracking [#251](https://github.com/vanderpol/scap-ng/issues/251).

A pinned nondeprecated original now exercises `linux.rpmverifyfile` through the
existing converter's mapped selectors and shared source-behavior engine. No
new capability-specific lowering, schema, compiler or normative syntax is added.
Activation increases from 48 to **49/51** approved-platform mappings (**49/100**
globally); construct support remains bounded, not a runtime collector claim.

[The original OpenSCAP Test and proof packet](../../tests/fixtures/v04-direct-rpmverifyfile/README.md)
are pinned at upstream `099cd84a0fa23c0e5d748e4e577c900c9b280623`.
Test `oval:x:tst:1` and its complete Object graph pass original OVAL 5.12.3
XSD/Schematron with no deprecation reports, preserving source bytes and IDs.
The generated native authoring passes schema/dataflow/field-requirement checks;
compilation and compiled-bundle schema, graph, integrity and operand checks pass.
Independent source/native typed semantic terms match.

All eleven verification switches are explicit Boolean acquisition parameters.
In particular, omitted `noconfigfiles` retains the original false default.
Neither the empty pattern selectors nor the literal filepath is normalized.
A frozen approved identity/default crosswalk extends the existing independent
scalar reader; it does not import the converter's mapping/lowering helpers.
The constructed compiled-package wrapper is shared with YAML regression tests.
The original Assessments and every YAML conversion receipt remain unchanged.

Verification:

- **27 focused regressions pass**, zero failures/errors/skips: five new RPM,
  eight YAML, seven diagnostic, six scalar-batch and the 100-contract parity gate.
- Each of the eleven native switches has a mutation check. Source default/Boolean
  lexical tests, supported `filedigest_differs: not performed`, deprecated MD5,
  invalid Boolean and foreign/unknown selector/behavior negatives fail closed.
- All **100** capability contract parity hashes are unchanged; no baseline edit.
- Self-Assertion remains **521 compiled/term-proved**, **519/803** additionally
  original-valid/nondeprecated. All previous 521 source/native terms, proof IDs
  and compiled program hashes are unchanged; zero mismatches.
- Configured inventory is now **713**, formerly 710. The three added cases are
  the original deprecated `md5_differs` Tests in
  `linux/linux-def_rpmverifyfile_test.xml`, IDs
  `oval:navy.navwar.niwcatlantic.scc.test:tst:1`, `:2` and `:3`. They remain
  rejected, not newly converted or source-repaired. The
  original corpus remains 803 Tests.
- The separate OpenSCAP cohorts are YAML **45/51** and RPM **1/1**. Their valid
  original-source evidence is not added to NIWC production Rule coverage.
- None of the six primary source inventories requires `linux.rpmverifyfile`;
  the existing **1,012/1,396** Rule/program proof floor is unchanged.

Hosted exact-head maintained regression and six-source workflow conclusions
are recorded in the #251 handoff after CI. Scanner/RPM execution, actual host
file integrity, full applicability and release readiness remain unproved.
SSHD's nil/default-path contract and missing original SQL512 evidence keep those
two capability names inactive. Canonical function production activation,
incomplete-result aggregation, float handling and invocation fan-out retain
their existing coordinated #255/#218 boundaries.
