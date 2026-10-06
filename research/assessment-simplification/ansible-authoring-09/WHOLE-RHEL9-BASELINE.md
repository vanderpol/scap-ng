# Provisional whole-RHEL-9 authoring feasibility baseline

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN OR COVERAGE CLAIM**

This is a first-pass classification of all 445 RHEL 9 Rules using the existing
diagnostic feature inventory. It is intentionally conservative and is meant to
set up the deeper rule-by-rule experiment.

## Buckets

Classification precedence:

1. default-manual Rule -> `manual_review`;
2. existing shellcommand Rule -> `existing_shellcommand`;
3. Variables/Sets/Filters/functions/field extraction -> `advanced_structured`;
4. multiple Tests/States, Boolean composition or negation -> `composed_native`;
5. remaining automated Rule -> `simple_native`.

| Provisional bucket | Rules | Percent |
| --- | ---: | ---: |
| Simple native | **207** | **46.5%** |
| Composed native | **106** | **23.8%** |
| Advanced structured | **84** | **18.9%** |
| Existing shellcommand | **21** | **4.7%** |
| Default manual / review | **27** | **6.1%** |
| **Total** | **445** | **100%** |

Therefore **313 / 445 = 70.3%** of the benchmark falls into the simple or
composed native buckets before any attempt to simplify the advanced dataflow
tail.

This is consistent with the broader production census: most direct
Test->Object and Test->State relationships are single-use and therefore have a
strong locality opportunity.

## Important limitations

This is **not** a claim that 70.3% has already been faithfully translated into
the straw-man syntax.

The source inventory used for bucketing is an older diagnostic serialization
and detects features by structure. Every Rule used as evidence for the new
authoring approach must still be compared to pinned SCAP 1.4 source / faithful
semantic IR.

The `advanced_structured` bucket is also intentionally broad. It includes
patterns that may become simple after proven constructs such as `for_each`,
local `let` bindings or direct structured composition. One goal of the
research is to see how much of that 18.9% moves into understandable authoring
without making the authoring language OVAL-like again.

Likewise, the 27 manual Rules are not assumed to remain manual. They are
reviewed separately because automation must preserve the actual requirement,
including organizational approvals and external facts, rather than merely
automating commands copied from Check Text.
