# Expansion plan and implementation priorities

## Current coverage

The [generated inventory](../generated/developer-guide-gaps.json) covers all
104 mappings: 100 supported, four experimental, 15 namespace families, three
reviewed pilots, **zero runtime-qualified records**. There are 145 selector
entries: 28 resolved, 117 unresolved (the supported subset is 141/113).
Every capability has a structural guide section; the remaining 101 capabilities
have no curated pilot notes in this model. Structural coverage is not a
physical collection algorithm or implementation guarantee.

The inventory records each capability's unresolved selectors, missing collected
datatypes, annotation coverage and qualification gaps. Existing NTUSER research
remains in its source audit; it is not counted as a fourth reviewed pilot.
The 38 fields without recorded datatypes belong to `ios.interface` and
`iosxe.interface`; their pages show “unresolved” rather than guessing types.

## Priority and exit gates

| Priority | Work | Exit gate |
| --- | --- | --- |
| P0 | Resolve registry traversal discrepancy; selector/result naming; registry encodings/time units; file links/ACL/time/mount rules; shell no-output/error/limits contracts | Owner-reviewed native decision tables; no inferred OVAL defaults |
| P1 | Finish the three pilots' acquisition and absence/error guidance | Platform runtime fixtures and independent expected results; review approval distinct from documentation approval |
| P2 | Expand to `windows.file`, `windows.service`, `linux.rpminfo`, `linux.partition`, `independent.textfilecontent` | Review reusable file, service, package and text patterns; validate annotation role maps against actual fields |
| P3 | Remaining supported Windows/Linux/UNIX and independent capabilities; then macOS, network and other platform families | Resolve selectors in reviewed batches, pin platform sources, record error/status tables and regression vectors |
| P4 | Four experimental mappings | Explicit scope/semantic adoption decision before any normative claim |

P2 capabilities are chosen to exercise reusable contracts, not as an assertion
of corpus usage. Inventory gaps are a review queue, not permission to implement
unspecified behavior. Use existing supported native capabilities rather than
expanding shellcommand into a generic collection escape hatch.

## Proposed schedule

Relative working days begin when owners and platform reviewers are available;
these are effort estimates, not release dates.

| Window | Deliverable | Dependency |
| --- | --- | --- |
| Days 1–3 | Annotation ownership decision and P0 decision packets | Owner review of this draft; frozen 0.4 remains unchanged |
| Days 4–8 | Three pilot acquisition/status tables and runtime fixtures | Windows and UNIX runtimes; owner decisions on ambiguous semantics |
| Days 9–13 | Five P2 capability reviews; role-map proposal refinement | Pilot patterns and platform-source provenance |
| Subsequent weekly batches | Five to ten supported capability documentation reviews per batch | Platform expertise and independent runtime evidence; unresolved cases remain labeled |
| After supported coverage review | Experimental scope review and future-version annotation migration | Separate owner approval; remove temporary duplicate authority during migration |

Track documentation completion and runtime qualification separately. Batch size
must shrink when new semantic questions appear. No release-readiness claim or
release preparation is part of this work.

## Validation and maintenance

Portable CI regenerates references offline, checks exact bytes and frozen-schema
integrity, validates examples against local Draft 2020-12 resources, and exercises
negative schema and annotation cases. Provenance harvesting is a separate local
check against the pinned original XSD checkout; CI does not download it. Platform
execution and independent scanner comparison remain future evidence gates.
