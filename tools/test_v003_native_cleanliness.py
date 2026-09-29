"""Focused regression tests for iteration-003 legacy-residue guard."""

from scap_upconvert_v003.cleanliness import assert_native_clean, find_legacy_residue


def test_clean_native_document_passes() -> None:
    doc = {
        "benchmark": {
            "id": "rhel9-stig",
            "platform": "rhel.9",
            "applicability": ["linux.gnome-installed"],
        }
    }
    assert find_legacy_residue(doc) == []
    assert_native_clean(doc)


def test_legacy_ids_and_namespaces_are_rejected() -> None:
    doc = {
        "rule": {
            "id": "RHEL-09-000001",
            "bad_ref": "oval:example:def:1",
            "other": "http://checklists.nist.gov/xccdf/1.2",
        }
    }
    findings = find_legacy_residue(doc)
    assert len(findings) >= 2


def test_legacy_source_tree_key_is_rejected() -> None:
    findings = find_legacy_residue({"assessment": {"source_tree": {"name": "check"}}})
    assert findings
    assert findings[0].reason.startswith("legacy/provenance")
