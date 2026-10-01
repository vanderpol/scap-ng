# SCAP-NG JSON Schema v0.1.0 draft

Status: **pre-alpha corpus-derived draft**

This directory contains the first versioned JSON Schema work for the current
SCAP-NG native architecture.

The schema work SHALL follow these rules:

- schemas describe native SCAP-NG content, not SCAP 1.4/XML serialization;
- Benchmark -> Rule -> selected Assessment is the authoritative architecture;
- there is no separate Policy document;
- Collection capability/type is first-class and remains on each Collection;
- Test and State/predicate capability/type remain independently meaningful;
- migration, conversion, quarantine, parity, and normalizer evidence are
  excluded from native content schemas;
- Assessment composition/shared Collection reuse is intentionally deferred and
  is not reserved through speculative fields;
- JSON Schema validates structural/type contracts; semantic compatibility,
  reference resolution, capability compatibility, dependency cycles, and other
  graph rules remain separate semantic validation.

Initial core document targets:

1. Benchmark
2. Rule
3. Assessment
4. Applicability catalog

Tailoring, organizational input, package manifest, and results schemas will be
added after the core authoring graph stabilizes.

The full pinned NIWC Current native corpus census is the primary evidence used
to classify fields as required, optional, conditional, extensible, or
migration-only before schemas are made normative.
