# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path(SPECPATH).resolve()
PROJECT = ROOT.parent

datas = [
    (str(PROJECT / "docs"), "docs"),
    (str(PROJECT / "stress_test_corpus"), "stress_test_corpus"),
]


a = Analysis(
    [str(ROOT / "ndim_desktop.py")],
    pathex=[str(PROJECT / "backend"), str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "app.main",
        "app.workflow_ui",
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
    ],
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
