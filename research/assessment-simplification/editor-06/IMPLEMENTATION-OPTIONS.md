# Language, deployment and Git integration recommendation

Sequencing correction: the owner's subsequent [all-content requirement](FULL-COVERAGE.md)
makes complete native-model handling and hard mixed dependency fixtures the first
architecture gate. The simple-slice-first task near the end remains historical
proposal text; it cannot establish complete editor capability on its own.

**Experimental recommendation, 2026-10-03.** Receiving `main` SHA
`30f01a6f3117a309cdea7051611508fcf943230c`. Owner favors a separate editor research
repository and direct editing for the straightforward majority of content. The
owner's approximate 90% is a planning hypothesis, not a measured classification
from the 736-rule reading. Recipes remain optional help for repeated/difficult
patterns. No new repository, app, schema or accepted toolkit architecture was
created by this recommendation.

## Recommended language and initial product

Use **TypeScript** for the new editor's document/editing core and CLI, with **React**
for its reference UI. The same editing code can run in a browser, a Node process
or a desktop wrapper. Typed models, available YAML document libraries, schema
validators and the web/IDE ecosystem make this a practical candidate for reuse.
This is an implementation hypothesis, not demonstrated portability or correctness.

Prefer a standalone application opening a local Git checkout for the first useful
product. **Electron** is a pragmatic research wrapper: one TypeScript/JavaScript
stack, local files and integration with installed Git. Its larger distribution
and runtime maintenance are costs. Tauri is an alternative if a smaller footprint
becomes important, with a Rust wrapper/toolchain and native integration cost. Do
not add a second desktop stack merely to demonstrate equivalent functionality.

The React UI can first be developed in a local browser while testing document
handling. That does not make a hosted website the required product. Later deploy
the same UI/core in an organization-hosted site with an appropriate backend.
Not every file/Git/auth feature can be reused unchanged across desktop and browser;
environment adapters must implement explicit contracts.

Retain the existing Python conversion/validation investment through an adapter.
The initial TypeScript core owns editing, document references, form state and
structural checks; it does NOT reimplement the OVAL evaluator or whole converter.
Use the maintained Python tool as the authority for checks it already implements.
Browser structural validation is not proof of full semantic validation. A hosted
service or local desktop adapter can invoke that tool; a disconnected browser
without it must report those checks as unperformed. Do not silently substitute a
different validator and imply equal coverage. Any later semantic port needs
independent differential/conformance fixtures and explicit ownership of authority.

## Core versus application boundary

| Component | Responsibility |
| --- | --- |
| Headless core | Native document model, deterministic edits, stable references, diagnostic/source locations, optional recipe expansion |
| Reference UI | Forms/tables, native text, dependency inspection, review/change explanation |
| Filesystem adapter | Open/save native files and preserve unedited document regions |
| Git adapter | Local working-tree/branch/commit operations using Git, or explicit hosted equivalents |
| Forge adapter | Repository discovery, pull requests, review links and validation status for a configured provider |
| Validation adapter | Invoke version-pinned existing authoritative tools; distinguish structural and semantic checks |

The core SHALL NOT require GitHub, Gitea, a browser, a database or a scanner.
Consumers MAY edit source without Git. Plain native files remain the content
interchange; no editor project database is the only authoritative representation.

Use a YAML document/AST representation capable of preserving comments and
unedited fields, with reference-aware editing; a parse-to-plain-JSON/reserialize
loop is insufficient. Keep valid unsupported forms in native view or untouched.
Reference sharing and capability declarations remain explicit. A form is a view
of the saved Assessment, not another compulsory assessment language.

## Git and forges solve different layers

The portable base is **ordinary Git**, including configured HTTPS/SSH remotes.
GitHub and Gitea add review/discovery/status services; do not encode GitHub URLs
into document identities or require a provider account for local authoring.

First desktop workflow:

