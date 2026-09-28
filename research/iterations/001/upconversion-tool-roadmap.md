# SCAP 1.4 to SCAP-NG Up-Conversion Tool Roadmap

**Status:** project roadmap  
**Current implementation:** research tooling in `tools/`  
**Long-term goal:** independently usable open-source converter published on GitHub

## Goal

Turn the conversion machinery developed for SCAP-NG research into a general,
open-source content up-conversion tool that can ingest standards-conformant SCAP
1.4 content and emit validated SCAP-NG source and distribution artifacts.

The research repository is the proving ground. The eventual converter must not
depend on DISA/NIWC-specific filenames, benchmark IDs, GitHub Actions, or the
iteration-001 directory layout.

## Design principle

Keep these layers separate:

1. **SCAP 1.4 ingestion**
   - datastream/package discovery;
   - XCCDF parsing;
   - OVAL parsing;
   - CPE/applicability parsing;
   - provenance capture;
   - schema validation.

2. **Faithful semantic intermediate representation**
   - XCCDF policy model;
   - OVAL collect/derive/predicate/evaluate/assert graph;
   - profile/value resolution;
   - applicability;
   - result-processing semantics;
   - source provenance and diagnostics.

3. **Migration analysis**
   - deprecated/effectively-deprecated construct detection;
   - unsupported constructs;
   - semantic-loss accounting;
   - source-remediation recommendations;
   - exact/normalized/legacy-compatible/requires-review/unsupported status.

4. **SCAP-NG renderers**
   - combined-rule;
   - split policy/assessment/binding;
   - Ansible-inspired;
   - later: the Board-selected canonical format.

5. **Validation**
   - renderer -> canonical semantic round-trip;
   - schema validation;
   - referential integrity;
   - package closure;
   - deterministic output;
   - content fingerprints;
   - eventually old-vs-new execution comparison using the reference scanner.

6. **Distribution**
   - deterministic package manifest;
   - signing interface;
   - policy-only vs automated packages;
   - SBOM/provenance metadata if adopted;
   - reproducible package verification.

## Proposed end-user CLI

The eventual tool should expose a small, stable CLI rather than requiring users
to run individual research scripts.

Example shape:

    scap-upconvert inspect input.zip

    scap-upconvert convert input.zip \
      --format split \
      --output converted/

    scap-upconvert convert input.zip \
      --format combined \
      --output converted/

    scap-upconvert validate converted/

    scap-upconvert package converted/ \
      --type automated \
      --output benchmark.scapng

    scap-upconvert report input.zip \
      --output migration-report.json

Possible future commands:

    scap-upconvert diff old-scap14.zip converted/
    scap-upconvert map benchmark-a.zip benchmark-b.zip
    scap-upconvert reuse corpus-directory/

The exact command names are provisional; the important point is that users
should not need to understand internal script ordering.

## Library/API shape

The CLI should be a thin wrapper over importable Python APIs so content
developers, CI systems, and other tools can call the converter directly.

Candidate modules:

    scap_upconvert/
      ingest/
        datastream.py
        xccdf.py
        oval.py
        cpe.py
      ir/
        policy.py
        assessment.py
        applicability.py
        provenance.py
      migrate/
        catalog.py
        blockers.py
        normalize.py
        reuse.py
      render/
        combined.py
        split.py
        ansible_inspired.py
        canonical.py
      validate/
        semantic.py
        schema.py
        package.py
      package/
        builder.py
        signer.py
      cli.py

The public API should use typed data structures rather than passing raw
dictionaries between modules.

## Migration from the current scripts

### Phase 1 — stabilize behavior in research

Continue using the existing top-level `tools/` scripts while the SCAP-NG
semantic model and Board-selected authoring format remain unsettled.

Required before extraction:

- four-anchor Linux/Windows conversion is reproducible;
- deprecated OVAL policy is stable;
- semantic round-trip validation is stable;
- applicability/profile/value handling is stable;
- full-corpus conversion accounting is available;
- Board-selected SCAP-NG source format is known or sufficiently stable.

