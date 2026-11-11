@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Restore tracked files from a commit
echo   Repository: %CD%
echo ==========================================
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto ERROR
git log -15 --oneline --all
if errorlevel 1 goto ERROR
set "HASH="
set /p "HASH=Commit hash to restore (blank cancels): "
if not defined HASH goto CANCEL
git cat-file -e "!HASH!^{commit}" 2>nul
if errorlevel 1 goto ERROR

echo.
echo WARNING: tracked files in the working tree will be overwritten.
echo Staged changes and untracked files will be left untouched.
choice /c YN /n /m "Restore tracked files from !HASH!? [Y/N] "
if errorlevel 2 goto CANCEL
git restore --source="!HASH!" --worktree -- .
if errorlevel 1 goto ERROR
echo Tracked working files restored from !HASH!.
goto END
:CANCEL
echo Restore canceled.
goto END
:ERROR
echo Restore failed. Check the commit hash and repository status.
:END
popd
pause