1. Open an existing local repository; clone can be added as a convenience.
2. Select/create the author's working branch according to that repository's policy.
3. Edit native files through forms or text and run available validation.
4. Review the actual diff and any explanatory semantic change summary.
5. Commit locally, push explicitly, then open/link a pull request if that workflow
   is used. Direct-main workflows remain possible when repository policy permits.
6. Link provider checks/reviews without turning successful syntax checks into a
   semantic-equivalence or compliance badge.

Existing installed Git credentials/SSH agents can serve local Git operations.
The authoring core never stores them in assessment files. Dirty checkouts,
external edits and merge conflicts must be visible; do not overwrite them or
silently force-push. These are future product behavior requirements, not additional
approval steps imposed on the current research workflow.

A provider interface can expose discover repositories, create/link pull request,
read status and open review location. Separate implementations use the GitHub and
Gitea APIs. Gitea must support a configurable base URL, including private instances.
Similar Git transport does not mean identical forge APIs or feature availability.
Unsupported operations should be explicit, with an ordinary web review link as
a simple initial fallback. No need for an elaborate forge integration in v0.

GitHub App authorization is a candidate for a hosted integration; Gitea OAuth or
an appropriate narrowly scoped credential is a candidate depending on deployment.
These are design options, not completed registrations or token provisioning.
Desktop-only v0 can avoid forge credentials entirely by using installed Git and
opening the provider's website after push.

## A hosted website needs another deployment adapter

A hosted browser cannot just run the developer's Git binary or access arbitrary
local checkouts. The service needs a defined workspace/storage model, concurrent
edit handling and authenticated Git/forge operations, or an explicitly implemented
browser Git approach with its CORS/auth constraints. A browser file importer is
not equivalent to full working-directory support in every browser.

An organization-hosted backend can operate on service-side checkouts, expose
document/validation/review operations and retain forge credential material outside
the frontend. Reuse core operations in the backend and UI as appropriate; keep
server identity and access control separate from assessment authoring. The same
native output remains usable in standalone/offline operation.

Open code does not require a public SaaS. Private Gitea plus a local desktop editor
is a complete plausible workflow. An air-gapped site can use local Git and pinned
tool/recipe bundles with no live forge. A public hosted editor is a later optional
service, not an interoperability dependency.

## Separate research repository

Suggested name: **scap-ng-editor-research**. This is a recommendation, not an
existing repository/link or an instruction to transfer standards ownership.
Its initial content could be:

```text
docs/                 proposals, scope and evidence limits
packages/core/        headless native document/edit operations
packages/ui/          reference React components
apps/desktop/         first local application
apps/cli/             repeatable validation/edit tooling
adapters/             Git, forge and existing-validator boundaries
examples/             small pinned native fixtures and author scenarios
recipes/              optional experimental authoring recipes
```

Do not populate every directory with placeholder frameworks up front. First prove
one document load/edit/save path and preservation behavior. Schema/converter
authority stays in scap-ng; reference versioned releases or pinned commits and
record fixture provenance. Do not fork a second normative schema/specification
into the editor repository. Licensing is a separate unresolved project choice;
TypeScript/Electron selection does not change existing code/content reuse terms.

Next bounded prototype (moderate usage): direct editing of the ready unix.file
slice, native text repair, named-reference preservation, a local checkout and a
reviewable Git diff. Verify the CLI and UI use the same edits; make other supported
native forms survivable even without widgets. Add registry/right-list forms when
their native mappings are ready. Follow with Git push/review links and explicit
GitHub/Gitea adapters. Hosted collaboration, rich recipes and full runtime preview
follow evidence; no reference scanner is needed for the first authoring prototype.

Provenance: **Inherited** native architecture, prior editor research and existing
Python tooling; **Adapted** portable core into a TypeScript/direct-editor proposal;
**Common** deployment/adapters/repository layout recommendation; **Evidence/Audit**
costs, authority boundaries and unverified claims. No software, external repository
or forge integration was implemented; only documentation links/diff were checked.
