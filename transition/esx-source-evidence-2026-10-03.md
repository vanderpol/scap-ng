# ESX sample-content and result investigation — 2026-10-03

Owner asked to inspect issues and pull requests for ESX sample content and results.
Repository checkpoint: main `9c729604509e80c7e66bc663a668ab9152fd8ce9`.
Provenance: Evidence/Audit of retrieved primary records; no vendor data published.

| Primary record | Inspected evidence | Content/result disposition |
| --- | --- | --- |
| [OVAL #214](https://github.com/OVAL-Community/OVAL/issues/214) | Proposal to replace unused older ESX with CIS/Arctic Wolf extension; closing comment says PR completed | Describes operational use; no sample/result attachment in retrieved body/comment |
| [OVAL PR #215](https://github.com/OVAL-Community/OVAL/pull/215) | Merged; exact changed-file list is esx-definitions-schema.xsd and esx-system-characteristics-schema.xsd; comment confirms schema validation/use | Two schemas only; no Assessment content or scan results |
| [Discussion #207](https://github.com/orgs/OVAL-Community/discussions/207) | ESX capability list, jOVAL source link, Arctic Wolf endorsement | No attached sample/results in retrieved discussion bodies |
| [Discussion #165](https://github.com/orgs/OVAL-Community/discussions/165) | Arctic Wolf supported-Test list; owner asks for lesser-used examples including ESX; response links CIS-CAT coverage documentation | Operational-use evidence, not supplied runnable content or expected-result oracle |
| [OVAL #301](https://github.com/OVAL-Community/OVAL/issues/301) | Backport request links #207/#214; no comments retrieved | No new sample/results |
| [SCAP-NG PR #140](https://github.com/vanderpol/scap-ng/pull/140) | Merged service/advanced-setting native Assessments, synthetic Items and explained expectations | Available synthetic 0.2.0 representation evidence |
| [SCAP-NG PR #141](https://github.com/vanderpol/scap-ng/pull/141) | Merged account/VIB Assessments, Items and expected equality results; explicit live-target limits | Available synthetic 0.2.0 representation evidence |

The complete recursive default-branch trees of `OVAL-Community/SCAP-Self-Assertion`
and `joval/jOVAL` were searched by ESX/VMware path names. Self-Assertion had no
matching paths. jOVAL matches were four official-wrapper/unofficial schema files;
no ESX-named fixture/result paths were found. Filename search cannot exclude
content embedded in unrelated files. This bounded investigation does not establish
that CIS/Arctic Wolf private content or results are unavailable generally.

Discussion pages were read through public HTML because #207 is a Discussion,
not an Issue (the issue endpoint returned 404). HTML contains loading warnings;
conclusions are limited to retrieved bodies, not hidden or missing comments.

Continue source-backed draft mappings and clearly labeled synthetic fixtures.
Real collector/result evidence remains a gap in #128/#131. Do not treat vendor
usage statements or PowerCLI snippets as conformance proof, nor the source XSD's
illustrative Boolean lockdown snippet as proof of normal/strict category acquisition.
