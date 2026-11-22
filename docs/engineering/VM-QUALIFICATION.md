# Codex VM qualification procedure

Expensive canonical conformance, generated-schema/documentation, and normative
OVAL inventory runs use the retained Codex VM while hosted Actions allowance is
exhausted. Hosted workflows remain available through `workflow_dispatch` for
funded independent replay. Lightweight PR stack, publication-boundary, schema
pin and focused language checks remain hosted.

## Exact VM commands

Run from a clean checkout of the reviewed commit, write receipts outside the
checkout, and do not overwrite an existing output directory:

```bash
df -BG /tmp
python3 -m pip install -r requirements-dev.txt
python3 tools/generate_native_selector_schema.py --check
python3 tools/generate_docs.py --check
python3 tools/generate_unix_file_reference.py --check
python3 tools/generate_approved_annotation_pilot.py --check
python3 tools/generate_review_documentation_pack.py --check
python3 tools/generate_documentation.py --check
python3 tools/audit_schema_documentation.py --check
python3 tools/audit_documentation_fidelity.py --check
python3 tools/check_documentation_examples.py --check
python3 -m unittest discover -s tests -v
```

For the full conformance corpus, preserve the unchanged commands from
`.github/workflows/conformance.yml`:

```bash
python conformance/tools/runner.py validate
python conformance/tools/runner.py coverage
python conformance/tools/audit.py
git diff --exit-code -- conformance/coverage-audit.json
PYTHONPATH=tests python -m unittest test_issue87_conformance test_model_a_oracle -v
```

For the OVAL 5.12.3 inventory, check out the pinned OVAL commit
`2f140ee5c5dd1ed9606fcd5afc301f6baeb48706` and run:

```bash
python3 -m unittest discover -s tests -p 'test_audit_oval_language.py' -v
python3 tools/audit_oval_language.py \
  --oval-dir upstream/oval/oval-schemas \
  --mapping-root schema/capability-mappings \
  --output "$OUT/oval-5.12.3-grammar.json"
```

Record exact command argv, exit code, reviewed/canonical SHA, every generated
file SHA-256, dependency/tool versions, disk preflight and PASS/FAIL/HOLD in a
machine-readable receipt. A stale generated file or missing source pin is a
failure, never a reason to skip the gate.
