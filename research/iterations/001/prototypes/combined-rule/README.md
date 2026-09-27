# Combined-Rule Prototype

In this candidate architecture, the rule is the primary authored object. Policy, Check Content, Fix Text, applicability, and automation are colocated.

A policy-only rule is the same object with no `assessment` member.

This layout optimizes one-file readability but may make reuse and independent policy/automation provenance more difficult. Iteration 001 intentionally tests those tradeoffs rather than assuming an answer.

The published SCAP-NG bundle would still contain all required content in one signed package.
