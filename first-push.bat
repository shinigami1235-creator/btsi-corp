@echo off
setlocal

rem Run this once, to move from the old arrangement to the new one.
rem
rem Until now this folder held the source and a second folder, btsi-corp-repo,
rem held the built pages that were pushed. From now on there is one repository
rem and it holds the source, since GitHub builds the pages itself. Someone can
rem then edit the site without this computer being involved.
rem
rem WHAT IT CHANGES
rem   On GitHub: everything in the btsi-corp repository is replaced by this
rem   folder. What is there now is the built site, which GitHub rebuilds from
rem   this folder within two minutes, so nothing in it is lost for good.
rem   On this computer: it creates a .git folder here. Your files are not
rem   touched, and btsi-corp-repo next door is not touched.

cd /d "%~dp0"

git --version >nul 2>&1
if errorlevel 1 (
  echo Git is not installed. Get it from git-scm.com, then run this again.
  goto fail
)

rem Without this file GitHub has no build instructions, so the push would
rem succeed and the site would go blank the moment Pages is switched over.
if not exist ".github\workflows\deploy.yml" (
  echo The build instructions are missing.
  echo.
  echo   Run setup-workflow.bat first, then run this again.
  goto fail
)

rem Git refuses to commit until it knows who is committing, and the error it
rem gives for that looks like a different problem entirely.
for /f "delims=" %%N in ('git config user.name 2^>nul') do set "GITNAME=%%N"
for /f "delims=" %%E in ('git config user.email 2^>nul') do set "GITMAIL=%%E"
if not defined GITNAME goto whoareyou
if not defined GITMAIL goto whoareyou

echo This replaces everything in
echo   https://github.com/shinigami1235-creator/btsi-corp
echo with this folder. That repository currently holds the built site, which
echo GitHub is about to rebuild from here.
echo.
echo To keep a copy first: open the repository on GitHub, press the green Code
echo button, Download ZIP. Otherwise there is nothing there to keep.
echo.
echo One setting has to change before anything will publish, now or straight
echo after:
echo.
echo   On GitHub: the repository, Settings, Pages,
echo   under "Build and deployment" set Source to "GitHub Actions".
echo.
echo   It is currently "Deploy from a branch". Left alone, the push succeeds
echo   and the site goes blank, because the branch no longer holds any pages.
echo.
set /p GO="Type yes to continue: "
if /i not "%GO%"=="yes" goto stop

if not exist ".git" (
  git init -b main
  if errorlevel 1 goto fail
  git remote add origin https://github.com/shinigami1235-creator/btsi-corp.git
  if errorlevel 1 goto fail
) else (
  git branch -M main
)

git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo Nothing to commit, which means this folder has already been pushed.
  echo Use ship.bat from now on.
  goto fail
)

git commit -m "Build the site from source on GitHub, and add the website editor"
if errorlevel 1 goto fail

git push -u --force origin main
if errorlevel 1 goto pushfail

echo.
echo Pushed. Now, if you have not already:
echo   Settings, Pages, Source: "GitHub Actions".
echo.
echo Then watch the build:
echo   https://github.com/shinigami1235-creator/btsi-corp/actions
echo.
echo After it goes green:
echo   the site   https://shinigami1235-creator.github.io/btsi-corp/
echo   the editor https://shinigami1235-creator.github.io/btsi-corp/admin/
echo.
echo From now on, use ship.bat.
echo.
pause
exit /b 0

:whoareyou
echo Git does not know who you are yet, and will not commit until it does.
echo.
echo Run these two lines, with your own name and the email on your GitHub
echo account, then run this again:
echo.
echo   git config --global user.name "Your Name"
echo   git config --global user.email "you@example.com"
echo.
pause
exit /b 1

:pushfail
echo.
echo The push failed. The usual reason is that GitHub wants you to sign in:
echo a browser window or a username and password prompt should have appeared.
echo Nothing on GitHub was changed. Run this again to retry.
pause
exit /b 1

:stop
echo Nothing done.
pause
exit /b 0

:fail
echo.
echo Stopped. Nothing was pushed.
pause
exit /b 1
