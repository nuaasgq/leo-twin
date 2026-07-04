@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" stop
if errorlevel 1 pause
