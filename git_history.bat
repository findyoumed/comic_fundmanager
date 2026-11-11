@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Git History - comic_fundmanager
echo   Repository: %CD%
echo ==========================================
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto ERROR
git log -20 --oneline --decorate
if errorlevel 1 goto ERROR
echo.
powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; if ([System.Windows.Forms.MessageBox]::Show('Open searchable commit history?', 'Git History', 'YesNo', 'Question') -eq 'Yes') { git log --oneline --all | Out-GridView -Title 'comic_fundmanager Git History' }"
goto END
:ERROR
echo Git history could not be read. Check that this file is in the repository root and that commits exist.
:END
popd
pause
