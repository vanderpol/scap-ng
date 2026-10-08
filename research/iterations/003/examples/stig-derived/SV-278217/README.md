# SV-278217 — Registry type and value must both be preserved

**Research-only SCAP-NG 0.3 authoring proposal, not current schema-valid or scanner-tested.** Real source: Microsoft Windows Server 2025 STIG, WN25-SO-000230 / V-278217 (anonymous share enumeration). [Published rule](https://www.ignyteplatform.com/stigs/Microsoft_Windows_Server_2025_Security_Technical_Implementation_Guide/finding/V-278217).

## Actual STIG requirement

The Registry value below must **exist** and be configured as **REG_DWORD = 1**:

- Hive: `HKEY_LOCAL_MACHINE`
- Key: `SYSTEM\CurrentControlSet\Control\Lsa`
- Name: `RestrictAnonymous`
- Registry type: `REG_DWORD`
- Value: `0x00000001` (1)

This makes a stronger test of lossless simplification than a generic `value: 1` assertion. A `REG_SZ` containing the character `1` is not a valid substitute.

## Readable *proposed* authoring syntax

```yaml
# Proposed syntax — NOT currently schema-valid
assessment:
  id: windows.server2025.sv-278217
  version: 1
  assessment_title: Prevent anonymous enumeration of shares
  mode: automated
  class: compliance
  purpose: assessment

  tests:
    restrict-anonymous-test:
      capability: windows.registry
      object:
        select:
          hive:
            equals: local_machine
          key:
            equals: 'SYSTEM\CurrentControlSet\Control\Lsa'
          name:
            equals: RestrictAnonymous
      states:
        - expect:
            type:
              equals: dword
            value:
              equals: 1
            # The type determines the legal data representation:
            # value is an integer, not the string "1".
            match: all
            existence: one_or_more
      reported_elements: all
      existence: one_or_more
      match: all

  evaluate:
    test: restrict-anonymous-test
```

The `expect` syntax is the feature under design, not a normative 0.3 object. In the compiler, explicit `type: dword` constrains `value` to an integer, and both predicates must hold for the **same Registry item**. Collection failure, missing value, wrong type and wrong data remain distinguishable.

## Required evidence/result semantics

| Observed Registry item | Expected result | Explanation |
| --- | --- | --- |
| REG_DWORD 1 | pass | Correct type and integer value |
| REG_DWORD 0 | fail | Wrong integer value |
| REG_SZ "1" | fail | Wrong Registry type, even though characters look similar |
| REG_MULTI_SZ ["1"] | fail | Wrong Registry type and value representation |
| Value absent | fail | The STIG requires the value to exist |
| Registry collection unavailable | unknown/error | Never silently treat missing evidence as absence |

## Current implementation boundary

The [v0.3 windows.registry mapping](../../../../../schema/v0.3.0/capability-mappings/supported/windows.registry.json) already has distinct `type` and `value` fields, `dword`, `string`, and `multi_string` type enums, and typed comparison. Current canonical State authoring requires `field`, `operation`, `datatype`, `match`, and `existence`. The shorter operator-as-key authoring and a compiler-enforced mapping of Registry type to value datatype are proposals, not currently proven by the compiler.

`REG_MULTI_SZ` element-by-element native array fidelity needs separate research; this Rule itself mandates DWORD and does not require introducing any new scanner capability.

**Acceptance gate:** Can a compiler reconstruct an explicit, faithful `type=dword AND value=integer 1` State with exact existence/cardinality, without deriving a value from a coercion or a hidden default? Compare results of the canonical and proposed source against the same fixtures.
