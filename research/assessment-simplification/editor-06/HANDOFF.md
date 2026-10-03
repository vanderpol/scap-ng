# Resume the open editor/recipe brainstorming

Latest continuation: [implementation options](IMPLEMENTATION-OPTIONS.md), receiving
`30f01a6f3117a309cdea7051611508fcf943230c`. Owner favors a separate research repo
and direct editing for the straightforward majority. TypeScript/React with an
initial Electron/local-checkout product, existing Python validation adapter and
separate Git/forge integrations are recommendations. The suggested repository
scap-ng-editor-research has NOT been created. The approximate 90% is unmeasured.

2026-10-03, `vanderpol/scap-ng`, `main`; receiving
`b13f665be9b39e7f0f19825954fe33632f4e5c3d`, clean. Find publication using
`git log -1 -- research/assessment-simplification/editor-06`.

Owner asked to expand the editor idea using previous research, especially reusable
recipes/templates and open-source use in multiple environments. This wave proposes
a shared native-authoring core/CLI with optional desktop, self-hosted browser, IDE
and vendor clients. Distinguishes copied templates, versioned authoring recipes,
observation recipes and intentionally shared native Assessments.

Primary recommendation: native output remains usable without editor/catalog;
recipes are pinned, inspectable, explicitly regenerated and detachable. Native
editing is distinct from semantic expansion; do not promise arbitrary recipe/native
bidirectional mapping. Unsupported valid advanced forms are preserved/native-only,
never flattened/dropped. Scope/fact/expectation/missing-error questions are explicit.

No implementation, mock application, license change, runtime schema/converter or
review-build change. No new vote/issue or target execution. Verification is
documentation diff/link checking only, no semantic suite or author trial. User
is reviewing the earlier full-STIG findings; this brainstorming is not adoption.

Next bounded experiment (moderate usage): build one direct editor/native preview
for the stable unix.file slice and prepare registry absence/set recipes only when
their current capability mappings support exact constructions. Reuse current
validator/model helpers, keep frontend replaceable, and compare CLI/UI handling.
Include native manual edit/repair, shared references, unsupported valid forms,
recipe version changes, deterministic expansion and detachment cases. Invite an
author trial assessing correct scope/missing/error reasoning and debugging, not
just number of clicks. Multiple clients and product packaging follow that evidence.

Read AGENTS/current design/transition decisions and editor-06 README first. Keep
Benchmark→Rule→Assessment, separate applicability, independently declared capability
types, publisher-owned requirements and constrained Organizational Input. A new
Apache-2.0 toolkit is proposed only; no claim existing source assets have that
license. Suitable shellcommand API queries are legitimate, all filesystem
searches stay native-scanner-owned. No rare-feature removal/deprecated support.
