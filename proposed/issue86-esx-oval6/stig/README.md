# Representative DISA ESXi requirements

The pinned representatives are drawn from the public MITRE/MITRE-derived
`vmware-esxi-6.5-stig-baseline` source at commit
`2967554bf747766e5251720ba1329866129ec9c0`. The profile identifies its source
as the DISA VMware ESXi 6.5 STIG v1.0.0. They are source witnesses for designing
generic `esx.host_advancedsetting` and `esx.host_service` capabilities—not a
current ESXi 8 qualification artifact.

The exact V-ID/title/selector/value crosswalk is in
`representative-requirements.json`. A future promotion must pin the current
DISA ESXi STIG release artifact and replace or supplement these rows after
review. No collector may branch on a V-ID or STIG identifier.
