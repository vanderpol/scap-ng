# Original RPM file-verification evidence

The complete, byte-exact original is
[OpenSCAP's RPM verification probe Test](https://github.com/OpenSCAP/openscap/blob/099cd84a0fa23c0e5d748e4e577c900c9b280623/tests/probes/rpm/rpmverifyfile/test_probes_rpmverifyfile.xml),
pinned at `099cd84a0fa23c0e5d748e4e577c900c9b280623`.
[Provenance](provenance.json) records its upstream Git blob and SHA-256.
The original generator version and IDs are unchanged.

Original Test `oval:x:tst:1` and its complete Object closure pass OVAL 5.12.3
XSD/Schematron with no deprecation diagnostics. It selects `/usr/bin/true`
with original empty-pattern package selectors. Ten verification switches are
explicitly true; omitted `noconfigfiles` defaults to false. The converter
materializes all eleven approved native Boolean parameters through the existing
shared source-behavior engine. No dedicated RPM conversion implementation,
new grammar or schema change is needed.

The [receipt](conversion-evidence.json) binds this original Test to source/native
semantic terms and a native compiled program. Tests validate source preservation,
exact dependency identities, native authoring, compiled operands, and a compiled
bundle's schema/graph/integrity in an explicitly constructed packaging wrapper.
An independently frozen crosswalk lets the existing scalar proof reader check
selectors, defaults, supported State fields and Boolean parameter types without
importing the renderer. The shared fixture wrapper is test infrastructure, not
an original production Benchmark or Rule.

Negative regressions change each of the eleven native switches, retain the
source's empty regex versus literal filepath, reject unknown/nonboolean source
behaviors and deprecated `nomd5`, and distinguish supported string
`filedigest_differs: not performed` from `pass` or Boolean success. The State
regression is an explicitly constructed derivative, not a second original Test.
Original deprecated Self-Assertion `md5_differs` cases stay unsupported; no
source repair, substitution or increased proof count is claimed for them.

This adds **one separately counted public probe Test**. It is not part of the
803-Test Self-Assertion denominator or NIWC production Rule coverage. Source/
native typed terms and compiled operands do not establish host RPM verification,
collector execution, file integrity or scanner-runtime equivalence.

```bash
PYTHONPATH=.:tools python -m unittest test_v04_direct_rpmverifyfile
```
