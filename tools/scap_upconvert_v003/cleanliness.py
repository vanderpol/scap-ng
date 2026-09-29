"""Native SCAP-NG output cleanliness checks for iteration 003."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class LegacyResidue:
    path: str
    value: str
    reason: str


# These patterns are deliberately conservative.  Native NG may discuss a legacy
# standard in human documentation, but machine-facing source emitted by the
# converter must not depend on legacy identifiers/namespaces/hrefs.
_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bxccdf[_:-]"), "XCCDF identifier"),
    (re.compile(r"(?i)\boval:[^\s]+"), "OVAL identifier"),
    (re.compile(r"(?i)\bocil:[^\s]+"), "OCIL identifier"),
    (re.compile(r"(?i)https?://[^\s]*(?:xccdf|oval|ocil|cpe)[^\s]*"), "legacy namespace URI"),
    (re.compile(r"(?i)check-content-ref"), "XCCDF check-content-ref structure"),
    (re.compile(r"(?i)oval-definitions"), "OVAL namespace/structure"),
    (re.compile(r"(?i)cpe\.mitre\.org/language"), "CPE Applicability Language namespace"),
)

_FORBIDDEN_KEYS = {
    "source_tree",
    "source_namespace",
    "source_object_id",
    "source_definition_id",
    "source_test_id",
    "source_state_id",
    "source_variable_id",
    "source_component",
    "source_checks",
    "source_check_logic",
}


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{path}.{key}"
            yield from _walk(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def find_legacy_residue(document: Any) -> list[LegacyResidue]:
    findings: list[LegacyResidue] = []

    for path, value in _walk(document):
        if isinstance(value, Mapping):
            for key in value:
                if str(key) in _FORBIDDEN_KEYS:
                    findings.append(
                        LegacyResidue(
                            path=f"{path}.{key}",
                            value=str(key),
                            reason="legacy/provenance field is forbidden in native output",
                        )
                    )

        if isinstance(value, str):
            for pattern, reason in _PATTERNS:
                if pattern.search(value):
                    findings.append(
                        LegacyResidue(path=path, value=value, reason=reason)
                    )

    return findings


def assert_native_clean(document: Any) -> None:
    findings = find_legacy_residue(document)
    if findings:
        details = "\n".join(
            f"- {item.path}: {item.reason}: {item.value!r}" for item in findings[:20]
        )
        if len(findings) > 20:
            details += f"\n- ... {len(findings) - 20} additional finding(s)"
        raise ValueError(
            "Native SCAP-NG output contains prohibited legacy residue:\n" + details
        )
