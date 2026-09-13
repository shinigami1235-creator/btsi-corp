@echo off
setlocal enabledelayedexpansion

rem Day to day: check, then push. GitHub builds and publishes.
rem
rem The checks here are the same ones the deploy runs, done first so a mistake
rem costs you ten seconds instead of a failed build and an email.

cd /d "%~dp0"

git --version >nul 2>&1
if errorlevel 1 (
  echo Git not found. Install it from git-scm.com and run this again.
  goto fail
)

set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python --version >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python not found. Install it from python.org and run this again.
  goto fail
)

if not exist ".git" (
  echo This folder is not connected to GitHub yet. Run first-push.bat once.
  goto fail
)

echo [1/4] Check the data
call %PY% validate.py
if errorlevel 1 goto fail

echo.
echo [2/4] Check the writing
call %PY% lint.py

echo.
echo [3/4] Build and check the links
call %PY% build.py
if errorlevel 1 goto fail
call %PY% check-links.py
if errorlevel 1 goto fail

echo.
echo [4/4] Push
git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo      nothing has changed since the last push
  goto done
)
set /p MSG="What changed? (enter for 'Update site') "
if "!MSG!"=="" set "MSG=Update site"
git commit -m "!MSG!" >nul
if errorlevel 1 goto fail
git push
if errorlevel 1 goto fail

echo.
echo Pushed. GitHub is building it now, which takes about a minute and a half.
echo Watch it: https://github.com/shinigami1235-creator/btsi-corp/actions

:done
echo.
echo https://shinigami1235-creator.github.io/btsi-corp/
echo.
pause
exit /b 0

:fail
echo.
echo Stopped. Nothing was pushed.
pause
exit /b 1
