# Native auditor explanation: Every relevant forward lookup zone, if any, must be directory integrated

**Research-only compiled policy.** This is a deterministic explanation
of the same AST used by fixture tests, not separate executable prose.

## What must be true

- Every selected Windows DNS zone whose direction equals forward
  No matching resource is required to exist if selection is confirmed complete.
  Required: directory integration equals true

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
