# Windows 11 five-rule SCAP-NG source sample

Five Rules from the signed Windows 11 V2R10 STIG SCAP 1.4 benchmark (enhanced V18).

Each Rule includes:

- Rule policy;
- a procedure-only Manual Assessment preserving the source Check Text;
- a Stage-1 lossless Automated Assessment preserving the source OVAL behavior.

The sample also includes the lossless Windows 11 Platform Assessment and the
two Rule-applicability Assessments required by the selected Rules.

The five Rule Assessments deliberately exercise different source constructs:

- registry;
- independent shell command;
- WMI 5.7;
- PowerShell cmdlet;
- mixed OR logic across cmdlet and shell-command tests.

Historical SCAP identifiers appear only as authoring comments or typed
publisher identifiers; they are not scanner execution semantics.

This is pre-alpha design-review source, not a frozen schema.
