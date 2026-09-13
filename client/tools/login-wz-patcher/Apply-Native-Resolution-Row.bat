@echo off
setlocal
cd /d "%~dp0"
echo EverLeaf native System Options Resolution row
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Make-Native-Resolution-Row.ps1" -UIPath "%CD%\UI.wz"
if errorlevel 1 (
  echo.
  echo Resolution-row patch FAILED. Your original UI.wz was not replaced unless the rebuild fully verified.
  pause
  exit /b 1
)
echo.
echo Done. Launch EverLeaf and open System Options.
pause
