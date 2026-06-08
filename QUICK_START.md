# 🚀 Quick Start Guide

## ✅ Status Setup Anda:
- ✅ Virtual environment: **BERHASIL**
- ✅ Dependencies: **TERINSTALL**
- ✅ Kamera test: **SUKSES**
- ✅ Kamera terdeteksi di: **Indeks 1 (1280x720 HD)**

## 🎯 Cara Menjalankan:

### 1️⃣ **Pastikan ada foto referensi**
```
📂 faces/
└── vito.jpeg  ✅ (sudah ada)
```

### 2️⃣ **Jalankan aplikasi**
Double-click: `run_app.bat`

Atau dari terminal:
```cmd
.\venv\Scripts\Activate.ps1
python main.py
```

## 🎮 **Kontrol saat running:**
- **Q** = Quit (keluar)
- **D** = Toggle debug mode
- **F** = Toggle FPS display

## ⚙️ **Konfigurasi sudah optimal:**
- Camera Index: **1** (Insta360 Link 2)
- Resolusi: **1280x720** (HD)
- Tolerance: **0.5** (balanced)

## 🔧 **Jika ada masalah:**

### Kamera tidak terdeteksi:
- Pastikan Insta360 Link 2 terhubung USB
- Coba restart aplikasi
- Check di config.py: `CAMERA_INDEX = 1`

### Performance lambat:
- Edit config.py: `FRAME_RESIZE = 0.15` (lebih kecil = lebih cepat)

### Face recognition tidak akurat:
- Edit config.py: `TOLERANCE = 0.4` (lebih ketat)

---

## 🎉 **Siap digunakan!**
Sistem Anda sudah setup dengan sempurna dan siap dijalankan!