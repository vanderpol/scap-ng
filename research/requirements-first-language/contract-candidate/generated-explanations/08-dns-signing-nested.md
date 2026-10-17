# Native auditor explanation: Every forward DNS zone must be signed with both key kinds in validity range

**Research-only compiled policy.** This is a deterministic explanation
of the same AST used by fixture tests, not separate executable prose.

## What must be true

- Every selected Windows DNS zone whose direction equals forward
  At least one matching resource must exist in this selected population.
  ALL of these conditions must hold:
    - signed equals true
    - Every selected zone-signing key belonging to the same DNS zone
      At least one matching resource must exist in this selected population.
      Required: validity (hours) is between 48 and 168
    - Every selected key-signing key belonging to the same DNS zone
      At least one matching resource must exist in this selected population.
      Required: validity (hours) is between 48 and 168

## Evidence and status rules

Resource counts refer to fully selected resource Items, not only Items that passed.
Confirmed complete-empty, incomplete/unknown selection, unreadable fields and
acquisition errors are distinct. A proven violation can be decisive even
when other evidence is incomplete. Named singleton resources must be
uniquely identified by their provider contract; duplicate candidates
are a provider error, not a convenient selection of one passing record.
Nested key/file evidence is scoped to the parent Item and requires its
own explicit completeness and identity status.

**Source-conversion boundary:** Nothing here proves that this native
policy reproduces an original SCAP 1.4 / OVAL assessment.
