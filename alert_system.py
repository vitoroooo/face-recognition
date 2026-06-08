"""
Alert System for Face Recognition & PPE Compliance.
Sends notifications via email, SMS, or webhooks.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from typing import Optional, List
import json
import os
from pathlib import Path


class AlertSystem:
    """Handle alerts and notifications for violations and events."""
    
    def __init__(self, config_file: str = "alert_config.json"):
        """Initialize alert system with configuration."""
        self.config = self._load_config(config_file)
        self.enabled = self.config.get('enabled', False)
    
    def _load_config(self, config_file: str) -> dict:
        """Load alert configuration from file."""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "enabled": False,
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your-email@gmail.com",
                    "sender_password": "your-app-password",
                    "recipients": ["admin@company.com"]
                },
                "webhook": {
                    "enabled": False,
                    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                },
                "thresholds": {
                    "ppe_violations_per_hour": 5,
                    "unknown_persons_per_hour": 3
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    # ========== EMAIL ALERTS ==========
    
    def send_email_alert(self, subject: str, body: str, 
                        html_body: Optional[str] = None,
                        attachments: Optional[List[str]] = None) -> bool:
        """Send email alert."""
        if not self.enabled or not self.config['email']['enabled']:
            print("Email alerts disabled")
            return False
        
        try:
            email_config = self.config['email']
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipients'])
            
            # Attach text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-Disposition', 
                                         f'attachment; filename="{os.path.basename(file_path)}"')
                            msg.attach(img)
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
            print(f"✓ Email alert sent: {subject}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email alert: {e}")
            return False
    
    def send_ppe_violation_alert(self, violation_data: dict) -> bool:
        """Send alert for PPE violation."""
        subject = f"⚠️ PPE Violation Detected - {violation_data['missing_equipment']}"
        
        body = f"""
PPE Violation Alert
==================

Time: {violation_data['timestamp']}
Violation Type: {violation_data['violation_type']}
Missing Equipment: {violation_data['missing_equipment']}
Severity: {violation_data['severity']}
Person: {violation_data.get('person_name', 'Unknown')}
Camera: {violation_data['camera_id']}
Confidence: {violation_data['confidence']:.2%}

Please take immediate action to resolve this violation.

---
Automated alert from Face Recognition & PPE Compliance System
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
        <h2 style="margin: 0;">⚠️ PPE Violation Detected</h2>
    </div>
    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #ddd; border-top: none;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 150px;">Time:</td>
                <td style="padding: 8px;">{violation_data['timestamp']}</td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 8px; font-weight: bold;">Violation Type:</td>
                <td style="padding: 8px;">{violation_data['violation_type']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Missing Equipment:</td>
                <td style="padding: 8px;">{violation_data['missing_equipment']}</td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 8px; font-weight: bold;">Severity:</td>
                <td style="padding: 8px;"><span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px;">{violation_data['severity']}</span></td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Person:</td>
                <td style="padding: 8px;">{violation_data.get('person_name', 'Unknown')}</td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 8px; font-weight: bold;">Camera:</td>
                <td style="padding: 8px;">{violation_data['camera_id']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Confidence:</td>
                <td style="padding: 8px;">{violation_data['confidence']:.2%}</td>
            </tr>
        </table>
        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
            <strong>⚡ Action Required:</strong> Please take immediate action to resolve this violation.
        </div>
    </div>
    <div style="background: #343a40; color: #adb5bd; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 5px 5px;">
        Automated alert from Face Recognition & PPE Compliance System
    </div>
</body>
</html>
        """
        
        attachments = []
        if violation_data.get('frame_path') and os.path.exists(violation_data['frame_path']):
            attachments.append(violation_data['frame_path'])
        
        return self.send_email_alert(subject, body, html_body, attachments)
    
    def send_daily_report(self, attendance_count: int, violations_count: int,
                         compliance_rate: float) -> bool:
        """Send daily summary report."""
        subject = f"📊 Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
Daily Summary Report
===================

Date: {datetime.now().strftime('%Y-%m-%d')}

ATTENDANCE
----------
Total Check-ins: {attendance_count}

PPE COMPLIANCE
--------------
Total Violations: {violations_count}
Compliance Rate: {compliance_rate:.1f}%

---
Automated report from Face Recognition & PPE Compliance System
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px 5px 0 0;">
        <h2 style="margin: 0;">📊 Daily Summary Report</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #ddd; border-top: none;">
        <div style="background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #667eea;">👥 Attendance</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #333;">{attendance_count}</p>
            <p style="color: #666; margin: 0;">Total Check-ins</p>
        </div>
        <div style="background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #dc3545;">⚠️ PPE Violations</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #333;">{violations_count}</p>
            <p style="color: #666; margin: 0;">Total Violations</p>
        </div>
        <div style="background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #28a745;">✅ Compliance Rate</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #333;">{compliance_rate:.1f}%</p>
            <p style="color: #666; margin: 0;">Overall Compliance</p>
        </div>
    </div>
    <div style="background: #343a40; color: #adb5bd; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 5px 5px;">
        Automated report from Face Recognition & PPE Compliance System
    </div>
</body>
</html>
        """
        
        return self.send_email_alert(subject, body, html_body)
    
    # ========== WEBHOOK ALERTS ==========
    
    def send_webhook_alert(self, message: str, severity: str = "info") -> bool:
        """Send webhook alert (e.g., to Slack, Discord, Teams)."""
        if not self.enabled or not self.config['webhook']['enabled']:
            return False
        
        try:
            import requests
            
            webhook_url = self.config['webhook']['url']
            
            # Slack-style payload
            payload = {
                "text": message,
                "username": "PPE Monitor",
                "icon_emoji": ":warning:" if severity == "error" else ":information_source:"
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                print(f"✓ Webhook alert sent")
                return True
            else:
                print(f"✗ Webhook alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to send webhook alert: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    print("Testing Alert System...")
    
    # Initialize alert system
    alert = AlertSystem()
    
    print(f"\nAlert system enabled: {alert.enabled}")
    print(f"Email alerts enabled: {alert.config['email']['enabled']}")
    print(f"Webhook alerts enabled: {alert.config['webhook']['enabled']}")
    
    # Test PPE violation alert (will only work if email is configured)
    if alert.config['email']['enabled']:
        test_violation = {
            'timestamp': datetime.now().isoformat(),
            'violation_type': 'missing_helmet',
            'missing_equipment': 'Safety Helmet',
            'severity': 'high',
            'person_name': 'Test Person',
            'camera_id': 'camera_1',
            'confidence': 0.95
        }
        
        print("\nSending test PPE violation alert...")
        alert.send_ppe_violation_alert(test_violation)
        
        print("\nSending test daily report...")
        alert.send_daily_report(
            attendance_count=25,
            violations_count=3,
            compliance_rate=92.5
        )
    else:
        print("\n⚠️  Email alerts not configured. Edit alert_config.json to enable.")
        print("Example configuration:")
        print(json.dumps(alert.config, indent=2))
    
    print("\n✅ Alert system test complete!")
