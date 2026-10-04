# Native dependency: platform guard, conditional paths and reuse

Read [Assessment](../content/dependency.assessment.yaml), [expectations](../expected/dependency.json),
and [provenance](../provenance/dependency.json). Human status: **pending-review**.
Provenance: Common original native content; Evidence/Audit scheduling oracle.

The native Assessment first tests the observed system family against `unix`.
It invokes [the UNIX file Assessment](../content/unix-file.assessment.yaml) only
when that Test is true. A Windows family chooses explicit N/A. Platform
applicability evidence remains distinct from the file configuration/resource Test.
No Organizational Input selects Tests or injects executable content.

The dependency declares its relative file path, exact logical identity
`board.unix-file` and revision 3. The two references in `then/all` consume one
dependency execution for the same target/bindings. Reuse retains both references
and the execution identity; it does not import the dependency's Items locally.
The compiler remains responsible for immutable digest binding in a package.

| Guard result | Invoked file Assessment | Final result in these cases |
| --- | --- | --- |
| true (UNIX) | Once; second reference reuses it | true |
| false (Windows) | None | not_applicable, authored reason |
| error | None | error |
| unknown | None | unknown |
| not_evaluated | None | not_evaluated |
| not_applicable | None | not_applicable |

The skipped case injects a **synthetic provider lifecycle status**: the Test
leaf was invoked but its provider performed no Test evaluation. This is not a
new collected-object flag or live collection evidence. The other synthetic
guard statuses exercise existing collection/Test mappings.

This is source-authored native conditional logic, not automatic rewriting of
OVAL Boolean criteria. The pinned `oval-def_extend_definition.xml` analog is
excluded because its alleged true Variable declares binary datatype with value
`true` while its State compares Boolean. See the [minimal reproducer](../../../../tests/focused-regressions/board-pilot/README.md).
