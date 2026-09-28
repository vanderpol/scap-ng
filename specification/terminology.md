# SCAP-NG Terminology

**Status:** pre-alpha normative terminology draft

This glossary defines current SCAP-NG terms. Definitions remain subject to
revision until the specification stabilizes.

## Assessment Method

A method that determines Platform identity, applicability, compliance, or
another assessment fact.

An Assessment Method declares its own modality, such as `manual` or
`automated`.

## Assessment Request

A run-time request that identifies the Benchmark/Profile to evaluate and binds
Tailoring and Organizational Input used for that execution.

## Benchmark

The authoritative publisher policy container defining Platform scope, Rule
membership, Groups, Parameters, and publisher-defined Profiles.

## Capability

A portable Assessment collection/evaluation interface, such as file,
registry, package, or shell-command inspection.

A Capability is implementation semantics, not a policy Rule.

## Compiled Package

The scanner-facing, self-contained representation produced after source
references, Profiles, applicability, Parameters, and other authoring constructs
have been validated and normalized as required by the package model.

## Group

A meaningful logical collection of Rules and, where useful, Parameters.

Group membership does not change Rule truth or applicability.

## Manual Assessment

An Assessment Method in which a human operator follows a procedure and supplies
the completed assessment outcome or other permitted manual observations.

A procedure-only Manual Assessment is a first-class SCAP-NG form.

## Organizational Input

Typed expected-state policy data intentionally left unresolved by the
publisher and supplied by an organization or authorized run-time source.

Organizational Input is not Tailoring merely because it is locally supplied.

## Parameter

A typed policy value definition consumed by policy and/or Assessment expected-
state bindings.

## Platform

A named product or operating-system family/version identity targeted by a
Benchmark and established through an explicit Assessment binding.

A role, feature, installed package, or configuration condition is normally
applicability rather than Platform identity.

## Profile

A publisher-defined policy variation contained in a Benchmark.

Benchmark membership enables all Rules. Profile Rule selection is subtractive.

## Rule

A stable logical policy requirement owned by a Benchmark.

Rule identity is distinct from Rule revision.

## Rule applicability

A reusable condition, additional to Benchmark Platform identity, that
determines whether a Rule is relevant to the target.

## Tailoring

An external modification to already-resolved publisher policy.

Tailoring is distinct from Organizational Input.

## Source

Human-authoring content before reference resolution and canonical compilation.

Paths, filenames, comments, and source organization aid authoring but do not
define semantic identity.

## Result package

The normalized output of an assessment run containing run, target, policy,
summary, and per-Rule result information.

## Decisive outcome explanation

Structured logical/evidentiary information sufficient to justify an Assessment
outcome without requiring a consumer to reconstruct the complete Assessment
graph.

## Historical provenance

Legacy-source lineage useful for migration and review, such as XCCDF/OVAL/OCIL
identifiers.

Historical provenance is normally preserved in comments or conversion reports,
not scanner-facing Assessment semantics.

## Runtime provenance

Information needed to identify what actually executed and produced a result,
such as package identity, Benchmark/Profile identity, effective inputs,
Assessment identity/version, scanner identity, and timestamps.
