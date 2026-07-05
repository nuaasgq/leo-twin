@echo off
setlocal
echo.
echo LEO-Twin / SEES Launcher
echo =======================
echo 1. Start console
echo 2. Start dashboard
echo 3. Status
echo 4. Smoke health check
echo 5. Restart console
echo 6. Stop services
echo 7. Product acceptance verification (fast)
echo 8. Product acceptance verification (with build)
echo.
choice /C 12345678 /N /M "Select an action [1-8]: "
if errorlevel 8 goto acceptance_full
if errorlevel 7 goto acceptance
if errorlevel 6 goto stop
if errorlevel 5 goto restart
if errorlevel 4 goto smoke
if errorlevel 3 goto status
if errorlevel 2 goto dashboard
if errorlevel 1 goto start

:start
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" start
goto end

:dashboard
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" start -OpenSurface dashboard
goto end

:status
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" status
goto end

:smoke
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\smoke_runtime_health.ps1"
goto end

:restart
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" restart
goto end

:stop
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sees_launcher.ps1" stop
goto end

:acceptance
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\verify_product_acceptance.ps1" -SkipBuild
goto end

:acceptance_full
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\verify_product_acceptance.ps1"
goto end

:end
if errorlevel 1 pause
