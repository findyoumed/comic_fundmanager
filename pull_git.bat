@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "EXPECTED=https://github.com/findyoumed/comic_fundmanager.git"
set "REMOTE="

echo ==========================================
echo   Pull - findyoumed/comic_fundmanager
echo   Repository: %CD%
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
  echo This helper only pulls into the main branch. Current branch: !BRANCH!
  goto ERROR
)
set "DIRTY="
for /f "delims=" %%S in ('git status --porcelain 2^>nul') do set "DIRTY=1"
if defined DIRTY (
  echo Local changes are present. Commit or otherwise handle them before pulling.
  goto ERROR
)
git ls-remote --exit-code --heads origin main >nul 2>&1
if errorlevel 1 (
  echo Remote main branch was not found or could not be reached.
  goto ERROR
)
git pull --ff-only origin main
if errorlevel 1 goto ERROR
echo Pull completed.
goto END
:ERROR
echo Pull failed. Check the repository, branch, local changes, network, and GitHub credentials.
:END
popd
pause
