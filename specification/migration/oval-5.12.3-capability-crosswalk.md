# OVAL 5.12.3 Test-Type to SCAP-NG Capability Crosswalk

**Status:** pre-alpha informative migration appendix  
**Normative migration rules:** `oval-5.12.3-to-ng.md`

This appendix explains how OVAL 5.12.3 Test families map into the current
SCAP-NG 0.2.0 capability model.

**The authoritative current capability names are the versioned 0.2.0 mappings
under [`schema/v0.2.0/capability-mappings/supported/`](../../schema/v0.2.0/capability-mappings/supported/).**
The large candidate inventory that originally drove the migration study was
research input, not a second supported catalog.

The converter SHALL account for every source Test it encounters:

- a supported, non-deprecated Test resolves through a reviewed 0.2.0 mapping;
- a deprecated Test blocks conversion and identifies the required remediation/replacement;
- an unknown or publisher-extension Test blocks conversion rather than being silently invented as a native capability.

## Native capability naming

SCAP-NG names a **capability**, not an XML Test element. Native names therefore
remove the XML `_test` suffix and MAY use a clearer semantic name when the
reviewed mapping proves equivalence.

The exact OVAL source identity is always retained in mapping provenance
(`source.test`, `source.object`, `source.state`, and `source.item`).
That is where historical OVAL revision suffixes belong.

Examples of completed native-name cleanup include:

| OVAL source Test | Native capability |
| --- | --- |
| `windows:wmi57_test` | `windows.wmi.query` |
| `independent:filehash58_test` | `file.hash` |
| `independent:variable_test` | `variable.value` |

### Remaining historical suffixes in 0.2.0

Some reviewed 0.2.0 mappings still carry the historical OVAL revision suffix in
their **native** capability name. This is unfinished naming cleanup, not a
recommended SCAP-NG naming convention:

- `independent.environmentvariable58`
- `independent.sql512`
- `independent.textfilecontent54`
- `macos.nvram512`
- `macos.plist511`
- `macos.pwpolicy512`
- `solaris.package511`
- `unix.process58`
- `windows.fileeffectiverights53`
- `windows.regkeyeffectiverights53`
- `windows.user_sid55`

These names remain unchanged during the current 0.2.0 human-review window so
that documentation cleanup does not silently become a schema/API rename.
After review, each SHALL be checked against its deprecated/older predecessor
and given a semantic native name where collapsing the suffix is demonstrably
safe. The exact versioned OVAL name SHALL remain in migration provenance
regardless of the native spelling.

## Current 0.2.0 capability authority

There is no separate “reviewed mappings” catalog and “supported candidate”
catalog to reconcile.

For 0.2.0:

1. **Supported now:** use the canonical
   [supported capability catalog](../../schema/v0.2.0/capability-mappings/supported/README.md).
2. **Experimental:** use the
   [experimental catalog](../../schema/v0.2.0/capability-mappings/experimental/README.md);
   these mappings are not part of the supported authoring baseline.
3. **Deprecated / unsupported / publisher extension:** conversion stops with an
   explicit diagnostic; these are not native capabilities.
4. **Historical candidate inventory:** retained only as migration research and
   audit evidence. It does not override or supplement the current supported catalog.

The original inventory study counted 258 standard OVAL 5.12.3 Test types after
excluding the SCC/NIWC-only `independent.sqlext_test`. That historical study
was useful for establishing the migration surface, but its provisional
candidate names and `name-review` markers are no longer a normative/current
capability list.

For the complete current Test → capability mapping, inspect the `source` and
`migration_crosswalk` fields in the supported mapping JSON files. For the
historical inventory and deprecated/excluded research, see
[`research/iterations/002/decisions/oval-test-type-crosswalk.md`](../../research/iterations/002/decisions/oval-test-type-crosswalk.md).

### Why OVAL revision suffixes still appear in provenance

Suffixes such as `53`, `54`, `55`, `57`, `58`, `511`, and `512`
identify the OVAL revision in which a revised Test family was introduced. They
can matter during migration because the suffixed Test may replace a deprecated
predecessor with different semantics.

For example:

- `wmi57` supports multiple selected WMI fields where deprecated `wmi` permitted a single field;
- `textfilecontent54` adds multi-line and multi-instance behavior relative to deprecated `textfilecontent`.

SCAP-NG therefore SHALL preserve the exact suffixed **source** identity, while
the native capability name SHOULD describe the capability semantically once
equivalence and predecessor handling have been reviewed.

## Excluded/deprecated Test types

The complete deprecated/excluded inventory and rationale is maintained in the
research evidence file:

    research/iterations/002/decisions/oval-test-type-crosswalk.md

For specification purposes, an effectively deprecated/out-of-scope Test type:

- SHALL be recognized during source ingestion;
- SHALL be reported by exact OVAL family/Test name;
- SHALL NOT be silently converted to a different Capability;
- SHOULD identify a documented replacement where one exists;
- SHALL block conversion of the affected Definition until source remediation
  or an explicit standards decision permits another migration path.

This appendix will be regenerated as Capability naming and OVAL-governance
decisions stabilize.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: OVAL 5.12.3 to SCAP-NG Migration](oval-5.12.3-to-ng.md) · [Contents](../README.md) · [Next: Security Considerations →](../security/security-considerations.md)

<!-- spec-nav:end -->


## Publisher extension exclusion: `sqlext`

SCC/NIWC `sqlext_test`, `sqlext_object`, and `sqlext_state` appear
in locally augmented OVAL schemas but are absent from pinned upstream OVAL
5.12.3. They SHALL NOT be listed as standard OVAL-derived SCAP-NG capabilities.
The generic converter SHALL diagnose these as out-of-scope publisher-extension
constructs rather than silently emit schema-invalid standard OVAL.
Migration of the source SQL content to standard `sql512` is a separate
future content-maintenance effort; this specification does not claim that
`sqlext` and `sql512` are behaviorally interchangeable.

See
[OVAL-derived specification lessons](../../research/iterations/003/design/oval-derived-specification-lessons.md).
