# Draft ESXi host cases

These are native 0.2.0 Assessments with synthetic Items, an independently
explained scalar/status oracle, and schema/graph/result regressions. They do not
connect to VMware or prove complete collector/comparator conformance.

- [Service Assessment](content/service.assessment.yaml) selects service key
  `TSM-SSH` and requires Boolean `service_running` false.
- [Advanced-setting Assessment](content/advancedsetting.assessment.yaml) selects
  `UserVars.ESXiShellTimeOut` and requires integer value 600.
- [Expected results](expected-results/cases.json) explain matching/failing scalar
  values and missing/error/not-collected/incomplete/N/A collection statuses.
- `service-item.json` and `advancedsetting-item.json` simulate one host's
  observations; they are not output from an installed VMware collector.

Source: OVAL-Community/OVAL v6.0 commit
`5afcf590fb5d334687bfdc47f98716424cdb7f3d`, new Test contracts only. Shared
native existence/status behavior retains the later 5.12.3 baseline. Service key
is distinct from label; activation policy is distinct from running state.
Repeated advanced-setting values retain their types and occurrences.

A live fixture must specify ESXi version, host identity, access/privileges,
exact setup/restoration steps, acquisition backend and independently reviewed
expected settings. These example values are not universal policy or availability
claims. PowerCLI source examples illustrate acquisition, not a mandatory backend.

From the repository root:

```sh
python tools/test_esx_host_capabilities_v02.py
python tools/validate_native_json_schemas.py tests/esx-host-0.2.0/content --schema-dir schema/v0.2.0
python tools/check_current_authoring_contract.py tests/esx-host-0.2.0/content
```

The focused suite covers version isolation, compiler preflight, invalid unused
Tests, selectors, State fields, cross-capability references, typed/multiple/status
Items, reporting/redaction, and exact committed source/license preservation.
Simple synthetic equality cases are not a general State evaluator. Full vendor
and target coverage remains tracked in #128/#131.

## Host account and installed software slice

- [Account Assessment](content/account.assessment.yaml) selects `audit-user`
  and requires Boolean shell access false. [Item](account-item.json) includes
  domain, description and role as synthetic supporting observations.
- [VIB Assessment](content/vib.assessment.yaml) selects `fixture-vib` and requires
  the `VMwareCertified` category. [Item](vib-item.json) preserves vendor, creation
  date and version as strings.
- [Expected equality results](expected-results/identity-software.json) explain
  passing/failing examples, including `Unknown` as a present category yielding
  false against `VMwareCertified`, not the technical unknown outcome.

Run `python tools/test_esx_identity_software_v02.py` with the commands above.
It checks exact source field/type/cardinality declarations, category enums,
XML-placeholder removal versus native Variable references, unavailable/redacted
entities, JSON payload types, report identity, invalid unused nodes, graph
compatibility, version isolation and real unsigned compilation/verification.
Structural Variable-reference validation is not a runtime value-resolution
oracle. Account description/role can require confidentiality controls. The
comparator oracle uses independently stated scalar equality, not a converter's
output. Existing collection-status expectations apply to both new capabilities.

Provenance: Adapted source contracts; Common native fixtures; Evidence/Audit
synthetic expected results. All original XSD license notices remain retained.
Live-target and complete vendor conformance remain open.
