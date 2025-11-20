"""
Migration script to add google_maps_link and custom_invitation_url fields to events table
and remove invitation_message field if it exists
"""
import pymysql
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wedcrafts',
    'charset': 'utf8mb4'
}

def migrate_database():
    """Add new fields to events table and remove old invitation_message field"""
    connection = None
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Connected to database successfully")
        
        # Check if google_maps_link column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'events' 
            AND COLUMN_NAME = 'google_maps_link'
        """)
        google_maps_exists = cursor.fetchone()[0] > 0
        
        # Check if custom_invitation_url column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'events' 
            AND COLUMN_NAME = 'custom_invitation_url'
        """)
        custom_url_exists = cursor.fetchone()[0] > 0
        
        # Check if invitation_message column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'events' 
            AND COLUMN_NAME = 'invitation_message'
        """)
        invitation_message_exists = cursor.fetchone()[0] > 0
        
        # Add google_maps_link column if it doesn't exist
        if not google_maps_exists:
            print("Adding google_maps_link column...")
            cursor.execute("""
                ALTER TABLE events 
                ADD COLUMN google_maps_link VARCHAR(1000) NULL
                AFTER location
            """)
            print("✓ google_maps_link column added successfully")
        else:
            print("✓ google_maps_link column already exists")
        
        # Add custom_invitation_url column if it doesn't exist
        if not custom_url_exists:
            print("Adding custom_invitation_url column...")
            cursor.execute("""
                ALTER TABLE events 
                ADD COLUMN custom_invitation_url VARCHAR(1000) NULL
                AFTER google_maps_link
            """)
            print("✓ custom_invitation_url column added successfully")
        else:
            print("✓ custom_invitation_url column already exists")
        
        # Remove invitation_message column if it exists
        if invitation_message_exists:
            print("Removing invitation_message column...")
            cursor.execute("""
                ALTER TABLE events 
                DROP COLUMN invitation_message
            """)
            print("✓ invitation_message column removed successfully")
        else:
            print("✓ invitation_message column doesn't exist (already removed or never created)")
        
        # Commit changes
        connection.commit()
        print("\n✓ Database migration completed successfully!")
        
        # Show current table structure
        print("\nCurrent events table structure:")
        cursor.execute("DESCRIBE events")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[0]}: {column[1]} {'NULL' if column[2] == 'YES' else 'NOT NULL'}")
        
    except pymysql.Error as e:
        print(f"\n✗ Database error: {e}")
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("\nDatabase connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("Event Fields Migration Script")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        migrate_database()
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        print(f"Error: {e}")