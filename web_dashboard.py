"""
Web Dashboard for Face Recognition & PPE Compliance Monitoring.
Real-time monitoring interface with Flask.
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from database import Database
from datetime import datetime, timedelta
import os
from pathlib import Path
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Initialize database
db = Database()

# Configuration
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'


# ========== WEB ROUTES ==========

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/attendance')
def attendance_page():
    """Attendance tracking page."""
    return render_template('attendance.html')


@app.route('/ppe')
def ppe_page():
    """PPE compliance monitoring page."""
    return render_template('ppe.html')


@app.route('/reports')
def reports_page():
    """Reports and analytics page."""
    return render_template('reports.html')


# ========== API ENDPOINTS ==========

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Attendance stats
        att_today = db.get_attendance_today()
        att_stats = db.get_attendance_stats(30)
        
        # PPE stats
        ppe_today = db.get_ppe_violations_today(resolved=False)
        ppe_stats = db.get_ppe_stats(30)
        
        # System events
        recent_events = db.get_recent_events(limit=10)
        
        # Camera status
        cameras = db.get_camera_status()
        
        return jsonify({
            'success': True,
            'data': {
                'attendance': {
                    'today': len(att_today),
                    'unique_today': len(set(r['person_name'] for r in att_today)),
                    'total_30d': att_stats['summary']['total_records'],
                    'avg_confidence': round(att_stats['summary'].get('avg_confidence', 0) or 0, 2)
                },
                'ppe': {
                    'violations_today': len(ppe_today),
                    'pending': ppe_stats['summary']['pending_count'],
                    'total_30d': ppe_stats['summary']['total_violations'],
                    'resolved_rate': round(
                        (ppe_stats['summary']['resolved_count'] / 
                         max(ppe_stats['summary']['total_violations'], 1)) * 100, 1
                    )
                },
                'cameras': {
                    'total': len(cameras),
                    'active': len([c for c in cameras if c['status'] == 'active'])
                },
                'recent_events': recent_events[:5]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/today')
def get_attendance_today():
    """Get today's attendance records."""
    try:
        records = db.get_attendance_today()
        return jsonify({'success': True, 'data': records})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/person/<person_name>')
def get_attendance_by_person(person_name):
    """Get attendance history for a person."""
    try:
        days = request.args.get('days', 7, type=int)
        records = db.get_attendance_by_person(person_name, days)
        return jsonify({'success': True, 'data': records})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/stats')
def get_attendance_stats():
    """Get attendance statistics."""
    try:
        days = request.args.get('days', 30, type=int)
        stats = db.get_attendance_stats(days)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ppe/violations/today')
def get_ppe_violations_today():
    """Get today's PPE violations."""
    try:
        resolved = request.args.get('resolved', None)
        if resolved is not None:
            resolved = resolved.lower() == 'true'
        
        violations = db.get_ppe_violations_today(resolved)
        return jsonify({'success': True, 'data': violations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ppe/stats')
def get_ppe_stats():
    """Get PPE violation statistics."""
    try:
        days = request.args.get('days', 30, type=int)
        stats = db.get_ppe_stats(days)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ppe/violation/<int:violation_id>/resolve', methods=['POST'])
def resolve_violation(violation_id):
    """Mark a violation as resolved."""
    try:
        success = db.resolve_violation(violation_id)
        if success:
            db.log_event(
                'violation_resolved',
                f'Violation #{violation_id} marked as resolved',
                metadata={'violation_id': violation_id}
            )
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Violation not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/events')
def get_events():
    """Get system events."""
    try:
        limit = request.args.get('limit', 100, type=int)
        severity = request.args.get('severity', None)
        
        events = db.get_recent_events(limit, severity)
        return jsonify({'success': True, 'data': events})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cameras')
def get_cameras():
    """Get camera status."""
    try:
        camera_id = request.args.get('camera_id', None)
        cameras = db.get_camera_status(camera_id)
        return jsonify({'success': True, 'data': cameras})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/<table>')
def export_data(table):
    """Export table data to JSON."""
    try:
        if table not in ['attendance', 'ppe_violations', 'system_events']:
            return jsonify({'success': False, 'error': 'Invalid table name'}), 400
        
        days = request.args.get('days', None, type=int)
        output_file = f'exports/{table}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Create exports directory
        os.makedirs('exports', exist_ok=True)
        
        count = db.export_data(table, output_file, days)
        
        return jsonify({
            'success': True,
            'data': {
                'file': output_file,
                'records': count,
                'table': table
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/report/daily')
def get_daily_report():
    """Get daily report."""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Parse date
        target_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Get attendance for the day
        db.cursor.execute("""
            SELECT * FROM attendance 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp
        """, (date,))
        attendance = [dict(row) for row in db.cursor.fetchall()]
        
        # Get violations for the day
        db.cursor.execute("""
            SELECT * FROM ppe_violations 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp
        """, (date,))
        violations = [dict(row) for row in db.cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'data': {
                'date': date,
                'attendance': {
                    'total': len(attendance),
                    'unique_persons': len(set(r['person_name'] for r in attendance)),
                    'records': attendance
                },
                'violations': {
                    'total': len(violations),
                    'resolved': len([v for v in violations if v['resolved']]),
                    'pending': len([v for v in violations if not v['resolved']]),
                    'records': violations
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ========== HELPER FUNCTIONS ==========

def create_static_files():
    """Create necessary static files and templates."""
    # Create directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    print("✓ Created static directories")


# ========== MAIN ==========

if __name__ == '__main__':
    print("🚀 Starting Face Recognition Web Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("📝 API documentation: http://localhost:5000/api/dashboard/stats")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Create necessary directories
    create_static_files()
    
    # Log startup event
    db.log_event(
        'dashboard_start',
        'Web dashboard started',
        metadata={'host': 'localhost', 'port': 5000}
    )
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
