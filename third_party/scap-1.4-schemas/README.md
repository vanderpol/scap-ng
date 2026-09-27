# Vendored SCAP 1.4 schema set

This directory is a pinned copy of the SCAP 1.4 schema set used by the SCAP-NG
iteration 001 migration tooling.

Source repository: `vanderpol/scap-content`  
Source revision: `32ab7642b4d9e9eb02476d59698dd3f83ae0e282`  
Source path: `schemas/scap-1.4-oval-5.12.3/`

The source directory name reflects the bundled OVAL 5.12.3 version, but the
vendored dependency is referred to in SCAP-NG as the **SCAP 1.4 schema set**
because it contains the SCAP 1.4 datastream schemas and the OVAL schemas used
by SCAP 1.4 validation, including `omni-schema.xsd`.

The files are retained with their original contents and embedded
license/disclaimer text. They are reference dependencies for validating source
SCAP 1.4 content and generated standalone OVAL research artifacts. They are not
SCAP-NG schemas.

The vendoring workflow copies the complete source schema directory without
modification and writes `VENDOR-MANIFEST.json` containing SHA-256 digests.
