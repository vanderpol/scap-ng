# Native auditor explanation: Observed Apache KeepAlive and MaxKeepAliveRequests directives must satisfy policy

**Research-only compiled policy.** This is a deterministic explanation
of the same AST used by fixture tests, not separate executable prose.

## What must be true

ALL of these conditions must hold:
  - Every selected Apache configuration directive observation whose name equals KeepAlive
    At least one matching resource must exist in this selected population.
    Required: raw directive value equals On
  - Every selected Apache configuration directive observation whose name equals MaxKeepAliveRequests
    At least one matching resource must exist in this selected population.
    Required: integer value is at least 100

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
