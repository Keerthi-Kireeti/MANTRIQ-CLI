@echo off
setlocal
set SCRIPT_DIR=%~dp0
python -m mantriq.cli %*
endlocal
