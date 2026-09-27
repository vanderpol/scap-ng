# Ansible-Inspired SCAP-NG Authoring Experiment

Iteration: 001
Status: Generated parallel syntax experiment
Ansible runtime dependency: NONE

This directory is generated from the same native assessment semantics used by
the existing real-world OVAL migration cases. The original prototypes under
../oval-migration-cases/ are not modified.

The experiment tests whether familiar Ansible authoring conventions improve
readability or instead add ceremony.

Conventions tested:
- name for human-readable steps
- ordered steps
- register for typed evidence/derived-value bindings
- vars in bindings for declared parameter values
- assert/that assertion blocks
- FQCN-like capability names such as scapng.linux.audit.effective_rules

SCAP-NG-specific semantics remain explicit:
- every, any, and none
- cardinality
- typed comparison operators
- applies_when
- deterministic if/elif/else
- diagnostic/evidence limits

Not supported:
- Jinja2
- template expressions
- arbitrary string condition expressions
- handlers
- mutable facts
- task side effects
- Python execution
- Ansible inventory/plugins/runtime

This is not a second scanner format. Both authoring spellings must compile to
the same canonical SCAP-NG semantic model.

Long-term hard requirement:
SCAP 1.4 -> faithful semantic IR -> both authoring renderings -> equivalent canonical NG

See comparison-metrics.json for descriptive size/line comparisons.
