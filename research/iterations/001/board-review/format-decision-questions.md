# SCAP-NG Format Decision Questions

Use the same four-anchor evidence and the same exact-reuse groups for all
candidate formats.

## Rule and policy comprehension

- Can a reviewer understand the policy requirement without following excessive references?
- Can a reviewer see the automated assessment associated with that requirement?
- Can policy-only publication remain straightforward?
- Does the format make applicability/profile behavior discoverable?

## Assessment reuse

- How is one technical assessment shared by multiple STIG rules?
- Is the reuse relationship explicit or inherited?
- Can policy identity remain independent from assessment identity?
- Can the shared assessment be versioned independently when appropriate?
- Can a reviewer identify every rule affected by a shared assessment change?

## Combined-rule overlays

- What exact fields may an overlay change?
- Can tooling prove that an overlay did not mutate technical assessment semantics?
- Is a shared rule base still understandable when policy identity/title/check/fix text are supplied by overlays?
- Does the overlay mechanism remain simpler than explicit bindings at large reuse fan-out?

## Split policy / assessment / binding

- Is the binding layer easy enough for content authors and reviewers to navigate?
- Does explicit composition make provenance and impact analysis clearer?
- Can tools provide a resolved "show me the whole rule" view so separation does not harm readability?
- How should assessment versions and binding compatibility be expressed?

## Ansible-inspired authoring

- Do ordered steps/register/assert conventions make assessment logic easier to learn?
- Does the syntax add ceremony without reducing semantic complexity?
- Is it sufficiently clear that there is no Ansible/Jinja/runtime dependency?
- Does familiarity improve review while still preserving typed SCAP-NG semantics?

## Migration and implementation

- Does SCAP 1.4 conversion require any format-specific semantic compromise?
- Can all formats compile to the same canonical semantics?
- Can a reference scanner consume one resolved package model regardless of authoring syntax?
- Can source-vs-NG differential execution remain independent from the chosen authoring format?

## Evidence reviewers should use

Reviewers should compare:

- the same RHEL/Oracle exact-reuse examples;
- the same Windows Client/Server exact-reuse examples;
- the Check-Text-only Linux mapping that intentionally does **not** qualify for reuse;
- the Windows deprecated-source blockers;
- the complete four-anchor maintenance/reuse counts.

The format decision should be based on clarity, safety, maintainability,
migration fidelity, and implementation burden—not on unequal example content.
