@echo off
setlocal
cd /d "%~dp0"
echo EverLeaf responsive login background test
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Make-Responsive-Login.ps1" -MapPath "%CD%\Map.wz" -TargetWidth 1920
if errorlevel 1 (
  echo.
  echo Responsive login patch FAILED. Your original Map.wz was not replaced unless the rebuild fully verified.
  pause
  exit /b 1
)
echo.
echo Patch complete. Start EverLeaf with the test launcher and try 800x600 through 1920x1080.
pause
