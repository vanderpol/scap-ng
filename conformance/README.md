# Native SCAP-NG 0.4.1 conformance corpus

This is the issue #87 native Self-Assertion and Conformance Test Content. The
active corpus is **only** the root `manifest.json`, `schema-coverage.json`,
`cases/`, `fixtures/`, and `expected/` generated from the exact canonical
0.4.1 schema family. The older `0.4/` material is retained as historical
Model-A evidence and is not an active 0.4.1 authoring corpus.

## Current inventory receipt

The generated inventory (`schema-coverage.json`) and conservative audit
(`coverage-audit.json`) record the source commit, whole-family digest, every
schema JSON document, `$ref`, property group, enum and constraint, plus each
supported/experimental capability mapping and its selectors, fields, datatypes,
and semantic validator rules. Regenerate it after a canonical schema change:

```sh
python conformance/tools/generate.py
python conformance/tools/runner.py validate
python conformance/tools/runner.py coverage
python -m unittest tests/test_issue87_conformance.py -v
```

At the initial issue #87 increment the inventory is pinned to commit
`860d63e84d5aba12daa6d5037bdb83d78a95088a` and contains 104 capability
mappings (100 supported, 4 experimental), 35 root schemas, 145 JSON resources,
693 schema references, 141 enum nodes and 10,960 constraint nodes. The schema
family SHA-256 is
`33c0867870c04a411f769646a8f5c8c785134673d56a26b7a1cd3c8d213a7a91`. The exact
SHA-256 is in both generated receipts; do not edit the version label without
regenerating the complete pack.

The audit derives coverage from source mappings, authored Assessment YAML, and
corresponding fixture JSON—not from declared inventory counts or expected keys.
It finds 710/710 fields in both authored positive Assessments and positive
fixtures. Each capability has seven base vectors plus a deterministic
multi-Item vector (832 expanded capability vectors total); a dedicated suite
adds 103 applicable multi-value witnesses. Negative fixtures are derived from
each Assessment: selector fields remain unchanged when a Require field is
mismatched, and selector-only capabilities use a collected empty population.
The strict receipt oracle verifies identity, exact schema pin, fixture/expected
hashes, Test outcomes, decisive reasons, typed evidence, and provenance.
Dedicated suites cover all 67 active comparison operators, all 94 declared
selector alternatives, every cardinality token, `not_evaluated`, and
profile-disabled Rules. Native enum boundary values beyond the sentinel audit,
schema property/constraint combinations, collector execution, and scale remain
explicitly incomplete.
Core Evaluate content also covers FALSE, `not(false)`, double negation,
AND/OR/ONE/XOR, and status propagation. `not` is the only canonical negation
spelling; `negate` is an invalid-authoring regression.

## Qualification boundary

The offline runner checks schema validity, deterministic fixture structure,
manifest hashes, expected typed outcomes, and inventory/vector completeness. It
does not execute a scanner and does not prove compliance or RI equivalence.
Scanner-neutral replay and receipt integration is coordinated with RI issue
#196. Platform collector qualification, large-scale execution evidence, and
independent multi-scanner evidence remain explicit follow-up gates rather than
being fabricated by this source corpus.
