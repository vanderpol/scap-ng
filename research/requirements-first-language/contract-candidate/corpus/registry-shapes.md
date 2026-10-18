# B six-STIG Windows registry source patterns

**Research-only converted 0.3 source shapes; NOT original SCAP 1.4 OVAL parity.**

**Referenced registry Assessments:** 156
**Registry Test nodes:** 190

## Frequent source attributes

| Attribute | Test nodes |
| --- | ---: |
| has_variables=False | 183 |
| existence=one_or_more | 170 |
| shared_object_reference=False | 167 |
| match=all | 160 |
| state=complex_keys:all | 135 |
| direct_single_test=True | 122 |
| exact_HKLM_selector=True | 114 |
| exact_HKLM_selector=False | 76 |
| direct_single_test=False | 68 |
| shared_object_reference=True | 23 |
| match=one | 19 |
| state=value/pattern_match/one_or_more/all/string | 17 |
| state=multiple_or_empty | 15 |
| state=none | 15 |
| match=one_or_more | 11 |
| existence=optional | 10 |
| has_variables=True | 7 |
| existence=all | 6 |
| existence=none | 4 |
| state=value/equals/one_or_more/all/integer | 4 |
| state=value/equals/one_or_more/all/string | 3 |
| state=value/less_than_or_equal/one_or_more/all/integer | 1 |

## Combined shapes

| Shape | Test nodes | Example IDs |
| --- | ---: | --- |
| complex_keys:all \| one_or_more \| all \| True \| True | 66 | SV-253358.automated, SV-253361.automated, SV-253365.automated, SV-253375.automated |
| complex_keys:all \| one_or_more \| all \| True \| False | 32 | SV-253261.automated, SV-253389.automated, SV-253399.automated, SV-253401.automated |
| complex_keys:all \| one_or_more \| all \| False \| True | 14 | SV-253263.automated, SV-253263.automated, SV-253300.automated, SV-253359.automated |
| value/pattern_match/one_or_more/all/string \| one_or_more \| one \| False \| False | 11 | SV-253446.automated, SV-253446.automated, SV-253446.automated, SV-253446.automated |
| none \| one_or_more \| one_or_more \| False \| False | 9 | SV-253428.automated, SV-253428.automated, ng.shared.the-dow-interoperability-root-ca-cross-certificates-must-be-installed-in, ng.shared.the-dow-interoperability-root-ca-cross-certificates-must-be-installed-in |
| complex_keys:all \| one_or_more \| all \| False \| False | 8 | SV-253260.automated, SV-253260.automated, SV-253260.automated, SV-253260.automated |
| complex_keys:all \| optional \| all \| True \| True | 8 | SV-253364.automated, SV-253377.automated, SV-253400.automated, ng.shared.prevent-internet-explorer-security-prompt-for-windows-installer-scripts |
| multiple_or_empty \| one_or_more \| all \| True \| True | 8 | SV-253254.automated, SV-253372.automated, SV-278104.automated, SV-278234.automated |
| value/pattern_match/one_or_more/all/string \| one_or_more \| all \| False \| False | 6 | SV-253340.automated, SV-253341.automated, SV-253342.automated, SV-278043.automated |
| multiple_or_empty \| one_or_more \| all \| False \| True | 5 | SV-253394.automated, SV-253394.automated, SV-256893.automated, ng.shared.hardened-unc-paths-must-be-defined-to-require-mutual-authentication-and |
| complex_keys:all \| all \| all \| True \| True | 4 | SV-253284.automated, SV-253423.automated, ng.shared.powershell-transcription-is-enabled-on-windows, ng.shared.turn-off-autoplay-is-set-to-enabled-all-drives |
| value/equals/one_or_more/all/integer \| one_or_more \| one \| False \| True | 4 | SV-253274.automated, SV-277998.automated, SV-277999.automated, SV-278000.automated |
| complex_keys:all \| all \| all \| False \| False | 2 | SV-278208.automated, SV-278208.automated |
| none \| none \| all \| False \| False | 2 | SV-256893.automated, SV-256893.automated |
| none \| none \| one \| False \| False | 2 | SV-257592.automated, SV-257592.automated |
| none \| one_or_more \| all \| False \| False | 2 | SV-253470.automated, SV-253470.automated |
| value/equals/one_or_more/all/string \| one_or_more \| one \| True \| True | 2 | SV-253291.automated, SV-253350.automated |
| complex_keys:all \| optional \| all \| False \| False | 1 | ng.shared.zone-information-must-be-preserved-when-saving-attachments |
| multiple_or_empty \| one_or_more \| all \| True \| False | 1 | ng.shared.the-machine-inactivity-limit-is-set-to-15-minutes-or-less |
| multiple_or_empty \| optional \| all \| True \| True | 1 | SV-278091.automated |
| value/equals/one_or_more/all/string \| one_or_more \| one_or_more \| False \| True | 1 | SV-253392.automated |
| value/less_than_or_equal/one_or_more/all/integer \| one_or_more \| one_or_more \| False \| True | 1 | SV-253392.automated |

[Complete machine-readable shapes](registry-shapes.json).

Source omitted registry-view behaviors must be verified against
original XML. Typed value mismatch is not silently coerced.
Source Test counts are NOT unique Assessment counts or scanner parity.
