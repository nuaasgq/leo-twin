@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\smoke_runtime_control_cycle.ps1"
if errorlevel 1 pause
