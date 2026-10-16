#!/usr/bin/env python3
"""Exhaustive six-STIG full-Assessment research-format inversion census.

Rebuilds ENTIRE source Assessment dictionary, with no acceptance on mismatch.
Readability still untested; OVAL/scanner semantics not proven.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from research_english_first_04_complex import to_human, to_native

SHA = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"


def census(archive):
    digest = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest != SHA:
        raise ValueError("Pinned source digest mismatch")
    counts, by_benchmark, by_reject, passed, rejected = Counter(), {}, Counter(), [], []
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError("Corrupted six-STIG source ZIP")
        for file in sorted(z.namelist()):
            if not (file.startswith("authoring/") and "/assessments/" in file and file.endswith(".yaml")):
                continue
            doc = yaml.safe_load(z.read(file))
            source = (doc or {}).get("assessment") or {}
            if source.get("mode") != "automated" or not source.get("tests"):
                continue
            counts["total_automated_documents"] += 1
            benchmark = file.split("/")[1]
            if benchmark not in by_benchmark:
                by_benchmark[benchmark] = {"exact": 0, "rejected": 0}
            try:
                human = to_human(source)
                restored = to_native(human)
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                counts["rejected_unsupported_source_shape"] += 1
                by_benchmark[benchmark]["rejected"] += 1
                category = f"{type(exc).__name__}: {str(exc)[:100]}"
                by_reject[category] += 1
                if len(rejected) < 35:
                    rejected.append({"source": file, "reason": category})
                continue
            if restored != source:
                counts["rejected_structural_difference"] += 1
                by_benchmark[benchmark]["rejected"] += 1
                if len(rejected) < 35:
                    rejected.append({"source": file, "reason": "source reconstruction not identical"})
                continue
            # Independent mutation of the translated document must break equivalence.
            mutant = deepcopy(human)
            test_id = next(iter(mutant["checks"]))
            mutant["checks"][test_id]["require"]["unexpected_rule"] = True
            try:
                to_native(mutant)
            except ValueError:
                counts["negative_guards_passed"] += 1
            else:
                raise AssertionError("Invalid requirement accepted in "+file)
            counts["exact_complete_assessment"] += 1
            counts["source_tests_in_exact_assessments"] += len(source["tests"])
            by_benchmark[benchmark]["exact"] += 1
            passed.append({
                "source": file,
                "tests": len(source["tests"]),
                "shared_sources": len(source.get("shared_objects", {})),
                "variables": len(source.get("variables", {})),
                "source_equivalence": "complete Assessment dictionary exact"
            })
    if counts["total_automated_documents"] != 872:
        raise AssertionError("Distinct automated corpus size changed")
    covered = counts["exact_complete_assessment"] + counts["rejected_unsupported_source_shape"] + counts["rejected_structural_difference"]
    if covered != 872:
        raise AssertionError("Incomplete corpus classifications")
    return {
        "source_sha256": digest,
        "status": "FULL SOURCE ASSESSMENT DICTIONARY INVERSION, NOT SCANNER SEMANTIC PARITY",
        "counts": dict(counts),
        "per_benchmark": by_benchmark,
        "common_rejection_reasons": dict(by_reject.most_common(35)),
        "exact_assessments": passed,
        "rejected_examples": rejected,
        "warning": "No 0.4 schema change, full SCAP 1.4 lossless migration or actual collected evidence proof"
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output")
    a = p.parse_args()
    result = census(a.archive)
    if a.output:
        Path(a.output).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "counts": result["counts"],
        "per_benchmark": result["per_benchmark"],
        "common_rejections": list(result["common_rejection_reasons"].items())[:12],
        "exact_examples": result["exact_assessments"][:10],
    }, indent=2))


if __name__ == "__main__":
    main()
