@echo off
setlocal

rem Puts the build instructions where GitHub looks for them.
rem
rem It creates a folder named .github\workflows and copies deploy-workflow.yml
rem into it as deploy.yml. Explorer will not let you make a folder whose name
rem starts with a dot, which is the only reason this exists.
rem
rem It writes one file and creates one folder inside this project. It changes
rem nothing else, on this computer or on GitHub. To read what is about to be
rem copied, open deploy-workflow.yml in Notepad first.

cd /d "%~dp0"

if not exist "deploy-workflow.yml" (
  echo deploy-workflow.yml is missing from this folder, so there is nothing to copy.
  goto fail
)

if not exist ".github\workflows" mkdir ".github\workflows"
if errorlevel 1 goto fail

copy /y "deploy-workflow.yml" ".github\workflows\deploy.yml" >nul
if errorlevel 1 goto fail

if not exist ".github\workflows\deploy.yml" goto fail

echo Done. GitHub will now find the build instructions at
echo   .github\workflows\deploy.yml
echo.
echo Next: first-push.bat
echo.
pause
exit /b 0

:fail
echo.
echo Could not write the file. Nothing was changed.
pause
exit /b 1
