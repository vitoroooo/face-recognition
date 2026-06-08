# 🦺 PPE Compliance Monitoring System

## Production-Ready System dengan Akurasi Tinggi & UI/UX Professional

Sistem monitoring compliance PPE (Personal Protective Equipment) yang mengintegrasikan:
- ✅ **YOLOv8** untuk deteksi PPE (Hardhat, Safety Vest, Mask, dll)
- ✅ **Face Recognition** untuk identifikasi karyawan
- ✅ **Insta360 Link 2** untuk input video berkualitas tinggi
- ✅ **Real-time Statistics & Reporting**
- ✅ **Professional UI/UX** dengan overlay informatif

---

## 🎯 Features

### Core Features
- ✅ **PPE Detection**: Hardhat, Safety Vest, Mask (positive & negative detection)
- ✅ **Face Recognition**: Identifikasi karyawan otomatis
- ✅ **Compliance Evaluation**: Real-time check compliance berdasarkan aturan
- ✅ **Auto-Camera Detection**: Deteksi otomatis Insta360 Link 2
- ✅ **Violation Logging**: Log violations ke JSON dengan timestamp
- ✅ **Screenshot Capture**: Simpan evidence photo saat violation

### UI/UX Features
- ✅ **Professional Overlay**: Header bar dengan title & timestamp
- ✅ **Real-time Statistics**: FPS, persons detected, compliance rate
- ✅ **Color-Coded Detection**: Green (compliant), Red (violation)
- ✅ **Person Name Display**: Tampilkan nama dari face recognition
- ✅ **Missing PPE Indicator**: List PPE items yang kurang
- ✅ **Keyboard Controls**: Q, S, D, R untuk kontrol interaktif

### Technical Features
- ✅ **Performance Optimized**: Face recognition run setiap 5 frames
- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Error Handling**: Graceful degradation jika model tidak tersedia
- ✅ **Simulation Mode**: Testing tanpa YOLO model
- ✅ **Logging System**: Automatic violations logging

---

## 📦 Installation

### Step 1: Clone Repository
```bash
cd "c:/Project vito/pengembangan face recognition"
```

### Step 2: Aktifkan Virtual Environment
```bash
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install PPE detection dependencies
pip install -r requirements_ppe.txt

# Ini akan install:
# - ultralytics (YOLOv8)
# - torch & torchvision (PyTorch)
# - cvzone (untuk visualisasi)
# - Dan dependencies lainnya
```

**Catatan**: Instalasi PyTorch (~2GB) memakan waktu. Pastikan internet stabil.

### Step 4: Download PPE Model

**Option A: Gunakan Model dari Reference Repo** ✅
```
Model sudah tersedia di: ppe_reference/ppe.pt
(Otomatis di-download saat clone repo)
```

**Option B: Download Custom Model**
1. Visit: https://universe.roboflow.com/search?q=ppe
2. Download PPE detection model
3. Place di project root sebagai `ppe.pt`

---

## 🚀 Quick Start

### Method 1: Menggunakan Batch Script (Recommended)
```bash
# Double-click atau run:
run_ppe_system.bat
```

### Method 2: Manual Python
```bash
# Aktifkan venv
.\venv\Scripts\activate

# Run sistem
python ppe_system_main.py
```

### Method 3: Demo Sederhana (Tanpa Face Recognition)
```bash
python demo_ppe_insta360.py
```

---

## ⌨️ Controls & Usage

### Keyboard Controls
- **Q** - Quit (keluar dari aplikasi)
- **S** - Screenshot (simpan frame saat ini)
- **D** - Toggle Debug Info (show/hide control panel)
- **R** - Reset Statistics (reset counter ke 0)

### UI Elements

**Header Bar (Top)**
```
PPE COMPLIANCE MONITORING SYSTEM
Insta360 Link 2 | 2026-06-08 18:35:00
```

**Statistics Panel (Top Right)**
```
FPS: 25.3
Frames: 1520
Persons Detected: 45
Compliant: 38       (Green)
Violations: 7       (Red)
```

**Controls Panel (Bottom Left)**
```
Q - Quit
S - Screenshot
D - Toggle Debug
R - Reset Stats
```

**Detection Overlay**
- **Green Box**: Person compliant (semua PPE lengkap)
- **Red Box**: Person violation (ada PPE yang kurang)
- **Yellow Box**: PPE items detected
- **White Text**: Person name (dari face recognition)
- **Red Text**: Missing PPE items list

---

## 📁 Project Structure

