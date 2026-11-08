# Third-party sources and licensing

SCAP-NG project-owned material is offered under [Apache-2.0](../LICENSE). This does **not** relicense OVAL, DISA, NIST, NIWC or other referenced third-party materials. Preserve their original source identifiers, notices and provenance.

This repository contains schemas, capability mapping metadata and four small source-derived Assessment examples. It does **not** contain the original SCAP 1.4 benchmarks, OVAL XML corpus, research archives or bulk proof assets. The [provenance record](PROVENANCE.md) identifies the original example locations; schema-valid examples are **not** independently proved scanner results.

Before any public 0.4.0 distribution, review the full collection of source rights, attribution, notices and packaging.

## OVAL XSD research

The OVAL 5.12.3 Windows `ntuser` XSD includes implementation annotations and a Government License/Disclaimer. Copying or modifying the original XSD can require reproducing its notice. The generated SCAP-NG scanner notes instead use original summaries, source links and an offline audit of annotation counts and hashes, **without copying the XSD prose**.

Translated scanner notes are research candidates, not approved SCAP-NG semantics. Any later verbatim incorporation requires a separate attribution and notices review.

## Proposed schema-derived documentation

The proposed documentation schemas contain translated and excerpted field annotations from OVAL Community 5.12.3 and the four retained experimental ESX mappings from the pinned 6.0 new-Test source. Exact source commits, file hashes and field pointers are recorded in `proposed-schema/documentation/`. This does not adopt legacy scanner behavior or expand ESX support. The applicable source notice is reproduced below.

This software is an open standard developed by multiple parties, including the United States Government (Government). The Government hereby grants you a non-exclusive, royalty-free, worldwide license to use, modify, and/or reproduce the software for any lawful purpose provided that you reproduce this License/Disclaimer language with any use/modification/copy of the software. The Government assumes no responsibility whatsoever for this software's use by other parties, and the software is provided "AS IS" without warranty or guarantee of any kind, express or implied, including, but not limited to, the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the Government be liable for any claim, damages or other liability, whether in an action of contract, tort or other dealings in the software. The Government has no obligation hereunder to provide maintenance, support, updates, enhancements, or modifications to the software. Users may submit proposals and/or updates regarding the software, which proposals and/or updates the Government, at its sole discretion, can choose to incorporate into the software. Proposals and/or updates submitted to the Government by users must be accompanied by a license to such proposals and/or updates that is no more restrictive than this License/Disclaimer.
