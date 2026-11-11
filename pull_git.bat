@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Git Pull - findyoumed/comic_fund
echo   Repository: %CD%
echo ==========================================
for /f "delims=" %%R in ('git remote get-url origin 2^>nul') do set "REMOTE=%%R"
if /i not "%REMOTE%"=="https://github.com/findyoumed/comic_fund.git" (
  echo Unexpected or missing origin: %REMOTE%
  goto ERROR
)
git pull --ff-only origin main
if errorlevel 1 goto ERROR
echo Pull completed.
goto END
:ERROR
echo Pull failed. Check local changes, repository path, network, and GitHub credentials.
:END
popd
pause
