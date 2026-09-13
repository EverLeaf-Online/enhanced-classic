param(
    [string]$MapPath = (Join-Path (Get-Location) 'Map.wz'),
    [int]$TargetWidth = 1920,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Write-ResponsiveCanvas {
    param(
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][int]$Width
    )

    $src = [System.Drawing.Bitmap]::FromFile($InputPath)
    try {
        [int]$srcWidth = $src.Width
        [int]$srcHeight = $src.Height

        if ($srcWidth -gt $Width) {
            throw "Current login canvas ($srcWidth px) is wider than target ($Width px)."
        }

        [int]$difference = $Width - $srcWidth
        if (($difference % 2) -ne 0) {
            throw 'Target width must preserve an integer-centered inset.'
        }

        [int]$inset = $difference / 2
        if ($inset -gt $srcWidth) {
            throw "Target width requires a $inset px edge sample, but the source is only $srcWidth px wide."
        }

        $dst = [System.Drawing.Bitmap]::new(
            $Width,
            $srcHeight,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            $g = [System.Drawing.Graphics]::FromImage($dst)
            try {
                $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
                $g.DrawImageUnscaled($src, $inset, 0)

                if ($inset -gt 0) {
                    # Reflect the existing edge strips into the newly exposed area.
                    # This preserves the entire original composition pixel-for-pixel.
                    $leftRect = [System.Drawing.Rectangle]::new(0, 0, $inset, $srcHeight)
                    [int]$rightX = $srcWidth - $inset
                    $rightRect = [System.Drawing.Rectangle]::new($rightX, 0, $inset, $srcHeight)
                    $left = $src.Clone($leftRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
                    $right = $src.Clone($rightRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
                    try {
                        $left.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX)
                        $right.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX)
                        $g.DrawImageUnscaled($left, 0, 0)
                        [int]$rightDestX = $inset + $srcWidth
                        $g.DrawImageUnscaled($right, $rightDestX, 0)
                    }
                    finally {
                        $left.Dispose()
                        $right.Dispose()
                    }
                }
            }
            finally {
                $g.Dispose()
            }

            $dst.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        }
        finally {
            $dst.Dispose()
        }
    }
    finally {
        $src.Dispose()
    }
}

if ($SelfTest) {
    $selfTestRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("everleaf-responsive-login-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force $selfTestRoot | Out-Null
    try {
        $input = Join-Path $selfTestRoot 'input.png'
        $output = Join-Path $selfTestRoot 'output.png'
        $fixture = [System.Drawing.Bitmap]::new(
            1400,
            16,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            $fixture.Save($input, [System.Drawing.Imaging.ImageFormat]::Png)
        }
        finally {
            $fixture.Dispose()
        }

        Write-ResponsiveCanvas -InputPath $input -OutputPath $output -Width 1920

        $verified = [System.Drawing.Bitmap]::FromFile($output)
        try {
            if ($verified.Width -ne 1920 -or $verified.Height -ne 16) {
                throw "Padding self-test produced $($verified.Width)x$($verified.Height), expected 1920x16."
            }
        }
        finally {
            $verified.Dispose()
        }

        Write-Host 'RESPONSIVE_LOGIN_PADDING_SELF_TEST_OK'
    }
    finally {
        Remove-Item -LiteralPath $selfTestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 0
}

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

Write-ResponsiveCanvas -InputPath $extracted -OutputPath $responsive -Width $TargetWidth

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
