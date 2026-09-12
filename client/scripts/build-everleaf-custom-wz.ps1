param(
    [string]$RepositoryRoot,
    [string]$ManifestPath,
    [string]$OutputPath,
    [string]$WorkRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$LibWzRepository = 'https://github.com/toyobayashi/libwz.git'
$LibWzCommit = '98e69cd50504a55feecc4277cc041c52c1cc538d'

if (-not $RepositoryRoot) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
}
if (-not $ManifestPath) {
    $ManifestPath = Join-Path $RepositoryRoot 'client/custom-wz/manifest.tsv'
}
if (-not $OutputPath) {
    $OutputPath = Join-Path $RepositoryRoot 'client/generated/EverLeaf_Custom.wz'
}
if (-not $WorkRoot) {
    $WorkRoot = Join-Path ([System.IO.Path]::GetTempPath()) 'everleaf-custom-wz-builder'
}

$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot)
$ManifestPath = [System.IO.Path]::GetFullPath($ManifestPath)
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$WorkRoot = [System.IO.Path]::GetFullPath($WorkRoot)

if (-not (Test-Path $ManifestPath -PathType Leaf)) {
    throw "EverLeaf custom WZ manifest not found: $ManifestPath"
}

$LibWzRoot = Join-Path $WorkRoot "libwz-$LibWzCommit"
$BuildRoot = Join-Path $WorkRoot 'build'
$ToolSource = Join-Path $RepositoryRoot 'client/tools/everleaf-custom-wz'
$OutputDirectory = Split-Path -Parent $OutputPath

New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$needsCheckout = $true
if (Test-Path (Join-Path $LibWzRoot '.git')) {
    $head = (& git -C $LibWzRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -eq 0 -and $head -eq $LibWzCommit) {
        $needsCheckout = $false
    }
}

if ($needsCheckout) {
    if (Test-Path $LibWzRoot) {
        Remove-Item -Recurse -Force $LibWzRoot
    }
    New-Item -ItemType Directory -Force -Path $LibWzRoot | Out-Null
    & git -C $LibWzRoot init
    if ($LASTEXITCODE -ne 0) { throw 'git init for pinned libwz failed' }
    & git -C $LibWzRoot remote add origin $LibWzRepository
    if ($LASTEXITCODE -ne 0) { throw 'adding libwz origin failed' }
    & git -C $LibWzRoot fetch --depth 1 origin $LibWzCommit
    if ($LASTEXITCODE -ne 0) { throw 'fetching pinned libwz commit failed' }
    & git -C $LibWzRoot checkout --detach FETCH_HEAD
    if ($LASTEXITCODE -ne 0) { throw 'checking out pinned libwz commit failed' }
}

$resolvedCommit = (& git -C $LibWzRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $resolvedCommit -ne $LibWzCommit) {
    throw "libwz checkout is not pinned to $LibWzCommit"
}

# Only the two native build dependencies are initialized. The GPL reference/test
# submodule is intentionally not checked out or used by EverLeaf's build path.
& git -C $LibWzRoot submodule update --init --depth 1 deps/tiny-aes deps/zlib
if ($LASTEXITCODE -ne 0) { throw 'initializing pinned libwz native dependencies failed' }

if (Test-Path $BuildRoot) {
    Remove-Item -Recurse -Force $BuildRoot
}

& cmake -S $ToolSource -B $BuildRoot `
    "-DLIBWZ_SOURCE_DIR=$LibWzRoot" `
    '-DBUILD_TESTS=OFF' `
    '-DBUILD_CAPI=OFF' `
    '-DBUILD_JNI=OFF' `
    '-DBUILD_WASM=OFF'
if ($LASTEXITCODE -ne 0) { throw 'configuring EverLeaf custom WZ builder failed' }

& cmake --build $BuildRoot --config Release --target everleaf-custom-wz-builder
if ($LASTEXITCODE -ne 0) { throw 'building EverLeaf custom WZ builder failed' }

$BuilderCandidates = @(
    (Join-Path $BuildRoot 'Release/everleaf-custom-wz-builder.exe'),
    (Join-Path $BuildRoot 'everleaf-custom-wz-builder.exe'),
    (Join-Path $BuildRoot 'Release/everleaf-custom-wz-builder'),
    (Join-Path $BuildRoot 'everleaf-custom-wz-builder')
)
$Builder = $BuilderCandidates | Where-Object { Test-Path $_ -PathType Leaf } | Select-Object -First 1
if (-not $Builder) {
    throw 'EverLeaf custom WZ builder output was not found'
}

& $Builder $ManifestPath $OutputPath
if ($LASTEXITCODE -ne 0) { throw 'EverLeaf custom WZ build/verification failed' }

if (-not (Test-Path $OutputPath -PathType Leaf)) {
    throw "EverLeaf_Custom.wz was not produced: $OutputPath"
}

$hash = Get-FileHash $OutputPath -Algorithm SHA256
Write-Host "EverLeaf custom WZ built from manifest"
Write-Host "libwz commit: $LibWzCommit"
Write-Host "output: $OutputPath"
Write-Host "sha256: $($hash.Hash)"
