@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   GitHub Push - findyoumed/comic_fund
echo   Repository: %CD%
echo   Scope: ALL files and folders
echo ==========================================
for /f "delims=" %%R in ('git remote get-url origin 2^>nul') do set "REMOTE=%%R"
if /i not "!REMOTE!"=="https://github.com/findyoumed/comic_fund.git" (
  echo Unexpected or missing origin: !REMOTE!
  goto ERROR
)
git status --short
set /p MSG=Commit message (blank uses default): 
if not defined MSG set "MSG=Update all project files"
echo.
echo This will stage every file and folder, including PDFs and source images.
set "CONFIRM=Y"
set /p "CONFIRM=Commit all changes and push to origin/main [Y/n]: "
if /i not "!CONFIRM!"=="Y" goto CANCEL
git add -A
if errorlevel 1 goto ERROR
git diff --cached --quiet
if not errorlevel 1 (
  echo No local changes to commit; pushing existing commits.
) else (
  git commit -m "!MSG!"
  if errorlevel 1 goto ERROR
)
git pull --ff-only origin main
if errorlevel 1 goto ERROR
git push -u origin main
if errorlevel 1 goto ERROR
echo All project files pushed successfully.
goto END
:CANCEL
echo Push canceled.
goto END
:ERROR
echo Operation failed. Check repository path, file size limits, network, and GitHub credentials.
:END
popd
pause
