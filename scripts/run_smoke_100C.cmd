@echo off
setlocal
cd /d "%~dp0\.."

if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv is missing. Run powershell -ExecutionPolicy Bypass -File scripts\bootstrap_windows.ps1
  exit /b 1
)

.venv\Scripts\python.exe scripts\check_environment.py --config configs\one_eighth_100C.toml
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe scripts\run_femm_map.py ^
  --config configs\one_eighth_100C.toml ^
  --points examples\smoke_points.csv ^
  --run-id smoke_100C

endlocal
