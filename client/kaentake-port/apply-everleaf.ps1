param([Parameter(Mandatory=$true)][string]$SourceRoot)
$ErrorActionPreference = 'Stop'

function Replace-Exact([string]$Path, [string]$Old, [string]$New) {
    $full = Join-Path $SourceRoot $Path
    $text = [IO.File]::ReadAllText($full)
    if (-not $text.Contains($Old)) { throw "Missing expected marker in $Path`: $Old" }
    $text = $text.Replace($Old, $New)
    [IO.File]::WriteAllText($full, $text, [Text.UTF8Encoding]::new($false))
}

Replace-Exact 'CMakeLists.txt' 'project(Kaentake)' 'project(EverLeaf)'
Replace-Exact 'src/constants.h' '#define CONSTANTS_WINDOW_NAME "Kaentake"' '#define CONSTANTS_WINDOW_NAME "EverLeaf"'
Replace-Exact 'src/constants.h' '#define CONSTANTS_DLL_NAME    "Kaentake.dll"' '#define CONSTANTS_DLL_NAME    "EverLeaf.dll"'
Replace-Exact 'src/launcher.cpp' '"kaentake.dll"' '"EverLeaf.dll"'
Replace-Exact 'src/stringpool.cpp' 'REPLACE_STRING(1163, "Kaentake");' 'REPLACE_STRING(1163, "EverLeaf");'
Replace-Exact 'src/launcher.manifest' 'name="Kaentake"' 'name="EverLeaf"'
Replace-Exact 'src/launcher.manifest' '<description>Kaentake</description>' '<description>EverLeaf</description>'
Replace-Exact 'src/launcher.rc' 'VALUE "CompanyName",      "Kaentake"' 'VALUE "CompanyName",      "EverLeaf Online"'
Replace-Exact 'src/launcher.rc' 'VALUE "FileDescription",  "Kaentake"' 'VALUE "FileDescription",  "EverLeaf Client"'
Replace-Exact 'src/launcher.rc' 'VALUE "InternalName",     "Kaentake"' 'VALUE "InternalName",     "EverLeaf"'
Replace-Exact 'src/launcher.rc' 'VALUE "OriginalFilename", "Kaentake.exe"' 'VALUE "OriginalFilename", "EverLeaf.exe"'
Replace-Exact 'src/launcher.rc' 'VALUE "ProductName",      "Kaentake"' 'VALUE "ProductName",      "EverLeaf"'
Replace-Exact 'src/launcher.rc' 'VALUE "LegalCopyright",   "Kaentake"' 'VALUE "LegalCopyright",   "Kaentake contributors / EverLeaf integration"'

$cmake = Join-Path $SourceRoot 'src/CMakeLists.txt'
$text = [IO.File]::ReadAllText($cmake)
if (-not $text.Contains('loginlayout.cpp')) {
    $text = $text.Replace("    resolution.cpp`r`n", "    resolution.cpp`r`n    loginlayout.cpp`r`n")
    if (-not $text.Contains('loginlayout.cpp')) {
        $text = $text.Replace("    resolution.cpp`n", "    resolution.cpp`n    loginlayout.cpp`n")
    }
}
if (-not $text.Contains('loginlayout.cpp')) { throw 'Could not add loginlayout.cpp to src/CMakeLists.txt' }
[IO.File]::WriteAllText($cmake, $text, [Text.UTF8Encoding]::new($false))

$hook = Join-Path $SourceRoot 'src/hook.h'
$text = [IO.File]::ReadAllText($hook)
if (-not $text.Contains('void AttachLoginLayoutMod();')) {
    $text = $text.Replace("void AttachTempStatMod();", "void AttachTempStatMod();`r`nvoid AttachLoginLayoutMod();")
}
if (-not $text.Contains('    AttachLoginLayoutMod();')) {
    $text = $text.Replace("    AttachTempStatMod();", "    AttachTempStatMod();`r`n    AttachLoginLayoutMod();")
}
if (-not $text.Contains('void AttachLoginLayoutMod();') -or -not $text.Contains('    AttachLoginLayoutMod();')) {
    throw 'Could not wire AttachLoginLayoutMod into src/hook.h'
}
[IO.File]::WriteAllText($hook, $text, [Text.UTF8Encoding]::new($false))

Copy-Item (Join-Path $PSScriptRoot 'loginlayout.cpp') (Join-Path $SourceRoot 'src/loginlayout.cpp') -Force
Write-Host 'EverLeaf Kaentake integration patch applied.'
