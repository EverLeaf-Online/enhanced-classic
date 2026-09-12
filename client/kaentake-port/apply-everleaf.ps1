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
Replace-Exact 'src/launcher.cpp' '"MapleStory.exe"' '"EverLeafClient.exe"'
Replace-Exact 'src/stringpool.cpp' 'REPLACE_STRING(1163, "Kaentake");' 'REPLACE_STRING(1163, "EverLeaf");'
Replace-Exact 'src/system.cpp' 'typedef decltype(&CreateMutexA) CreateMutexA_t;' @'
// Old GMS v83 DirectInput calls GetModuleFileNameW with the executable image base.
// On modern Windows that can intermittently fail with E_INVALIDARG (-2147024809).
// Passing NULL is documented to mean the current executable and is equivalent here.
typedef decltype(&GetModuleFileNameW) GetModuleFileNameW_t;
static GetModuleFileNameW_t GetModuleFileNameW_orig = reinterpret_cast<GetModuleFileNameW_t>(GetAddress("KERNEL32", "GetModuleFileNameW"));

DWORD WINAPI GetModuleFileNameW_hook(HMODULE hModule, LPWSTR lpFilename, DWORD nSize) {
    if (hModule && hModule == GetModuleHandleW(nullptr)) {
        hModule = nullptr;
    }
    return GetModuleFileNameW_orig(hModule, lpFilename, nSize);
}


typedef decltype(&CreateMutexA) CreateMutexA_t;
'@
Replace-Exact 'src/system.cpp' '    ATTACH_HOOK(SetUnhandledExceptionFilter_orig, SetUnhandledExceptionFilter_hook);' @'
    ATTACH_HOOK(SetUnhandledExceptionFilter_orig, SetUnhandledExceptionFilter_hook);
    ATTACH_HOOK(GetModuleFileNameW_orig, GetModuleFileNameW_hook);
'@
Replace-Exact 'src/launcher.manifest' 'name="Kaentake"' 'name="EverLeaf"'
Replace-Exact 'src/launcher.manifest' '<description>Kaentake</description>' '<description>EverLeaf</description>'
Replace-Exact 'src/system.cpp' '#include <intrin.h>' @'
#include <intrin.h>
#include <shellapi.h>

#pragma comment(lib, "shell32.lib")
'@
Replace-Exact 'src/system.cpp' '    g_WndProc = reinterpret_cast<WNDPROC>(SetWindowLongPtrA(hWnd, GWLP_WNDPROC, reinterpret_cast<LONG_PTR>(&WndProc_hook)));' @'
    g_WndProc = reinterpret_cast<WNDPROC>(SetWindowLongPtrA(hWnd, GWLP_WNDPROC, reinterpret_cast<LONG_PTR>(&WndProc_hook)));
    HICON hLarge = nullptr;
    HICON hSmall = nullptr;
    if (ExtractIconExA("EverLeaf.exe", 0, &hLarge, &hSmall, 1) > 0) {
        if (hLarge) SendMessageA(hWnd, WM_SETICON, ICON_BIG, reinterpret_cast<LPARAM>(hLarge));
        if (hSmall) SendMessageA(hWnd, WM_SETICON, ICON_SMALL, reinterpret_cast<LPARAM>(hSmall));
    }
