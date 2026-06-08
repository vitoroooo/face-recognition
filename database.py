"""
Database module for face recognition and PPE compliance logging.
Stores attendance records, PPE violations, and system events.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class Database:
    """SQLite database handler for attendance and PPE compliance."""
    
    def __init__(self, db_path: str = "face_recognition.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        
        # Attendance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                camera_id TEXT,
                photo_path TEXT,
                status TEXT DEFAULT 'present'
            )
        """)
        
        # PPE violations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ppe_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                violation_type TEXT NOT NULL,
                missing_equipment TEXT,
                confidence REAL,
                camera_id TEXT,
                frame_path TEXT,
                severity TEXT DEFAULT 'medium',
                resolved BOOLEAN DEFAULT 0
            )
        """)
        
        # System events table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                description TEXT,
                metadata TEXT,
                severity TEXT DEFAULT 'info'
            )
        """)
        
        # Camera status table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT NOT NULL UNIQUE,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                resolution TEXT,
                fps INTEGER,
                location TEXT
            )
        """)
        
        self.conn.commit()
    
    # ========== ATTENDANCE METHODS ==========
    
    def log_attendance(self, person_name: str, confidence: float, 
                      camera_id: str = "default", photo_path: Optional[str] = None) -> int:
        """Log an attendance record."""
        self.cursor.execute("""
            INSERT INTO attendance (person_name, confidence, camera_id, photo_path)
            VALUES (?, ?, ?, ?)
        """, (person_name, confidence, camera_id, photo_path))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_attendance_today(self) -> List[Dict[str, Any]]:
        """Get all attendance records for today."""
        self.cursor.execute("""
            SELECT * FROM attendance 
            WHERE DATE(timestamp) = DATE('now')
            ORDER BY timestamp DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_attendance_by_person(self, person_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get attendance history for a specific person."""
        self.cursor.execute("""
            SELECT * FROM attendance 
            WHERE person_name = ? 
            AND timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """, (person_name, days))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_attendance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get attendance statistics."""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT person_name) as unique_persons,
                DATE(timestamp) as date
            FROM attendance 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (days,))
        
        stats = [dict(row) for row in self.cursor.fetchall()]
        
        # Calculate summary
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT person_name) as unique_persons,
                AVG(confidence) as avg_confidence
            FROM attendance 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        summary = dict(self.cursor.fetchone())
        
        return {
            "summary": summary,
            "daily_stats": stats
        }
    
    # ========== PPE VIOLATION METHODS ==========
    
    def log_ppe_violation(self, violation_type: str, missing_equipment: str,
                         person_name: Optional[str] = None, confidence: float = 0.0,
                         camera_id: str = "default", frame_path: Optional[str] = None,
                         severity: str = "medium") -> int:
        """Log a PPE violation."""
        self.cursor.execute("""
            INSERT INTO ppe_violations 
            (person_name, violation_type, missing_equipment, confidence, 
             camera_id, frame_path, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (person_name, violation_type, missing_equipment, confidence, 
              camera_id, frame_path, severity))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_ppe_violations_today(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get PPE violations for today."""
        query = "SELECT * FROM ppe_violations WHERE DATE(timestamp) = DATE('now')"
        params = []
        
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)
        
        query += " ORDER BY timestamp DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def resolve_violation(self, violation_id: int) -> bool:
        """Mark a violation as resolved."""
        self.cursor.execute("""
            UPDATE ppe_violations 
            SET resolved = 1 
            WHERE id = ?
        """, (violation_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_ppe_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get PPE violation statistics."""
        # Total violations
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_violations,
                COUNT(DISTINCT person_name) as persons_involved,
                SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved_count,
                SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) as pending_count
            FROM ppe_violations 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        summary = dict(self.cursor.fetchone())
        
        # By violation type
        self.cursor.execute("""
            SELECT 
                violation_type,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM ppe_violations 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY violation_type
            ORDER BY count DESC
        """, (days,))
        
        by_type = [dict(row) for row in self.cursor.fetchall()]
        
        # By severity
        self.cursor.execute("""
            SELECT 
                severity,
                COUNT(*) as count
            FROM ppe_violations 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY severity
            ORDER BY count DESC
        """, (days,))
        
        by_severity = [dict(row) for row in self.cursor.fetchall()]
        
        return {
            "summary": summary,
            "by_type": by_type,
            "by_severity": by_severity
        }
    
    # ========== SYSTEM EVENTS METHODS ==========
    
    def log_event(self, event_type: str, description: str, 
                  metadata: Optional[Dict] = None, severity: str = "info") -> int:
        """Log a system event."""
        metadata_json = json.dumps(metadata) if metadata else None
        
        self.cursor.execute("""
            INSERT INTO system_events (event_type, description, metadata, severity)
            VALUES (?, ?, ?, ?)
        """, (event_type, description, metadata_json, severity))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_recent_events(self, limit: int = 100, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent system events."""
        query = "SELECT * FROM system_events"
        params = []
        
        if severity:
            query += " WHERE severity = ?"
            params.append(severity)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(query, params)
        
        events = []
        for row in self.cursor.fetchall():
            event = dict(row)
            if event['metadata']:
                event['metadata'] = json.loads(event['metadata'])
            events.append(event)
        
        return events
    
    # ========== CAMERA STATUS METHODS ==========
    
    def update_camera_status(self, camera_id: str, status: str = "active",
                            resolution: Optional[str] = None, fps: Optional[int] = None,
                            location: Optional[str] = None):
        """Update camera status."""
        self.cursor.execute("""
            INSERT INTO camera_status (camera_id, status, resolution, fps, location, last_seen)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(camera_id) DO UPDATE SET
                status = excluded.status,
                resolution = COALESCE(excluded.resolution, resolution),
                fps = COALESCE(excluded.fps, fps),
                location = COALESCE(excluded.location, location),
                last_seen = CURRENT_TIMESTAMP
        """, (camera_id, status, resolution, fps, location))
        self.conn.commit()
    
    def get_camera_status(self, camera_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get camera status."""
        if camera_id:
            self.cursor.execute("SELECT * FROM camera_status WHERE camera_id = ?", (camera_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        else:
            self.cursor.execute("SELECT * FROM camera_status ORDER BY last_seen DESC")
            return [dict(row) for row in self.cursor.fetchall()]
    
    # ========== UTILITY METHODS ==========
    
    def cleanup_old_records(self, days: int = 90):
        """Remove records older than specified days."""
        tables = ['attendance', 'ppe_violations', 'system_events']
        
        for table in tables:
            self.cursor.execute(f"""
                DELETE FROM {table} 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (days,))
        
        self.conn.commit()
        self.log_event("cleanup", f"Removed records older than {days} days")
    
    def export_data(self, table: str, output_file: str, days: Optional[int] = None):
        """Export table data to JSON."""
        query = f"SELECT * FROM {table}"
        params = []
        
        if days:
            query += " WHERE timestamp >= datetime('now', '-' || ? || ' days')"
            params.append(days)
        
        self.cursor.execute(query, params)
        rows = [dict(row) for row in self.cursor.fetchall()]
        
        with open(output_file, 'w') as f:
            json.dump(rows, f, indent=2, default=str)
        
        return len(rows)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = Database()
    
    # Log some test data
    print("Testing database operations...")
    
    # Attendance
    att_id = db.log_attendance("John Doe", 0.95, "camera_1")
    print(f"✓ Logged attendance (ID: {att_id})")
    
    # PPE violation
    viol_id = db.log_ppe_violation(
        "missing_helmet", 
        "Safety Helmet",
        person_name="Jane Smith",
        confidence=0.87,
        severity="high"
    )
    print(f"✓ Logged PPE violation (ID: {viol_id})")
    
    # System event
    event_id = db.log_event(
        "system_start",
        "Face recognition system started",
        metadata={"version": "1.0", "cameras": 2}
    )
    print(f"✓ Logged system event (ID: {event_id})")
    
    # Get stats
    att_stats = db.get_attendance_stats(7)
    print(f"\n📊 Attendance Stats (7 days):")
    print(f"   Total records: {att_stats['summary']['total_records']}")
    print(f"   Unique persons: {att_stats['summary']['unique_persons']}")
    
    ppe_stats = db.get_ppe_stats(7)
    print(f"\n⚠️  PPE Violation Stats (7 days):")
    print(f"   Total violations: {ppe_stats['summary']['total_violations']}")
    print(f"   Resolved: {ppe_stats['summary']['resolved_count']}")
    print(f"   Pending: {ppe_stats['summary']['pending_count']}")
    
    print("\n✅ Database test complete!")
    
    db.close()
