# EXPERIMENTAL acquisition adapter. Not target-tested or deployable content.
# Fixed administrative queries only; no filesystem traversal or input scripts.
# Requires Windows Server DnsServer module and authorized read access.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$envelope = [ordered]@{
    format = 'research.dns-rr.v1'
    snapshot_id = [guid]::NewGuid().ToString()
    inventory = [ordered]@{ status = 'not_collected'; keys = @() }
    zones = @()
}
try {
    Import-Module DnsServer -ErrorAction Stop
    $allZones = @(Get-DnsServerZone -ErrorAction Stop)
    # This candidate scope must be compared with the original source on target.
    $zones = @($allZones | Where-Object {
        -not $_.IsAutoCreated -and -not $_.IsReverseLookupZone -and
        $_.ZoneType -notin @('Forwarder', 'TrustAnchors')
    })
    $envelope.inventory.status = 'complete'
    $envelope.inventory.keys = @($zones | ForEach-Object { $_.ZoneName })
    foreach ($zone in $zones) {
        if ($null -eq $zone.ZoneName -or $null -eq $zone.IsDsIntegrated -or $null -eq $zone.IsSigned) {
            throw 'Required zone metadata missing; no Boolean coercion of null'
        }
        $rr = [ordered]@{}
        foreach ($type in @('RRSIG', 'DNSKEY', 'NSEC3')) {
            try {
                $records = @(Get-DnsServerResourceRecord -ZoneName $zone.ZoneName -RRType $type -ErrorAction Stop)
                $rr[$type] = [ordered]@{ status = 'complete'; count = $records.Count }
            } catch {
                # A query exception is not an empty successful collection.
                $rr[$type] = [ordered]@{ status = 'error' }
            }
        }
        $envelope.zones += [ordered]@{
            key = $zone.ZoneName
            integrated = [bool]$zone.IsDsIntegrated
            signed = [bool]$zone.IsSigned
            rr = $rr
        }
    }
} catch {
    $envelope.inventory.status = 'error'
}
$envelope | ConvertTo-Json -Depth 8 -Compress
# Caller SHALL enforce timeout/output budgets and validate the whole envelope.
# Sequential query timestamps are not an atomic DNS snapshot; consistency is unproven.
