# Iteration 003 Applicability Registry

**Status:** accepted working direction

## Purpose

SCAP-NG Rules and Benchmarks SHOULD reference applicability conditions by stable
semantic identifier rather than by assessment file path.

The applicability registry provides the indirection:

    applicability id -> Assessment Method

This prevents every Rule from embedding repository layout and allows the
Assessment implementation to change location without changing policy semantics.

## Native source form

Illustrative form:

    applicability:
      - id: linux.gnome-installed
        assessment: assessments/applicability/linux.gnome-installed.assessment.yaml

      - id: linux.fips-enabled
        assessment: assessments/applicability/linux.fips-enabled.assessment.yaml

A Rule then references only the semantic identifier:

    applicability:
      - linux.gnome-installed

The exact serialization remains under schema review, but the semantic boundary
is accepted for iteration 003.

## Scope

A benchmark source tree MAY contain a local `applicability.yaml` registry for
conditions used by that Benchmark.

A future shared applicability registry MAY be introduced for conditions whose
semantics and Assessment Methods are proven reusable across Benchmarks.

A local registry SHALL NOT duplicate shared bindings merely because a Rule uses
them.

## Registry contents

The registry contains only native SCAP-NG applicability identity and binding
information needed to resolve an applicability condition to an Assessment
Method.

It SHALL NOT contain legacy source serialization.

In particular, native applicability registry output SHALL NOT contain:

- XCCDF identifiers;
- OVAL identifiers;
- OCIL identifiers;
- CPE Applicability Language identifiers;
- XML namespace URIs;
- source component hrefs or filenames;
- raw XML element/attribute trees;
- source OVAL definition/test/object/state IDs;
- OCIL questionnaire IDs or structures.

Legacy lineage belongs only in separate conversion provenance/evidence.

## Assessment path versus identity

File paths are authoring/package resolution details, not stable semantic
identity.

The applicability identifier is authoritative for policy references.

The registry binds that identifier to the declared Assessment object. A future
package format MAY replace source file paths with package-local object
references without changing Rule semantics.

## Conversion rule

During SCAP 1.4 up-conversion:

1. classify each source applicability predicate semantically;
2. create or reuse a meaningful NG applicability identifier;
3. lower the executable predicate to a native Assessment Method;
4. bind the applicability identifier to that Assessment in the registry;
5. retain source IDs/namespaces/hrefs only in the separate provenance ledger.

If a legacy identifier, namespace, href, or XML structure appears to be
required in native NG output to preserve behavior, conversion of that path
SHALL stop for design review. It SHALL NOT be emitted automatically.