```
pengembangan face recognition/
│
├── ppe_system_main.py          # ⭐ Main application
├── ppe_detector.py             # ⭐ PPE detection module
├── demo_ppe_insta360.py        # Demo script
├── run_ppe_system.bat          # Quick start script
│
├── requirements_ppe.txt        # PPE dependencies
├── PPE_SETUP_GUIDE.md         # Setup guide lengkap
├── PPE_SYSTEM_README.md       # Documentation (this file)
│
├── faces/                      # Face database
│   └── vito.jpeg              # Known faces
│
├── ppe_reference/             # Reference implementation
│   ├── ppe.pt                 # YOLOv8 PPE model
│   ├── PPE-Detection.py       # Reference code
│   └── requirements.txt       # Reference dependencies
│
├── logs/                      # Auto-generated
│   └── violations_YYYYMMDD.json
│
└── screenshots/               # Auto-generated
    └── ppe_YYYYMMDD_HHMMSS.jpg
```

---

## 🎓 How It Works

### Detection Pipeline

```
1. CAMERA INPUT (Insta360 Link 2)
   ↓
2. PPE DETECTION (YOLOv8)
   - Detect persons
   - Detect PPE items (Hardhat, Vest, etc.)
   - Detect NO-PPE items (violations)
   ↓
3. FACE RECOGNITION (face_recognition)
   - Identify persons
   - Match dengan database
   ↓
4. ASSOCIATION
   - Link faces dengan persons
   - Link PPE items dengan persons
   ↓
5. COMPLIANCE EVALUATION
   - Check required PPE
   - Identify missing items
   - Mark compliant/violation
   ↓
6. VISUALIZATION & LOGGING
   - Draw bounding boxes
   - Display names & status
   - Log violations
   - Update statistics
```

### PPE Detection Classes

**Positive Detection** (Compliant):
- `Hardhat` - Helm keselamatan
- `Mask` - Masker wajah
- `Safety Vest` - Rompi keselamatan

**Negative Detection** (Violation):
- `NO-Hardhat` - Tidak pakai helm
- `NO-Mask` - Tidak pakai masker
- `NO-Safety Vest` - Tidak pakai rompi

**Other Classes**:
- `Person` - Deteksi orang
- `Safety Cone`, `machinery`, `vehicle` - Objects lain

### Compliance Rules

**Default Requirements**:
- ✅ Hardhat (wajib)
- ✅ Safety Vest (wajib)
- ⚪ Mask (opsional, bisa disesuaikan)

**Customization**: Edit di `ppe_detector.py` → `evaluate_compliance()`

---

## 📊 Outputs & Logging

### Violations Log
File: `logs/violations_YYYYMMDD.json`

Format:
```json
[
  {
    "timestamp": "2026-06-08T18:35:42",
    "person_name": "Vito",
    "person_id": "vito",
    "missing_ppe": ["Hardhat"],
    "confidence": 0.85
  },
  {
    "timestamp": "2026-06-08T18:36:15",
    "person_name": "Unknown",
    "person_id": "unknown",
    "missing_ppe": ["Hardhat", "Safety Vest"],
    "confidence": 0.78
  }
]
```

### Screenshots
File: `screenshots/ppe_YYYYMMDD_HHMMSS.jpg`

Captured saat tekan tombol **S** atau otomatis saat violation (opsional).

### Final Statistics
Printed saat aplikasi ditutup:
```
============================================================
📊 FINAL STATISTICS
============================================================
Total Runtime: 125.45 seconds
Total Frames: 3761
Average FPS: 29.96
Total Persons Detected: 142
Compliant: 118
Violations: 24
Compliance Rate: 83.1%
============================================================
```

---

## 🔧 Configuration & Customization

### 1. Change Required PPE Items
Edit `ppe_system_main.py`:
```python
# Di method run(), ubah:
print("🎯 Required PPE: Hardhat, Safety Vest, Mask")  # Update display

# Di ppe_detector.py, method evaluate_compliance():
required_ppe = ['Hardhat', 'Safety Vest', 'Mask']  # Update list
```

### 2. Adjust Detection Confidence
Edit `ppe_system_main.py`:
```python
self.ppe_detector = PPEDetector(
    model_path=self.model_path,
    confidence_threshold=0.6  # Ubah dari 0.5 ke 0.6 (lebih strict)
)
```

### 3. Change Camera Index
Edit `ppe_system_main.py`:
```python
system = PPEComplianceSystem(
    camera_index=0,  # Ubah ke 0 untuk default webcam
    model_path="ppe_reference/ppe.pt"
)
```

### 4. Adjust Face Recognition Frequency
Edit `ppe_system_main.py`, di method `run()`:
```python
# Run setiap 3 frames (lebih sering)
if self.stats['total_frames'] % 3 == 0:
    faces = self.face_recognizer.recognize_faces(frame)

# Run setiap 10 frames (lebih jarang, lebih cepat)
if self.stats['total_frames'] % 10 == 0:
    faces = self.face_recognizer.recognize_faces(frame)
```

### 5. Add New Known Faces
```bash
# Tambahkan foto ke directory faces/
cp foto_baru.jpg faces/nama_person.jpg

# Sistem akan auto-load saat restart
```

