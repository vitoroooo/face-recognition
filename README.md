# 📷 Insta360 Link 2 - Real-Time Face Recognition System

Sistem Pengenalan Wajah (*Real-Time Face Recognition*) cerdas yang memanfaatkan aliran video mentah (*raw video stream*) dari webcam premium **Insta360 Link 2** menggunakan Python, OpenCV, dan Dlib (Deep Learning).

Sistem ini memadukan kemampuan *hardware auto-tracking* (gimbal) bawaan Insta360 Link 2 dengan logika AI lokal untuk mengidentifikasi identitas spesifik wajah yang tertangkap kamera secara *real-time*.

---

## 🛠️ Komponen & Arsitektur Sistem

Sistem ini bekerja dengan memadukan tiga pilar utama:
1. **Insta360 Link 2 (Hardware):** Bertindak sebagai sensor kamera input. Fitur *AI Gimbal Tracking* bawaan perangkat keras akan menjaga wajah target tetap berada di tengah *frame* (*centered*).
2. **Face Recognition & Dlib (AI Engine):** Melakukan ekstraksi titik landmark wajah (*face embedding*) dan mencocokkannya dengan database gambar lokal berdasarkan kalkulasi jarak geometri (*face distance*).
3. **OpenCV & Python (Logic Layer):** Mengelola *stream* video via USB, melakukan *downscaling frame* (untuk menjaga FPS tetap tinggi), serta memvisualisasikan kotak pelacak dan label nama di layar.

---

## 📂 Struktur Direktori Proyek

Pastikan struktur folder di dalam workspace Anda tersusun seperti ini:

```text
📂 pengembangan face recognition/
├── 📂 faces/
│   └── vito.jpeg          <-- Foto referensi wajah Anda (format .jpg/.png/.jpeg)
├── 📂 venv/               <-- Virtual Environment Python (Python 3.12)
├── main.py                <-- Skrip utama aplikasi
└── README.md              <-- Dokumentasi ini
```

---

## 📦 Dependencies & Installation

### 1. Setup Virtual Environment
```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment (Windows)
venv\Scripts\activate

# Aktifkan virtual environment (Linux/Mac)
source venv/bin/activate
```

### 2. Install Required Libraries
Pastikan Anda menginstall library berikut di virtual environment:

```bash
pip install opencv-python
pip install face-recognition
pip install numpy
```

**Catatan Penting:** 
- Library `face-recognition` memerlukan `dlib` yang akan otomatis terinstall
- Pada Windows, mungkin perlu install Microsoft Visual C++ Build Tools jika ada error kompilasi

---

## ⚙️ Konfigurasi Parameter

Sistem dapat disesuaikan melalui konstanta berikut di `main.py`:

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `TOLERANCE` | `0.5` | Tingkat sensitivitas pengenalan (0.0-1.0, semakin kecil semakin ketat) |
| `FRAME_RESIZE` | `0.25` | Skala resize frame untuk performa (0.1-1.0, semakin kecil semakin cepat) |
| `CAMERA_INDEX` | `0` | Indeks kamera (biasanya 0, coba 1-2 jika tidak terdeteksi) |

### Contoh Penyesuaian:
```python
TOLERANCE = 0.4        # Lebih ketat dalam pengenalan wajah
FRAME_RESIZE = 0.15    # Frame lebih kecil untuk performa lebih cepat
CAMERA_INDEX = 1       # Gunakan kamera dengan indeks 1
```

---

## 🚀 Cara Menjalankan

### 1. Persiapan Database Wajah
- Letakkan foto referensi wajah di folder `faces/`
- Format yang didukung: `.jpg`, `.png`, `.jpeg`
- Nama file akan menjadi nama yang ditampilkan (contoh: `vito.jpeg` → "Vito")
- **Tips:** Gunakan foto dengan pencahayaan yang baik dan wajah menghadap kamera

### 2. Jalankan Aplikasi
```bash
# Pastikan virtual environment aktif
python main.py
```

### 3. Menggunakan Sistem
- Jendela video akan terbuka menampilkan feed dari Insta360 Link 2
- Wajah yang dikenali akan ditandai dengan **kotak hijau** dan nama
- Wajah tidak dikenal akan ditandai dengan **kotak merah** dan label "Unknown"
- Tekan tombol **'q'** untuk menghentikan aplikasi

---

## 🎯 Fitur Utama

### ✅ **Real-Time Face Detection**
- Deteksi wajah langsung dari video stream
- Optimisasi performa dengan frame resizing
- Support multiple faces dalam satu frame

