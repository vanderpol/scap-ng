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

Content that depends on SCC/NIWC additions SHALL be reported as a publisher
extension unless and until a publisher-specific conversion profile defines its
execution semantics and reverse mapping.

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
