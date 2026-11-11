@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Save ALL project files locally
echo   Repository: %CD%
echo ==========================================
git status --short
set /p MSG=Commit message (blank uses default): 
if not defined MSG set "MSG=Update all project files"
choice /c YN /m "Stage every file and folder, then commit"
if errorlevel 2 goto CANCEL
git add -A
if errorlevel 1 goto ERROR
git diff --cached --quiet
if not errorlevel 1 (
  echo No changes to save.
  goto END
)
git commit -m "!MSG!"
if errorlevel 1 goto ERROR
echo All changes committed locally. Run push_github.bat to upload them.
goto END
:CANCEL
echo Save canceled.
goto END
:ERROR
echo Save failed. Check Git status and repository permissions.
:END
popd
pause
