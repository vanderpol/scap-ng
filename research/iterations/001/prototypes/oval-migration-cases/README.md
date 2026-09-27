# OVAL Migration Case Prototypes

These examples translate difficult existing OVAL definitions from `vanderpol/scap-content` into candidate SCAP-NG structures.

They are **semantic research cases**, not official replacement content and not yet conformance examples.

Each case is intended to answer four questions:

1. Can the OVAL semantics be represented natively without silent loss?
2. Is the NG source easier for an author/reviewer to understand?
3. Can a scanner collect the evidence efficiently using semantic capabilities?
4. Can the result explain a failure without reconstructing the complete OVAL graph?

Where useful, both architecture candidates are shown:

- `split/assessment.yaml` — reusable assessment object;
- `combined/rule.yaml` or shared-rule + overlay — policy and automation together.

Result fixtures use the decisive-outcome explanation model from `../../result-explanation-model.md`.

## Implemented cases

| Case | OVAL semantics stressed |
|---|---|
| RHEL 10 SV-281055 | nested AND/OR, sets/filters, local variables, derived path, default/alternate branch, mode bits |
| RHEL 8 SV-230385 | check=all + at_least_one_exists, regex matching, required population in three files |
| Windows Server 2012 SV-226208 | OVAL OR used to encode policy N/A, existence + registry state |
| PostgreSQL 16 SV-261875 | multi-valued external variable, object expansion, check=all |
| RHEL 10 SV-281050 / SV-281053 | local variables, regex capture, concat/group lookup, dynamic expected GID |
| PostgreSQL 16 SV-261956 / SV-261957 | opaque shellcommand decomposed into instance discovery + typed DB settings + universal assertion |

## Migration status

These are `prototype_native_translation` examples. They have not yet completed differential execution against the original OVAL and therefore must not be labeled `exact_native`.
