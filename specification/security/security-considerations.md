# Security Considerations

**Status:** initial pre-alpha draft

## 1. Untrusted content

SCAP-NG content SHALL be treated as potentially untrusted input.

Processors SHALL validate package structure, integrity metadata, object
schemas, semantic constraints, and references before executing Assessment
content.

Invalid content SHALL NOT be executed merely because it can be parsed.

## 2. Executable capabilities

Capabilities that execute commands, interpreters, queries, or equivalent
active operations require particular care.

Assessment execution behavior SHALL come from publisher-authored Assessment
content, not from Tailoring or Organizational Input.

Policy data SHALL NOT be allowed to inject commands, scripts, shell fragments,
SQL, XPath, interpreter input, collector choice, privileges, or operations.

## 3. Shell command execution

When an Assessment uses `independent.shellcommand`, the Assessment SHALL
identify the intended interpreter/shell and command semantics explicitly.

Implementations SHOULD avoid adding implicit shell interpretation where the
Assessment did not request it.

## 4. Package integrity

Compiled packages SHOULD support integrity verification and digital signatures.

Consumers SHOULD verify declared integrity information before executing
content.

The final trust/signature profile remains under design.

## 5. Sensitive results

Assessment results may disclose host identity, configuration state,
vulnerabilities, organizational policy values, paths, accounts, and other
sensitive information.

SCAP-NG SHALL define a result model that permits minimization of retained
evidence.

The final confidentiality, redaction, and encryption requirements remain open.

## 6. Security value of policy

SCAP-NG can standardize how policy and assessments are expressed and executed.

Conformance to the SCAP-NG format SHALL NOT be interpreted as an assertion that
the underlying security policy is effective, appropriate, or complete.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: OVAL 5.12.3 Capability Crosswalk](../migration/oval-5.12.3-capability-crosswalk.md) · [Contents](../README.md) · [Next: SCAP 1.4 to SCAP-NG Concept Crosswalk →](../crosswalk/scap-1.4-concept-crosswalk.md)

<!-- spec-nav:end -->
