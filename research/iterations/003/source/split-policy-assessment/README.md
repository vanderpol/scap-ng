# Split Policy / Assessment Source

This directory contains native SCAP-NG source for the currently selected
architecture:

    Benchmark Rule -> Policy -> selected check -> Assessment

Only native source belongs here.

No SCAP 1.4 source XML, XCCDF/OVAL/OCIL IDs, migration provenance, converter
diagnostics, or sample scanner results belong in this tree.

Each benchmark receives its own directory.

Expected shape:

    <benchmark>/
      benchmark.yaml
      applicability.yaml
      policy/
      assessments/
        automated/
        manual/
        applicability/

This layout is intentionally review-oriented and may evolve as native source
examples expose better organization.
