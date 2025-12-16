@echo off
echo Starting Quant Analytics Dashboard...
echo Do not close this window.

:: Check Python
python --version
if %errorlevel% neq 0 (
    echo Python not found!
    pause
    exit /b
)

:: Install Requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Start Services in Background
start "Ingestion Service" /min python src/ingestion/binance_client.py
start "Resampling Engine" /min python src/analytics/core/resampler.py

:: Start Frontend
echo Starting Frontend...
streamlit run src/frontend/app.py

:: Cleanup on exit (This part is tricky in batch, user has to close windows manually)
echo.
echo Dashboard closed. Please close the other minimized windows manually.
pause
