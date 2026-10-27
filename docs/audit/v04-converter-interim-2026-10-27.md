# Schema-independent converter checkpoint, 2026-10-27

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) from
[`041be96df`](https://github.com/vanderpol/scap-ng/commit/041be96dfbe78a027ea29a86dbeaba4d18265485).
The owner superseded the whole-assignment stop for `file.hash`: record and skip
isolated schema dependencies while continuing independent converter work. The
schema owner separately audits mappings, generated contracts, static Variables,
arrays and quantifiers. This checkpoint changes none of those contracts,
generators, normative definitions, 0.3 files, compiler/scanner/editor code, or
original OVAL payloads. Repository separation under #254 remains deferred.

## Implemented

The existing visitor now enables **46 capabilities**, adding
`linux.selinuxsecuritycontext`, `windows.file`, and
`independent.xmlfilecontent`, and `windows.regkeyeffectiverights53`. Shared scalar behavior routing reads original XSD
inheritance, validates combined scalar/traversal attributes before splitting
them, and retains XML item-creation controls. Independent proof reads traversal,
filesystem scope and nullable filenames from frozen identity data without
calling converter helpers. Unknown/deprecated behaviors still fail closed.

Five [unmodified original files](../../tests/fixtures/v04-direct-interim-files/provenance.json)
provide 35 Tests: 31 compile with matching typed terms; 30 also have valid,
nondeprecated original closures. One diagnostic conversion has an invalid
original closure and cannot be admitted; four invalid/deprecated original
cases remain conversion-blocked. Original Windows Set union/intersection/
difference, post-collection filters, constant Variable edges, shared Objects and
dependency hashes remain explicit. Negative mutations distinguish multi-operand
Set operators and Filter actions; singleton union/intersection correctly retain
the same identity meaning.

Registry hierarchy traversal also preserves finite/unbounded downward depth and
hive-root selection. Five original Registry effective-rights Tests validate,
compile and prove; their two deprecated group-expansion cases remain blocked.
The existing direct-SID proof guard checks original default include_group=true
and resolve_group=false, with no member expansion. No group-control fallback
is introduced.

Existing Registry/WMI proof readers also recognize established identity
correspondence: original Registry State `HKEY_*` names versus native hive labels,
nullable Registry key/value names, and original WMI State `wql` versus native
`query`. This corrects independent comparisons; it changes no generated program.
Their [original fixtures](../../tests/fixtures/v04-direct-proof-aliases/provenance.json)
and value/cardinality mutations guard against simply ignoring those fields.

For example, original UNIX XML Test `oval:navy.navwar.niwcatlantic.scc:tst:1`
produces this acquisition using the current approved grammar:

```yaml
object:
  directory: {equals: /opt/support/xml/classes/class1}
  name: {equals: section1.xml}
  xpath: {equals: "//*/grades/grade[@type='test']/text()"}
  item_creation: all_object_elements_fullfilled
  filesystem: all
```

The item-creation default comes from original `XMLFileContentBehaviors`, whose
base supplies traversal defaults. It is not inferred from the native enum.
Changing that flag can change item existence; proof mutations must reject it.

## Verification and gap reporting

The [compact receipt](v04-converter-interim-2026-10-27.json) contains local
validation results, six-source proof counts, every newly admitted Rule,
original pins and program-retention evidence. Exact-head maintained results are
recorded by GitHub Actions and the issue #251 handoff. The 803-Test corpus retains all
347 preceding proof/program hashes and adds 53 typed-term proofs: **400 proved,
408 compiled among 704 configured Tests**. **398** configured proofs additionally
have valid, nondeprecated original closures. There are zero comparison
mismatches. These standalone diagnostic Assessments do not establish whole
Benchmark or scanner equivalence.

The [CLI guide](../developer/DIRECT-V04-CONVERTER.md) documents the existing
verified upgrader and new `report_v04_conversion_gaps.py` supporting utility.
The consolidated report joins original XSD/Schematron/reference validity,
standalone conversion diagnostics and six-source acceptance results. It separates
configured, diagnostic-only and primary-Rule cases; a case can have more than one
category. It preserves original diagnostics, source IDs and evidence bases:

- Converter implementation or independent proof missing.
- Source-pinned capability schema limitation.
- Variable/collection representation limitation.
- Unsupported OVAL operation.
- Invalid/deprecated original source, including unresolved catalog bindings.
- External infrastructure failure, kept separate from conversion/source failures.

A native-schema rejection alone is classified as a converter obligation, not
permission to change the schema. Source-invalid cases remain visible even when
their diagnostic conversion compiles and typed terms agree. Only the existing
verified acceptance gate can admit a primary package.

The existing invalid-pattern-path regression exposed a Windows input boundary:
SV-278008 carries forbidden depth/direction attributes on pattern paths. The
shared Windows file handler rejects that input; no original payload was repaired
and the 249-Assessment/500-document raw baseline remains unchanged. The verified
gate also rejects it using original Schematron evidence. Mixed scalar/hierarchy
routing preserves the existing NTUSER item-creation controls.

## Deferred integration

The [dependency register](../../tests/fixtures/v04-converter-schema-dependencies.json)
pins the hash acquisition cases and three original SSH default-path cases.
While this checkpoint was being verified, the schema owner committed
[`d3132ae`](https://github.com/vanderpol/scap-ng/commit/d3132ae57432924f21d01a9b6ca2689d70f1b2f2),
replacing the old `file.hash` scalar parameter with a selector route. That commit
was fast-forwarded without overwriting converter edits. Its schema, parity lock
and tests were preserved; 17 compatibility checks pass. `file.hash` remains
inactive pending the explicitly requested follow-up integration assignment. Original SSH `filepath xsi:nil="true"` selects default
configuration; substituting `/etc/ssh/sshd_config` would invent a platform choice.
The current mapping does not declare that filepath nullable. The SSH limitation was not resolved here, and no hash lowering was added. The original SSH file also contains a separate invalid
`var_check="none exist"`; validity and schema dependence remain distinct.

Other remaining coverage is explicitly unverified: all three pinned
`linux.rpmverifyfile` cases use deprecated `md5_differs`; the pinned 803-Test collection
has no SQL512 or YAML file-content Tests. These are not all schema defects, and
no fallback or repaired source was introduced to inflate support.

After the schema owner commits the new baseline, the follow-up assignment should
review changed mapping fingerprints, integrate approved Variable/array/quantifier
representations through shared handlers, revisit pinned counterexamples, and
rerun these gates. Do not automatically refresh frozen proof hashes. Existing
`unix.process58` acquisition and all eight original process proofs are retained.
Applicability, scanner runtime, publisher trust, production readiness and release
acceptance remain separate gates.
