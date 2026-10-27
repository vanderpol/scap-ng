# Direct converter continuation: 42 enabled capabilities

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) and
[#248](https://github.com/vanderpol/scap-ng/issues/248), from the published
[owner-approved selector correction](https://github.com/vanderpol/scap-ng/commit/6f2e9d0992c70981fa7ef42a58fc1e11012147bb).
The existing visitor and CLI remain authoritative. No normative schema,
capability mapping, original XML, compiler or scanner change.

Seven ordinary mappings use activation and independent frozen proof data:
`linux.apparmorstatus`, `linux.dpkginfo`, `linux.kernelmodule`,
`linux.rpmverifypackage`, `windows.sid`, `windows.sid_sid`, and
`windows.wuaupdatesearcher`. Their seven unmodified original files contain
32 Tests: 28 prove and compile; two ordered Debian EVR comparisons, one generic
Test `all_exist`, and one datatype cast remain blocked. The last case also has
an original invalid State/Variable binding. Every admitted closure separately
passes original XSD/Schematron; the invalid source file is preserved.

The eighth mapping, `independent.unknown`, uses the approved fixed-result
contract with canonical structured `require`, no Object, and no authored result.
Original Test `oval:org.mitre.oval.test:tst:939` proves and compiles. Legacy count
controls do not govern its fixed unknown result. Unknown source provenance:
OVAL-Community/SCAP-Self-Assertion at
`e3538595c5083b9c34d937a81d319234df9bbfaa`,
`SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_unknown_test.xml`, SHA-256
`f5e8901c703438819f20ef4761d1b4f9f62f630c6c8e96ca016d0d0dd67862a7`.

Shared logical conversion now retains `ONE` and `XOR`, including singletons.
Field/record `all_exist` retains `every`; this does not broaden the separately
restricted generic Test `all_exist` normalization. Record members still reject
`check_existence`, absent from their original grammar. Controlled variations
exercise those boundaries without changing the original fixtures.

Validation: 3,166 maintained tests, zero failures/errors, one existing skip.
All 100 generated contracts remain unchanged from the approved correction.
All 1,001 existing six-source primary program hashes remain identical. Three
additional Windows 11 account Rules prove through SID identity predicates;
the [receipt](v04-direct-continuation-42.json) identifies each. Primary total:
1,004/1,396, with 171 manual/OCIL-only Rules separately inventoried. The original
803-Test corpus retains all 318 configured proofs/program hashes and adds 29:
347 proved, 368 compiled among 662 configured Tests. Diagnostic conversions
outside configured admission are not accepted packages.

Reproduction (Python dependencies and source pins as in the maintained CI):

```bash
PYTHONPATH=tools python -m unittest test_v04_direct_ordinary_continuation test_v04_direct_shared_controls -v
PYTHONPATH=tools python tools/run_current_tool_regressions.py --report /tmp/current-regressions.json
PYTHONPATH=tools python tools/audit_v04_oval_test_corpus.py --source-root ORIGINAL_OVAL_TEST_CONTENT --output /tmp/corpus.json
PYTHONPATH=tools python tools/verify_v04_direct_scope.py --inputs ORIGINAL_SIX_ZIPS --output /tmp/direct-six
```

The maintained regression workflow supplies original-source environment paths;
see [its exact environment](../../.github/workflows/rebaseline-smoke.yml).
The [CLI guide](../developer/DIRECT-V04-CONVERTER.md) describes verified conversion.
Applicability remains unproved; this is no scanner-runtime, release or production
equivalence claim. Nine approved capability routes remain to finish, listed in
the receipt. Further work is stopped at the
[multi-algorithm hash acquisition conflict](v04-filehash-acquisition-conflict.md)
for the owner decision required by #251. Repository separation under #254
remains deferred.
