# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


root = Path(SPECPATH).resolve()
project_root = root.parent
app_exe = project_root / "dist" / "NDIM Engine.exe"
app_dir = project_root / "dist" / "NDIM Engine Runtime"
package_notes = project_root / "desktop" / "PACKAGE_NOTES.md"

if app_dir.exists():
    app_payload = app_dir
elif app_exe.exists():
    app_payload = app_exe
else:
    raise SystemExit("Build the NDIM desktop app before building the installer.")

a = Analysis(
    [str(project_root / "desktop" / "ndim_installer.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(app_payload), "payload/NDIM Engine Runtime"),
        (str(package_notes), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="NDIM Engine Setup",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
