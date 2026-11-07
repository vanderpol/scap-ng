# SCAP-NG application developer guide

**Status:** documentation architecture pilot. SCAP-NG 0.4 remains pre-alpha;
schema-valid Assessments do not imply scanner support.

## Read only what you implement

1. [Common schema and authoring reference](../generated/schema-reference.md)
2. [Capability catalog](../generated/capability-catalog.md)
3. Choose your platform:
   - [Windows pilot](../generated/developer-guide-windows-pilot.md)
   - [UNIX/Linux pilot](../generated/developer-guide-unix-pilot.md)
   - [Platform-independent command pilot](../generated/developer-guide-independent-pilot.md)
4. [Full scanner guidance coverage and documented gaps](../generated/scanner-implementation-catalog.md)

The platform pages are generated from the pinned capability contracts and a
small **proposal-only** field-annotation overlay. The 0.4 schema bytes are
unchanged. If the annotation vocabulary is approved for a future schema
version, the field-level source moves into the canonical schema generation
pipeline and this temporary overlay is removed.

## Common requirements not captured by field annotations

- **Trust:** authenticate content before privileged execution. The reference
  implementation's application-specific signer trust store and opt-in unsigned
  developer mode are design decisions pending normative documentation.
- **Target and applicability:** determine the assessed target, record its
  identity, and apply Benchmark/Rule applicability; preserve instance evidence
  when presenting host-level results. Aggregation behavior needs a separate
  contract review.
- **Collection:** bound traversal and enumeration; distinguish absent,
  inaccessible, and incomplete evidence. Never invent nonexistent Items.
- **Results:** retain decisive reasons, error/unknown semantics, and evidence
  provenance. Human-readable explanations and text/HTML reports are application
  views of structured results.
- **Performance:** benchmark large filesystems and identities; balance reuse,
  parallelism, caching, and resource limits without prescribing a database,
  programming language, or operating-system API.

Missing collection algorithms, failure mappings, and conformance vectors are
explicit gaps. Legacy OVAL 5.12.3 XSD descriptions are **research inputs**,
not automatically authoritative SCAP-NG behavior.
