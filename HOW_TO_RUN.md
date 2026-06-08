# 🚀 Cara Run & Cara Kerja System

## 📋 QUICK START - 3 LANGKAH MUDAH

### Langkah 1: Setup Environment (Sekali Saja)

```bash
# Buka PowerShell/CMD di folder project

# Aktifkan virtual environment
venv\Scripts\activate

# Install dependencies
pip install flask flask-cors requests
```

### Langkah 2: Pilih Mode

**Ada 3 mode yang bisa dijalankan:**

#### A. 🌐 **Web Dashboard** (Untuk monitoring)
```bash
run_dashboard.bat
# atau manual:
python web_dashboard.py
```
Buka browser: **http://localhost:5000**

#### B. 👤 **Face Recognition** (Untuk absensi)
```bash
python main.py
```
Akan buka kamera untuk face recognition

#### C. ⚠️ **PPE Detection** (Untuk keselamatan kerja)
```bash
run_ppe_system.bat
# atau manual:
python ppe_system_main.py
```
Akan buka kamera untuk PPE detection

### Langkah 3: Lihat Hasilnya!
- Web dashboard akan menampilkan data real-time
- Database akan menyimpan semua log
- Alert bisa dikirim via email

---

## 🎯 CARA KERJA SYSTEM

### Sistem 1: Face Recognition (Absensi Otomatis)

```
┌─────────────────────────────────────────────────┐
│  1. CAMERA CAPTURE                              │
│     - Buka kamera (webcam/Insta360)             │
│     - Ambil frame video real-time               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  2. FACE DETECTION                              │
│     - Deteksi wajah di frame                    │
│     - Extract face encoding (128 dimensi)       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  3. FACE RECOGNITION                            │
│     - Compare dengan database (faces/ folder)   │
│     - Hitung similarity (confidence score)      │
│     - Match = "John Doe" | Unknown              │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  4. LOG TO DATABASE                             │
│     - Save ke tabel 'attendance'                │
│     - Timestamp, nama, confidence, camera_id    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  5. DISPLAY RESULT                              │
│     - Tampilkan nama di video                   │
│     - Green box = dikenali                      │
│     - Red box = unknown                         │
└─────────────────────────────────────────────────┘
```

**Kode yang bekerja:**
- `main.py` - Main loop
- `camera_utils.py` - Camera handling
- `database.py` - Database logging
- Reference photos di `faces/` folder

---

### Sistem 2: PPE Detection (Safety Monitoring)

```
┌─────────────────────────────────────────────────┐
│  1. CAMERA CAPTURE                              │
│     - Buka kamera untuk monitoring area kerja   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  2. YOLO DETECTION                              │
│     - Run YOLOv8 model (ppe.pt)                 │
│     - Detect objects: helmet, vest, person, etc │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  3. PPE COMPLIANCE CHECK                        │
│     - Check: Apakah pakai helmet?               │
│     - Check: Apakah pakai safety vest?          │
│     - Result: COMPLIANT atau VIOLATION          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  4. LOG VIOLATIONS                              │
│     - Save ke tabel 'ppe_violations'            │
│     - Violation type, severity, timestamp       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  5. SEND ALERTS (Optional)                      │
│     - Email ke admin@company.com                │
│     - Webhook ke Slack/Discord                  │
└─────────────────────────────────────────────────┘
```

**Kode yang bekerja:**
- `ppe_system_main.py` - Main loop
- `ppe_detector.py` - YOLOv8 detection
- `database.py` - Violation logging
- `alert_system.py` - Alert notifications
- Model: `ppe_reference/ppe.pt`

---

### Sistem 3: Web Dashboard (Monitoring & Analytics)

```
┌─────────────────────────────────────────────────┐
│  1. FLASK SERVER                                │
│     - Run di http://localhost:5000              │
│     - Serve HTML dashboard                      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  2. READ DATABASE                               │
│     - Query attendance records                  │
│     - Query PPE violations                      │
│     - Query system events                       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  3. CALCULATE STATISTICS                        │
│     - Total attendance today                    │
│     - PPE violations count                      │
│     - Compliance rate percentage                │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  4. API RESPONSE                                │
│     - Return JSON data                          │
│     - Example: {"attendance": 25, ...}          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  5. DISPLAY IN BROWSER                          │
│     - Beautiful cards dengan statistics         │
│     - Charts & graphs                           │
│     - Auto-refresh setiap 30 detik              │
└─────────────────────────────────────────────────┘
```

**Kode yang bekerja:**
- `web_dashboard.py` - Flask server
- `database.py` - Data queries
- `templates/dashboard.html` - Frontend UI

---

## 🔄 COMPLETE WORKFLOW

### Skenario: Monitoring Kantor/Pabrik

**Pagi hari (07:00):**
```
1. Karyawan datang ke entrance
2. Camera mendeteksi wajah → main.py
3. System recognize: "John Doe" (confidence: 95%)
4. Log ke database: attendance table
   - person_name: "John Doe"
   - timestamp: 2026-06-08 07:15:30
   - camera_id: "entrance_cam"
5. Dashboard update: Total attendance +1
```

