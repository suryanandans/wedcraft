#!/usr/bin/env python3
"""
Database migration script to add event_name column to events table
"""

import pymysql
import sys

def migrate_database():
    """Add event_name column to events table and make bride_name/groom_name nullable"""
    try:
        # MySQL connection configuration
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'wedcrafts',
            'charset': 'utf8mb4'
        }
        
        # Connect to database
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if event_name column already exists
        cursor.execute("SHOW COLUMNS FROM events LIKE 'event_name'")
        columns = cursor.fetchall()
        
        if len(columns) > 0:
            print("✅ event_name column already exists, skipping migration")
            return
        
        # Add event_name column
        print("📝 Adding event_name column to events table...")
        cursor.execute("ALTER TABLE events ADD COLUMN event_name VARCHAR(255)")
        
        # Since SQLite doesn't support modifying column constraints directly,
        # we'll create a new table with the updated schema and migrate data
        print("🔄 Creating new events table with updated schema...")
        
        # Create new table with updated schema
        cursor.execute("""
            CREATE TABLE events_new (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                event_name TEXT,
                bride_name TEXT,
                groom_name TEXT,
                wedding_date TEXT NOT NULL,
                location TEXT NOT NULL,
                invitation_message TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from old table to new table
        print("📋 Migrating existing data...")
        cursor.execute("""
            INSERT INTO events_new (id, user_id, bride_name, groom_name, wedding_date, location, invitation_message, is_active, created_at)
            SELECT id, user_id, bride_name, groom_name, wedding_date, location, invitation_message, is_active, created_at
            FROM events
        """)
        
        # Drop old table and rename new table
        print("🔄 Replacing old table with new schema...")
        cursor.execute("DROP TABLE events")
        cursor.execute("ALTER TABLE events_new RENAME TO events")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        print(f"📊 Migrated {event_count} events")
        
        # Show sample of migrated data
        cursor.execute("SELECT id, event_name, bride_name, groom_name FROM events LIMIT 3")
        sample_events = cursor.fetchall()
        print("\n📋 Sample migrated events:")
        for event in sample_events:
            event_id, event_name, bride_name, groom_name = event
            display_name = event_name if event_name else f"{bride_name} & {groom_name}"
            print(f"   Event {event_id}: {display_name}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()