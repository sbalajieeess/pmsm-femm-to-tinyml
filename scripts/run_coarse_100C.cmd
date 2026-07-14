@echo off
setlocal
cd /d "%~dp0\.."

if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv is missing. Run scripts\bootstrap_windows.ps1 first.
  exit /b 1
)

.venv\Scripts\python.exe scripts\run_femm_map.py ^
  --config configs\one_eighth_100C.toml ^
  --points examples\coarse_20point_map.csv ^
  --run-id coarse_20point_100C

endlocal
