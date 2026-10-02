# SCC/NIWC OVAL Schema Augmentation Boundary

**Status:** active provenance note  
**Observed:** 2026-09-30  
**Scope:** bundled SCAP 1.4 / OVAL 5.12.3 schemas used by SCAP-NG research

## Finding

The schema tree currently bundled under:

`third_party/scap-1.4-schemas/oval_5.12.3/`

is not a pristine copy of the authoritative OVAL-Community OVAL 5.12.3 schema
set.

In particular, the bundled `independent-definitions-schema.xsd` contains the
SCC/NIWC SQL extension elements:

- `sqlext_test`
- `sqlext_object`
- `sqlext_state`

The authoritative upstream schema at
`OVAL-Community/OVAL`, tag `v5.12.3`, does not declare these elements.

## Consequence

The SCC/NIWC-augmented schema tree remains useful for validating historical SCC
content that intentionally uses these local extensions, but it SHALL NOT be
used as the authority for deciding whether a Test, Object, or State is part of
standard OVAL 5.12.3.

Generic SCAP 1.4 → SCAP-NG conversion SHALL derive the standard OVAL vocabulary
from the pinned authoritative upstream OVAL schemas.

The only currently known SCC/NIWC custom Test/Object/State family in this workstream is `sqlext`. Approved Windows OVAL tests SHALL NOT be classified as publisher extensions because of omissions in a checked-in schema snapshot.

## Current implementation

Regression workflows set:

`SCAP_NG_OVAL_SCHEMA_ROOT=oval-language/oval-schemas`

where `oval-language` is an exact checkout of:

- repository: `OVAL-Community/OVAL`
- ref: `v5.12.3`

The converter uses those schemas to distinguish standard OVAL
Test/Object/State QNames from local extension QNames.

A manifest generator,
`tools/scap_ng_roundtrip_v003/build_standard_oval_vocabulary.py`, is available
to produce a compact pinned vocabulary for offline use.

## Provenance implication

Future documentation and directory naming SHOULD distinguish:

1. authoritative upstream OVAL 5.12.3 schemas; and
2. SCC/NIWC-augmented OVAL 5.12.3-compatible schemas.

Calling both simply “OVAL 5.12.3” is ambiguous and can create a false sense of
standards conformance.

## Windows schema verification correction

The checked-in Windows definitions XSD is the authoritative OVAL-Community v5.12.3 blob. A large-file connector read returned an empty content payload and temporarily caused approved Windows definitions to appear absent. Direct Git-blob retrieval confirmed the definitions are present. This was a tooling artifact, not a schema-source defect.


Project-owner clarification: all other OVAL Test/Object/State families used by this project are standard SCAP 1.4 schema/test-content surface. Only `independent:sqlext` is custom.
