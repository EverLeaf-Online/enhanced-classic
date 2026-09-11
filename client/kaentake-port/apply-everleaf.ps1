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
if (-not $text.Contains('startup.cpp')) {
    $text = $text.Replace("    loginlayout.cpp`r`n", "    loginlayout.cpp`r`n    startup.cpp`r`n")
    if (-not $text.Contains('startup.cpp')) {
        $text = $text.Replace("    loginlayout.cpp`n", "    loginlayout.cpp`n    startup.cpp`n")
    }
}
if (-not $text.Contains('discordpresence.cpp')) {
    $text = $text.Replace("    startup.cpp`r`n", "    startup.cpp`r`n    discordpresence.cpp`r`n")
    if (-not $text.Contains('discordpresence.cpp')) {
        $text = $text.Replace("    startup.cpp`n", "    startup.cpp`n    discordpresence.cpp`n")
    }
}
if (-not $text.Contains('weblinks.cpp')) {
    $text = $text.Replace("    discordpresence.cpp`r`n", "    discordpresence.cpp`r`n    weblinks.cpp`r`n")
    if (-not $text.Contains('weblinks.cpp')) {
        $text = $text.Replace("    discordpresence.cpp`n", "    discordpresence.cpp`n    weblinks.cpp`n")
    }
}
if (-not $text.Contains('loginlayout.cpp') -or
    -not $text.Contains('startup.cpp') -or
    -not $text.Contains('discordpresence.cpp') -or
    -not $text.Contains('weblinks.cpp')) {
    throw 'Could not add EverLeaf client modules to src/CMakeLists.txt'
}
[IO.File]::WriteAllText($cmake, $text, [Text.UTF8Encoding]::new($false))

$hook = Join-Path $SourceRoot 'src/hook.h'
$text = [IO.File]::ReadAllText($hook)
if (-not $text.Contains('void AttachLoginLayoutMod();')) {
    $text = $text.Replace("void AttachTempStatMod();", "void AttachTempStatMod();`r`nvoid AttachLoginLayoutMod();")
}
if (-not $text.Contains('void AttachEverLeafStartupMod();')) {
    $text = $text.Replace("void AttachLoginLayoutMod();", "void AttachLoginLayoutMod();`r`nvoid AttachEverLeafStartupMod();")
}
if (-not $text.Contains('void AttachEverLeafDiscordPresenceMod();')) {
    $text = $text.Replace("void AttachEverLeafStartupMod();", "void AttachEverLeafStartupMod();`r`nvoid AttachEverLeafDiscordPresenceMod();")
}
if (-not $text.Contains('void AttachEverLeafWebLinksMod();')) {
    $text = $text.Replace("void AttachEverLeafDiscordPresenceMod();", "void AttachEverLeafDiscordPresenceMod();`r`nvoid AttachEverLeafWebLinksMod();")
}
if (-not $text.Contains('    AttachLoginLayoutMod();')) {
    $text = $text.Replace("    AttachTempStatMod();", "    AttachTempStatMod();`r`n    AttachLoginLayoutMod();")
}
if (-not $text.Contains('    AttachEverLeafStartupMod();')) {
    $text = $text.Replace("    AttachLoginLayoutMod();", "    AttachLoginLayoutMod();`r`n    AttachEverLeafStartupMod();")
}
if (-not $text.Contains('    AttachEverLeafDiscordPresenceMod();')) {
    $text = $text.Replace("    AttachEverLeafStartupMod();", "    AttachEverLeafStartupMod();`r`n    AttachEverLeafDiscordPresenceMod();")
}
if (-not $text.Contains('    AttachEverLeafWebLinksMod();')) {
    $text = $text.Replace("    AttachEverLeafDiscordPresenceMod();", "    AttachEverLeafDiscordPresenceMod();`r`n    AttachEverLeafWebLinksMod();")
}
if (-not $text.Contains('void AttachLoginLayoutMod();') -or
    -not $text.Contains('void AttachEverLeafStartupMod();') -or
    -not $text.Contains('void AttachEverLeafDiscordPresenceMod();') -or
    -not $text.Contains('void AttachEverLeafWebLinksMod();') -or
    -not $text.Contains('    AttachLoginLayoutMod();') -or
    -not $text.Contains('    AttachEverLeafStartupMod();') -or
    -not $text.Contains('    AttachEverLeafDiscordPresenceMod();') -or
    -not $text.Contains('    AttachEverLeafWebLinksMod();')) {
    throw 'Could not wire EverLeaf client modules into src/hook.h'
}
[IO.File]::WriteAllText($hook, $text, [Text.UTF8Encoding]::new($false))

Copy-Item (Join-Path $PSScriptRoot 'loginlayout.cpp') (Join-Path $SourceRoot 'src/loginlayout.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'startup.cpp') (Join-Path $SourceRoot 'src/startup.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'discordpresence.cpp') (Join-Path $SourceRoot 'src/discordpresence.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'weblinks.cpp') (Join-Path $SourceRoot 'src/weblinks.cpp') -Force
Write-Host 'EverLeaf Kaentake integration patch applied.'
