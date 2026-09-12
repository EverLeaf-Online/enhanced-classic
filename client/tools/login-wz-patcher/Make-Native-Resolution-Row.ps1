param(
    [string]$UIPath = (Join-Path (Get-Location) 'UI.wz')
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $UIPath
if ([string]::IsNullOrWhiteSpace($root)) { $root = (Get-Location).Path }
$patcher = Join-Path $PSScriptRoot 'everleaf-system-options-wz.exe'
if (-not (Test-Path $patcher)) { throw "Missing patcher: $patcher" }
if (-not (Test-Path $UIPath)) { throw "Missing UI.wz: $UIPath" }

$info = (& $patcher inspect $UIPath) -join "`n"
if ($LASTEXITCODE -ne 0) { throw "UI.wz inspection failed ($LASTEXITCODE)" }
$width = [int]([regex]::Match($info, 'WIDTH=(\d+)').Groups[1].Value)
$height = [int]([regex]::Match($info, 'HEIGHT=(\d+)').Groups[1].Value)
if ($width -ne 299) { throw "Unexpected System Options width: $width" }
if ($height -eq 396) {
    Write-Host 'Native Resolution row is already installed.' -ForegroundColor Green
    exit 0
}
if ($height -ne 366) { throw "Unexpected System Options height: $height" }

$backup = Join-Path $root 'UI.wz.pre-resolution-row.bak'
$extracted = Join-Path $root 'EverLeaf-SysOpt-current.png'
$native = Join-Path $root 'EverLeaf-SysOpt-native.png'
$output = Join-Path $root 'UI.wz.resolution-row.tmp'

& $patcher extract $UIPath $extracted
if ($LASTEXITCODE -ne 0) { throw "System Options extraction failed ($LASTEXITCODE)" }

Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Bitmap]::FromFile($extracted)
try {
    if ($src.Width -ne 299 -or $src.Height -ne 366) {
        throw "Expected 299x366 System Options artwork; found $($src.Width)x$($src.Height)."
    }

    $dst = [System.Drawing.Bitmap]::new(299, 396, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        $g = [System.Drawing.Graphics]::FromImage($dst)
        try {
            $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
            # Existing settings through Viewing Mode stay pixel-identical.
            $g.DrawImage($src,
                [System.Drawing.Rectangle]::new(0, 0, 299, 330),
                [System.Drawing.Rectangle]::new(0, 0, 299, 330),
                [System.Drawing.GraphicsUnit]::Pixel)
            # Reuse the clean Monster Info row shell; its right side was designed
            # for a native combo and therefore has no baked checkbox text.
            $g.DrawImage($src,
                [System.Drawing.Rectangle]::new(0, 330, 299, 30),
                [System.Drawing.Rectangle]::new(0, 270, 299, 30),
                [System.Drawing.GraphicsUnit]::Pixel)
            # Move the original footer/button chrome down exactly one row.
            $g.DrawImage($src,
                [System.Drawing.Rectangle]::new(0, 360, 299, 36),
                [System.Drawing.Rectangle]::new(0, 330, 299, 36),
                [System.Drawing.GraphicsUnit]::Pixel)
        }
        finally { $g.Dispose() }

        # Remove the copied MONSTER INFO glyphs while preserving the row's
        # vertical pink gradient. Borders stay untouched.
        for ($yy = 333; $yy -le 357; $yy++) {
            $counts = @{}
            for ($xx = 4; $xx -le 50; $xx++) {
                $c = $dst.GetPixel($xx, $yy)
                if ($c.R -gt 235 -and $c.G -gt 235 -and $c.B -gt 235) { continue }
                $key = ('{0},{1},{2},{3}' -f $c.A,$c.R,$c.G,$c.B)
                if (-not $counts.ContainsKey($key)) { $counts[$key] = 0 }
                $counts[$key]++
            }
            if ($counts.Count -gt 0) {
                $best = ($counts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key.Split(',')
                $fill = [System.Drawing.Color]::FromArgb([int]$best[0],[int]$best[1],[int]$best[2],[int]$best[3])
                for ($xx = 4; $xx -le 50; $xx++) { $dst.SetPixel($xx, $yy, $fill) }
            }
        }

        $g2 = [System.Drawing.Graphics]::FromImage($dst)
        try {
            $g2.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit
            $font = [System.Drawing.Font]::new('Arial', 7.0, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
            $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
            $fmt = [System.Drawing.StringFormat]::new()
            try {
                $fmt.Alignment = [System.Drawing.StringAlignment]::Center
                $fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
                $g2.DrawString('RESOLUTION', $font, $brush,
                    [System.Drawing.RectangleF]::new(3.0, 332.0, 49.0, 26.0), $fmt)
            }
            finally { $fmt.Dispose(); $brush.Dispose(); $font.Dispose() }
        }
        finally { $g2.Dispose() }

        $dst.Save($native, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally { $dst.Dispose() }
}
finally { $src.Dispose() }

if (Test-Path $output) { Remove-Item -Force $output }
Write-Host 'Rebuilding UI.wz with a native Resolution row...'
& $patcher patch $UIPath $native $output
if ($LASTEXITCODE -ne 0) { throw "UI.wz rebuild failed ($LASTEXITCODE)" }
if (-not (Test-Path $output) -or (Get-Item $output).Length -lt 10MB) {
    throw 'Patched UI.wz output is missing or implausibly small.'
}

if (-not (Test-Path $backup)) {
    Move-Item -LiteralPath $UIPath -Destination $backup
} else {
    Write-Host "Backup already exists: $backup"
    Remove-Item -LiteralPath $UIPath -Force
}
Move-Item -LiteralPath $output -Destination $UIPath
Remove-Item -Force $extracted, $native -ErrorAction SilentlyContinue

Write-Host ''
Write-Host 'NATIVE RESOLUTION ROW INSTALLED' -ForegroundColor Green
Write-Host "Backup: $backup"