---

## 🎯 Use Cases

### 1. Construction Site Monitoring
```
Required PPE: Hardhat, Safety Vest
Cameras: Multiple Insta360 Link 2 di berbagai zona
Alert: Real-time notification saat violation
```

### 2. Factory/Manufacturing
```
Required PPE: Hardhat, Safety Glasses, Work Uniform
Integration: CCTV existing + face recognition
Reporting: Daily/weekly compliance reports
```

### 3. Warehouse Operations
```
Required PPE: Safety Vest, Safety Shoes
Features: Person tracking + violation history
Dashboard: Real-time compliance monitoring
```

### 4. Chemical Processing Plant
```
Required PPE: Helmet, Mask, Gloves, Safety Vest
Critical: High-accuracy detection + immediate alerts
Logging: Comprehensive audit trail
```

---

## 🐛 Troubleshooting

### Issue: Model tidak ter-load
```
ERROR: Failed to load model: ppe.pt

Solution:
1. Check file ppe.pt exists di ppe_reference/
2. Download dari: https://github.com/ishita126jain/PPE-Detection
3. Atau jalankan dalam simulation mode (auto-fallback)
```

### Issue: Insta360 Link 2 tidak terdeteksi
```
⚠️ Insta360 not found, using default camera

Solution:
1. Check USB connection
2. Update Insta360 driver
3. Test dengan: python test_camera.py
4. Manual set camera_index di code
```

### Issue: Face recognition lambat
```
FPS turun saat face recognition

Solution:
1. Adjust face recognition frequency:
   if self.stats['total_frames'] % 10 == 0:  # Dari 5 ke 10
2. Reduce frame resolution
3. Use GPU acceleration (jika tersedia)
```

### Issue: Detection tidak akurat
```
Banyak false positive/negative

Solution:
1. Adjust confidence_threshold (naik ke 0.6-0.7)
2. Improve lighting conditions
3. Train custom model dengan dataset lokal
4. Fine-tune YOLO parameters
```

---

## 📈 Performance Optimization Tips

### 1. Frame Rate Optimization
```python
# Skip frame processing
if self.stats['total_frames'] % 2 == 0:  # Process every 2 frames
    ppe_detections = self.ppe_detector.detect(frame)
```

### 2. Resolution Optimization
```python
# Resize frame before detection
small_frame = cv2.resize(frame, (640, 480))
detections = self.ppe_detector.detect(small_frame)
```

### 3. GPU Acceleration
```python
# Install CUDA version of PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 4. Multi-Threading
```python
# Process face recognition in separate thread
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)
```

---

## 🔐 Security & Privacy

### Data Protection
- ✅ Face encodings tidak disimpan (hanya reference photos)
- ✅ Violations log hanya nama & timestamp (no photos by default)
- ✅ Screenshots optional (hanya saat tekan S)
- ✅ Local processing (no cloud upload)

### Access Control
```python
# TODO: Implement user authentication
# TODO: Role-based access untuk logs
# TODO: Encryption untuk sensitive data
```

---

## 🚀 Next Steps & Roadmap

### Phase 1: Current (✅ DONE)
- [x] PPE Detection dengan YOLOv8
- [x] Face Recognition integration
- [x] Insta360 Link 2 support
- [x] Real-time UI/UX
- [x] Violation logging

### Phase 2: Enhancement (🚧 In Progress)
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Web dashboard (FastAPI + React)
- [ ] Email/SMS alerts
- [ ] Multi-camera support
- [ ] CCTV integration (RTSP streams)

### Phase 3: Advanced Features
- [ ] AI-powered analytics
- [ ] Trend analysis & predictions
- [ ] Custom training interface
- [ ] Mobile app
- [ ] Cloud deployment

---

## 📞 Support & Contact

### Documentation
- **Setup Guide**: `PPE_SETUP_GUIDE.md`
- **Quick Start**: `QUICK_START.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

### Reference
- **GitHub PPE-Detection**: https://github.com/ishita126jain/PPE-Detection
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Face Recognition**: https://github.com/ageitgey/face_recognition

### Issues & Feedback
Untuk bug reports atau feature requests, silakan buat issue atau contact developer.

---

## 📄 License & Credits

### Credits
- **YOLOv8**: Ultralytics (https://github.com/ultralytics/ultralytics)
- **Face Recognition**: Adam Geitgey
- **PPE Detection Reference**: Ishita Jain (https://github.com/ishita126jain/PPE-Detection)
- **CVZone**: Computer Vision Zone

### System Developed By
**Project**: PPE Compliance Monitoring System  
**Version**: 1.0.0  
**Date**: 2026-06-08  
**Status**: Production Ready ✅

---

**🦺 Stay Safe, Stay Compliant!**
