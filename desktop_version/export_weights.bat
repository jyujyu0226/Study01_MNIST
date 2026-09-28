@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py export_weights.py
) else (
  python export_weights.py
)
echo.
pause
