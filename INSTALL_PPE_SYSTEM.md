# 🚀 Installation Guide - PPE Compliance System

## Panduan Lengkap Setup dari Awal sampai Running

---

## 📋 Prerequisites

### Hardware Requirements
- ✅ **Camera**: Insta360 Link 2 (atau webcam lain)
- ✅ **RAM**: Minimum 8GB (16GB recommended)
- ✅ **Storage**: 5GB free space
- ✅ **OS**: Windows 10/11

### Software Requirements
- ✅ **Python**: 3.8 - 3.12 (sudah installed ✓)
- ✅ **Git**: Untuk clone repo (optional)
- ✅ **Internet**: Untuk download dependencies

---

## ⚡ Quick Install (5 Menit)

### Langkah 1: Aktifkan Virtual Environment
```bash
cd "c:/Project vito/pengembangan face recognition"
.\venv\Scripts\activate
```

### Langkah 2: Install Dependencies
```bash
pip install -r requirements_ppe.txt
```

**Catatan**: Ini akan download ~2.5GB (termasuk PyTorch). Tunggu 5-10 menit.

### Langkah 3: Verifikasi Installation
```bash
python -c "import ultralytics; print('✓ ultralytics OK')"
python -c "import torch; print('✓ torch OK')"
python -c "import cv2; print('✓ opencv OK')"
python -c "import face_recognition; print('✓ face_recognition OK')"
```

### Langkah 4: Run System
```bash
# Method 1: Batch file
run_ppe_system.bat

# Method 2: Python direct
python ppe_system_main.py
```

✅ **DONE! System siap digunakan.**

---

## 📦 Detailed Installation

### Step 1: Persiapan Environment

**1.1 Check Python Version**
```bash
python --version
# Expected output: Python 3.8.x - 3.12.x
```

**1.2 Check Virtual Environment**
```bash
# Check jika venv sudah ada
dir venv

# Jika belum ada, create:
python -m venv venv
```

**1.3 Aktifkan Virtual Environment**
```bash
# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Jika sukses, akan muncul (venv) di prompt
```

### Step 2: Install Dependencies

**2.1 Update pip**
```bash
python -m pip install --upgrade pip
```

**2.2 Install PPE System Dependencies**
```bash
pip install -r requirements_ppe.txt
```

**Packages yang akan ter-install**:
- ultralytics (YOLOv8) - ~50MB
- torch (PyTorch) - ~2GB
- torchvision - ~20MB
- cvzone - ~5MB
- Dan dependencies lainnya

**2.3 Install CVZone (Optional tapi Recommended)**
```bash
pip install cvzone==1.5.6
```

### Step 3: Download PPE Detection Model

> ⚠️ Model `ppe.pt` **tidak** ikut ter-clone (di-ignore karena besar). Unduh dulu.

**Option A: Script unduh (Recommended) ✅**
```bash
python download_ppe_model.py
```
Model tersimpan di `ppe_reference/ppe.pt` (sumber: Ansarimajid/Construction-PPE-Detection, MIT).

**Option B: Download Manual (Jika diperlukan)**

