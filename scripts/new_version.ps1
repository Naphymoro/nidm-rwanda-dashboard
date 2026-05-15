param(
  [Parameter(Mandatory = $true)]
  [string]$Version
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

if ($Version.StartsWith("v")) {
  $Version = $Version.Substring(1)
}

Set-Content -LiteralPath (Join-Path $ProjectRoot "VERSION") -Value $Version -Encoding UTF8

$innoPath = Join-Path $ProjectRoot "installer\windows\ndim_engine.iss"
if (Test-Path $innoPath) {
  $content = Get-Content -LiteralPath $innoPath -Raw
  $content = $content -replace '#define MyAppVersion ".*"', "#define MyAppVersion `"$Version`""
  Set-Content -LiteralPath $innoPath -Value $content -Encoding UTF8
}

Write-Host "Updated NDIM Engine version to $Version"
