# Assessment simplification: refinement 01

**Experimental research, 2026-10-03. No accepted schema, converter, scanner or policy change.**

Receiving checkout: branch `work`, SHA `5a36e7b1be002b76f5501e500be2eeb1e0a17764`;
clean and equal to GitHub `main`. Work continued on local `main` at the same SHA,
following the pre-alpha direct-main convention. See `git log -- this-directory`
for the containing checkpoint commits. The established architecture is
Benchmark → Rule → Assessment, with policy owned by Benchmark/Rule; a separate
Policy file is superseded. Applicability remains separate from configuration.

This builds on the [12-case study](../README.md), rather than rerunning its
explanations as new discoveries. The initial study is preserved. This directory
is development research, not a second external review surface. Schema
stabilization, converter changes, review-build changes and target deployment are
outside this checkpoint.

Read [sample refinements](SAMPLES.md), [comparison and execution contracts](CONTRACTS.md),
[versioned decision candidates](DECISIONS.md), [evidence](evidence/), and
[resumption instructions](HANDOFF.md).

## Experiments and revisions

1. **Finite tables:** replace a regex-only comparison with independently derived
   XML and emitted-node contracts for RHEL9 audit and crypto. The expander consumes
   the publisher tables alone; the oracle does not import its templates. Keep 24
   audit Tests and 12 crypto Tests, each with its own resource existence contract.
   Source/default inspection corrected the research oracle's initial assumption:
   omitted Test `check_existence` defaults to `at_least_one_exists`, not `all_exist`.
   A pinned-XSD regression now checks that default. Nothing in production changed.
2. **Acquisition contracts:** prototype a fixed, non-traversing DNS query and a
   shared Apache explicit-occurrence library over native snapshots. Neither is a
   full collector or a deployment. These attack the source's command/dataflow
   complexity without adding a general join to the language.
3. **Falsification:** the first Apache implementation accepted an uncollected
   optional include as absent. A failing fixture drove explicit native absence
   handling. Further fixtures retain query errors, incomplete inventories,
   duplicate/missing keys, source anomalies, repeated includes and conflicting
   directive occurrences. Stronger DNS per-zone checking remains a changed-method
   proposal, not an allegation that original OVAL loses variable-instance scope.
4. **Documentation-driven challenge:** Apache2.4 documentation confirms that
   relative Includes use ServerRoot. A new failing fixture exposed selection
   against the old caller-supplied root after a ServerRoot change. The restricted
   parser now fails that unsupported change before selecting subsequent Includes.
   [Pre-fix failure](evidence/server-root-falsification.txt) is retained separately
   from passing final verification.

## Readable before/after examples

Original [audit](../samples/rhel_9/assessments/automated/niwc.rhel_9.SV-258179.automated.assessment.yaml)
and [crypto](../samples/rhel_9/assessments/automated/niwc.rhel_9.SV-258236.automated.assessment.yaml)
snapshots remain unchanged. After authoring:
[24 audit rows](tables/SV-258179.yaml), [12 backend rows](tables/SV-258236.yaml).
Expansion: [audit](expanded/SV-258179.assessment.yaml), [crypto](expanded/SV-258236.assessment.yaml).

```yaml
# EXPERIMENTAL compile-time authoring, not runtime syntax.
kind: crypto_backends
id: research.refinement.SV-258236
defaults: {capability: unix.symlink, existence: some, match: all}
templates: {}
rows:
  - id: bind
    full_path: /etc/crypto-policies/back-ends/bind.config
    field: canonical_path
    expected: /usr/share/crypto-policies/FIPS/bind.txt
  - id: nss
    capability: unix.file
    full_path: /etc/crypto-policies/back-ends/nss.config
    field: type
    expected: regular
# The actual table retains all twelve rows, not just this excerpt.
```

