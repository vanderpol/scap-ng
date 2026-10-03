# Capability coverage / new-test audit checkpoint

Owner's final scope: SCAP-NG replaces OVAL 6.0; inspect **new 6.0 tests only**.
Keep the current 5.12.3 fixes. Existing-test/core/result/namespace/encapsulation
differences are outside this pass. The broader original #131 delta proposal is
superseded. Registry view and effectively deprecated predecessors stay excluded.

[The development audit](../docs/audit/capability-coverage-2026-10-03/README.md)
contains a pinned 22-Test inventory (20 ESX, 2 Kubernetes), associated inherited
Object/State/Item contracts and per-Test implementation candidates. There are no
current mappings for those new tests. This does not implement collectors or
change native schemas/converter behavior. Introduce new capabilities in a
versioned 0.2.0 mapping/schema integration rather than expanding stable 0.1.0.

The current-mapping matrix covers 100 authoring mappings and 99 Item contracts.
Only unix.file and variable.value have standalone Assessment content in tests/;
98 mapped capabilities lack that content there. Item validity cases, unit-test
reference candidates and dated corpus mentions are recorded separately. Static
mentions are not positive/negative method-level proof or runtime conformance.
Keep #128 and #131 open for remaining coverage and implementation work.

All four new-family XSDs compile. An isolated namespace-aware regression proves
four Kubernetes Test binding contexts do not select the actual Test elements;
track #137 without modifying upstream files or claiming complete validator
behavior. Source pins and exact Git-blob reading make the upstream inventory
reproducible across Windows newline settings. Twelve focused audit tests cover
scope, inheritance, choices, cardinality, type identity, missing contracts,
cycles, pins and the isolated binding-pattern finding.

Next bounded task: native ESX mappings and standalone known-result fixtures in
small groups, then Kubernetes structured-resource/record cases. Preserve every
non-deprecated supported contract and explicitly resolve target/resource context,
status/completeness and source ambiguities before claiming a group complete.
Provenance: Evidence/Audit, Adapted source schema metadata, Common audit tools.