### Phase 2 — identify reusable core

Move logic out of command-line scripts into importable modules without changing
behavior.

Current likely source material includes:

- `oval_semantic_ir.py`;
- `scap14_rule_splitter.py`;
- `scap14_benchmark_ir.py`;
- `scap14_to_scapng.py`;
- `build_oval_schema_semantic_catalog.py`;
- renderer/verifier modules;
- reuse/mapping analysis.

Research-only orchestration and evidence-generation code should remain outside
the public package.

### Phase 3 — define stable IR contracts

Version the semantic IR independently from the external SCAP-NG syntax.

The converter should be able to say:

    SCAP 1.4 -> IR vN -> SCAP-NG format vM

This allows later syntax changes without rewriting the SCAP 1.4 parser and lets
tests distinguish ingestion defects from renderer defects.

### Phase 4 — package as a normal open-source project

Recommended project infrastructure:

- `pyproject.toml`;
- installable console entry point;
- semantic versioning;
- SPDX-compatible license;
- CONTRIBUTING.md;
- SECURITY.md;
- CODE_OF_CONDUCT.md if appropriate;
- architecture/developer documentation;
- generated CLI reference;
- unit and integration tests;
- pinned public conformance fixtures;
- GitHub Actions on Linux and Windows;
- release artifacts and checksums.

The tool should run locally with no GitHub dependency.

### Phase 5 — conformance and compatibility gates

Every release should test:

- OVAL Community Self-Assertion content;
- pinned public SCAP 1.4 production corpus;
- representative Linux and Windows STIGs;
- deprecated-test blocker behavior;
- renderer semantic equivalence;
- deterministic repeated builds;
- package verification.

After the reference SCAP-NG scanner exists, add differential execution tests:

    SCAP 1.4 scanner result
           vs
    converted SCAP-NG reference-scanner result

for the same target.

## Output philosophy

The tool must never silently improve or rewrite ambiguous source semantics.

Every source construct must be accounted for as one of:

- exactly represented;
- equivalently normalized;
- represented through a documented compatibility construct;
- requires review;
- unsupported/source remediation required.

A successful conversion report should therefore be as important as the emitted
YAML.

## Source remediation

When obsolete/deprecated SCAP 1.4 constructs prevent conversion, the converter
should emit machine-readable and human-readable diagnostics including:

- source rule/definition;
- deprecated construct;
- current effective governance status;
- supported replacement when known;
- source location/provenance;
- whether the blocker affects ordinary assessment logic, applicability, or both.

The converter should not carry deprecated runtime semantics into SCAP-NG merely
to achieve a nominal 100% conversion rate.

## Reuse discovery

Cross-benchmark mapping and reuse analysis should become an optional converter
capability rather than a requirement for basic conversion.

Supported evidence classes:

- normalized Check Text equality for policy-rule alignment;
- complete normalized OVAL semantic equivalence for exact assessment reuse;
- reviewed parameterization candidates.

This can support content-library refactoring after up-conversion.

## Repository strategy

During research, keep the implementation in `vanderpol/scap-ng` so format and
converter changes can evolve together.

Once the semantic model and CLI are stable enough for external users, consider
extracting the reusable package into a dedicated repository such as
`scap-upconvert` while retaining integration/conformance workflows in
`scap-ng`.

Do not split prematurely: extracting before the format stabilizes would create
unnecessary compatibility/versioning overhead.

## Definition of an initial public release

A reasonable v0.1 milestone would be:

- installable from source with one command;
- accepts a SCAP 1.4 datastream or signed benchmark ZIP;
- emits the Board-selected SCAP-NG source layout;
- emits a complete migration/blocker report;
- validates its own output;
- produces deterministic package inputs;
- successfully converts the agreed Linux and Windows reference benchmarks;
- has zero silently dropped XCCDF/OVAL constructs;
- includes reproducible examples and documentation.

A later v1.0 should require a stable SCAP-NG specification version and
differential execution evidence from the reference scanner.
