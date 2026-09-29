# Iteration 003 Applicability Registry

## Purpose

Rules and Benchmarks SHOULD reference applicability conditions by stable
semantic identifier rather than Assessment file path.

The registry provides:

    applicability ID -> Assessment Method

Example:

    applicability:
      - id: linux.gnome-installed
        assessment: assessments/applicability/linux.gnome-installed.assessment.yaml

A Rule references only:

    applicability:
      - linux.gnome-installed

## Contents

The registry contains native SCAP-NG applicability identity and Assessment
binding information only.

It SHALL NOT contain XCCDF, OVAL, OCIL, or CPE Applicability Language IDs,
namespace URIs, hrefs, XML element trees, source component names, or legacy
definition/test/object/state IDs.

Legacy lineage belongs in evidence/provenance.

## Scope

A Benchmark-specific applicability.yaml MAY define bindings used by that
Benchmark.

A future shared registry MAY exist when applicability semantics and Assessment
implementations are proven reusable across Benchmarks.
