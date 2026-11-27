#!/usr/bin/env python3
"""Verify canonical manual questions with RI workbook generation, upgrade and import."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from build_content_fixture import build, json_bytes
from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, load, schema_validator

FIXTURE = CONFORMANCE / "manual-lifecycle"


def revise_package(source, target, expected, changed_question):
    shutil.copytree(source, target)
    manifest_path = target / "manifest.json"
    manifest = load(manifest_path)
    revision = expected["revised_assessment"]
    for row in manifest["objects"].values():
        kind = row["type"]
        if kind not in {"assessment", "rule"}:
            continue
        path = target / row["path"]
        doc = load(path)
        if kind == "assessment":
            document = doc["assessment_document"]
            assessment = document["assessment"]
            assessment["version"] = revision["version"]
            row["version"] = revision["version"]
            if changed_question:
                assessment["procedure"] = revision["changed_procedure"]
        else:
            document = doc
            rule = doc["rule"]
            rule["assessment_choices"][rule["default_assessment_choice"]]["expected_version"] = revision["version"]
        schema_validator(kind + ".schema.json").validate(document)
        raw = json_bytes(doc)
        row.update(sha256=sha256(raw).hexdigest(), size=len(raw))
        path.write_bytes(raw)
    schema_validator("package-manifest.schema.json").validate(manifest)
    manifest_path.write_bytes(json_bytes(manifest))


def answer_variant(template, outcome, provenance):
    question, marker, _ = template.partition("    response:\n")
    if not marker:
        raise ValueError("RI workbook has no response section")
    evidence, = provenance["evidence"]
    return (question + marker + f"""      status: 'answered'
      outcome: '{outcome}'
      completed_at: '{provenance["completed_at"]}'
      comment: '{provenance["comment"]}'
      evidence:
        - '{evidence}'
""")


def workbook(binary, output, package, previous=None):
    command = [str(binary), "answers"]
    command += ["init"] if previous is None else ["upgrade", "--from", str(previous)]
    subprocess.run([*command, "--package", str(package), "--output", str(output)],
                   capture_output=True, text=True, timeout=15, check=True)
    return load(output)


def check_question(document, package, assessment, expected):
    question, = document["questions"]
    identity = f'{expected["benchmark"]}/{expected["rule"]}/{expected["assessment"]}'
    require_equal(question["id"], identity, "workbook question")
    require_equal(document["benchmark"]["id"], expected["benchmark"], "workbook Benchmark")
    choices = {choice["value"]: (choice["label"], choice["outcome"]) for choice in question["choices"]}
    authored = {choice["value"]: (choice["label"], choice["outcome"]) for choice in assessment["response"]["choices"]}
    require_equal(choices, authored, "workbook authored choices")
    raw = (package / "assessments/approval.json").read_bytes()
    require_equal(question["fingerprint"], sha256(raw).hexdigest(), "workbook exact Assessment fingerprint")
    return question


def replay(binary, ri, go):
    expected = load(FIXTURE / "expected.json")
    assessment = load(CONFORMANCE / expected["assessment_source"])["assessment"]
    provenance = expected["response_provenance"]
    schema_pin = load(FIXTURE / "sources.json")["schema_pin"]
    with TemporaryDirectory(prefix="scap-ng-manual-") as directory:
        root = Path(directory)
        package = root / "package"
        build(package, FIXTURE / "sources.json")
        manifest_digest = sha256((package / "manifest.json").read_bytes()).hexdigest()
        initial_path = root / "initial.yaml"
        initial = check_question(workbook(binary, initial_path, package), package, assessment, expected)
        template = initial_path.read_text(encoding="utf-8")

        answer_paths = {}
        for outcome in expected["completed"]:
            path = root / f"completed-{outcome}.yaml"
            path.write_text(answer_variant(template, outcome, provenance), encoding="utf-8")
            answer_paths[outcome] = path

        questions = {"initial": initial}
        workbook_paths = {"initial": initial_path}
        for name, changed in (("revision_only", False), ("changed_question", True)):
            target = root / name
            revise_package(package, target, expected, changed)
            path = root / f"{name}.yaml"
            upgraded = workbook(binary, path, target, answer_paths["true"])
            questions[name] = check_question(upgraded, target, assessment, expected)
            require_equal(questions[name]["stable_id"] == initial["stable_id"],
                          not changed, f"{name} source question identity")
            require_equal(questions[name]["fingerprint"] == initial["fingerprint"], False, f"{name} member digest")
            require_equal(questions[name]["semantic_fingerprint"] == initial["semantic_fingerprint"],
                          not changed, f"{name} semantic fingerprint")
            workbook_paths[name] = path

        paths = {**answer_paths, **workbook_paths}
        load_result = subprocess.run([go, "run", str(FIXTURE / "ri-answers.go"), *map(str, paths.values())],
                                     cwd=ri, capture_output=True, text=True, timeout=120, check=True)
        results = dict(zip(paths, json.loads(load_result.stdout), strict=True))

    completed = {}
    for outcome, disposition in expected["completed"].items():
        observed = results[outcome]
        if disposition["imported"]:
            check_import(observed, initial, outcome, provenance)
            completed[outcome] = {"imported": True}
        else:
            diagnostic = observed["diagnostic"]
            if f'invalid answered outcome "{outcome}"' not in diagnostic:
                raise ValueError(f"Unexpected import diagnostic for {outcome}: {diagnostic}")
            completed[outcome] = {"imported": False, "diagnostic": diagnostic}

    lifecycle = {}
    for name, disposition in expected["lifecycle"].items():
        question = questions[name]
        response = question["response"]
        require_equal(response["status"], disposition["status"], name)
        if disposition["imported"]:
            check_import(results[name], question, "true", provenance)
        else:
            require_equal(results[name], {}, name)
            require_equal(response["outcome"], None, name)
        if name == "changed_question":
            require_equal(response["previous_outcome"], "true", "stale answer marker")
            require_equal(response["previous_stable_id"], initial["stable_id"], "prior question identity")
            require_equal(question["procedure"], expected["revised_assessment"]["changed_procedure"], name)
        lifecycle[name] = {"status": response["status"], "imported": bool(results[name]),
                           "package_assessment_sha256": question["fingerprint"]}
    return {
        "format": "scap-ng-manual-workbook-ri-receipt-1", "schema_pin": schema_pin,
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "manifest_sha256": manifest_digest, "completed": completed, "lifecycle": lifecycle,
        "scope": "RI workbook generation and upgrade through ri-content, and answer import through the RI loader.",
    }


def check_import(observed, question, outcome, provenance):
    require_equal(observed["answers"], {question["assessment_id"]: {
        "Status": "answered", "Outcome": outcome, "Fingerprint": question["fingerprint"],
        "Comment": provenance["comment"], "Evidence": provenance["evidence"],
        "CompletedAt": provenance["completed_at"],
    }}, outcome)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ri-content", type=Path, required=True)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json_bytes(replay(args.ri_content.resolve(strict=True), args.ri, args.go))
    if args.check and (FIXTURE / "ri-receipt.json").read_bytes() != rendered:
        raise SystemExit("manual workbook receipt differs from the replay")
    print(rendered.decode(), end="")
