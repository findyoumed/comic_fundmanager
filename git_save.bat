@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Save project changes locally
echo   Repository: %CD%
echo ==========================================
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto ERROR
git status --short
set "MSG="
set /p "MSG=Commit message (blank uses default): "
if not defined MSG set "MSG=Update project files"
set "CONFIRM=Y"
set /p "CONFIRM=Stage all changes and create local commit? [Y/n]: "
if /i "!CONFIRM!"=="N" goto CANCEL
if /i not "!CONFIRM!"=="Y" goto CANCEL
git add -A
if errorlevel 1 goto ERROR
git diff --cached --quiet
if not errorlevel 1 (
  echo No changes to save.
  goto END
)
git diff --cached --stat
git commit -m "!MSG!"
if errorlevel 1 goto ERROR
echo Changes committed locally. Run push_github.bat when ready to upload them.
goto END
:CANCEL
echo Save canceled.
goto END
:ERROR
echo Save failed. Check Git status and repository permissions.
:END
popd
pause
