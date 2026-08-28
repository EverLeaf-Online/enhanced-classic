param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")),
    [string]$OutputDirectory = (Join-Path (Get-Location) "EverleafClient")
)

$ErrorActionPreference = "Stop"
$baselinePath = Join-Path $RepositoryRoot "client/managed-client-baseline.json"
$baseline = Get-Content -LiteralPath $baselinePath -Raw | ConvertFrom-Json

if ($baseline.schemaVersion -ne 1) { throw "Unsupported managed-client baseline schema." }
if (-not $baseline.managedFiles -or $baseline.managedFiles.Count -eq 0) { throw "Managed-client baseline is empty." }

$seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$packagedPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$root = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$output = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -Force | Out-Null

foreach ($entry in $baseline.managedFiles) {
    if ($entry.redistributable -ne $true) { throw "Managed file is not approved for distribution: $($entry.path)" }
    if ([string]::IsNullOrWhiteSpace($entry.path) -or [IO.Path]::IsPathRooted($entry.path)) { throw "Unsafe managed path." }
    if ($entry.path.Contains('\') -or $entry.path.Split('/') -contains '..') { throw "Unsafe managed path: $($entry.path)" }
    if (-not $seen.Add([string]$entry.path)) { throw "Duplicate managed path: $($entry.path)" }

    # Entries without a repository source come from the authorized bootstrap
    # client and remain on the patch server. This package contains only overlays
    # that are reproducibly built from this repository.
    if ([string]::IsNullOrWhiteSpace([string]$entry.source)) { continue }
    [void]$packagedPaths.Add([string]$entry.path)

    $source = [IO.Path]::GetFullPath((Join-Path $RepositoryRoot $entry.source))
    if (-not $source.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) { throw "Managed source escapes repository: $($entry.source)" }
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing canonical managed file: $($entry.source)" }

    $destination = [IO.Path]::GetFullPath((Join-Path $output $entry.path))
    $outputRoot = $output.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $destination.StartsWith($outputRoot, [StringComparison]::OrdinalIgnoreCase)) { throw "Managed destination escapes package." }
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Force
}

$packaged = Get-ChildItem -LiteralPath $output -File -Recurse | ForEach-Object {
    [IO.Path]::GetRelativePath($output, $_.FullName).Replace('\', '/')
}
$unexpected = @($packaged | Where-Object { -not $packagedPaths.Contains($_) })
$missing = @($packagedPaths | Where-Object { $_ -notin $packaged })
if ($unexpected.Count -or $missing.Count) {
    throw "Canonical package does not exactly match the managed baseline. Unexpected=[$($unexpected -join ', ')] Missing=[$($missing -join ', ')]"
}

Copy-Item -LiteralPath $baselinePath -Destination (Join-Path $output "managed-client-baseline.json") -Force
Write-Host "Built $($packagedPaths.Count) repository overlays for a $($seen.Count)-file managed client."
