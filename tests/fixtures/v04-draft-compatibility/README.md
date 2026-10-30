# Original draft-compatibility fixtures

Original signed NIWC source ZIP bytes, pinned in `provenance.json` to repository
revision, Git blob, SHA-256 and size. No source or signature was repaired.
These are SCAP benchmark sources, not authoritative replacements for DISA manual
XCCDF releases. Embedded publisher notices remain intact.

- Active Directory Domain: observed exact nonstandard `ds:uri` catalog chain.
- Amazon Linux 2023: Test-level `all_exist` and retained strict-proof Rules.
- Windows Defender Firewall: typed XCCDF check-export / external Variable binding.

Negative tests mutate in-memory copies or explicitly labeled synthetic ZIPs.
Draft admissions are not source-validity, publisher-trust or runtime assertions.
