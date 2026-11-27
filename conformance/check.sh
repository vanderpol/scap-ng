#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
python conformance/tools/runner.py validate
python conformance/tools/runner.py coverage
python conformance/tools/audit.py --check
python conformance/tools/audit_schema_occurrences.py --check
python -m unittest discover -s tests -p 'test_issue87*.py'
python -m unittest discover -s tests -p 'test_model_a_oracle.py'
