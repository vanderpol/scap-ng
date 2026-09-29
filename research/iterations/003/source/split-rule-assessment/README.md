# Split Rule / Assessment Source

This directory contains native SCAP-NG source for the currently selected
architecture:

    Benchmark -> Rule -> selected check -> Assessment

Only native source belongs here.

No SCAP 1.4 source XML, legacy execution IDs, migration provenance, converter
diagnostics, or sample scanner results belong in this tree.

Each Benchmark receives its own directory.

Expected shape:

    <benchmark>/
      benchmark.yaml
      applicability.yaml
      rules/
      assessments/
        automated/
        manual/
        applicability/

The Benchmark declares its primary SCAP-NG `use_case`. Assessment `class`
remains independent and describes the truth semantics of an individual
Assessment.

This layout is intentionally review-oriented and may evolve as native source
examples expose better organization.
