@echo off
title 🏢 OFFICE ATTENDANCE - Face Recognition System

echo ========================================
echo  🏢 PROFESSIONAL OFFICE ATTENDANCE
echo ========================================
echo.
echo 🚀 Enterprise Features:
echo    📷 Insta360 Link 2 Auto-Priority
echo    👁️  Multi-Biometric (Face + Eye Detection)
echo    🎯 Professional Accuracy Standards
echo    ⚡ Real-time Processing
echo    🔒 Office-Grade Security
echo.

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Run setup_environment.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "main_office_attendance.py" (
    echo ❌ main_office_attendance.py not found!
    pause
    exit /b 1
)

echo 🎥 Starting OFFICE ATTENDANCE SYSTEM...
echo Sistem akan otomatis prioritaskan Insta360 Link 2
echo Professional threshold untuk akurasi kantor
echo.

python main_office_attendance.py

echo.
echo ========================================
echo  Office Attendance System Terminated
echo ========================================
echo.
echo 💡 Professional Tips:
echo    - System otomatis pilih Insta360 Link 2
echo    - Threshold 0.45 (standar industri)
echo    - Multi-biometric validation aktif
echo    - Tekan 'S/N/R' untuk adjust security level
pause