1. Unduh file `ppe.pt` dari sumber PPE YOLOv8 (mis. https://github.com/Ansarimajid/Construction-PPE-Detection)
2. Place di folder: `ppe_reference/ppe.pt`

**Option C: Use Roboflow Model**
```bash
# Visit Roboflow Universe
https://universe.roboflow.com/search?q=ppe

# Download PPE detection dataset
# Train atau download pre-trained model
# Save sebagai ppe.pt
```

### Step 4: Setup Face Recognition Database

**4.1 Buat Directory untuk Faces (Already Done) ✅**
```bash
# Directory sudah ada di: faces/
dir faces
```

**4.2 Tambah Known Faces**
```bash
# Copy foto wajah ke directory faces/
# Format: nama_person.jpg

# Contoh:
copy foto_vito.jpg faces\vito.jpg
copy foto_john.jpg faces\john.jpg
copy foto_sarah.jpg faces\sarah.jpg
```

**Requirements untuk foto**:
- ✅ Format: JPG, JPEG, atau PNG
- ✅ 1 wajah per foto
- ✅ Wajah jelas dan terang
- ✅ Resolution minimum: 640x480
- ✅ Nama file = nama person (tanpa spasi)

**4.3 Test Face Recognition**
```bash
python -c "import face_recognition; import os; print(f'Faces loaded: {len([f for f in os.listdir(\"faces\") if f.endswith((\".jpg\", \".jpeg\", \".png\"))])}')"
```

### Step 5: Camera Setup

**5.1 Check Available Cameras**
```bash
python test_camera.py
```

Output expected:
```
Available cameras:
  [0] Integrated Webcam - 640x480
  [1] Insta360 Link 2 - 1280x720 ✓
```

**5.2 Test Insta360 Link 2**
```bash
python -c "import cv2; cap = cv2.VideoCapture(1); print('Insta360 OK' if cap.isOpened() else 'Failed'); cap.release()"
```

### Step 6: Verify Installation

**6.1 Run Verification Script**
```bash
python -c "
import sys
print('Python Version:', sys.version)

try:
    import cv2
    print('✓ OpenCV:', cv2.__version__)
except: print('✗ OpenCV not found')

try:
    import face_recognition
    print('✓ face_recognition: OK')
except: print('✗ face_recognition not found')

try:
    import ultralytics
    print('✓ ultralytics: OK')
except: print('✗ ultralytics not found')

try:
    import torch
    print('✓ PyTorch:', torch.__version__)
    print('  CUDA available:', torch.cuda.is_available())
except: print('✗ PyTorch not found')

try:
    from ppe_detector import PPEDetector
    print('✓ PPE Detector module: OK')
except Exception as e: print('✗ PPE Detector:', e)

print('\n✅ Installation verification complete!')
"
```

**6.2 Expected Output**
```
Python Version: 3.12.x
✓ OpenCV: 4.8.x
✓ face_recognition: OK
✓ ultralytics: OK
✓ PyTorch: 2.x.x
  CUDA available: False (or True jika punya GPU)
✓ PPE Detector module: OK

✅ Installation verification complete!
```

### Step 7: First Run

**7.1 Run dalam Simulation Mode (Tanpa Model)**
```bash
# Jika model belum ready, sistem auto-fallback ke simulation
python ppe_system_main.py
```

**7.2 Run dengan PPE Model**
```bash
# Pastikan ppe.pt ada di ppe_reference/
python ppe_system_main.py
```

**7.3 Run Simple Demo**
```bash
# Demo tanpa face recognition
python demo_ppe_insta360.py
```

---

## 🔧 Troubleshooting Installation

### Issue 1: pip install gagal
```bash
ERROR: Could not install packages due to an OSError

Solution:
1. Run sebagai Administrator
2. Atau install dengan --user flag:
   pip install --user -r requirements_ppe.txt
```

### Issue 2: PyTorch installation lambat
```bash
# Download lambat karena size besar (~2GB)

Solution:
1. Gunakan mirror lokal (jika ada)
2. Atau download manual:
   https://pytorch.org/get-started/locally/
   
3. Install dengan wheel file:
   pip install torch-2.x.x-cp312-win_amd64.whl
```

### Issue 3: face_recognition error di Windows
```bash
ERROR: Microsoft Visual C++ 14.0 or greater is required

Solution:
1. Install Visual C++ Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
   
2. Atau install via conda:
   conda install -c conda-forge face_recognition
```

### Issue 4: CUDA not available
```bash
PyTorch installed tapi CUDA not available

Solution:
1. Check GPU compatibility:
   https://developer.nvidia.com/cuda-gpus
   
2. Install CUDA Toolkit:
   https://developer.nvidia.com/cuda-downloads
   
3. Install PyTorch dengan CUDA:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

Note: CPU-only PyTorch juga works fine untuk testing
```

### Issue 5: ultralytics import error
```bash
ImportError: cannot import name 'YOLO' from 'ultralytics'

Solution:
1. Reinstall ultralytics:
   pip uninstall ultralytics
   pip install ultralytics==8.0.26
   
2. Check version:
   pip show ultralytics
```

### Issue 6: Module tidak ditemukan
```bash
ModuleNotFoundError: No module named 'ppe_detector'

Solution:
1. Pastikan file ppe_detector.py ada
2. Run dari directory yang benar:
   cd "c:/Project vito/pengembangan face recognition"
3. Check PYTHONPATH:
   python -c "import sys; print(sys.path)"
```

---

## ⚙️ Configuration

### 1. Config Camera Index
Edit `ppe_system_main.py` line ~362:
```python
system = PPEComplianceSystem(
    camera_index=1,  # Ubah ke 0 untuk default camera
    model_path="ppe_reference/ppe.pt"
)
```

### 2. Config Confidence Threshold
Edit `ppe_system_main.py` line ~135:
```python
self.ppe_detector = PPEDetector(
    model_path=self.model_path,
    confidence_threshold=0.5  # Ubah 0.5 ke 0.6 (more strict)
)
```

### 3. Config Required PPE
Edit `ppe_detector.py` line ~220:
```python
if required_ppe is None:
    required_ppe = ['Hardhat', 'Safety Vest', 'Mask']  # Tambah 'Mask'
```

### 4. Config Face Recognition Frequency
Edit `ppe_system_main.py` line ~300:
```python
# Run setiap 5 frames (default)
if self.stats['total_frames'] % 5 == 0:

# Ubah ke 10 untuk lebih cepat (less accurate)
if self.stats['total_frames'] % 10 == 0:

# Ubah ke 3 untuk lebih akurat (slower)
if self.stats['total_frames'] % 3 == 0:
```

---

## 📊 Performance Tuning

### For Low-End Systems (4-8GB RAM)
```python
# 1. Reduce frame processing
if self.stats['total_frames'] % 3 == 0:  # Process every 3rd frame

# 2. Lower resolution
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 3. Increase confidence threshold
confidence_threshold=0.6  # Fewer detections = faster
```

### For High-End Systems (16GB+ RAM, GPU)
```python
# 1. Process every frame
# (Remove modulo check)

# 2. Higher resolution
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 3. Enable GPU
# PyTorch auto-detects CUDA
```

---

## ✅ Post-Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (requirements_ppe.txt)
- [ ] PPE model downloaded (ppe.pt)
- [ ] Face database setup (faces/ directory)
- [ ] Insta360 Link 2 connected & detected
- [ ] Verification script passed
- [ ] First run successful
- [ ] Logs directory created
- [ ] Screenshots directory created

---

## 🎯 Next Steps

Setelah installation selesai:

1. **Test System**
   ```bash
   python ppe_system_main.py
   ```

2. **Add More Faces**
   ```bash
   # Add employee photos to faces/
   copy foto_karyawan.jpg faces\nama.jpg
   ```

3. **Review Documentation**
   - `PPE_SYSTEM_README.md` - Complete usage guide
   - `PPE_SETUP_GUIDE.md` - Development roadmap
   - `TROUBLESHOOTING.md` - Common issues

4. **Customize Configuration**
   - Adjust required PPE items
   - Set confidence thresholds
   - Configure logging preferences

5. **Start Monitoring**
   ```bash
   run_ppe_system.bat
   ```

---

## 📞 Support

Jika mengalami issues saat installation:

1. **Check Logs**: Review error messages carefully
2. **Verify Dependencies**: Run verification script
3. **Search Issues**: Check GitHub PPE-Detection issues
4. **Documentation**: Review TROUBLESHOOTING.md

---

## 📝 Installation Summary

**Estimated Time**: 10-15 menit  
**Download Size**: ~2.5GB  
**Disk Space**: ~5GB  
**Difficulty**: ⭐⭐☆☆☆ (Easy-Medium)  

**Key Commands**:
```bash
# 1. Activate venv
.\venv\Scripts\activate

# 2. Install
pip install -r requirements_ppe.txt

# 3. Verify
python -c "import ultralytics; print('OK')"

# 4. Run
python ppe_system_main.py
```

---

**🎉 Installation Complete! Selamat menggunakan PPE Compliance System!**
