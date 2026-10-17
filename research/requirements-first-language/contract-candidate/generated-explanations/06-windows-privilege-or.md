# Native auditor explanation: Deny remote interactive logon to prohibited account categories

**Research-only compiled policy.** This is a deterministic explanation
of the same AST used by fixture tests, not separate executable prose.

## What must be true

AT LEAST ONE of these alternatives must hold:
  ALL of these conditions must hold:
    - The uniquely identified Windows computer role
      Required: role equals domain_member
    - At least one selected Windows user-right assignment (provider inputs: right=SeDenyRemoteInteractiveLogonRight)
      Required: principal equals Guests
    - At least one selected Windows user-right assignment (provider inputs: right=SeDenyRemoteInteractiveLogonRight)
      Required: principal equals LocalAccount
  - At least one selected Windows user-right assignment (provider inputs: right=SeDenyRemoteInteractiveLogonRight)
    Required: principal equals Everyone

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
