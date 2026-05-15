param(
  [string]$Version = "",
  [switch]$InstallRequirements
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonExe = (Get-Command python -ErrorAction Stop).Source
$PythonRoot = Split-Path $PythonExe -Parent

if (-not $Version -and (Test-Path (Join-Path $ProjectRoot "VERSION"))) {
  $Version = (Get-Content (Join-Path $ProjectRoot "VERSION") -Raw).Trim()
}

Remove-Item -LiteralPath (Join-Path $ProjectRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $ProjectRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "dist") | Out-Null

& (Join-Path $ProjectRoot "scripts\build_runtime_bundle.ps1") -PythonRoot $PythonRoot -InstallRequirements:$InstallRequirements
& $PythonExe -m PyInstaller --clean --noconfirm (Join-Path $ProjectRoot "desktop\ndim_installer.spec")

Copy-Item -LiteralPath (Join-Path $ProjectRoot "desktop\PACKAGE_NOTES.md") -Destination (Join-Path $ProjectRoot "dist\PACKAGE_NOTES.md") -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "RELEASE_NOTES.md") -Destination (Join-Path $ProjectRoot "dist\RELEASE_NOTES.md") -Force

$zipName = if ($Version) { "NDIM-Engine-Windows-Portable-$Version.zip" } else { "NDIM-Engine-Windows-Portable.zip" }
$zipPath = Join-Path $ProjectRoot "dist\$zipName"
Compress-Archive -LiteralPath (Join-Path $ProjectRoot "dist\NDIM Engine Runtime"),(Join-Path $ProjectRoot "dist\PACKAGE_NOTES.md"),(Join-Path $ProjectRoot "dist\RELEASE_NOTES.md") -DestinationPath $zipPath -CompressionLevel Optimal

if ($Version) {
  Copy-Item -LiteralPath (Join-Path $ProjectRoot "dist\NDIM Engine Setup.exe") -Destination (Join-Path $ProjectRoot "dist\NDIM-Engine-Setup-$Version.exe") -Force
}

Write-Host "Windows release build complete."
Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "dist") | Where-Object {
  $_.Name -like "NDIM-Engine-Setup*.exe" -or $_.Name -like "NDIM-Engine-Windows-Portable*.zip"
} | Select-Object Name,Length,LastWriteTime | Format-Table -AutoSize
