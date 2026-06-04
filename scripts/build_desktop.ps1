param(
  [switch]$Clean,
  [switch]$UseVenv,
  [switch]$Installer,
  [string]$PythonExe = $env:PYTHON_EXE
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendRequirements = Join-Path $ProjectRoot "backend\requirements.lock.txt"
if (!(Test-Path $BackendRequirements)) {
  $BackendRequirements = Join-Path $ProjectRoot "backend\requirements.txt"
}
$Venv = Join-Path $ProjectRoot ".venv-desktop"
$Python = Join-Path $Venv "Scripts\python.exe"
$PyInstaller = Join-Path $Venv "Scripts\pyinstaller.exe"

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

if (-not $PythonExe) {
  throw "Python was not found. Pass -PythonExe 'C:\Path\To\python.exe' or set PYTHON_EXE."
}

if ($Clean) {
  Remove-Item -LiteralPath (Join-Path $ProjectRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath (Join-Path $ProjectRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue
}

if ($Clean -and $UseVenv -and (Test-Path $Venv)) {
  Remove-Item -LiteralPath $Venv -Recurse -Force
}

if ($UseVenv) {
  if (!(Test-Path $Python)) {
    & $PythonExe -m venv $Venv
  }
  & $Python -m pip install --upgrade pip
  & $Python -m pip install -r $BackendRequirements
  & $Python -m pip install -r (Join-Path $ProjectRoot "desktop\requirements-desktop.txt")
  & $PyInstaller --clean --noconfirm (Join-Path $ProjectRoot "desktop\ndim_desktop.spec")
  if ($Installer) {
    & $PyInstaller --clean --noconfirm (Join-Path $ProjectRoot "desktop\ndim_installer.spec")
  }
} else {
  & $PythonExe -m pip install -r $BackendRequirements
  & $PythonExe -m pip install -r (Join-Path $ProjectRoot "desktop\requirements-desktop.txt")
  & $PythonExe -m PyInstaller --clean --noconfirm (Join-Path $ProjectRoot "desktop\ndim_desktop.spec")
  if ($Installer) {
    & $PythonExe -m PyInstaller --clean --noconfirm (Join-Path $ProjectRoot "desktop\ndim_installer.spec")
  }
}

Write-Host ""
Write-Host "NDIM desktop build complete."
Write-Host "Output folder: $(Join-Path $ProjectRoot 'dist')"
if ($Installer) {
  Write-Host "Installer: $(Join-Path $ProjectRoot 'dist\NDIM Engine Setup.exe')"
}
