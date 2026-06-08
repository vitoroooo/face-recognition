# Face Recognition & PPE Compliance System - Advanced Features

## 🎯 Overview

Production-ready face recognition dan PPE compliance monitoring system dengan:

- ✅ **Face Recognition** - Automatic attendance tracking
- ✅ **PPE Detection** - YOLOv8-based safety equipment monitoring  
- ✅ **Web Dashboard** - Real-time monitoring interface
- ✅ **Database Logging** - SQLite dengan support untuk PostgreSQL
- ✅ **Alert System** - Email & webhook notifications
- ✅ **Docker Support** - Containerized deployment
- ✅ **RESTful API** - Complete API endpoints
- ✅ **Auto-testing** - Unit tests dengan pytest

## 🚀 Quick Start

### 1. Basic Installation

```bash
# Clone repository
git clone <repo-url>
cd "pengembangan face recognition"

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements_web.txt
pip install -r requirements_ppe.txt

# Download PPE model
python download_ppe_model.py

# Add reference photos
# Place photos in faces/ folder: faces/john_doe.jpg
```

### 2. Run Web Dashboard

```bash
python web_dashboard.py
```

Dashboard: http://localhost:5000

### 3. Run Face Recognition

```bash
python main.py
```

### 4. Run PPE Detection

```bash
python ppe_system_main.py
```

## 📊 Web Dashboard Features

### Dashboard Home (`/`)
- Real-time attendance statistics
- PPE violation summary
- Active camera monitoring
- Recent activity feed
- System status

### API Endpoints

#### Attendance APIs
```bash
# Get today's attendance
GET /api/attendance/today

# Get person's attendance history
GET /api/attendance/person/<name>?days=7

# Get attendance statistics
GET /api/attendance/stats?days=30
```

#### PPE Compliance APIs
```bash
# Get today's violations
GET /api/ppe/violations/today?resolved=false

# Get PPE statistics
GET /api/ppe/stats?days=30

# Resolve violation
POST /api/ppe/violation/<id>/resolve
```

#### System APIs
```bash
# Dashboard statistics
GET /api/dashboard/stats

# System events
GET /api/events?limit=100&severity=error

# Camera status
GET /api/cameras?camera_id=camera_1

# Export data
GET /api/export/<table>?days=30

# Daily report
GET /api/report/daily?date=2026-06-08
```

### Example API Usage

```python
import requests

# Get dashboard stats
response = requests.get('http://localhost:5000/api/dashboard/stats')
data = response.json()

if data['success']:
    print(f"Attendance today: {data['data']['attendance']['today']}")
    print(f"PPE violations: {data['data']['ppe']['violations_today']}")
    print(f"Compliance rate: {data['data']['ppe']['resolved_rate']}%")
```

```javascript
// JavaScript/jQuery example
$.ajax({
    url: 'http://localhost:5000/api/attendance/today',
    method: 'GET',
    success: function(result) {
        if (result.success) {
            console.log('Today\'s attendance:', result.data);
        }
    }
});
```

## 🗄️ Database Management

### Using Database Module

```python
from database import Database

# Initialize database
db = Database()

# Log attendance
att_id = db.log_attendance(
    person_name="John Doe",
    confidence=0.95,
    camera_id="camera_1",
    photo_path="faces/john_doe.jpg"
)

# Log PPE violation
viol_id = db.log_ppe_violation(
    violation_type="missing_helmet",
    missing_equipment="Safety Helmet",
    person_name="Jane Smith",
    confidence=0.87,
    camera_id="camera_1",
    severity="high"
)

# Log system event
event_id = db.log_event(
    event_type="system_start",
    description="System started successfully",
    metadata={"version": "2.0", "cameras": 2},
    severity="info"
)

# Get statistics
att_stats = db.get_attendance_stats(days=30)
ppe_stats = db.get_ppe_stats(days=30)

# Export data
db.export_data('attendance', 'backup.json', days=30)

# Cleanup old records
db.cleanup_old_records(days=90)

db.close()
```

### Database Schema

**attendance** - Attendance records
- id, person_name, timestamp, confidence, camera_id, photo_path, status

**ppe_violations** - PPE violation records
- id, person_name, timestamp, violation_type, missing_equipment, confidence, camera_id, frame_path, severity, resolved

**system_events** - System event logs
- id, timestamp, event_type, description, metadata, severity

**camera_status** - Camera status monitoring
- id, camera_id, last_seen, status, resolution, fps, location

## 🔔 Alert System

### Email Alerts Setup

1. Create/edit `alert_config.json`:

```json
{
  "enabled": true,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "alerts@company.com",
    "sender_password": "your-app-password",
    "recipients": [
      "admin@company.com",
      "security@company.com"
    ]
  },
  "webhook": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  },
  "thresholds": {
    "ppe_violations_per_hour": 5,
    "unknown_persons_per_hour": 3
  }
}
```

