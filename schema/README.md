# SCAP-NG 0.4.1 — single active schema family

This repository carries **only 0.4.1** under the flat `schema/` tree on `main`. The 35 root JSON Schemas and 110 supporting JSON documents, including capability mappings and native selector contracts, use the 0.4.1 version. No side-by-side version directories, parallel schema loaders or compatibility packs are supported.

The prior 0.4.0 baseline is preserved in Git history and at [`archive/scap-ng-0.4.0-main-20261113`](https://github.com/vanderpol/scap-ng/tree/archive/scap-ng-0.4.0-main-20261113). To inspect it, check out that branch instead of expecting two versions in `main`.

Native Variables contain `kind` and `expression`; they do **not** declare `datatype`. Result types are determined from typed literal values, canonical collected Item fields, referenced Variables and defined operation semantics, with no implicit lexical casts. Collected Item fields, Require comparison contracts and Organizational Inputs retain their types. Source OVAL datatype remains in conversion provenance.

Consumer applications (converter, editor, RI) must pin **0.4.1 only** and reject documents with another specification version. Updating old documents is an explicit migration, not a silent scanner/GUI fallback.

For authoring documentation, see the [schema reference](../docs/generated/schema-reference.md), [capability mappings](capability-mappings/README.md), and [0.4.1 integration requirements](https://github.com/vanderpol/scap-ng/issues/66).
