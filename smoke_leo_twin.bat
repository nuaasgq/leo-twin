@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\smoke_runtime_health.ps1"
if errorlevel 1 pause
