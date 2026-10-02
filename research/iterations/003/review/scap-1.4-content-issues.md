# SCAP 1.4 Content Issue Register

**Status:** active working register  
**Scope:** defects found in SCAP 1.4 validation / Self-Assertion / published assessment content while developing SCAP-NG  
**Separation of concerns:** this page tracks **content defects**. OVAL language/schema defects and semantic-validation gaps belong in [upstream-oval-schema-issues.md](../design/upstream-oval-schema-issues.md).

## Purpose

SCAP-NG migration and round-trip testing intentionally exercises real SCAP 1.4 content. When that process exposes content that is internally inconsistent, invalid, ambiguous, or dependent on non-standard publisher constructs, record it here rather than silently correcting it during conversion.

A finding belongs here when the problem is in authored SCAP 1.4 content or its packaging, including:

- a Test references an incompatible Object or State;
- a content file uses the wrong element/type for its intended semantics;
- a published fixture conflicts with the governing schema or validation rules;
- source content relies on an accidental validator gap;
- a content package ships mismatched schema/version material;
- expected-result metadata disagrees with the actual authored test semantics.

Do **not** record a pure OVAL language/schema design issue here unless concrete content is also defective. Link to the upstream schema register instead.

## Required fields for each issue

Each finding SHOULD capture:

- stable issue ID;
- source repository/package and exact commit/version;
- source file and Definition/Test/Object/State IDs;
- affected SCAP/OVAL version;
- concise defect description;
- evidence showing expected versus actual behavior;
- validation status under XSD and Schematron;
- conversion/round-trip impact;
- whether SCAP-NG quarantines, rejects, or preserves the source;
- proposed upstream/content-owner correction;
- regression fixture or test;
- status: candidate / confirmed / reported / fixed / closed.

## SCAP14-CONTENT-001 — Cross-family Test/Object/State mismatch in nginx content

**Status:** confirmed; previously identified during SCAP-NG source audit  
**Source:** nginx STIG rule SV-278400 / OVAL definition `oval:navy.navwar.niwcatlantic.scc.nginx:def:278400`  
**Observed:** a `unix.file_test` references `independent.shellcommand_object` and `independent.shellcommand_state`. Identity/reference validation allowed the references to resolve, but the referenced collector families are not compatible with the Test family.

**Impact:** a converter that preserves source tags faithfully can reproduce the defect; a converter that silently retags the Object/State would hide a content error and change provenance.

**SCAP-NG disposition:** preserve source fidelity, diagnose the mismatch, and do not silently repair it.

**Related language/schema issue:** [OV-XSD-001](../design/upstream-oval-schema-issues.md#ov-xsd-001--cross-family-testobjectstate-reference-compatibility).

## Packaging / schema-source discrepancies

If a SCAP 1.4 package appears to omit an approved OVAL Test/Object/State family that is present in the authoritative OVAL schema/test-content distribution, record the exact package/version here only after confirming the mismatch. Do not reclassify the approved capability as a publisher extension.

The only currently known SCC/NIWC custom Test/Object/State family in this workstream is `independent:sqlext`; that is an intentional publisher extension, not a content defect by itself.

## Filing rule

Before calling something a SCAP 1.4 content bug, verify it against:

1. the exact SCAP/OVAL version declared by the content;
2. the authoritative OVAL-Community schema set for that version;
3. applicable embedded Schematron / validation content;
4. the SCAP Self-Assertion corpus when relevant;
5. any documented OVAL Board decision or deprecation/reinstatement record.

When confidence is high, create or link a GitHub Issue for the content owner and retain this page as the durable project index.


## SCAP14-CONTENT-002 — Windows Update Searcher Item exposes unfilterable scalar source_path

**Status:** confirmed schema/content-surface mismatch  
**Source:** OVAL 5.12.3 Windows `wuaupdatesearcher_item` / `wuaupdatesearcher_state`  
**Observed:** `wuaupdatesearcher_item` collects scalar `source_path` (Windows Update Server URL or offline CAB filepath), but `wuaupdatesearcher_state` exposes no matching `source_path` entity. The field is not deprecated and is documented as normal collected data.

**Impact:** authors can receive `source_path` in collected results but cannot test or filter it with a State. This violates the intended scalar Item/State symmetry used by Set filters.

**SCAP-NG disposition:** include `source_path` in the native canonical Item/State model so it is filterable. Preserve migration provenance noting that legacy OVAL 5.12.3 State could not express the predicate.

**Upstream recommendation:** add matching `source_path` to `wuaupdatesearcher_state` in a future OVAL maintenance release (candidate 5.12.4) if the Board agrees.