'@
Replace-Exact 'src/launcher.rc' 'VALUE "CompanyName",      "Kaentake"' 'VALUE "CompanyName",      "EverLeaf Online"'
Replace-Exact 'src/launcher.rc' 'VALUE "FileDescription",  "Kaentake"' 'VALUE "FileDescription",  "EverLeaf Client"'
Replace-Exact 'src/launcher.rc' 'VALUE "InternalName",     "Kaentake"' 'VALUE "InternalName",     "EverLeaf"'
Replace-Exact 'src/launcher.rc' 'VALUE "OriginalFilename", "Kaentake.exe"' 'VALUE "OriginalFilename", "EverLeaf.exe"'
Replace-Exact 'src/launcher.rc' 'VALUE "ProductName",      "Kaentake"' 'VALUE "ProductName",      "EverLeaf"'
Replace-Exact 'src/launcher.rc' 'VALUE "LegalCopyright",   "Kaentake"' 'VALUE "LegalCopyright",   "EverLeaf Online"'

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
if (-not $text.Contains('diagnostics.cpp')) {
    $text = $text.Replace("    weblinks.cpp`r`n", "    weblinks.cpp`r`n    diagnostics.cpp`r`n")
    if (-not $text.Contains('diagnostics.cpp')) {
        $text = $text.Replace("    weblinks.cpp`n", "    weblinks.cpp`n    diagnostics.cpp`n")
    }
}
if (-not $text.Contains('loginlayout.cpp') -or
    -not $text.Contains('startup.cpp') -or
    -not $text.Contains('discordpresence.cpp') -or
    -not $text.Contains('weblinks.cpp') -or
    -not $text.Contains('diagnostics.cpp')) {
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
if (-not $text.Contains('void AttachEverLeafDiagnosticsMod();')) {
    $text = $text.Replace("void AttachEverLeafWebLinksMod();", "void AttachEverLeafWebLinksMod();`r`nvoid AttachEverLeafDiagnosticsMod();")
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
if (-not $text.Contains('    AttachEverLeafDiagnosticsMod();')) {
    $text = $text.Replace("    AttachEverLeafWebLinksMod();", "    AttachEverLeafWebLinksMod();`r`n    AttachEverLeafDiagnosticsMod();")
}
if (-not $text.Contains('void AttachLoginLayoutMod();') -or
    -not $text.Contains('void AttachEverLeafStartupMod();') -or
    -not $text.Contains('void AttachEverLeafDiscordPresenceMod();') -or
    -not $text.Contains('void AttachEverLeafWebLinksMod();') -or
    -not $text.Contains('void AttachEverLeafDiagnosticsMod();') -or
    -not $text.Contains('    AttachLoginLayoutMod();') -or
    -not $text.Contains('    AttachEverLeafStartupMod();') -or
    -not $text.Contains('    AttachEverLeafDiscordPresenceMod();') -or
    -not $text.Contains('    AttachEverLeafWebLinksMod();') -or
    -not $text.Contains('    AttachEverLeafDiagnosticsMod();')) {
    throw 'Could not wire EverLeaf client modules into src/hook.h'
}
[IO.File]::WriteAllText($hook, $text, [Text.UTF8Encoding]::new($false))

Copy-Item (Join-Path $PSScriptRoot 'loginlayout.cpp') (Join-Path $SourceRoot 'src/loginlayout.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'startup.cpp') (Join-Path $SourceRoot 'src/startup.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'discordpresence.cpp') (Join-Path $SourceRoot 'src/discordpresence.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'weblinks.cpp') (Join-Path $SourceRoot 'src/weblinks.cpp') -Force
Copy-Item (Join-Path $PSScriptRoot 'diagnostics.cpp') (Join-Path $SourceRoot 'src/diagnostics.cpp') -Force

$iconParts = @(Get-ChildItem (Join-Path (Split-Path $PSScriptRoot -Parent) 'branding/everleaf-app-icon.ico.gz.b64.part*') -File | Sort-Object Name)
if ($iconParts.Count -eq 0) { throw 'EverLeaf icon source parts are missing.' }
$iconPayload = (($iconParts | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }) -join '') -replace '\s',''
$iconCompressed = [Convert]::FromBase64String($iconPayload)
$iconInput = [IO.MemoryStream]::new($iconCompressed)
try {
    $iconGzip = [IO.Compression.GZipStream]::new($iconInput, [IO.Compression.CompressionMode]::Decompress)
    try {
        $iconPath = Join-Path $SourceRoot 'src/launcher.ico'
        $iconOutput = [IO.File]::Create($iconPath)
        try { $iconGzip.CopyTo($iconOutput) } finally { $iconOutput.Dispose() }
    } finally { $iconGzip.Dispose() }
} finally { $iconInput.Dispose() }
$iconHash = (Get-FileHash -LiteralPath (Join-Path $SourceRoot 'src/launcher.ico') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($iconHash -ne '3fdea6b7873dfff399d7a6600c864ad1a5933706392adb7c53415301ac774ceb') {
    throw "EverLeaf launcher icon SHA-256 mismatch: $iconHash"
}
Write-Host 'EverLeaf Kaentake integration patch applied.'
