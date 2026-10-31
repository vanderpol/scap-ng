# Native identity and invocation compatibility (#255/#268)

Implements Decisions 6, 10, 18 and 23. Current schema and direct program
compiler reject invalid/overlength native IDs, incorrect prescribed local
suffixes, and intrinsic Assessment purpose. Original external provenance
identities are outside this check. Library navigation now diagnoses duplicate
Assessment IDs across separate private Benchmark scopes, matching the existing
compiled graph's global Assessment identity rule; Test identities remain local.

Dependency resolution retains exact versions, visibility and cycle checks.
It no longer compares an obsolete target purpose. Typed Rule/applicability/
dependency use determines context; standalone absence stays unspecified.
Historical source-IR metadata is retained without turning it into an inferred
current Assessment purpose. New current authoring still rejects the old field.

The cmdlet module_version collection parameter now validates a quoted lexical
version, or declared Variable reference, or the existing unconstrained nil.
Pinned OVAL common DatatypeEnumeration/version (lines 411–415) describes
nonnegative integer components separated by a single nonnumeric character.
Thus 1.2.3 and 1-2c3 are lexical versions; garbage, 1..2 and unquoted YAML
numbers are rejected. This does not compute version ordering, validate runtime
Variable output or assert PowerShell/scanner execution. No generic coercion or
new default annotation was added.

Five new focused identity/context/version tests PASS (0.310s). The combined
existing owner producer/conditional/schema/name suites PASS 36 tests (1.076s).
Tests include schema and direct compiler negatives, duplicate Assessment IDs
across private scopes, context-free exact-version dependency resolution,
version positives/negatives and incompatible datatype wrappers. Real-source
Linux/Windows producer/schema/compilation/static proof checks remain passing.

The wider maintained suites still contain old synthetic IDs/purpose and frozen
historical authoring. Those are not current-schema positives and their pins
must not be replaced merely to claim green. PR #268 remains draft pending the
compatibility/default packet and observed maintained integration gates.
