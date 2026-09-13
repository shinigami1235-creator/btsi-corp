@echo off
setlocal
cd /d "%~dp0"

set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python --version >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python not found. Install it from python.org and run this again.
  pause
  exit /b 1
)

%PY% -c "import PIL" >nul 2>&1
if errorlevel 1 (
  echo Installing Pillow so the photographs get resized.
  %PY% -m pip install --quiet pillow
)

%PY% fetch-photos.py
echo.
echo Next: ship.bat
pause
