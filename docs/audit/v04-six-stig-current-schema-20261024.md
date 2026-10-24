# Six-STIG current-schema regeneration checkpoint — 2026-10-24

**Status: blocked on one source-semantic review. No replacement package released.**
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
- The existing reversible, explicit legacy-review adapter processes 4,011 of
  4,012 documents in memory with exact inverse. The remaining document fails
  closed; no output archive is written. Counts: 990 structured Test conversions,
  399 presence-only conversions, and 207 source-retained Test `all_exist`
  normalization diagnostics. These are *not* full-schema or scanner passes.
- Separately, the maintained original-OVAL production CLI acceptance script
  passes four pinned Linux/Windows definition cases; the focused approved
  pipeline passes five tests. Neither is a full six-STIG original-source sweep.

## One exact blocker: Oracle Linux 9 SV-271844

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
`stderr_line: {values_found: none}`. The current adapter correctly refuses
to discard the regex operand without a reviewed semantic/provenance rule.

**Owner review question:** For this *exact pinned source shape*, is it
acceptable to normalize the OVAL entity's `none_exist` plus universal `.*`
matcher to comparator-free `values_found: none`, retaining the full original
State, comparator, Test attributes and rationale in migration provenance?
This must be justified for present/absent, empty-value, incomplete, error,
and unknown collection boundaries; do not generalize to arbitrary regexes.

If accepted: add one source-pinned positive fixture and negative mutations,
implement the narrow reusable converter rule (no schema alias), rerun the
4,012-document YAML/JSON migration, strict schema, reference closure, six
native `.scapng` builds, deterministic rebuild, and source-accounting ledger.
Rebuild from pinned original SCAP 1.4 next; the archive bridge by itself is
not a fresh original-SCAP conversion or scanner parity proof.

The diagnostic runner is `tools/migrate_v04_six_stig_review_archive.py`, with
focused regressions in `tools/test_migrate_v04_six_stig_review_archive.py`.
It rejects source SHA drift, input YAML/JSON divergence and incomplete output.
