# Constants: direct Variable comparison

Compare [source](../sources/constants.xml), [Assessment](../content/constants.assessment.yaml),
[provenance](../provenance/constants.json), and [expectations](../expected/constants.json).
Human status: **pending-review**. Provenance: Inherited source / Common explanation.

The complete Definition `oval:org.mitre.oval.test:def:92` checks a single integer
against 9 and eight integers against a strict lower bound of 7. Both Tests must
be true. There are no external inputs or target resources.

Before: each Test references a `variable_object`, which references a constant
Variable. After: `test-reference-integer → reference-integer` and `test-candidate-integers → candidate-integers` use `variable.value`.
States `equals-nine` and `greater-than-seven` remain separate named comparison nodes. Native
integers are numbers, not XML lexical strings. The removed Object IDs remain
in separate provenance; an Object wrapper is not recreated for visual similarity.

The published case is true: 9 equals 9 and the smallest source list value, 15,
exceeds 7. The authored boundary variant `[15, 7]` is false because 7 is not
strictly greater than 7. A second variant changes the single integer to 8;
that Test is false while the eight-value Test remains true. The overall result
is false. Zero-value behavior is covered by the derived Object-component edge
variant in the concat sample; an empty authored constant is not assumed valid.

Multiple values are represented as entities of one Variable Item. They are not
independent Items whose Test quantifier could replace entity `match: all`.
The variants are derivative content fixtures, not a way to override publisher
constants with Organizational Input.
