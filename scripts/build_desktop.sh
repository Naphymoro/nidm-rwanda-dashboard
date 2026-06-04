#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_REQUIREMENTS="$PROJECT_ROOT/backend/requirements.lock.txt"
if [[ ! -f "$BACKEND_REQUIREMENTS" ]]; then
  BACKEND_REQUIREMENTS="$PROJECT_ROOT/backend/requirements.txt"
fi
VENV="$PROJECT_ROOT/.venv-desktop"
BASE_PYTHON="${PYTHON_EXE:-python3}"
PYTHON="$VENV/bin/python"
PYINSTALLER="$VENV/bin/pyinstaller"
USE_VENV="${USE_VENV:-0}"
BUILD_INSTALLER="${BUILD_INSTALLER:-0}"

if [[ "${1:-}" == "--clean" ]]; then
  rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist"
  if [[ "$USE_VENV" == "1" && -d "$VENV" ]]; then
    rm -rf "$VENV"
  fi
fi

if [[ "$USE_VENV" == "1" ]]; then
  if [[ ! -x "$PYTHON" ]]; then
    "$BASE_PYTHON" -m venv "$VENV"
  fi
  "$PYTHON" -m pip install --upgrade pip
  "$PYTHON" -m pip install -r "$BACKEND_REQUIREMENTS"
  "$PYTHON" -m pip install -r "$PROJECT_ROOT/desktop/requirements-desktop.txt"
  "$PYINSTALLER" --clean --noconfirm "$PROJECT_ROOT/desktop/ndim_desktop.spec"
  if [[ "$BUILD_INSTALLER" == "1" ]]; then
    "$PYINSTALLER" --clean --noconfirm "$PROJECT_ROOT/desktop/ndim_installer.spec"
  fi
else
  "$BASE_PYTHON" -m pip install -r "$BACKEND_REQUIREMENTS"
  "$BASE_PYTHON" -m pip install -r "$PROJECT_ROOT/desktop/requirements-desktop.txt"
  "$BASE_PYTHON" -m PyInstaller --clean --noconfirm "$PROJECT_ROOT/desktop/ndim_desktop.spec"
  if [[ "$BUILD_INSTALLER" == "1" ]]; then
    "$BASE_PYTHON" -m PyInstaller --clean --noconfirm "$PROJECT_ROOT/desktop/ndim_installer.spec"
  fi
fi

echo
echo "NDIM desktop build complete."
echo "Output folder: $PROJECT_ROOT/dist"
