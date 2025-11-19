#!/usr/bin/env python3

import pymysql
import os

def migrate_custom_invitation_field():
    """Add custom_invitation_file column to events table"""
    
    # MySQL connection configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'wedcrafts',
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to database
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("SHOW COLUMNS FROM events LIKE 'custom_invitation_file'")
        columns = cursor.fetchall()
        
        if len(columns) > 0:
            print("custom_invitation_file column already exists!")
            return
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN custom_invitation_file VARCHAR(500)
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("SHOW COLUMNS FROM events LIKE 'custom_invitation_file'")
        columns = cursor.fetchall()
        
        if len(columns) > 0:
            print("✅ Successfully added custom_invitation_file column to events table")
        else:
            print("❌ Failed to add custom_invitation_file column")
        
        # Show current events count
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"📊 Total events in database: {count}")
        
    except pymysql.Error as e:
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