#!/usr/bin/env python3
"""Bounded HEAD toolchain clean-extract gate; no release or scanner claim.

Requires the original OVAL Community checkout and exact runtime dependencies.
All conversion/compilation imports after packaging come from the extracted ZIP.
Refs #232 #27.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REVISION = "e3538595c5083b9c34d937a81d319234df9bbfaa"
SOURCE = "SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_family_test.xml"
SOURCE_SHA256 = "6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7"
DEFINITION = "oval:org.mitre.oval.test:def:95"
DEPENDENCIES = {"lxml": "6.1.1", "PyYAML": "6.0.3", "jsonschema": "4.25.1"}
REQUIRED = (
    "tools/build_versioned_toolchain.py", "tools/scap_converter_core.py",
    "tools/v04_native_bundle_compiler.py", "tools/test_v04_public_cli_smoke.py",
    "schema/v0.4.0/assessment.schema.json",
    "schema/v0.3.0/capability-mappings/supported/independent.family.json",
    "schema/v0.4.0/capability-mappings/supported/independent.family.json",
)

# The helper runs in isolated Python: only this extracted tools directory is
# added to sys.path. Reuse the existing public schema-valid miniature graph.
WRAP = r'''
import json, pathlib, sys
root, assessment, output = map(pathlib.Path, sys.argv[1:])
sys.path.insert(0, str(root / "tools"))
import test_v04_public_cli_smoke as smoke
import v04_native_bundle_compiler as compiler
assert pathlib.Path(smoke.__file__).resolve().is_relative_to(root)
assert pathlib.Path(compiler.__file__).resolve().is_relative_to(root)
docs = smoke.schema_valid_docs()
native = json.loads(assessment.read_text())
docs["authoring/demo/assessments/a1.json"] = native
docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"]["automated"]["assessment"] = native["assessment"]["id"]
output.mkdir()
archives = smoke.authoring_archives(docs, output)
print(json.dumps({"archives": [str(p) for p in archives],
                  "fixture_module": smoke.__file__, "compiler_module": compiler.__file__}))
'''

VERIFY_BUNDLE = r'''
import json, pathlib, sys
root, bundle = map(pathlib.Path, sys.argv[1:])
sys.path.insert(0, str(root / "tools"))
import v04_native_bundle_compiler as compiler
assert pathlib.Path(compiler.__file__).resolve().is_relative_to(root)
result = compiler.verify_bundle(bundle.read_bytes(), validate_schema=True)
assert (result["documents"], result["programs"], result["tests"]) == (3, 1, 1), result
assert result["scanner_evaluated"] is False, result
assert result["signature_verified"] is False, result
print(json.dumps(result, sort_keys=True))
'''


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def smoke(self_assertion: Path, evidence: Path):
    require(sys.version_info[:2] == (3, 12), "Python 3.12 is required")
    versions = {name: importlib.metadata.version(name) for name in DEPENDENCIES}
    require(versions == DEPENDENCIES, f"dependency version mismatch: {versions}")
    self_assertion, evidence = self_assertion.resolve(), evidence.resolve()
    source = self_assertion / SOURCE
    require(source.is_file(), f"missing original pinned source: {source}")
    revision = subprocess.check_output(
        ["git", "-C", str(self_assertion), "rev-parse", "HEAD"], text=True).strip()
    require(revision == REVISION, f"Self-Assertion revision mismatch: {revision}")
    require(digest(source) == SOURCE_SHA256, "original family source SHA256 mismatch")
    evidence.mkdir(parents=True, exist_ok=False)  # Never accept stale outputs.
    commands = []
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}

    def run(name, args, cwd):
        result = subprocess.run(list(map(str, args)), cwd=cwd, env=env,
                                capture_output=True, text=True, timeout=180)
        (evidence / f"{name}.log").write_text(result.stdout + result.stderr)
        commands.append({"step": name, "argv": list(map(str, args)),
                         "cwd": str(cwd), "returncode": result.returncode})
        (evidence / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        result.check_returncode()
        return result.stdout

    def python(script, *args):
        # Ignore Python environment injection and user site packages. Script
        # imports resolve beside the extracted entry point, never the checkout.
        return [sys.executable, "-E", "-s", script, *args]

    head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                   text=True).strip()
    with tempfile.TemporaryDirectory(prefix="scap-ng-clean-extract-") as tmp:
        clean = Path(tmp).resolve()
        require(not clean.is_relative_to(ROOT), "clean extraction must be outside the checkout")
        run("build", python(ROOT / "tools/build_versioned_toolchain.py", "--repo", ROOT,
            "--version", "0.4.0", "--ref", "HEAD", "--output-dir", evidence / "toolchain"), clean)
        archives = list((evidence / "toolchain").glob("*.zip"))
        require(len(archives) == 1, "expected exactly one toolchain ZIP")
        archive = archives[0]
        archive_hash = digest(archive)
        sums = evidence / "toolchain/SHA256SUMS.txt"
        require(sums.read_text() == f"{archive_hash}  {archive.name}\n",
                "toolchain SHA256SUMS mismatch")
        verified = json.loads(run("verify-zip", python(ROOT / "tools/build_versioned_toolchain.py",
                                                      "--verify", archive), clean))
        require(verified["source_commit"] == head, "toolchain is not built from HEAD")
        with zipfile.ZipFile(archive) as zf:
            require(zf.testzip() is None, "damaged toolchain ZIP")
            zf.extractall(clean)  # Builder verification has checked inventory and safe paths.
        extracted = clean / "scap-ng-0.4.0-toolchain"
        require(not (extracted / ".git").exists(), "extract unexpectedly depends on Git metadata")
        for component in REQUIRED:
            require((extracted / component).is_file(), f"missing extracted component: {component}")
        # Run the snapshot's own verifier as well, without the source checkout.
        run("verify-extracted-toolchain", python(extracted / "tools/build_versioned_toolchain.py",
                                                 "--verify", archive), extracted)
        original = clean / "ind-def_family_test.xml"
        original.write_bytes(source.read_bytes())
        require(digest(original) == SOURCE_SHA256, "copied source SHA256 mismatch")
        (evidence / original.name).write_bytes(original.read_bytes())
        assessment = evidence / "family.assessment.json"
        conversion = evidence / "conversion-evidence.json"
        run("convert", python(extracted / "tools/scap_converter_core.py", "--source-xml", original,
            "--definition-id", DEFINITION, "--assessment-id", "clean-extract-family-assessment",
            "--output", assessment, "--evidence", conversion), extracted)
        proof = json.loads(conversion.read_text())
        require(proof["source_sha256"] == SOURCE_SHA256 and proof["definition_id"] == DEFINITION,
                "converter evidence source mismatch")
        require(proof["scanner_parity"] is False, "unexpected scanner parity claim")
        wrapped = json.loads(run("wrap", [sys.executable, "-I", "-c", WRAP,
                                 extracted, assessment, evidence / "authoring"], extracted))
        json_zip, yaml_zip = wrapped["archives"]
        compiled = evidence / "compiled"
        compiler_report = evidence / "compiler-report.json"
        run("compile", python(extracted / "tools/v04_native_bundle_compiler.py",
            "--json-archive", json_zip, "--yaml-archive", yaml_zip,
            "--output-dir", compiled, "--report", compiler_report), extracted)
        bundles = list(compiled.glob("*.scapng"))
        require(len(bundles) == 1, "expected exactly one compiled bundle")
        bundle = bundles[0]
        checked = json.loads(run("verify-bundle", [sys.executable, "-I", "-c", VERIFY_BUNDLE,
                                                  extracted, bundle], extracted))
        require(json.loads(compiler_report.read_text()) == {"demo": checked},
                "independent bundle verification differs from compiler report")
        bundle_hash = digest(bundle)
        bundle_sums = compiled / "SHA256SUMS.txt"
        bundle_sums.write_text(f"{bundle_hash}  {bundle.name}\n")
        require(bundle_sums.read_text() == f"{digest(bundle)}  {bundle.name}\n",
                "bundle SHA256SUMS mismatch")
        run("public-cli-smoke", python(extracted / "tools/test_v04_public_cli_smoke.py", "-v"),
            extracted)
        report = {
            "status": "PASS_CLEAN_EXTRACT_NOT_SCANNER_TESTED", "source_commit": head,
            "self_assertion_revision": revision, "definition_id": DEFINITION,
            "original_source_sha256": SOURCE_SHA256, "toolchain_sha256": archive_hash,
            "toolchain_files": verified["files"], "bundle_sha256": bundle_hash,
            "bundle_verification": checked, "python": sys.version,
            "dependencies": versions, "extracted_root": str(extracted),
            "public_cli_smoke": "PASS", "scanner_evaluated": False,
            "distribution_versions": {d.metadata["Name"]: d.version
                                      for d in importlib.metadata.distributions()},
        }
        (evidence / "clean-extract-report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-assertion-root", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    smoke(args.self_assertion_root, args.evidence_dir)


if __name__ == "__main__":
    main()
