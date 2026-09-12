param(
    [string]$MapPath = (Join-Path (Get-Location) 'Map.wz'),
    [int]$TargetWidth = 1920
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MapPath
if ([string]::IsNullOrWhiteSpace($root)) { $root = (Get-Location).Path }
$patcher = Join-Path $PSScriptRoot 'everleaf-responsive-login-wz.exe'
if (-not (Test-Path $patcher)) { throw "Missing patcher: $patcher" }
if (-not (Test-Path $MapPath)) { throw "Missing Map.wz: $MapPath" }

$backup = Join-Path $root 'Map.wz.pre-responsive-login.bak'
$extracted = Join-Path $root 'EverLeaf-login-current.png'
$responsive = Join-Path $root 'EverLeaf-login-responsive.png'
$output = Join-Path $root 'Map.wz.responsive.tmp'

Write-Host 'Inspecting current EverLeaf login background...'
& $patcher inspect $MapPath
if ($LASTEXITCODE -ne 0) { throw "Map.wz inspection failed ($LASTEXITCODE)" }

& $patcher extract $MapPath $extracted
if ($LASTEXITCODE -ne 0) { throw "Map.wz login extraction failed ($LASTEXITCODE)" }

Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Bitmap]::FromFile($extracted)
try {
    if ($src.Width -gt $TargetWidth) {
        throw "Current login canvas ($($src.Width) px) is wider than target ($TargetWidth px)."
    }
    if ((($TargetWidth - $src.Width) % 2) -ne 0) {
        throw 'Target width must preserve an integer-centered inset.'
    }

    $inset = [int](($TargetWidth - $src.Width) / 2)
    $dst = New-Object System.Drawing.Bitmap($TargetWidth, $src.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        $g = [System.Drawing.Graphics]::FromImage($dst)
        try {
            $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
            $g.DrawImageUnscaled($src, $inset, 0)

            if ($inset -gt 0) {
                # Reflect the existing edge strips into the newly exposed area.
                # This preserves the entire original 1400px composition pixel-for-pixel.
                $leftRect = New-Object System.Drawing.Rectangle(0, 0, $inset, $src.Height)
                $rightRect = New-Object System.Drawing.Rectangle($src.Width - $inset, 0, $inset, $src.Height)
                $left = $src.Clone($leftRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
                $right = $src.Clone($rightRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
                try {
                    $left.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX)
                    $right.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX)
                    $g.DrawImageUnscaled($left, 0, 0)
                    $g.DrawImageUnscaled($right, $inset + $src.Width, 0)
                }
                finally {
                    $left.Dispose()
                    $right.Dispose()
                }
            }
        }
        finally { $g.Dispose() }
        $dst.Save($responsive, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally { $dst.Dispose() }
}
finally { $src.Dispose() }

if (Test-Path $output) { Remove-Item -Force $output }
Write-Host 'Rebuilding a test Map.wz. This can take a minute or two...'
& $patcher patch $MapPath $responsive $output
if ($LASTEXITCODE -ne 0) { throw "Responsive Map.wz rebuild failed ($LASTEXITCODE)" }
if (-not (Test-Path $output) -or (Get-Item $output).Length -lt 100MB) {
    throw 'Responsive Map.wz output is missing or implausibly small.'
}

if (-not (Test-Path $backup)) {
    Move-Item -LiteralPath $MapPath -Destination $backup
} else {
    Write-Host "Backup already exists: $backup"
    Remove-Item -LiteralPath $MapPath -Force
}
Move-Item -LiteralPath $output -Destination $MapPath
Remove-Item -Force $extracted, $responsive -ErrorAction SilentlyContinue

Write-Host ''
Write-Host 'RESPONSIVE LOGIN MAP INSTALLED' -ForegroundColor Green
Write-Host "Backup: $backup"
Write-Host 'The original center composition is preserved; the canvas now covers up to 1920px wide.'
