@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Restore ALL files from a commit
echo   Repository: %CD%
echo ==========================================
git log -15 --oneline --all
if errorlevel 1 goto ERROR
set /p HASH=Commit hash to restore (blank cancels): 
if not defined HASH goto CANCEL
git cat-file -e "!HASH!^{commit}" 2>nul
if errorlevel 1 goto ERROR

echo WARNING: this overwrites tracked files throughout the repository.
choice /c YN /m "Restore all files from !HASH!"
if errorlevel 2 goto CANCEL
git restore --source=!HASH! --worktree -- .
if errorlevel 1 goto ERROR
echo All tracked files restored. Untracked files are left untouched.
goto END
:CANCEL
echo Restore canceled.
goto END
:ERROR
echo Restore failed. Check the commit hash and repository status.
:END
popd
pause
