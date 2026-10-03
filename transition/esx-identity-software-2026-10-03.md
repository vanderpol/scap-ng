# ESXi host accounts and installed VIBs — 2026-10-03

Repository: `vanderpol/scap-ng`; base `main` at
`a36ab1fc8583c62b075fb7f4492d705b9c7723f4` (merged #140).
Implementation branch: `esx-host-identity-software-20261003`.

## Implemented scope

Draft 0.2.0 `esx.host_account` and `esx.host_vib` mappings retain named Object
selectors and every source State/Item field. Account shell-access observations
are Boolean; other account data is string. Installed VIB acceptance categories
retain all five exact values, including `Unknown` as a category distinct from
the unknown technical outcome. VIB date/version fields remain strings.

Explicit `item_value_types` and `item_value_enums` constrain present observed
payloads in reviewed mappings. Unavailable/status-only and redacted entities
remain valid without values. This closes wrong-JSON-payload acceptance for these
new contracts without altering stable schemas. The source's empty XML enum
placeholder becomes a native Variable reference; no empty category is accepted.
Runtime Variable resolution/comparison is still a producer responsibility.

Two capability references document selection, acquisition boundaries, all
fields, expected behavior, confidentiality and conformance gaps. Field
explanations also appear in generated schema annotations. Standalone Assessments,
synthetic Items and an explained equality oracle are in `tests/esx-host-0.2.0/`.
Fixtures include `Unknown` failing a VMwareCertified requirement.

## Evidence

Source: OVAL-Community/OVAL v6.0 commit
`5afcf590fb5d334687bfdc47f98716424cdb7f3d`, exact licensed ESX blobs already
pinned in `third_party/oval-6.0-new-tests/`. Only newly added Test contracts are
adopted; no existing 5.12.3 behavior is replaced.

- `python tools/test_esx_identity_software_v02.py`: 8 focused tests pass,
  covering source fields/cardinality/categories, valid/invalid nodes, graph
  compatibility, version isolation, unavailable/redacted/typed Items, reporting,
  synthetic equality and actual unsigned compilation/verification.
- All 79 local maintained regression/generation commands pass, including the
  pinned upstream new-Test/XSD audit. The local runner initially omitted the
  multiline schema-generation command; that generation and the subsequent JSON
  validation were then explicitly executed successfully.
- `python tools/check_assessment_reference.py`: 9 documents, 6 capability
  references, 12 source pins; no missing links or field-table differences.
- Native schema CLI and authoring guard: all 4 standalone host Assessments pass.
- All 100 stable generated capability fragments compare identically against the
  generator at the base commit. No 0.1.0 mapping/schema file changed.
- `python tools/audit_repository_layout.py --check`: 34,242 baseline paths,
  zero preservation failures. `git diff --check` passes.

Exact-head Windows/Linux CI is the publication/merge gate. These checks establish
representation and graph consistency, not live acquisition or a full evaluator.

## Remaining work

Four of the 22 new OVAL 6.0 Test contracts have draft native mappings; 18 remain
(16 ESX and 2 Kubernetes). Continue host groups, then inherited VM/device and
management-plane contracts, and Kubernetes API/version requirements. Host
module version has a source State/Item type difference that needs explicit
review before that mapping is adopted. Singleton Object selection/filter
semantics also need an explicit reviewed contract.

Live collection, comparator operation boundaries, runtime enum-bound Variable
resolution, account/domain correlation and independent vendor conformance
remain #128/#131. Do not call 0.2.0 finalized or start exhaustive Codex corpus
expansion from this slice. Preserve current test-content/readiness plan.

Provenance: Inherited exact licensed upstream sources; Adapted fields, datatypes,
cardinality and category semantics; Common native mapping/reference/content;
Evidence/Audit source checks, synthetic expectations and coverage limits.
