@echo off
setlocal
cd /d "%~dp0dist"
set "PORT=8000"

py -3 --version >nul 2>&1 && goto usepy
python --version >nul 2>&1 && goto usepython
node --version >nul 2>&1 && goto usenode
goto nohost

:usepy
call :openbrowser
py -3 -m http.server %PORT%
goto :eof

:usepython
call :openbrowser
python -m http.server %PORT%
goto :eof

:usenode
call :openbrowser
npx -y serve -l %PORT% .
goto :eof

:openbrowser
start "" cmd /c "timeout /t 2 >nul & start "" http://localhost:%PORT%/"
echo Serving dist on http://localhost:%PORT%/
echo Close this window to stop.
exit /b

:nohost
echo Needs Python or Node. Install Python from python.org and run this again.
pause
