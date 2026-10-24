# Six-STIG current-schema regeneration checkpoint — 2026-10-24

**Status: owner-approved narrow source correction applied; all 4,012 YAML and
JSON documents pass current 0.4.0 schemas; all six native 0.4.0 content bundles
compile with YAML/JSON byte parity. Scanner and signing are not verified;
no replacement package released.**
Refs #232, #233, #251. Base `main`: `6514d7195faab384ed0f198592f6f241388171c4`.

## Verified inputs and results

- The previously released 2026-10-22 six-STIG authoring ZIPs are immutable:
  JSON SHA-256 `f481ff109b1f6abfda2d7f115e3140f4e82429517e4adc8cf9de00733180d8f5`;
  YAML SHA-256 `d7a989c66f32c8ea7af4c6e3355847da2d39d23b82366ce3f323cd71d4a6c5c1`.
- Review inventory: 4,012 documents, YAML/JSON parsed parity PASS, 1,567 Rules,
  1,550 manual Assessments, 883 automated Assessments, 1,390 Tests.
- Validation against *current* `schema/v0.4.0`: all 883 automated Assessment
  documents fail (old `require.items` / `all_items_must`, or old scalar `require`
  and `states`); all 1,567 Rule and 1,550 manual Assessment documents pass.
  The current native compiler rejects the first Apache Assessment. Thus the
  October 22 archive is **not** current-schema or current-compiler evidence.
- The initial adapter stopped at 4,011/4,012 documents without publishing
  incomplete output. After the owner-approved narrow correction, all 4,012
  documents migrated with checked inverse and YAML/JSON parsed parity.
  Strict independent full-schema checks passed **4,012/4,012 per format**, zero
  errors. The 883 changed automated Assessments contain 991 structured and 399
  presence-only Test conversions, with 207 source-retained Test `all_exist`
  normalization diagnostics. These are not original-OVAL/scanner passes.
- Separately, the maintained original-OVAL production CLI acceptance script
  passes four pinned Linux/Windows definition cases; the focused approved
  pipeline passes five tests. Neither is a full six-STIG original-source sweep.
- Native compiler accepts the complete migrated archive and emits six `.scapng`
  content bundles, with equal native bytes from JSON and YAML inputs. The
  compiler reports 3,573 programs and 5,365 Test references across the six
  benchmark packages; `scanner_evaluated: false` and
  `signature_verified: false` for each. Its package verifier checks manifest,
  exact content/program member inventory, hashes, source graph and Rule
  references. An entirely separate second full compilation produced all six
  bundles **byte-for-byte identical** to the first, and the JSON verification
  reports matched SHA-256. Bundle SHA-256 values (both runs):

  | Benchmark | Native bundle SHA-256 |
  | --- | --- |
  | Apache HTTP Server 2.4 | `f0dc8f1a2f7b1fbdc3dcedc2709b8bc2cd9f4827e93bf9d751708e02b153bc4e` |
  | Windows 11 | `fd6e8a15ca48979650a289dc0a9476d0f2abf365ddf342f4a08bb685180d2a3e` |
  | Windows Server 2025 | `c3b08d822ec363a6dadf2f3a3e430b7a3796a784a1f5f96475a4b70dc88577f4` |
  | Windows DNS | `82fdb4d0ea0bd614b799f2de595618a0511d31db600b25bdb5ab3568b28ec834` |
  | Oracle Linux 9 | `61e3336499c27f2f0deb635ebecc68344c18adb923cfad6e6466ba4dcc712b4b` |
  | RHEL 9 | `170b5013d90dbcb197e81b681eae5121ee923ab7c6b28a4f5784034059b5a809` |

## Approved source anomaly: Oracle Linux 9 SV-271844

Original NIWC `U_Oracle_Linux_9_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip`
SHA-256 `6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d`.
OVAL Definition `oval:navy.navwar.niwcatlantic.scc.rhel8:def:271844`,
Test `oval:navy.navwar.niwcatlantic.scc.rhel8:tst:27184401`:

```xml
<independent-def:shellcommand_test id="oval:navy.navwar.niwcatlantic.scc.rhel8:tst:27184401" version="5" comment="Confirm interactive user's home directories exist." check_existence="any_exist" check="all">
  <independent-def:object object_ref="oval:navy.navwar.niwcatlantic.scc.rhel8:obj:27184401"/>
  <independent-def:state state_ref="oval:navy.navwar.niwcatlantic.scc.rhel8:ste:27184401"/>
</independent-def:shellcommand_test>
<independent-def:stderr_line check_existence="none_exist" operation="pattern match">.*</independent-def:stderr_line>
```

The source-verified October 22 Assessment carries
`stderr_line: {field_requirement: none_exist, matches_regex: '.*'}`.
The approved 0.4.0 schema permits only **comparator-free** field absence:
`stderr_line: {values_found: none}`. On 2026-10-24 the owner identified `.*`
as likely erroneous/redundant source content and expressly approved removing
only this operand from generated NG. The exception is guarded by the exact
original SCAP ZIP SHA-256, Test/Object/State IDs and attributes, original
field text, rule path, Test ID, and entire old requirement. Positive and
negative regressions reject changes to this shape or to the source pin.
The migration report retains original and normalized requirements, original
OVAL attributes/text, hashes and the owner decision separately from content.
**The published original XML is not edited.**

Remaining: independent package-consumer acceptance, source/feature coverage
ledger and fresh original-SCAP import validation.
Absent/present/empty/incomplete/error/unknown scanner outcomes require later
independent execution; do not claim runtime equivalence from these tests.

The diagnostic runner is `tools/migrate_v04_six_stig_review_archive.py`, with
focused regressions in `tools/test_migrate_v04_six_stig_review_archive.py`.
It rejects source SHA drift, input YAML/JSON divergence, unrelated comparator
removal and incomplete output.