### ✅ **Face Recognition Database**
- Database lokal berbasis file gambar
- Auto-loading semua gambar dari folder `faces/`
- Ekstraksi face encoding otomatis

### ✅ **Visual Feedback**
- Bounding box berwarna (hijau = dikenal, merah = tidak dikenal)
- Label nama real-time
- Interface yang clean dan informatif

### ✅ **Hardware Integration**
- Optimized untuk Insta360 Link 2
- Support DirectShow (Windows) untuk koneksi stabil
- Compatible dengan webcam lain sebagai fallback

---

## 🔧 Troubleshooting

### ❌ **Kamera tidak terdeteksi**
```
Error: Kamera dengan indeks 0 tidak ditemukan
```
**Solusi:**
- Pastikan Insta360 Link 2 terhubung via USB
- Coba ganti `CAMERA_INDEX` ke 1 atau 2 di `main.py`
- Restart aplikasi setelah mencolok kamera
- Pastikan driver Insta360 Link 2 sudah terinstall

### ❌ **Performance lambat / FPS rendah**
```
Aplikasi berjalan lambat atau lag
```
**Solusi:**
- Turunkan nilai `FRAME_RESIZE` (contoh: dari 0.25 ke 0.15)
- Pastikan hanya ada 1 foto per person di folder `faces/`
- Tutup aplikasi lain yang menggunakan kamera
- Gunakan foto referensi dengan resolusi sedang (tidak perlu 4K)

### ❌ **Face recognition tidak akurat**
```
Wajah sering tidak dikenali atau salah identifikasi
```
**Solusi:**
- Sesuaikan nilai `TOLERANCE` (coba 0.4 untuk lebih ketat, 0.6 untuk lebih longgar)
- Gunakan foto referensi dengan kualitas baik dan pencahayaan cukup
- Pastikan wajah di foto referensi menghadap kamera
- Hindari foto dengan kacamata gelap atau masker

### ❌ **Error instalasi library**
```
ERROR: Microsoft Visual C++ 14.0 is required
```
**Solusi (Windows):**
- Download dan install Microsoft Visual C++ Build Tools
- Atau install Visual Studio Community dengan C++ workload
- Restart command prompt dan coba install ulang

---

## 🎛️ Kustomisasi Lanjutan

### Menambah Wajah Baru
1. Tambahkan foto baru ke folder `faces/`
2. Restart aplikasi (database akan reload otomatis)
3. Foto baru akan langsung dikenali

### Mengubah Tampilan
Edit bagian visualization di `main.py`:
```python
# Ubah warna kotak
color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)  # Hijau/Merah
# Bisa diganti dengan warna lain (B, G, R format)

# Ubah font dan ukuran text
cv2.putText(frame, name, (left + 10, bottom - 8), 
           cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
```

### Performance Tuning
```python
# Untuk sistem yang powerful
FRAME_RESIZE = 0.5    # Frame lebih besar, hasil lebih akurat
TOLERANCE = 0.4       # Pengenalan lebih ketat

# Untuk sistem yang terbatas
FRAME_RESIZE = 0.15   # Frame lebih kecil, performa lebih cepat
TOLERANCE = 0.6       # Pengenalan lebih longgar
```

---

## 📋 Spesifikasi Sistem

### **Minimum Requirements:**
- Python 3.8+
- RAM: 4GB
- CPU: Dual Core 2.0GHz
- USB 2.0 port
- Webcam compatible (Insta360 Link 2 recommended)

### **Recommended:**
- Python 3.10+
- RAM: 8GB+
- CPU: Quad Core 2.5GHz+
- USB 3.0 port
- Insta360 Link 2 dengan AI tracking

### **Tested Platforms:**
- ✅ Windows 10/11
- ✅ macOS 12+
- ✅ Ubuntu 20.04+

---

## 🔮 Roadmap & Future Features

### **Version 2.0 (Planned)**
- [ ] Web interface untuk monitoring
- [ ] Database SQLite untuk logging
- [ ] Multiple camera support
- [ ] Face recognition confidence score display
- [ ] Real-time training mode

### **Version 3.0 (Planned)**
- [ ] Cloud sync untuk face database
- [ ] Mobile app companion
- [ ] Advanced analytics dashboard
- [ ] Integration dengan sistem security

---

## 📄 License

Proyek ini dibuat untuk tujuan pembelajaran dan pengembangan. Silakan gunakan dan modifikasi sesuai kebutuhan Anda.

---

## 👤 Author

**Vito** - Face Recognition System Developer

Dibuat dengan ❤️ menggunakan Python, OpenCV, dan Insta360 Link 2