The implementation emits separately named Object/State/Test nodes using ordinary
Assessment structure. Tables are publisher-owned immutable artifacts; they are
not Variables, shell scripts or runtime Organizational Input. The output passes
the generic schema/vocabulary checks, but deep capability execution is unproven.
In particular the generic `unix.file` NSS State is a projection of the inherited
type predicate, not evidence of complete clean-native capability validation.

Apache after acquisition exposes records such as:

```yaml
# EXPERIMENTAL observation, never a compliance Boolean from the collector.
installation: one
context: [[VirtualHost, ['*:443']]]
path: /srv/httpd/conf/site.conf
line: 12
occurrence: 4
directive: SessionCookieName
arguments: ['session;HttpOnly;Secure']
```

KeepAlive, cookie and DocumentRoot Assessments can share this acquisition while
retaining their own Tests and States. The parser neither computes effective
values nor opens/traverses a filesystem. Native acquisition must provide files,
statuses, mount exclusions, links and privileges. Unsupported glob/conditional
syntax fails explicitly in this restricted experiment.

Final verification: **29 refinement + 22 original-study + 63 inherited evaluator
methods passed**. Logs and exit statuses are in [verification](evidence/verification.json).

## Reproduce

From `/workspace/scap-ng`, activate Python 3.12 with PyYAML, lxml and jsonschema.
The saved environment supplies `/workspace/.venvs/scap-ng`:

```bash
source /workspace/.venvs/scap-ng/bin/activate
export PYTHONPATH=/workspace/scap-ng/tools
export PYTHONDONTWRITEBYTECODE=1
python research/assessment-simplification/refinement-01/build_tables.py
python research/assessment-simplification/refinement-01/build_protocol_schema.py
python -m unittest discover -s research/assessment-simplification/refinement-01 -p test_refinement.py -v
python -m unittest discover -s research/assessment-simplification/experiments -p test_semantics.py -v
python -m unittest discover -s tools -p 'test_oval_result_truth_tables*.py' -v
python research/assessment-simplification/experiments/verify_study.py
python tools/check_current_authoring_contract.py research/assessment-simplification/refinement-01/expanded
python tools/validate_native_json_schemas.py research/assessment-simplification/refinement-01/expanded --schema-dir schema/v0.1.0
```

The five ZIPs were freshly fetched at the exact NIWC pin and SHA-256 checked.
Regenerating source evidence with the original extractor reproduced all 56 XML
extracts byte-for-byte. The fetch URLs, revisions, package hashes and command are
recorded in [source reproduction](evidence/source-reproduction.json); local ZIP
cache is not required for model tests. See the parent README for extraction.

The PowerShell adapter is **unexecuted**: there is no Windows DNS target or
PowerShell runtime in this machine. Do not execute inherited sample scripts.
Official API/grammar references were inspected at pinned MicrosoftDocs and
Apache2.4 repository revisions; [retrieval evidence](evidence/product-references.json)
includes hashes and excerpts. The public documentation sites were blocked, so
the corresponding official source repositories were used. Documentation confirms
the DNS RRType interface and Apache include/continuation complexity; it does not
establish target field availability or execution equivalence.
No upstream Self-Assertion target corpus was run. No scanner equivalence,
performance improvement, production false-pass rate or usability-study result
is claimed.

## Provenance

**Inherited:** original 83 sample/context files, 12 source Rule/OVAL closures,
five source package pins, current requirements/glossary and the existing study.
**Adapted:** finite tables from prior research proposals; bounded XML projection
from inspected source and pinned XSD defaults; named-node output using current
Assessment vocabulary. **Common:** newly authored expander, decoder, restricted
Apache parser, fixed query sketch and synthetic fixtures. **Evidence/Audit:**
contracts, source/row mappings, hashes, reproducibility, counts, counterexamples
and limitations. No external scanner implementation copied. Legacy IDs live
only in separate evidence; emitted Assessments have native local IDs and do not
depend on evidence for execution. No deprecated capability was added or supported
capability removed.
