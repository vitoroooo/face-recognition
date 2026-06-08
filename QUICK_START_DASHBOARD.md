# 🚀 Quick Start - Web Dashboard

## Langkah Super Cepat!

### 1. Install Dependencies (Sekali Saja)

```bash
pip install flask flask-cors requests
```

### 2. Start Dashboard

**Windows:**
```bash
run_dashboard.bat
```

**Manual:**
```bash
python web_dashboard.py
```

### 3. Akses Dashboard

Buka browser: **http://localhost:5000**

---

## 📊 Yang Bisa Dilakukan

### Dashboard Features
- ✅ Real-time attendance monitoring
- ✅ PPE violation tracking
- ✅ Active camera status
- ✅ Compliance rate statistics
- ✅ Recent activity feed
- ✅ Auto-refresh setiap 30 detik

### API Endpoints (untuk integrasi)

```bash
# Get dashboard stats
curl http://localhost:5000/api/dashboard/stats

# Get today's attendance
curl http://localhost:5000/api/attendance/today

# Get PPE violations
curl http://localhost:5000/api/ppe/violations/today

# Export data
curl http://localhost:5000/api/export/attendance?days=30
```

---

## 🧪 Test Dashboard

```bash
python test_dashboard.py
```

Atau test API manual:

```python
import requests

response = requests.get('http://localhost:5000/api/dashboard/stats')
data = response.json()
print(data)
```

---

## 📝 Log Data Programmatically

```python
from database import Database

db = Database()

# Log attendance
db.log_attendance("John Doe", 0.95, "camera_1")

# Log PPE violation
db.log_ppe_violation(
    "missing_helmet",
    "Safety Helmet", 
    person_name="Jane Smith",
    severity="high"
)

# Get stats
stats = db.get_attendance_stats(days=7)
print(f"Total attendance: {stats['summary']['total_records']}")
```

---

## 🔔 Enable Email Alerts (Optional)

Edit `alert_config.json`:

```json
{
  "enabled": true,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipients": ["admin@company.com"]
  }
}
```

**Gmail Setup:**
1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Gunakan App Password di config

Test alerts:
```bash
python alert_system.py
```

---

## 🐳 Docker (Advanced)

```bash
# Build and run
docker-compose up -d

# Stop
docker-compose down
```

---

## ❓ Troubleshooting

**Dashboard tidak bisa diakses?**
```bash
# Check if running
curl http://localhost:5000/api/dashboard/stats

# Check firewall
# Windows: Allow port 5000 in Windows Firewall
```

**ModuleNotFoundError?**
```bash
pip install flask flask-cors requests
```

**Database error?**
```bash
# Reset database (WARNING: deletes all data)
del face_recognition.db
python database.py
```

---

## 📞 Need Help?

- Documentation: See all `*.md` files
- Test database: `python database.py`
- Test alerts: `python alert_system.py`
- Test dashboard: `python test_dashboard.py`

---

**🎉 Happy Monitoring!**