2. For Gmail, enable 2FA and create App Password:
   - https://myaccount.google.com/apppasswords

3. Test alerts:

```python
from alert_system import AlertSystem

alert = AlertSystem()

# Test PPE violation alert
violation_data = {
    'timestamp': '2026-06-08 20:00:00',
    'violation_type': 'missing_helmet',
    'missing_equipment': 'Safety Helmet',
    'severity': 'high',
    'person_name': 'John Doe',
    'camera_id': 'camera_1',
    'confidence': 0.95
}

alert.send_ppe_violation_alert(violation_data)

# Test daily report
alert.send_daily_report(
    attendance_count=25,
    violations_count=3,
    compliance_rate=92.5
)
```

### Webhook Alerts (Slack/Discord)

```python
# Slack webhook
alert.send_webhook_alert(
    "⚠️ High PPE violation rate detected!",
    severity="error"
)
```

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop
docker-compose down
```

### Docker Services

1. **dashboard** - Web dashboard (port 5000)
2. **face_recognition** - Face recognition processor (optional)
3. **ppe_detection** - PPE detection processor (optional)

### Production Deployment

```bash
# Build for production
docker-compose -f docker-compose.prod.yml build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale face_recognition=3
```

## 🔧 Advanced Configuration

### Multi-Camera Setup

```python
# config.py
CAMERAS = {
    'entrance': {
        'id': 0,
        'location': 'Main Entrance',
        'type': 'face_recognition'
    },
    'warehouse': {
        'id': 1,
        'location': 'Warehouse Area',
        'type': 'ppe_detection'
    },
    'office': {
        'id': 2,
        'location': 'Office Floor',
        'type': 'both'
    }
}
```

### Custom PPE Rules

```python
# ppe_compliance/config/ppe_config.py
PPE_REQUIREMENTS = {
    'warehouse': ['helmet', 'vest', 'gloves'],
    'construction': ['helmet', 'vest', 'boots', 'gloves'],
    'laboratory': ['lab_coat', 'goggles', 'gloves']
}
```

### Performance Tuning

```python
# Adjust face recognition tolerance
FACE_TOLERANCE = 0.6  # Lower = stricter (0.4-0.7)

# Adjust PPE detection confidence
PPE_CONFIDENCE_THRESHOLD = 0.5  # (0.3-0.7)

# Frame skip for performance
PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame
```

## 📈 Monitoring & Analytics

### Generate Reports

```python
from database import Database

db = Database()

# Daily report
report = db.get_daily_report('2026-06-08')

# Export monthly data
db.export_data('attendance', 'monthly_attendance.json', days=30)
db.export_data('ppe_violations', 'monthly_violations.json', days=30)
```

### Grafana Integration (Optional)

1. Export data to Prometheus format
2. Configure Grafana dashboards
3. Set up alerts in Grafana

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_camera_utils.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run linter
ruff check .
```

## 🔒 Security Best Practices

1. **Change default passwords** in alert_config.json
2. **Enable HTTPS** for production deployment
3. **Implement authentication** for web dashboard
4. **Regular backups** of database and reference photos
5. **Update dependencies** regularly
6. **Restrict camera access** to authorized users only
7. **Review logs** regularly for suspicious activity

## 📱 Integration Examples

### Integrate with Existing System

```python
# your_app.py
from database import Database
from alert_system import AlertSystem

db = Database()
alert = AlertSystem()

# Log attendance from your system
def record_attendance(person_name, camera_id):
    att_id = db.log_attendance(person_name, 0.95, camera_id)
    print(f"Attendance logged: {att_id}")

# Check PPE violations
def check_ppe_compliance():
    violations = db.get_ppe_violations_today(resolved=False)
    
    if len(violations) > 5:
        alert.send_email_alert(
            "High PPE Violation Rate",
            f"Found {len(violations)} unresolved violations today"
        )
```

### Mobile App Integration

Use REST API endpoints:

```dart
// Flutter example
Future<Map<String, dynamic>> getAttendanceToday() async {
  final response = await http.get(
    Uri.parse('http://your-server:5000/api/attendance/today')
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  }
  throw Exception('Failed to load attendance');
}
```

## 🎓 Training Custom Models

### Add New People

```bash
# Add reference photo
cp photo.jpg faces/person_name.jpg

# System will automatically recognize new faces
```

### Train Custom PPE Model

```python
# Use YOLOv8 training
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
model.train(
    data='ppe_dataset.yaml',
    epochs=100,
    imgsz=640
)
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file

## 📞 Support

- Documentation: See all `*.md` files
- Issues: GitHub Issues
- Email: support@company.com

---

**Version**: 2.0.0  
**Built with**: Python, OpenCV, YOLOv8, Flask, SQLite  
**Last Updated**: 2026-06-08
