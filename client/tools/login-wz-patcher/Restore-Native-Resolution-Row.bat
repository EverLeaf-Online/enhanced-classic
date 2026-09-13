@echo off
setlocal
cd /d "%~dp0"
if not exist "UI.wz.pre-resolution-row.bak" (
  echo No UI.wz.pre-resolution-row.bak backup was found.
  pause
  exit /b 1
)
if exist "UI.wz" del /f /q "UI.wz"
move /y "UI.wz.pre-resolution-row.bak" "UI.wz" >nul
echo Original UI.wz restored.
pause
