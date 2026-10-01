#!/usr/bin/env python3
"""Native SCAP-NG disposition mapping for XCCDF 1.2 Rule role migration."""

ROLE_MAP = {
    "full": {
        "execute": True,
        "scoring_eligible": True,
        "reporting_disposition": "normal",
    },
    "unscored": {
        "execute": True,
        "scoring_eligible": False,
        "reporting_disposition": "informational",
    },
    "unchecked": {
        "execute": False,
        "scoring_eligible": False,
        "reporting_disposition": "not_evaluated",
        "reason": "policy_unchecked",
    },
}


def map_xccdf_role(role):
    role = role or "full"
    if role not in ROLE_MAP:
        raise ValueError(f"unsupported XCCDF Rule role: {role}")
    return dict(ROLE_MAP[role])


def canonicalize_rule_result(role, technical_outcome=None):
    """Return canonical NG execution/disposition without erasing technical truth."""
    mapping = map_xccdf_role(role)
    if not mapping["execute"]:
        if technical_outcome is not None:
            raise ValueError("unchecked Rule must not have an Assessment technical outcome")
        return {
            **mapping,
            "technical_outcome": "not_evaluated",
        }

    if technical_outcome is None:
        raise ValueError(f"{role or 'full'} Rule requires a technical outcome")
    return {
        **mapping,
        "technical_outcome": technical_outcome,
    }
