@echo off
echo ========================================
echo Face Recognition Web Dashboard
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements_web.txt
)

echo.
echo Starting Web Dashboard...
echo Dashboard will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python web_dashboard.py

pause
