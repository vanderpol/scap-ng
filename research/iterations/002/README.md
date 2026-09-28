# SCAP-NG Research Iteration 002

**Status:** active native-source design iteration

Iteration 001 is the fidelity/migration research archive. Iteration 002 starts
from the lessons learned there and focuses on a clean, concise, OVAL-aligned
native SCAP-NG authoring model suitable for review by existing SCAP/OVAL
content authors.

## Primary objective

Design source files that are:

- small enough to understand quickly;
- expressive enough to preserve SCAP 1.4/OVAL semantics;
- familiar to experienced OVAL authors;
- free of XCCDF/OVAL/OCIL runtime dependencies;
- explicit about applicability, reuse, and error semantics;
- suitable for later deterministic up-conversion from SCAP 1.4.

## Ground rules

1. **Reuse OVAL's platform-family taxonomy.**
   The default NG capability namespace is the OVAL family namespace plus the
   OVAL test basename.

   Examples:

       unix.file
       windows.registry
       linux.rpminfo
       solaris.package
       macos.plist511
       independent.textfilecontent54

   Do not invent a parallel taxonomy without a demonstrated semantic reason.

2. **Preserve family boundaries that OVAL learned through operational use.**
   A Windows file and a Unix file are not the same data model merely because
   both concern files.

3. **Simplify authoring structure, not collection semantics.**
   NG does not need to reproduce OVAL's XML definition/test/object/state
   layering when a smaller native form can express the same behavior exactly.

4. **Applicability uses the full assessment language.**
   Any NG assessment capability may be used to determine applicability.
   Content authors define applicability; scanners do not provide an opinionated
   platform oracle.

5. **Legacy standards are provenance, not runtime dependencies.**
   XCCDF, OVAL, OCIL, CPE language, source IDs, namespaces, and hrefs may be
   retained in migration provenance but are not required for native execution.

6. **Simple rules must stay simple.**
   Complexity belongs only where the underlying assessment really requires it.

7. **OVAL experience is design evidence.**
   OVAL is old, but its collector families, defaults, edge cases, and platform
   distinctions reflect years of deployed content. Reuse those lessons
   intentionally.

## Working areas

- `design-principles.md` — normative direction for this iteration.
- `examples/` — intentionally small native source examples.
- `decisions/` — design decisions as they stabilize.
- `provenance/` — migration/source linkage for review examples only.

Nothing enters iteration 002 merely because a converter can generate it.
Every example should be understandable and defensible as potential native
SCAP-NG source.
