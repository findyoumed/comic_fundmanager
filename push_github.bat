@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "EXPECTED=https://github.com/findyoumed/comic_fundmanager.git"
set "REMOTE="

echo ==========================================
echo   Push - findyoumed/comic_fundmanager
echo   Repository: %CD%
echo   Branch: main
echo ==========================================
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto ERROR
for /f "delims=" %%R in ('git remote get-url origin 2^>nul') do set "REMOTE=%%R"
if /i not "!REMOTE!"=="!EXPECTED!" (
  echo Expected origin: !EXPECTED!
  echo Configured origin: !REMOTE!
  goto ERROR
)
for /f "delims=" %%B in ('git branch --show-current 2^>nul') do set "BRANCH=%%B"
if /i not "!BRANCH!"=="main" (
  echo This helper only pushes the main branch. Current branch: !BRANCH!
  goto ERROR
)

git status --short
set "MSG="
set /p "MSG=Commit message if there are changes (blank uses default): "
if not defined MSG set "MSG=Update project files"
git add -A
if errorlevel 1 goto ERROR
git diff --cached --stat
git diff --cached --quiet
if errorlevel 1 (
  echo.
  choice /c YN /n /m "Commit all staged changes with message '!MSG!'? [Y/N] "
  if errorlevel 2 goto CANCEL
  git commit -m "!MSG!"
  if errorlevel 1 goto ERROR
) else (
  echo No local changes to commit; existing commits may still be pushed.
)

echo.
choice /c YN /n /m "Push main to origin now? [Y/N] "
if errorlevel 2 goto CANCEL
git ls-remote --exit-code --heads origin main >nul 2>&1
if errorlevel 1 (
  echo Remote main is absent or unreachable; attempting initial push.
) else (
  git pull --ff-only origin main
  if errorlevel 1 goto ERROR
)
git push -u origin main
if errorlevel 1 goto ERROR
echo Push completed successfully.
goto END
:CANCEL
echo Operation canceled. Any commit already created remains local.
goto END
:ERROR
echo Operation failed. Check repository, branch, conflicts, network, and GitHub credentials.
:END
popd
pause
