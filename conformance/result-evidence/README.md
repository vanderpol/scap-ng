# Supplied Result evidence

The two files in [the supplied snapshot](supplied.yaml) each have owner UID 42.
The [Assessment](owner.assessment.yaml) selects both paths from one shared
Object and extracts the two UIDs into a local Variable. Each file has one
observed UID and matches at least one element of the ordered Variable
population. The expected Test and Assessment outcomes are true. The
[expected manifest](expected.json) records the counts, order and repeated
integer value independently of a scanner.

The [Assessment Result](owner.result.yaml) retains the original Items beside
their individual verdicts, the completed Object, and the Variable audit record
with its consumed Item references. The [Item report](owner.item-report.yaml)
keeps each Item identity, provenance, owner UID and path and explicitly marks
the group field omitted. The [zero-retention Result](owner-capped.result.yaml)
keeps no Test-local Item observations. Its Test still evaluated two Items,
and the raw Items remain at Assessment scope to explain Variable extraction.
The local checks compare the Results and report with the source, the
snapshot and the expected manifest. Schema controls exercise all
Collection and Variable status tokens and invalid status/diagnostic and
status/cardinality combinations.

The [evidence contract](../../docs/contracts/0.4-evidence.md) requires retaining
ordered references, typed values and distinct acquisition and Variable statuses.
The [Model A contract](../../docs/contracts/0.4-evaluation.md) determines the
comparison over the complete, nonempty evidence. The report's field selection
and materialization counts describe this one fixture. The general authority for
required projection elements and cross-collection counting remain open in the
[contract decisions](../../docs/DOCUMENTATION-CONTRACT-DECISIONS.md#item-materialization-and-projection).
Status-only controls assert schema behavior. They carry no assertion about
evaluation precedence.
