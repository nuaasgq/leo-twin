@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_disposable_acceptance.ps1" %*
exit /b %ERRORLEVEL%
