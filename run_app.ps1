# PowerShell Script untuk menjalankan Face Recognition System
$Host.UI.RawUI.WindowTitle = "Insta360 Link 2 - Face Recognition System"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Face Recognition System..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "✗ Virtual environment tidak ditemukan!" -ForegroundColor Red
    Write-Host "Jalankan setup_environment.ps1 terlebih dahulu" -ForegroundColor Red
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}

# Activate virtual environment
Write-Host "Mengaktifkan virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "✗ main.py tidak ditemukan!" -ForegroundColor Red
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}

# Run the application
Write-Host "Menjalankan aplikasi..." -ForegroundColor Green
python main.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Aplikasi dihentikan." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Tekan Enter untuk keluar"