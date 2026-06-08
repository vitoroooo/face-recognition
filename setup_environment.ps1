# PowerShell Setup Script untuk Insta360 Link 2 Face Recognition
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Insta360 Link 2 Face Recognition Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python tidak ditemukan!" -ForegroundColor Red
    Write-Host "Silakan install Python dari https://python.org" -ForegroundColor Red
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}

Write-Host ""
Write-Host "[2/5] Membuat Virtual Environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment sudah ada, melewati pembuatan..." -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERROR: Gagal membuat virtual environment." -ForegroundColor Red
        Read-Host "Tekan Enter untuk keluar"
        exit 1
    }
    Write-Host "✓ Virtual environment berhasil dibuat" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/5] Mengaktifkan Virtual Environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "[4/5] Menginstall Dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ ERROR: Gagal menginstall dependencies." -ForegroundColor Red
    Write-Host "Coba jalankan manual: pip install opencv-python face-recognition numpy" -ForegroundColor Red
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}
Write-Host "✓ Dependencies berhasil diinstall" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Membuat folder faces jika belum ada..." -ForegroundColor Yellow
if (-not (Test-Path "faces")) {
    New-Item -ItemType Directory -Name "faces" | Out-Null
    Write-Host "✓ Folder 'faces' dibuat." -ForegroundColor Green
} else {
    Write-Host "✓ Folder 'faces' sudah ada." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Selesai!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah selanjutnya:" -ForegroundColor Yellow
Write-Host "1. Letakkan foto referensi di folder 'faces/'" -ForegroundColor White
Write-Host "2. Jalankan: python main.py" -ForegroundColor White
Write-Host "   atau: .\run_app.ps1" -ForegroundColor White
Write-Host ""
Read-Host "Tekan Enter untuk keluar"