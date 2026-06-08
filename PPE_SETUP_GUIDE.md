# 🦺 PPE Detection Setup Guide

## 📋 Overview

Panduan lengkap untuk setup dan menjalankan PPE (Personal Protective Equipment) Detection menggunakan Insta360 Link 2.

---

## ✅ Yang Sudah Siap

### 1. **Face Recognition System** ✓
- Sistem face recognition sudah production-ready
- Insta360 Link 2 sudah terintegrasi
- Database wajah di folder `faces/`

### 2. **PPE Compliance Framework** ✓
- Architecture lengkap di folder `ppe_compliance/`
- Configuration management
- Data models & interfaces
- Video stream processor
- Logging & audit trail

### 3. **Demo Script** ✓
- `demo_ppe_insta360.py` - Demo PPE detection dengan Insta360 Link 2
- Auto-detection kamera
- Simulation mode (jika YOLO belum terinstall)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Aktifkan virtual environment
.\venv\Scripts\activate

# Install PPE detection dependencies
pip install -r requirements_ppe.txt
```

**Catatan**: Instalasi PyTorch (~2GB) akan memakan waktu. Pastikan koneksi internet stabil.

### Step 2: Download PPE Detection Model

**Option A: Basic YOLO Model (Quick Start)**
```python
# Script akan auto-download saat pertama run
python demo_ppe_insta360.py
```

**Option B: PPE-Specific Model (Recommended)**

1. Visit: https://github.com/ishita126jain/PPE-Detection
2. Download pre-trained PPE model
3. Place di folder `models/ppe_detection/`

**Option C: Use Roboflow**
1. Visit: https://universe.roboflow.com/search?q=ppe
2. Download PPE detection model
3. Configure path di script

### Step 3: Run Demo

```bash
# Jalankan demo dengan Insta360 Link 2
python demo_ppe_insta360.py
```

**Controls saat running:**
- `Q` - Quit
- `S` - Screenshot
- `D` - Toggle debug info

---

## 📊 Task Checklist

### ✅ Completed

- [x] Analisis project structure
- [x] Review existing face recognition system
- [x] Setup PPE compliance framework
- [x] Create configuration management
- [x] Implement video stream processor
- [x] Create data models
- [x] Create demo script untuk Insta360 Link 2
- [x] Create requirements_ppe.txt

### 🚧 In Progress

- [ ] Install ultralytics & PyTorch
- [ ] Test basic PPE detection dengan webcam
- [ ] Download/train PPE-specific model

### 📝 To Do - Short Term (1-2 Minggu)

- [ ] **PPE Detection Implementation**
  - [ ] Integrate YOLO model dengan real PPE classes
  - [ ] Fine-tune detection parameters
  - [ ] Test dengan berbagai lighting conditions
  - [ ] Optimize performance (target >15 FPS)

- [ ] **Face Recognition Integration**
  - [ ] Combine PPE detection dengan face recognition existing
  - [ ] Associate detected faces dengan PPE status
  - [ ] Handle occlusion (wajah tertutup helm/mask)

- [ ] **Compliance Engine**
  - [ ] Implement zone-based rules
  - [ ] Violation detection logic
  - [ ] Evidence photo capture

### 📅 To Do - Medium Term (2-4 Minggu)

- [ ] **Storage & Database**
  - [ ] Setup SQLite database
  - [ ] Store violation events
  - [ ] Implement retention policy (731-735 days)

- [ ] **Alert System**
  - [ ] Email notifications
  - [ ] Dashboard real-time alerts
  - [ ] Cooldown mechanism

- [ ] **Reporting**
  - [ ] Daily/weekly/monthly reports
  - [ ] Export to PDF/Excel
  - [ ] Violation analytics

### 🎯 To Do - Long Term (1-2 Bulan)

- [ ] **CCTV Integration**
  - [ ] Migrate dari webcam ke CCTV
  - [ ] Multi-camera simultaneous processing
  - [ ] RTSP stream handling

- [ ] **Web Dashboard**
  - [ ] Real-time monitoring interface
  - [ ] Historical data viewing
  - [ ] Configuration management UI

- [ ] **Production Deployment**
  - [ ] Server setup
  - [ ] Performance optimization
  - [ ] Load testing
  - [ ] Security hardening

---

## 🔧 Testing Strategy

### Phase 1: Webcam Testing (Current)
```
Goal: Validate PPE detection accuracy
- Test with Insta360 Link 2
- Simulate PPE scenarios (pakai helm, vest, dll)
- Measure detection accuracy & FPS
- Iterate on model parameters
```

### Phase 2: Integration Testing
```
Goal: Combine PPE + Face Recognition
- Identify person (face recognition)
- Check PPE compliance
- End-to-end workflow test
```

### Phase 3: CCTV Migration
```
Goal: Production-ready system
- Replace webcam dengan CCTV feed
- Multi-camera handling
- 24/7 reliability testing
```

---

## 📁 Project Structure

```
pengembangan face recognition/
│
├── main.py                          # Face recognition (existing)
├── main_office_attendance.py        # Office attendance (existing)
├── demo_ppe_insta360.py            # PPE detection demo (NEW)
│
├── config.py                        # Face recognition config
├── requirements.txt                 # Face recognition deps
├── requirements_ppe.txt            # PPE detection deps (NEW)
│
├── faces/                          # Face database (existing)
│   └── vito.jpeg
│
├── ppe_compliance/                 # PPE system (framework ready)
│   ├── config/                     # ✅ Configuration
│   ├── models/                     # ✅ Data models
│   ├── video/                      # ✅ Stream processor
│   ├── detection/                  # 🚧 PPE detection (to implement)
│   ├── recognition/                # 🚧 Face recognition (to implement)
│   ├── compliance/                 # 🚧 Compliance engine (to implement)
│   ├── alerts/                     # 🚧 Alert system (to implement)
│   ├── storage/                    # 🚧 Database (to implement)
│   └── reporting/                  # 🚧 Reporting (to implement)
│
└── README.md                       # Main documentation
```

---

## 🎓 Learning Resources

### PPE Detection
- **GitHub**: https://github.com/ishita126jain/PPE-Detection
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Roboflow PPE**: https://universe.roboflow.com/search?q=ppe

### Computer Vision
- **OpenCV Tutorial**: https://docs.opencv.org/4.x/d9/df8/tutorial_root.html
- **YOLO Training**: https://docs.ultralytics.com/modes/train/

### Integration
- **Face Recognition with PPE**: Tips untuk handle occlusion
- **Multi-camera Management**: RTSP streaming best practices

---

## 💡 Tips & Best Practices

### 1. Start Small
- ✅ Test dengan 1 webcam dulu
- ✅ Validate accuracy sebelum scale
- ✅ Iterate cepat dengan simulation mode

### 2. Optimize Gradually
- Frame resize untuk performa
- Skip frames jika perlu (detect every N frames)
- Batch processing untuk multiple cameras

### 3. Handle Edge Cases
- Low lighting conditions
- Multiple persons in frame
- Partial occlusion (helm menutupi wajah)
- Unknown persons (no face match)

### 4. Data Management
- Log semua detections
- Capture evidence hanya saat violation
- Implement proper retention policy

---

## 🐛 Troubleshooting

### Issue: YOLO model tidak terinstall
```bash
# Solution:
pip install ultralytics torch torchvision
```

### Issue: Webcam tidak terdeteksi
```bash
# Solution:
python test_camera.py  # Check available cameras
```

### Issue: Detection lambat (FPS rendah)
```python
# Solutions:
1. Reduce frame size di config
2. Use smaller YOLO model (yolov8n vs yolov8l)
3. Skip frames (detect every 2-3 frames)
4. GPU acceleration (if available)
```

### Issue: PPE detection tidak akurat
```
Solutions:
1. Use PPE-specific model (bukan general YOLO)
2. Fine-tune confidence threshold
3. Train custom model dengan dataset lokal
4. Improve lighting conditions
```

---

## 📞 Next Steps

**Immediate (Hari ini):**
1. Install dependencies: `pip install -r requirements_ppe.txt`
2. Run demo: `python demo_ppe_insta360.py`
3. Test simulation mode dengan webcam

**Week 1:**
1. Download PPE-specific model
2. Test real detection accuracy
3. Tune parameters

**Week 2:**
1. Integrate dengan face recognition
2. Implement basic compliance rules
3. Test end-to-end

**Week 3-4:**
1. Add database & logging
2. Implement alert system
3. Create basic reporting

**Month 2:**
1. CCTV integration
2. Web dashboard
3. Production deployment

---

## ✅ Success Criteria

### Phase 1: Webcam Demo
- [ ] PPE detection works with Insta360 Link 2
- [ ] Detection accuracy >80%
- [ ] FPS >15 frames/second
- [ ] Compliance rules work correctly

### Phase 2: Integration
- [ ] Face recognition + PPE detection combined
- [ ] Violation detection functional
- [ ] Evidence capture working
- [ ] Basic logging implemented

### Phase 3: Production
- [ ] CCTV integration complete
- [ ] Multi-camera support (8+ cameras)
- [ ] Web dashboard operational
- [ ] 24/7 reliability achieved
- [ ] Data retention compliance

---

## 📝 Notes

- Framework sudah solid, tinggal implement detection engine
- Testing dengan webcam adalah approach yang TEPAT
- CCTV migration akan mudah setelah webcam validated
- Focus on accuracy dulu, optimization later

**Status**: Ready untuk implementasi Phase 1 ✅
