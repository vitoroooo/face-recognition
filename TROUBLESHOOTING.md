# 🔧 Troubleshooting Face Recognition

## ❌ **Problem: "Unknown" - Face tidak dikenali**

### **Root Cause Analysis:**
1. **Face Detection Issue:** Haar Cascade tidak sensitif untuk kamera laptop
2. **Template Matching Limitation:** OpenCV template matching kurang akurat
3. **Lighting Conditions:** Pencahayaan kamera laptop berbeda dengan foto referensi

### **Solutions (Step by Step):**

## 🎯 **Solution 1: Gunakan Insta360 Link 2**

**Kamera laptop vs Insta360 Link 2:**
- Laptop: 640x480, pencahayaan terbatas
- Insta360: 1280x720, auto-exposure, better lens

**Cara memastikan Insta360 Link 2 terpakai:**
1. Colok Insta360 Link 2 via USB
2. Tutup semua aplikasi kamera lain
3. Jalankan: `python test_camera.py`
4. Pilih indeks dengan resolusi 1280x720

## 🎯 **Solution 2: Optimasi Face Detection**

Edit `config.py`:
```python
# Lebih sensitif untuk deteksi wajah
FRAME_RESIZE = 0.5        # Frame lebih besar
DETECTION_FREQUENCY = 1   # Deteksi setiap frame
```

## 🎯 **Solution 3: Perbaiki Foto Referensi**

**Current photo issues:**
- 3 wajah terdeteksi di foto `vito.jpeg`
- Face recognition bingung mana wajah yang benar

**Fix:**
1. Buat foto baru dengan 1 wajah saja
2. Crop foto existing ke wajah utama
3. Nama file lebih spesifik: `vito_main.jpg`

## 🎯 **Solution 4: Install Face Recognition Library yang Proper**

**Current issue:** `face_recognition_models` tidak terinstall dengan benar

**Fix:**
```cmd
.\venv\Scripts\Activate.ps1
pip uninstall face-recognition face-recognition-models -y
pip install cmake
pip install dlib
pip install face-recognition
```

## 🎯 **Solution 5: Alternative - Manual Face Crop**

Buat foto referensi yang sudah di-crop untuk face yang tepat.