**Di area kerja (09:00):**
```
1. Camera monitoring area konstruksi → ppe_system_main.py
2. Detect person tanpa helmet
3. System detect: VIOLATION - Missing Helmet
4. Log ke database: ppe_violations table
   - violation_type: "missing_helmet"
   - severity: "high"
   - timestamp: 2026-06-08 09:23:15
5. Send email alert ke admin@company.com
6. Dashboard update: Violations count +1
```

**Admin monitoring (10:00):**
```
1. Admin buka http://localhost:5000
2. Dashboard menampilkan:
   ├── Attendance Today: 25 orang
   ├── PPE Violations: 3 violations
   ├── Active Cameras: 2/2
   └── Compliance Rate: 92%
3. Admin click "PPE Violations" tab
4. Lihat detail violations dengan photo
5. Mark violation as "resolved"
```

---

## 💻 CONTOH PENGGUNAAN

### A. Setup Awal (Pertama Kali)

```bash
# 1. Clone/download project
cd "c:\Project vito\pengembangan face recognition"

# 2. Aktifkan venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements_web.txt

# 4. Download PPE model (auto)
python download_ppe_model.py

# 5. Tambahkan reference photos
# Copy foto ke folder faces/
# Format: faces/john_doe.jpg
```

### B. Running Daily Operations

**Terminal 1 - Web Dashboard:**
```bash
venv\Scripts\activate
python web_dashboard.py
# Dashboard running at http://localhost:5000
```

**Terminal 2 - Face Recognition:**
```bash
venv\Scripts\activate
python main.py
# Press 'q' to quit
# Press 'd' for debug mode
```

**Terminal 3 - PPE Detection (Optional):**
```bash
venv\Scripts\activate
python ppe_system_main.py
# Press 'q' to quit
```

### C. Akses & Monitor

**Browser:**
```
http://localhost:5000          # Dashboard home
http://localhost:5000/api/dashboard/stats  # API stats
```

**Database:**
```python
from database import Database
db = Database()

# Lihat attendance hari ini
today = db.get_attendance_today()
print(f"Total: {len(today)} orang")

# Lihat violations
violations = db.get_ppe_violations_today(resolved=False)
print(f"Pending violations: {len(violations)}")
```

---

## 🎮 KEYBOARD CONTROLS

### Saat Running Face Recognition/PPE:

| Key | Action |
|-----|--------|
| `q` | Quit/Exit program |
| `d` | Toggle debug mode |
| `f` | Toggle FPS display |
| `s` | Save screenshot |
| `ESC` | Exit |

---

## 📊 DATABASE SCHEMA

### Table: attendance
```sql
id | person_name | timestamp | confidence | camera_id | photo_path
1  | John Doe    | 2026-06-08 07:15 | 0.95 | entrance_cam | faces/john.jpg
2  | Jane Smith  | 2026-06-08 07:20 | 0.92 | entrance_cam | faces/jane.jpg
```

### Table: ppe_violations
```sql
id | person_name | violation_type | severity | timestamp | resolved
1  | Unknown    | missing_helmet | high     | 2026-06-08 09:23 | 0
2  | John Doe   | missing_vest   | medium   | 2026-06-08 10:15 | 1
```

---

## 🔧 CONFIGURATION

### 1. Camera Settings (config.py)
```python
CAMERA_INDEX = 0  # 0 = default webcam, 1 = external camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
```

### 2. Face Recognition (config.py)
```python
FACE_TOLERANCE = 0.6  # Lower = stricter (0.4-0.7)
PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame for performance
```

### 3. PPE Detection (ppe_compliance/config/)
```python
PPE_CONFIDENCE_THRESHOLD = 0.5
REQUIRED_PPE = ['helmet', 'vest', 'gloves']
```

### 4. Alert System (alert_config.json)
```json
{
  "enabled": true,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "sender_email": "alerts@company.com",
    "recipients": ["admin@company.com"]
  }
}
```

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'flask'"
```bash
pip install flask flask-cors requests
```

### Error: "Camera not found"
```bash
# Test available cameras
python test_camera.py

# Change camera index in config.py
CAMERA_INDEX = 1  # Try different numbers
```

### Error: "PPE model not found"
```bash
python download_ppe_model.py --force
```

### Dashboard tidak bisa diakses
```bash
# Check if running
curl http://localhost:5000/api/dashboard/stats

# Try different port
# Edit web_dashboard.py, line: app.run(port=5001)
```

---

## 📞 SUPPORT

**Test Components:**
```bash
python database.py        # Test database
python alert_system.py    # Test alerts
python test_camera.py     # Test camera
python test_dashboard.py  # Test dashboard
```

**Logs:**
- Check `face_recognition.db` untuk data
- Check console output untuk errors
- Check browser console (F12) untuk web errors

---

## 🎯 TIPS & BEST PRACTICES

1. **Reference Photos**: 
   - Gunakan foto wajah clear, frontal
   - Format: JPG/PNG
   - Size: 800x800px recommended

2. **Performance**:
   - Process every 3rd frame untuk speed
   - Lower resolution jika laggy
   - Close other camera apps

3. **Accuracy**:
   - Multiple photos per person = better
   - Good lighting = better recognition
   - Face tolerance 0.6 = good balance

4. **Production**:
   - Use Docker untuk deployment
   - Setup email alerts
   - Regular database backups

---

**Version**: 2.0.0  
**Last Updated**: 2026-06-08  
**Status**: Production Ready ✅
