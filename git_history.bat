@echo off
setlocal
pushd "%~dp0" || exit /b 1

echo ==========================================
echo   Git History - findyoumed/comic_fund
echo   Repository: %CD%
echo ==========================================
git log -20 --oneline --decorate
if errorlevel 1 goto ERROR
powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; if ([System.Windows.Forms.MessageBox]::Show('Open searchable commit history?', 'Git History', 'YesNo', 'Question') -eq 'Yes') { git log --oneline --all | Out-GridView -Title 'comic_fund Git History' }"
goto END
:ERROR
echo Git history could not be read. Check that this file is in the repository root.
:END
popd
pause
