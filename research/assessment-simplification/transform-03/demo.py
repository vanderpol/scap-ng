#!/usr/bin/env python3
"""Synthetic result-to-author diagnostic, not a collected target observation."""
import json
from pathlib import Path
from compile_requirements import compile_author, load_author


def explain_false_comparison(mapping, state_id):
    """Called only with an existing false State comparison; do not suppress statuses."""
    clause = mapping["states"][state_id]
    return {"test": clause["test"], "author_path": clause["author_path"], "message": clause["message"]}


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    _, mapping = compile_author(load_author(here / "examples/initialization-files.author.yaml"))
    print(json.dumps({"kind": "synthetic_diagnostic_not_target_scan", "observed_field": "other_read",
                      "observed_value": True, "state_comparison_result": "false",
                      "finding": explain_false_comparison(mapping, "state-protect-user-files-other-read")}, indent=2))
