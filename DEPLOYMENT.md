# Deployment Guide

Panduan lengkap untuk deployment Face Recognition & PPE Compliance System.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop services
docker-compose down
```

Dashboard akan tersedia di: http://localhost:5000

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements_web.txt

# Download PPE model
python download_ppe_model.py

# Run web dashboard
python web_dashboard.py
```

## 📦 Production Deployment

### 1. Database Setup

Database SQLite akan dibuat otomatis. Untuk production dengan traffic tinggi, pertimbangkan PostgreSQL:

```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary

# Update database.py untuk PostgreSQL connection
```

### 2. Web Server Configuration

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app
```

### 3. Alert System Configuration

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
    "recipients": ["admin@company.com", "security@company.com"]
  },
  "webhook": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

#### Gmail Setup (untuk email alerts):

1. Enable 2-Factor Authentication di Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Gunakan App Password di `alert_config.json`

### 4. Systemd Service (Linux)

Create `/etc/systemd/system/face-recognition.service`:

```ini
[Unit]
Description=Face Recognition & PPE Compliance System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable face-recognition
sudo systemctl start face-recognition
sudo systemctl status face-recognition
```

### 5. Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  dashboard:
    build: .
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/face_recognition
    depends_on:
      - db

  db:
    image: postgres:15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=face_recognition
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=secure_password

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dashboard

volumes:
  postgres_data:
```

Run:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable authentication for dashboard
- [ ] Restrict camera access
- [ ] Review log retention policies
- [ ] Update dependencies regularly

## 📊 Monitoring

### Health Checks

```bash
# Check dashboard health
curl http://localhost:5000/api/dashboard/stats

# Check Docker services
docker-compose ps
```

### Log Management

```bash
# View logs
tail -f logs/system.log

# Docker logs
docker-compose logs -f
```

### Database Maintenance

```python
from database import Database

db = Database()

# Cleanup old records (older than 90 days)
db.cleanup_old_records(90)

# Export data
db.export_data('attendance', 'backup_attendance.json', days=30)
```

## 🔄 Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
cp face_recognition.db "$BACKUP_DIR/face_recognition_$DATE.db"

# Backup reference photos
tar -czf "$BACKUP_DIR/faces_$DATE.tar.gz" faces/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Setup cron job:

```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

## 🌐 Scaling

### Horizontal Scaling

1. **Load Balancer**: Gunakan Nginx/HAProxy untuk distribute traffic
2. **Multiple Workers**: Scale gunicorn workers berdasarkan CPU cores
3. **Database**: Migrate ke PostgreSQL dengan read replicas
4. **Caching**: Implement Redis untuk cache API responses

### Performance Optimization

```python
# Enable caching in web_dashboard.py
from flask_caching import Cache

app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

@app.route('/api/dashboard/stats')
@cache.cached(timeout=30)  # Cache for 30 seconds
def get_dashboard_stats():
    # ...
```

## 📱 Mobile Access

Dashboard sudah responsive. Untuk app native, gunakan API endpoints:

```bash
# Get attendance today
GET /api/attendance/today

# Get PPE violations
GET /api/ppe/violations/today

# Get statistics
GET /api/dashboard/stats
```

## 🆘 Troubleshooting

### Dashboard tidak bisa diakses

```bash
# Check if service running
curl http://localhost:5000/api/dashboard/stats

# Check firewall
sudo ufw status
sudo ufw allow 5000/tcp

# Check logs
tail -f logs/system.log
```

### Email alerts tidak terkirim

```bash
# Test email configuration
python alert_system.py

# Check alert_config.json
cat alert_config.json
```

### Database errors

```bash
# Check database integrity
sqlite3 face_recognition.db "PRAGMA integrity_check;"

# Rebuild database (WARNING: data loss)
rm face_recognition.db
python database.py
```

## 📞 Support

Untuk issues dan questions:
- GitHub Issues: [Create Issue]
- Email: support@company.com
- Documentation: [Wiki](https://github.com/your-repo/wiki)

---

**Version**: 2.0.0  
**Last Updated**: 2026-06-08
