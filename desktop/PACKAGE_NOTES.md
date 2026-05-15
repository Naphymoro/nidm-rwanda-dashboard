# NDIM Engine Windows Package

This package contains a bundled Windows runtime folder and, when included, a local user installer:

- `NDIM Engine Runtime/Launch NDIM Engine.cmd`
- `NDIM Engine Setup.exe`

Double-click `Launch NDIM Engine.cmd` to start the NDIM launcher. The launcher uses the bundled Python runtime, starts a local FastAPI backend, opens the NDIM workflow UI in the default browser, and stores research data in the OS data folder.

Double-click `NDIM Engine Setup.exe` to install the bundled runtime folder into the current user's local Programs folder and create a Start Menu shortcut. The installer does not require admin rights.

The standalone executable bundles:

- backend application code
- integrated workflow UI
- manual route
- stress-test guide
- `stress_test_corpus/` CSV and TXT files

Local data is stored outside the executable:

- Windows: `%APPDATA%\NDIM Engine`
- macOS: `~/Library/Application Support/NDIM Engine`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/ndim-engine`

The packaged executable uses deterministic local fallbacks when optional heavy analytics packages such as Torch/Pyro are not bundled.

No separate Python, Node, npm, pip, or requirements installation is needed for the Windows runtime package.

For public distribution, upload `NDIM Engine Setup.exe` and `NDIM-Engine-Windows-Portable.zip` as separate GitHub Release assets.
