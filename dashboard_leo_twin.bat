@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" start -OpenSurface dashboard
if errorlevel 1 pause
