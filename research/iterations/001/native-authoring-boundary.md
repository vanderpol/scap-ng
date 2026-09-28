# Native SCAP-NG Authoring Boundary

**Status:** architectural requirement for the Board-facing demonstration

## Decision

XCCDF, OVAL, OCIL, CPE XML identifiers, namespaces, hrefs, and source document
trees are **migration inputs and provenance**. They are not intended to be
normative SCAP-NG authoring constructs.

The current fidelity-first converter intentionally retains those details so
that every SCAP 1.4 construct can be accounted for during migration research.
That representation must not be mistaken for the desired long-term NG source
format.

## Required separation

The demonstration should expose two clearly different products.

### 1. Migration-fidelity view

Purpose: prove deterministic, loss-accounted conversion from SCAP 1.4.

May contain:

- original XCCDF Rule/Group/Profile/Value identifiers;
- OVAL definition/test/object/state/variable identifiers;
- OCIL questionnaire identifiers;
- original namespaces and hrefs;
- original source trees;
- migration status and diagnostics;
- source schema/version;
- exact source-to-NG reference mappings.

This view is converter evidence, not native NG authoring guidance.

### 2. Native NG authoring view

Purpose: show what a content developer would actually create and maintain if
starting with SCAP-NG.

Must use only NG-native concepts for executable semantics:

- policy rules;
- applicability references;
- assessments;
- collectors/capabilities;
- derived values/transforms;
- predicates;
- evaluation/assertion logic;
- manual procedures;
- bindings/overlays;
- profiles/parameter values;
- provenance references that are explicitly non-executable metadata.

It must not require a scanner to understand XCCDF, OVAL, OCIL, or legacy XML
namespaces.

## Examples of fields that should move out of native source

The fidelity-first output currently contains constructs such as:

    source_xccdf_tree:
    source_checks:
    source_check_logic:
    source_object_id:
    source_variable_id:
    source_state_id:
    source_test_id:
    source_definition_id:
    source_namespace:
    href: ...-oval.xml
    system: http://oval.mitre.org/...
    system: http://scap.nist.gov/schema/ocil/2

These belong in migration provenance.

Similarly, source-derived local identifiers such as:

    oval:mil.disa.stig.win:obj:25334002

should be replaced in native source by NG-local identifiers or meaningful
authoring names. A provenance mapping may preserve the original OVAL ID.

## Applicability

The following is fidelity evidence:

    kind: check_fact
    system: http://oval.mitre.org/XMLSchema/oval-definitions-5
    href: ...-oval.xml
    id_ref: oval:...:def:100002

Native NG source should instead bind a policy/platform to a native NG
applicability assessment, for example conceptually:

    applies_to:
      - windows-member-workstation

with the platform definition referencing an ordinary NG assessment.

Applicability does not get a weaker or scanner-defined test model. Anything
that can be expressed by the assessment language may be used to determine
applicability. The scanner supplies only the collector capabilities required by
the content; the content author decides which facts mean that a platform
applies.

A CPE name may remain useful as a standardized identifier, but it is not
executable evidence and must not be treated as a scanner-side platform oracle.

The exact final syntax remains subject to Board review, but legacy checking
systems must not be required at runtime.

## Automated assessment

The converter currently emits a faithful graph whose nodes still carry OVAL
source identifiers and source types. Long term, the executable graph should
contain NG concepts only.

For example, a source-derived operation such as:

    concat(
      object_component(registry-object),
      regex_capture(object_component(registry-object))
    )

may be preserved in migration provenance while the native source expresses the
same typed computation using NG-native collect/transform references.

The simplification must preserve cardinality, ordering, datatype, missing-value,
error, and result semantics.

## Manual assessment

OCIL references should not be required in native NG content.

A converted manual check should become an NG-native manual assessment/procedure.
The original OCIL questionnaire ID and source reference belong in provenance.

## Identifier strategy

During migration, stable source identifiers are valuable for traceability.
Native source should not imply that the XCCDF or OVAL identifier schemes are
part of SCAP-NG.

The prototype should therefore introduce deterministic NG-local identifiers and
maintain a separate mapping such as:

    ng_id: assessment.windows.event-log-permissions
    source:
      standard: oval
      id: oval:mil.disa.stig.windows11:def:253340

The exact naming scheme is still prototype material.

## Repository layout

Board-facing demonstration content should evolve toward:

    demonstrations/four-anchor/<benchmark>/
      source/                    # native NG only
      migration-provenance/      # XCCDF/OVAL/OCIL lineage and diagnostics
      distribution/              # package manifests/signature metadata

During transition, any fidelity-first tree must be labeled
`conversion-fidelity/` rather than simply `source/`.

## Validation requirement

Separating provenance from native source must not weaken migration proof.

CI must verify that:

1. native source reconstructs the same canonical NG semantics;
2. provenance maps every converted native item back to the original SCAP 1.4
   source;
3. removing migration provenance does not change executable behavior;
4. no legacy XCCDF/OVAL/OCIL namespace or href is required to execute the NG
   package;
5. deprecated source constructs remain visible as migration blockers without
   becoming NG runtime dependencies.

## Board-facing message

SCAP-NG is not intended to be "XCCDF + OVAL + OCIL rewritten as YAML."

Those standards are important sources for deterministic up-conversion and
backward migration evidence. The NG runtime and native authoring model should be
self-contained and independently specified.
