#!/usr/bin/env python3

import sqlite3
import os

def migrate_custom_invitation_field():
    """Add custom_invitation_file column to events table"""
    
    db_path = "wedcraft.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'custom_invitation_file' in columns:
            print("custom_invitation_file column already exists!")
            return
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE events 
            ADD COLUMN custom_invitation_file TEXT
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'custom_invitation_file' in columns:
            print("✅ Successfully added custom_invitation_file column to events table")
        else:
            print("❌ Failed to add custom_invitation_file column")
        
        # Show current events count
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"📊 Total events in database: {count}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Migrating database to add custom invitation file support...")
    migrate_custom_invitation_field()
    print("✅ Migration completed!")