# First new ESXi host capability group — 2026-10-03

Base: merged audit/documentation checkpoint
`6282b7785f08f02c9694d4fb5b60d1a065435a2e`.

Adds draft 0.2.0 `esx.host_service` and `esx.host_advancedsetting` native mappings,
schema annotations, versioned lookup, source-node validation, Item/reporting
integration, standalone synthetic content, hand-explained scalar/collection
status expectations and field references. Stable 0.1.0 mappings/schemas remain
unchanged. The registry prohibits a draft mapping shadowing a stable capability.

Source pin: OVAL-Community/OVAL v6.0 commit
`5afcf590fb5d334687bfdc47f98716424cdb7f3d`. Exact ESX definition/Item blobs retain
the upstream License/Disclaimer. The partial metadata snapshot is not itself a
compilable bundle; complete compilation stays in the existing source-pinned
new-Test audit. No OVAL 6.0 importer or embedded runtime is added.

The State/Item contracts preserve Boolean service fields and repeated AnySimple
advanced-setting values, with reviewed native datatypes. New descriptions carry
into generated Object/State/Item schema annotations. The validation harness
checks new node shapes, including unused Tests, with an offline local schema
registry. Existing cross-reference checks reject incompatible Objects/States.
Draft reporting/Assessment Result helpers and Item-contract export discover the
new mappings through the versioned registry.

Validation commands are in tests/esx-host-0.2.0/README.md. Synthetic scalar cases
show obvious equality outcomes; status-only cases exercise shared collection and
existence behavior. These are not complete State comparators, actual VMware
collection, or independent vendor execution. Source pins and legal notices are
checked against committed Git blobs, preserving LF/CRLF reproducibility.

Next: remaining ESXi host groups, explicit review of acceptance-level singleton
selection/filter semantics, inherited VM/device fields and management-plane VDS
identity. Kubernetes follows with API/version prerequisites. Twenty of the 22
new Tests still need native contracts. Do not declare finalized 0.2.0 or the
Codex corpus-expansion readiness gate from this bounded group.

Provenance: Inherited exact licensed source, Adapted source field/type/cardinality
semantics, Common native implementation/content/reference text, Evidence/Audit
pins, synthetic expectations and coverage limits.

Local verification: all 76 maintained workflow commands pass; subsequent compiler
changes pass the focused ESX, existing compiler and conditional integration
checks. The focused ESX suite has 13 cases, including actual unsigned content
bundle compilation/verification. Item export discovers 101 Item contracts
(the 102-capability draft catalog includes objectless unknown with no Item).
All 100 stable generated contracts compare identically against the generator at
the pinned base commit. The reference consistency check covers four capability
field inventories, seven Markdown documents and 12 dated source pins.
Preservation audit: 34,242 baseline paths, zero failures. Remote exact-head
Linux/Windows and preservation CI remain publication/merge gates.
