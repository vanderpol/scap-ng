# OVAL <-> SCAP-NG Round-Trip Stress Corpus

This corpus exists to expose semantic gaps before a native SCAP-NG interpreter
exists.

The fixtures intentionally use difficult OVAL dependency shapes rather than
simple one-object/one-test examples.

## Purpose

For each fixture:

1. identify authoritative OVAL 5.12.3 source semantics;
2. represent those semantics in provisional SCAP-NG stress-fixture form;
3. generate OVAL back from the NG fixture;
4. validate regenerated OVAL against the authoritative OVAL XSD/Schematron;
5. compare normalized source and regenerated semantic graphs.

A successful round trip is evidence of representational completeness, not proof
of correctness. Symmetric forward/reverse bugs can still survive round-trip
testing.

## Current fixtures

- `rhel-audit-log-partition.json`
  - real RHEL-family OVAL graph;
  - Object -> Variable -> Object dependencies;
  - object_component extraction;
  - concat over object-derived values;
  - variable-driven Object selectors;
  - behavior preservation.

- `rhel-rsyslog-set-filter.json`
  - real RHEL-family OVAL graph;
  - Object Set UNION;
  - Filter -> State dependency;
  - existence-only tests;
  - behavior preservation.

- `rhel-aide-variable-chain.json`
  - real RHEL-family OVAL graph;
  - nested OR/AND criteria and extend-definition flattening;
  - Test -> State dependency;
  - recursive file discovery behaviors;
  - multiple Object -> Variable -> Object chains;
  - concat over independently collected object components.

- `cartesian-variable-chain.json`
  - synthetic schema-derived language stress case;
  - variable -> variable chain;
  - nested arithmetic over multi-valued operands;
  - Cartesian-product semantics;
  - count over a derived collection.

## Important scope rule

The JSON format in this directory is a **round-trip test fixture format**, not a
proposal to standardize SCAP-NG JSON serialization.

The native YAML design remains under active review.

## Lossless expectation

For the OVAL-compatible subset exercised here:

    normalize(source OVAL semantics)
        ==
    normalize(regenerated OVAL semantics)

Differences in IDs, comments, namespace-prefix choice, element order where order
is non-semantic, or generator metadata do not constitute semantic loss.

Any behavioral difference is a conversion/design defect unless explicitly
classified as an approved SCAP-NG divergence.
