# SCAP-NG objectives

These objectives define why SCAP-NG exists and provide the test for major design
changes. A syntax change, smaller file, or new feature is not a goal by itself.

## O1 — Preserve meaning through migration

Provide a practical forward path from SCAP 1.4 and OVAL without silently changing
supported policy or assessment semantics. Unsupported or deprecated constructs
fail explicitly rather than being guessed.

## O2 — Make authoring and review substantially simpler

Reduce indirection, boilerplate, and legacy serialization burden so content is
easier to write, understand, review, version, and maintain. Preserve familiar
OVAL concepts and terminology unless a replacement is meaningfully clearer.

## O3 — Make semantics explicit and predictable

Eliminate hidden defaults and scanner-specific assumptions. Applicability,
quantifiers, inputs, dependencies, targeting, redaction, provenance, and other
behavior should have clear authored or schema-defined contracts.

## O4 — Scale through safe reuse

Reuse Assessments, Observations, collected facts, and caches only through
explicit contracts or proven semantic identity. Reuse must not change policy
truth, applicability, provenance, or evidence boundaries.

## O5 — Produce smaller, more useful results

Replace ARF-scale verbosity with results that clearly report outcome, decisive
reason, completeness, provenance, counters, and bounded evidence without
changing technical truth.

## O6 — Cover the complete policy lifecycle

Support automated and manual assessment, applicability, Organizational Input,
profiles/tailoring, and direct policy/STIG publishing in one coherent model.

## O7 — Be trustworthy, interoperable, and governable

Provide versioned specifications and schemas, documented OVAL mappings and
deliberate divergences, reproducible conformance evidence, package integrity,
and clear separation between machine validation and human/Board acceptance.

## O8 — Reduce implementation complexity and enable efficient execution

Replace the monolithic SCAP/XML processing model with modular native content and
a manifest-based signed package.

Native SCAP-NG should allow implementations to:

- avoid XML/XSD/XML-canonicalization/XML-signature processing during normal
  native execution;
- use straightforward typed data models and memory-safe implementation stacks;
- validate, hash, cache, diff, load, and update individual content components;
- avoid loading an entire benchmark/datastream into memory when unnecessary;
- produce focused version-control diffs from split source files; and
- build an explicit dependency graph so independent Assessments can execute
  concurrently while declared dependencies and shared acquisition constrain
  ordering where required.

Legacy conversion tools still have to parse authoritative SCAP 1.4 XML. This
objective applies to native SCAP-NG authoring, packaging, validation, and runtime
processing.

## Design-change requirement

Every major proposed change should identify the objective(s) it advances and any
objective it trades off against. The maintained issue mapping is
[OBJECTIVES.md](../OBJECTIVES.md).
