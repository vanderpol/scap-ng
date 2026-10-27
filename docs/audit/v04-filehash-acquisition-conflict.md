# Owner decision required: multi-algorithm hash acquisition

> **2026-10-27 schema-first disposition (#255):** The owner subsequently
> authorized a systematic 0.4 capability-mapping/schema correction, with Codex
> continuing converter work separately. The resulting schema-review candidate
> maps `hash_type` to the native `algorithm` selector and accepts explicit
> literal-array / Variable-reference quantifiers over the six-algorithm domain.
> [Full before/after, 100-capability audit and integration limits](v04-modernization-schema-reconciliation-20261027.md).
> The original converter is **still inactive** for these cases; scanner and
> source-result equivalence remain unproved. The investigation below is retained
> verbatim as the conflict evidence at the earlier `041be96` checkpoint, not as
> the updated candidate's mapping contract.

2026-10-27 investigation under
[#251](https://github.com/vanderpol/scap-ng/issues/251). Status: unresolved;
`file.hash` stays inactive. The exact-alternative approval did not authorize
changing this acquisition contract. No schema, mapping, original source,
compiler or scanner has been modified.

## Original counterexample

The [unmodified original UNIX fixture](../../tests/fixtures/v04-filehash-acquisition-conflict/ind-def_filehash58_test_unix.xml)
and [provenance](../../tests/fixtures/v04-filehash-acquisition-conflict/provenance.json)
pin OVAL-Community/SCAP-Self-Assertion commit
`e3538595c5083b9c34d937a81d319234df9bbfaa`, original SHA-256
`fee16d02756928ee1606921370d244fdb4d8c700db2c706443583e86cb7d38cf`.
The complete file passes original OVAL 5.12.3 XSD and Schematron validation.

Test `oval:org.mitre.oval.test:tst:305`, `check="all"`, references Object
`oval:org.mitre.oval.test:obj:313` and State
`oval:org.mitre.oval.test:ste:531`. Object acquisition includes:

```xml
<path>/bin</path>
<filename>ls</filename>
<hash_type var_ref="oval:org.mitre.oval.test:var:429"
           var_check="at least one"/>
```

Constant Variable 429 contains **MD5 and SHA-1**. Its State separately uses
Variable 761 (SHA-224, SHA-256, SHA-384, SHA-512) with `var_check="none satisfy"`.
Test 544 uses Object 105 with that four-value Variable and `none satisfy` in
**acquisition**; Test 354 uses Object 421 with the four-value Variable and
`at least one`. Object and State controls cannot be exchanged or discarded.

## Current target and exact gap

The approved [file.hash mapping](../../schema/v0.4.0/capability-mappings/supported/file.hash.json)
requires Object `algorithm` as one literal string in
`md5, sha1, sha224, sha256, sha384, sha512`. Its Object selector map includes
only filepath/path/filename; no route represents source Object `hash_type` or
its Variable quantifier. The State has a separate hash_type→algorithm field
route. Merely adding lowercase aliases would not resolve acquisition.

A native leaf with `algorithm: md5` validates. Omitting the algorithm, supplying
`[md5, sha1]`, a Variable reference, or a predicate all fail the unchanged
generated Object contract. The direct visitor fails closed on the original
Object with `unsupported Object field: hash_type`. No partial output is admitted.

## Decision and rejected shortcuts

An owner decision is needed on the representation for multi-valued and
complemented source algorithm acquisition. Two possible directions need separate
semantic review:

1. Retain scalar `algorithm` and authorize a specifically defined conversion
   into several acquisitions/Set composition, proving original `var_check`,
   correlation, incomplete/error evidence, and collection status boundaries.
   This report does not establish that such an expansion is equivalent.
2. Approve a version-local acquisition mapping/schema change that can retain the
   source selector and quantifiers. Such changes are outside this assignment's
   current authorization.

Selecting one algorithm drops original acquisition. Moving the selector into
State predicates changes the collected population and its errors. Expanding
Variables or inventing a Set without a reviewed evidence/status contract would
assert new conversion semantics. None is implemented or recommended as an
automatic fix. The safe current behavior is explicit unsupported diagnostics.

Three focused regressions verify original validity, native positive/negative
boundaries, and fail-closed inactive conversion:

```bash
PYTHONPATH=tools python -m unittest test_v04_filehash_acquisition_conflict -v
```

All three pass. They are review evidence, not delivered hash support or scanner
equivalence. [Verified continuation evidence](v04-direct-continuation-42.md)
records the completed work before this stop. #254 remains deferred.
