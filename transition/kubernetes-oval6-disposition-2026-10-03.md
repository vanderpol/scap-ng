# OVAL 6.0 Kubernetes new-Test disposition for SCAP-NG 0.2.0

Date: 2026-10-03

Status: **explicitly deferred for 0.2.0; not unsupported forever**.

Provenance: Evidence/Audit from the pinned OVAL 6.0 new-Test inventory and upstream Kubernetes/OVAL documentation; owner direction that SCAP-NG should inspect only genuinely new OVAL 6.0 Tests and should not mechanically adopt OVAL 6.0 structure.

## Scope

The pinned OVAL 6.0 audit identified two Kubernetes Tests not present in the OVAL 5.12.3 baseline:

- `kubectl_test`
- `kubepsp_test`

This disposition closes the 0.2.0 review question for those two Tests without adding native capabilities whose model is not yet justified.

## `kubepsp_test`

**0.2.0 disposition: deferred / legacy-target-specific.**

OVAL 6.0 describes this Test as assessing Kubernetes Pod Security Policy (PSP). Kubernetes deprecated PodSecurityPolicy in v1.21 and removed it in v1.25, replacing the old mechanism with Pod Security Admission and other admission mechanisms.

SCAP-NG SHALL NOT introduce a new native 0.2.0 capability whose primary contract is tied to an API removed from modern Kubernetes solely because OVAL 6.0 added that Test.

This does not mean old Kubernetes systems can never be assessed. If supported legacy Kubernetes content later requires faithful migration of PSP checks, handle that as an explicit legacy-platform migration requirement with pinned source/runtime evidence. Do not let that historical compatibility question define the modern native Kubernetes assessment vocabulary.

A future Kubernetes security model SHOULD focus on current platform mechanisms such as Pod Security Admission or ordinary resource/API observations when concrete content and target evidence justify them.

## `kubectl_test`

**0.2.0 disposition: deferred pending a native Kubernetes resource-query model and conformance evidence.**

The OVAL 6.0 Test is described in terms of `kubectl get ... -o=yaml`, resource names/namespaces, YAML paths, and record results. Those semantics demonstrate a useful need—querying Kubernetes resources and evaluating selected properties—but the CLI invocation itself is not a compelling native SCAP-NG capability boundary.

SCAP-NG SHOULD model the target observation being requested rather than require a particular command-line client when a scanner can use the Kubernetes API or another equivalent collector.

Do not map `kubectl_test` automatically to `independent.shellcommand`. That would lose resource/namespace/query semantics, collector completeness and typed result structure, and would make an external CLI a normative dependency.

Before adding a native Kubernetes capability, require:

1. representative current Kubernetes security content;
2. expected-results fixtures;
3. a resource identity and namespace model;
4. list/single-resource and absent-resource semantics;
5. typed/structured field selection semantics;
6. collection completeness and permission/error behavior;
7. API-version/resource-version provenance where relevant;
8. evidence that API-backed and any CLI-backed collectors can produce equivalent native Items;
9. a decision about current Pod Security Admission checks independently of obsolete PSP.

The future capability name should describe the observation (for example, a Kubernetes resource/API concept) rather than freeze `kubectl` into the language unless evidence proves the command itself is the security measurement.

## 0.2.0 consequence

Neither Kubernetes Test blocks the 0.2.0 authoring-contract freeze.

- `kubepsp_test`: deferred because it targets removed PSP functionality and lacks a current-platform justification for a new native capability.
- `kubectl_test`: deferred because the underlying resource-observation need is valid, but the OVAL 6.0 CLI-shaped model should not be adopted without a native Kubernetes data model and conformance corpus.

Record both as reviewed/deferred in coverage accounting rather than “missing implementation.”

This is consistent with the owner direction that SCAP-NG replaces the need to adopt OVAL 6.0 wholesale: new OVAL Tests are capability leads, not mandatory serialization contracts.
