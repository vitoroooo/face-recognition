@echo off
echo ========================================
echo  Insta360 Link 2 Face Recognition Setup
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan! 
    echo Silakan install Python dari https://python.org
    pause
    exit /b 1
)
echo Python detected: 
python --version

echo.
echo [2/5] Membuat Virtual Environment...
if exist "venv" (
    echo Virtual environment sudah ada, melewati pembuatan...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Gagal membuat virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo [3/5] Mengaktifkan Virtual Environment...
call venv\Scripts\activate.bat

echo.
echo [4/5] Menginstall Dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Gagal menginstall dependencies. Periksa koneksi internet.
    echo Coba jalankan: pip install opencv-python face-recognition numpy
    pause
    exit /b 1
)

echo.
echo [5/5] Membuat folder faces jika belum ada...
if not exist "faces" (
    mkdir faces
    echo Folder 'faces' dibuat.
) else (
    echo Folder 'faces' sudah ada.
)

echo.
echo ========================================
echo  Setup Selesai!
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Letakkan foto referensi di folder 'faces/'
echo 2. Jalankan: python main.py
echo    atau: .\run_app.bat
echo.
echo Tekan Enter untuk keluar...
pause > nul