import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import json

class DatabaseManager:
    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                location TEXT,
                organizer TEXT NOT NULL,
                source_url TEXT NOT NULL,
                event_type TEXT NOT NULL,
                tags TEXT, -- JSON string of tags
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, organizer, source_url)
            )
        """)
        
        # Scraping logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                events_found INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT 0,
                error_message TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_event(self, event_data: Dict[str, Any]) -> int:
        """Insert a new event into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(event_data.get('tags', []))
        
        cursor.execute("""
            INSERT OR REPLACE INTO events 
            (title, description, date, location, organizer, source_url, event_type, tags, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_data['title'],
            event_data.get('description'),
            event_data.get('date'),
            event_data.get('location'),
            event_data['organizer'],
            event_data['source_url'],
            event_data['event_type'],
            tags_json,
            datetime.now().isoformat()
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_events(self, limit: int = 50, event_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve events from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM events"
        params = []
        
        if event_type:
            query += " WHERE event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        events = [dict(row) for row in cursor.fetchall()]
        
        # Parse tags JSON
        for event in events:
            event['tags'] = json.loads(event['tags']) if event['tags'] else []
        
        conn.close()
        return events
    
    def log_scraping_result(self, source: str, events_found: int, success: bool, error_message: str = None):
        """Log scraping results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scraping_logs (source, events_found, success, error_message)
            VALUES (?, ?, ?, ?)
        """, (source, events_found, success, error_message))
        
        conn.commit()
        conn.close()