@echo off
REM Quick Start Script untuk PPE Compliance System
REM Menggunakan Insta360 Link 2

echo ============================================================
echo   PPE COMPLIANCE MONITORING SYSTEM
echo   Quick Start dengan Insta360 Link 2
echo ============================================================
echo.

REM Aktifkan virtual environment
echo [1/3] Aktivasi virtual environment...
call venv\Scripts\activate.bat

REM Check dependencies
echo.
echo [2/3] Cek dependencies...
python -c "import ultralytics" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: ultralytics belum terinstall!
    echo Sistem akan berjalan dalam SIMULATION MODE
    echo.
    echo Untuk install dependencies lengkap, jalankan:
    echo   pip install -r requirements_ppe.txt
    echo.
    pause
)

REM Run sistem
echo.
echo [3/3] Menjalankan PPE Compliance System...
echo.
python ppe_system_main.py

pause
