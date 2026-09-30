# Board design question: capability placement for Variable data sources

**Status:** non-voting design discussion; working prototype direction selected by
the owner on 2026-09-30, not a Board-approved normative rule.

Variables may consume existing named Collections, private embedded Collections,
other Variables, and combinations of these through nested functions. Both
Collection forms and full dependency chains are required working features.

For a directly associated Test/Collection/State contract, the Test declares the
capability once and type mismatches are rejected. Some Collections are used only
to produce Variable values and have no Test to supply the capability.

The owner selected declaring this capability on the **Variable** for the
prototype. The Board must review the placement and binding rules before a formal
voting proposal. A single unqualified Variable capability cannot represent a
Variable with several differently typed Collection operands. Shared named
Collections can also have multiple Variable consumers whose declarations must
be consistent; declaration order must not select a winner.

Questions to resolve:

1. Should the Variable own an explicit Collection-ID-to-capability binding for
   each independent named source it consumes?
2. How should an embedded private source be typed without requiring artificial
   globally addressable identity?
3. How do inherited types propagate through Collection sets and filters, and
   what exact cases require an explicit declaration?
4. How should conflicting, absent or mixed type declarations fail?
5. How can the same rules preserve source component types without duplicating
   capability declarations on Test-associated Collections and States?

These questions do not reopen support for Variable references or either
Collection form. They determine the explicit typing contract.

Provenance: **Evidence/Audit** of owner choice and identified graph constraints.
