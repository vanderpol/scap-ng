# Canonical manual response lifecycle

The Benchmark and Rule reuse the canonical manual approval Assessment.
The independent response manifest binds its six authored choices to
technical outcomes. Separate workbook variants test no submitted response,
a completed response with comment and evidence, an unchanged question
at a new Assessment revision, and a changed question at that revision.

The [standalone Result vectors](expected.json) publish all six outcomes
with exact response values and target Assessment identity. They exercise
direct, imported and delegated provenance in the canonical Result schema.

RI generated all six choices. Its importer accepted four completed
outcomes and rejected completed `error` and `not_evaluated`. A
revision-only upgrade preserved the completed response and rebound its
fingerprint to the new Assessment bytes. Changing the procedure marked
the old response stale, preserved its previous outcome for review and
made it unavailable for import. An initial unanswered workbook also
supplied no response.

```sh
python conformance/tools/replay_manual_lifecycle.py --check \
  --ri-content /path/to/pinned/ri-content \
  --ri /path/to/pinned/scap-ng-ri
```

The receipt covers workbook generation, upgrade and import. In this VM
the Benchmark CLI reaches filesystem admission after successful answer
loading and returns `unknown_mount_not_authorized`. A scanner-generated
Manual Assessment Result and OCIL migration remain unqualified.

- [Workbook lifecycle and import receipt](ri-receipt.json)
- [RI workbook scope](https://github.com/vanderpol/scap-ng-ri/issues/10)
- [RI VM filesystem admission](https://github.com/vanderpol/scap-ng-ri/issues/306)

The [Studio receipt](studio-receipt.json) records schema admission of
the same six Result bytes with the exact-pin metadata pack.
