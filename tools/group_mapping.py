"""Shared opt-in functional grouping for migration/editorial normalization.

This module is intentionally outside the frozen 0.2.0 Board converter baseline.
Grouping is editorial/navigation metadata only and must never change Rule or
Assessment semantics.
"""
from __future__ import annotations

import re


TOPICS = [
    ("ssh", "SSH", (r"\bssh\b", r"\bsshd\b", r"secure shell")),
    ("password-policy", "Password Policy", (r"password", r"pwquality", r"login\.defs", r"pam_")),
    ("auditing", "Auditing", (r"\baudit", r"auditd", r"audisp")),
    ("logging", "Logging", (r"journald", r"rsyslog", r"syslog", r"log file")),
    ("graphical-environment", "Graphical Environment", (r"graphical", r"gnome", r"display manager", r"gdm")),
    ("system-lifecycle", "System Lifecycle and Support", (r"vendor-supported", r"supported release", r"end of life")),
    ("login-notices", "Login Notices and Banners", (r"notice and consent banner", r"logon banner", r"login banner")),
    ("account-management", "Account Management", (r"user account", r"account management", r"inactive account", r"root account")),
    ("services", "Services", (r"\bservice\b", r"\bdaemon\b", r"systemd")),
    ("filesystem", "Filesystem and Permissions", (r"file permission", r"directory permission", r"file owner", r"mount point")),
    ("networking", "Networking", (r"firewall", r"ipv4", r"ipv6", r"tcp", r"udp", r"network interface")),
    ("cryptography", "Cryptography", (r"\bfips\b", r"cipher", r"certificate", r"cryptograph", r"private key")),
]


def functional_topic(title="", discussion="", remediation=""):
    haystack = " ".join((
        (title or "").lower(),
        (discussion or "").lower(),
        (remediation or "").lower(),
    ))
    for group_id, group_title, patterns in TOPICS:
        if any(re.search(pattern, haystack) for pattern in patterns):
            return group_id, group_title
    return None


def auto_map_groups(candidates):
    """Return (groups, evidence) for high-confidence candidate mappings.

    Each candidate is a mapping containing:
      rule, assessment_group, title, discussion, remediation.

    Rules with no confident topic are deliberately left ungrouped.
    """
    parents = {}
    evidence = []

    for candidate in candidates:
        topic = functional_topic(
            candidate.get("title"),
            candidate.get("discussion"),
            candidate.get("remediation"),
        )
        parent_id = candidate.get("assessment_group")
        if topic is None:
            evidence.append({
                "rule": candidate["rule"],
                "assessment_group": parent_id,
                "functional_group": None,
                "method": "heuristic",
                "mapped": False,
                "reason": "no_high_confidence_topic",
            })
            continue

        topic_id, topic_title = topic
        group_id = f"{parent_id}.{topic_id}" if parent_id else topic_id

        if parent_id:
            parent = parents.setdefault(
                parent_id,
                {
                    "id": parent_id,
                    "title": (
                        "Automated"
                        if parent_id == "automated"
                        else "Manual or Managerial"
                        if parent_id == "manual-or-managerial"
                        else parent_id.replace("-", " ").title()
                    ),
                    "groups": {},
                },
            )
            bucket = parent["groups"].setdefault(
                group_id,
                {"id": group_id, "title": topic_title, "rules": []},
            )
        else:
            parent = parents.setdefault(
                "__root__",
                {"id": None, "title": None, "groups": {}},
            )
            bucket = parent["groups"].setdefault(
                group_id,
                {"id": group_id, "title": topic_title, "rules": []},
            )

        bucket["rules"].append(candidate["rule"])
        evidence.append({
            "rule": candidate["rule"],
            "assessment_group": parent_id,
            "functional_group": group_id,
            "method": "heuristic",
            "mapped": True,
        })

    output = []
    root = parents.pop("__root__", None)
    if root:
        output.extend(root["groups"].values())
    for parent in parents.values():
        if parent["groups"]:
            output.append({
                "id": parent["id"],
                "title": parent["title"],
                "groups": list(parent["groups"].values()),
            })
    return output, evidence
