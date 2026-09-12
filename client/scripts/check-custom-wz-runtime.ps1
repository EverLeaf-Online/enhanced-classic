param(
    [Parameter(Mandatory = $false)]
    [string]$ClientDirectory = '.',

    [Parameter(Mandatory = $false)]
    [ValidateSet('present', 'absent')]
    [string]$Expected = 'present'
)

$ErrorActionPreference = 'Stop'

$resolvedClient = (Resolve-Path -LiteralPath $ClientDirectory).Path
$logPath = Join-Path $resolvedClient 'EverLeafClient.log'
$customWzPath = Join-Path $resolvedClient 'EverLeaf_Custom.wz'

if (-not (Test-Path -LiteralPath $logPath -PathType Leaf)) {
    throw "EverLeafClient.log was not found beside the client: $logPath"
}

$log = Get-Content -LiteralPath $logPath -Raw
if ([string]::IsNullOrWhiteSpace($log)) {
    throw 'EverLeafClient.log is empty'
}

$mountHookMarker = 'EverLeaf custom WZ mount hook installed'
$absentMarker = 'EverLeaf_Custom.wz not present; custom namespace disabled'
$activeMarkers = @(
    'EverLeaf custom WZ mounted in private namespace',
    'custom WZ override index built',
    'custom WZ local-object fallback enabled',
    'custom WZ partial property merge enabled'
)

$failureMarkers = @(
    'EverLeaf custom WZ mount unavailable; stock resources kept',
    'EverLeaf custom WZ lookup fallback unavailable; private mount retained',
    'EverLeaf custom WZ property merge unavailable; lookup fallback retained',
    'custom WZ override enumeration failed',
    'NameSpace local-object signature unavailable',
    'NameSpace local-object signature ambiguous',
    'custom WZ local-object fallback hook failed',
    'PCOM property serializer signature unavailable',
    'PCOM property serializer signature ambiguous',
    'custom WZ property serializer hook failed',
    'custom WZ property child merge failed',
    'custom WZ property merge skipped after guarded failure',
    '[CRASH]'
)

function Require-Marker([string]$marker) {
    if (-not $log.Contains($marker)) {
        throw "Missing runtime success marker: $marker"
    }
}

function Reject-Marker([string]$marker) {
    if ($log.Contains($marker)) {
        throw "Unexpected runtime marker: $marker"
    }
}

Require-Marker $mountHookMarker

if ($Expected -eq 'present') {
    if (-not (Test-Path -LiteralPath $customWzPath -PathType Leaf)) {
        throw "Expected EverLeaf_Custom.wz beside the client: $customWzPath"
    }

    $bytes = [System.IO.File]::ReadAllBytes($customWzPath)
    if ($bytes.Length -lt 32) {
        throw 'EverLeaf_Custom.wz is implausibly small'
    }
    $signature = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
    if ($signature -ne 'PKG1') {
        throw "EverLeaf_Custom.wz has an unexpected signature: $signature"
    }

    Reject-Marker $absentMarker
    foreach ($marker in $activeMarkers) {
        Require-Marker $marker
    }
    foreach ($marker in $failureMarkers) {
        Reject-Marker $marker
    }

    Write-Host 'EverLeaf custom WZ runtime validation: PASS (custom WZ present)'
    Write-Host "  client: $resolvedClient"
    Write-Host '  private mount: PASS'
    Write-Host '  override index: PASS'
    Write-Host '  stock-first lookup fallback hook: PASS'
    Write-Host '  partial property merge hook: PASS'
    Write-Host '  custom-WZ failure/crash markers: none'
    exit 0
}

if (Test-Path -LiteralPath $customWzPath -PathType Leaf) {
    throw "Expected EverLeaf_Custom.wz to be removed for the fail-closed test: $customWzPath"
}

Require-Marker $absentMarker
foreach ($marker in $activeMarkers) {
    Reject-Marker $marker
}
foreach ($marker in $failureMarkers) {
    Reject-Marker $marker
}

Write-Host 'EverLeaf custom WZ runtime validation: PASS (custom WZ absent)'
Write-Host "  client: $resolvedClient"
Write-Host '  mount hook installed: PASS'
Write-Host '  optional-file fail-closed path: PASS'
Write-Host '  custom namespace/index/fallback/merge remained inactive: PASS'
Write-Host '  custom-WZ failure/crash markers: none'
exit 0
