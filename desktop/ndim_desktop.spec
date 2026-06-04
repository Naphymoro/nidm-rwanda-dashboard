# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


ROOT = Path(SPECPATH).resolve()
PROJECT = ROOT.parent

datas = [
    (str(PROJECT / "docs"), "docs"),
    (str(PROJECT / "stress_test_corpus"), "stress_test_corpus"),
]

for package in ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "pandas", "numpy", "sklearn", "pyro", "torch", "pypdf"]:
    try:
        datas += copy_metadata(package)
    except Exception:
        pass

for package in ["pyro", "sklearn", "pypdf"]:
    try:
        datas += collect_data_files(package)
    except Exception:
        pass


a = Analysis(
    [str(ROOT / "ndim_desktop.py")],
    pathex=[str(PROJECT / "backend"), str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "app.main",
        "app.workflow_ui",
        "app.security",
        "app.storage",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
        "httptools.parser.parser",
        "websockets",
        "multipart",
        "pypdf",
        "pandas",
        "numpy",
        "torch",
        "pyro",
        "sklearn",
        "scipy",
    ]
    + collect_submodules("pyro")
    + collect_submodules("sklearn"),
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
    [],
    name="NDIM Engine",
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
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NDIM Engine App",
)
