@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\collect_operator_diagnostics.ps1"
if errorlevel 1 pause
