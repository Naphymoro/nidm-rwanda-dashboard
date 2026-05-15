@echo off
setlocal
set "APP_ROOT=%~dp0"
cd /d "%APP_ROOT%"
start "NDIM Engine" "%APP_ROOT%runtime\pythonw.exe" "%APP_ROOT%desktop\ndim_desktop.py"
endlocal
