@echo off
REM [LOG: 20261114_1529]
chcp 65001 >nul
setlocal EnableExtensions DisableDelayedExpansion
set "MODE="
if /i "%~1"=="--check" set "MODE=-Check"
if /i "%~1"=="--dry-run" set "MODE=-Check"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\push_github.ps1" %MODE%
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
  echo.
  echo Push failed. See the failed step above.
  if not defined MODE pause
)
exit /b %RESULT%
