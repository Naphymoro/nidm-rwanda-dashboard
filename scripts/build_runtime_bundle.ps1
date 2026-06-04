param(
  [string]$PythonRoot = "",
  [string]$PythonExe = $env:PYTHON_EXE,
  [switch]$InstallRequirements
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendRequirements = Join-Path $ProjectRoot "backend\requirements.lock.txt"
if (!(Test-Path $BackendRequirements)) {
  $BackendRequirements = Join-Path $ProjectRoot "backend\requirements.txt"
}
$RuntimeRoot = Join-Path $ProjectRoot "dist\NDIM Engine Runtime"

if (-not $PythonExe) {
  $candidate = Get-Command python -ErrorAction SilentlyContinue
  if ($candidate) {
    $PythonExe = $candidate.Source
  } else {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
      $PythonExe = $pyLauncher.Source
    }
  }
}

if (-not $PythonRoot) {
  if (-not $PythonExe) {
    throw "Python was not found. Pass -PythonRoot or -PythonExe."
  }
  $PythonRoot = Split-Path $PythonExe -Parent
}

if (!(Test-Path $PythonRoot)) {
  throw "Python runtime folder not found: $PythonRoot"
}

if ($InstallRequirements) {
  & (Join-Path $PythonRoot "python.exe") -m pip install --upgrade pip
  & (Join-Path $PythonRoot "python.exe") -m pip install -r $BackendRequirements
  & (Join-Path $PythonRoot "python.exe") -m pip install -r (Join-Path $ProjectRoot "desktop\requirements-desktop.txt")
}

if (Test-Path $RuntimeRoot) {
  Remove-Item -LiteralPath $RuntimeRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $ProjectRoot "backend") -Destination (Join-Path $RuntimeRoot "backend") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "desktop") -Destination (Join-Path $RuntimeRoot "desktop") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "docs") -Destination (Join-Path $RuntimeRoot "docs") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "stress_test_corpus") -Destination (Join-Path $RuntimeRoot "stress_test_corpus") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "desktop\Launch NDIM Engine.cmd") -Destination (Join-Path $RuntimeRoot "Launch NDIM Engine.cmd") -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "desktop\PACKAGE_NOTES.md") -Destination (Join-Path $RuntimeRoot "PACKAGE_NOTES.md") -Force
Copy-Item -LiteralPath $PythonRoot -Destination (Join-Path $RuntimeRoot "runtime") -Recurse -Force

$unneededPackages = @(
  "runtime\Lib\site-packages\artifact_tool_v2",
  "runtime\Lib\site-packages\artifact_tool_v2-2.7.8.dist-info"
)

foreach ($package in $unneededPackages) {
  $target = Join-Path $RuntimeRoot $package
  if (Test-Path $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
  }
}

Write-Host "NDIM runtime bundle complete: $RuntimeRoot"
