@echo off
setlocal
cd /d "%~dp0"
if not exist "Map.wz.pre-responsive-login.bak" (
  echo No responsive-login Map.wz backup was found.
  pause
  exit /b 1
)
if exist "Map.wz" del /f /q "Map.wz"
move /y "Map.wz.pre-responsive-login.bak" "Map.wz" >nul
if errorlevel 1 (
  echo Restore FAILED.
  pause
  exit /b 1
)
echo Original Map.wz restored.
pause
