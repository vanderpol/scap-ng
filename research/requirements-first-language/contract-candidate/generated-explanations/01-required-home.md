# Native auditor explanation: The home mount must disable setuid execution

**Research-only compiled policy.** This is a deterministic explanation
of the same AST used by fixture tests, not separate executable prose.

## What must be true

- Every selected Linux mounts WHERE mount point equals /home
  At least 1 selected resources must exist across THIS population.
  Required: mount options contains nosuid

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
