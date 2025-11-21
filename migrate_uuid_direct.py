#!/usr/bin/env python3
"""
Direct MySQL Database migration script to convert user IDs from integers to UUIDs
This script will automatically run the migration without user prompts.
"""

import pymysql
import uuid
import sys
from datetime import datetime
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wedcrafts',
    'charset': 'utf8mb4'
}

def generate_uuid():
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def backup_database():
    """Create a backup of the database before migration"""
    try:
        backup_name = f"wedcrafts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_cmd = f"mysqldump -h {DB_CONFIG['host']} -u {DB_CONFIG['user']} -p{DB_CONFIG['password']} {DB_CONFIG['database']} > {backup_name}"
        
        print(f"Creating database backup: {backup_name}")
        os.system(backup_cmd)
        print(f"✅ Database backed up to: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def migrate_database():
    """Main migration function"""
    print("Starting MySQL UUID migration...")
    
    # Connect to the database
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("✅ Connected to MySQL database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        # Step 1: Add new UUID columns to users and admins tables
        print("\n📝 Step 1: Adding UUID columns...")
        
        cursor.execute("ALTER TABLE users ADD COLUMN id_uuid VARCHAR(36)")
        cursor.execute("ALTER TABLE admins ADD COLUMN id_uuid VARCHAR(36)")
        print("✅ Added UUID columns to users and admins tables")
        
        # Step 2: Generate UUIDs for existing users
        print("\n📝 Step 2: Generating UUIDs for existing users...")
        
        # Get all existing users
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        
        user_id_mapping = {}
        for (old_id,) in users:
            new_uuid = generate_uuid()
            user_id_mapping[old_id] = new_uuid
            cursor.execute("UPDATE users SET id_uuid = %s WHERE id = %s", (new_uuid, old_id))
        
        print(f"✅ Generated UUIDs for {len(users)} users")
        
        # Get all existing admins
        cursor.execute("SELECT id FROM admins")
        admins = cursor.fetchall()
        
        admin_id_mapping = {}
        for (old_id,) in admins:
            new_uuid = generate_uuid()
            admin_id_mapping[old_id] = new_uuid
            cursor.execute("UPDATE admins SET id_uuid = %s WHERE id = %s", (new_uuid, old_id))
        
        print(f"✅ Generated UUIDs for {len(admins)} admins")
        
        # Step 3: Add UUID column to events table and update foreign keys
        print("\n📝 Step 3: Updating events table...")
        
        cursor.execute("ALTER TABLE events ADD COLUMN user_id_uuid VARCHAR(36)")
        
        # Update events table with new UUIDs
        cursor.execute("SELECT id, user_id FROM events")
        events = cursor.fetchall()
        
        for event_id, old_user_id in events:
            # Check if it's a user ID or admin ID
            new_uuid = None
            if old_user_id in user_id_mapping:
                new_uuid = user_id_mapping[old_user_id]
            elif old_user_id in admin_id_mapping:
                new_uuid = admin_id_mapping[old_user_id]
            
            if new_uuid:
                cursor.execute("UPDATE events SET user_id_uuid = %s WHERE id = %s", (new_uuid, event_id))
            else:
                print(f"⚠️  Warning: Could not find UUID mapping for user_id {old_user_id} in event {event_id}")
        
        print(f"✅ Updated {len(events)} events with new UUIDs")
        
        # Step 4: Create new tables with UUID primary keys
        print("\n📝 Step 4: Creating new tables with UUID primary keys...")
        
        # Create new users table
        cursor.execute("""
            CREATE TABLE users_new (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                wedding_date VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_users_email (email)
            )
        """)
        
        # Create new admins table
        cursor.execute("""
            CREATE TABLE admins_new (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'admin',
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_admins_email (email)
            )
        """)
        
        # Create new events table
        cursor.execute("""
            CREATE TABLE events_new (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                event_name VARCHAR(255) NOT NULL,
                wedding_date VARCHAR(20) NOT NULL,
                location VARCHAR(500) NOT NULL,
                google_maps_link VARCHAR(1000),
                custom_invitation_url VARCHAR(1000),
                custom_invitation_file VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_events_user_id (user_id)
            )
        """)
        
        print("✅ Created new tables with UUID structure")
        
        # Step 5: Copy data to new tables
        print("\n📝 Step 5: Copying data to new tables...")
        
        # Copy users
        cursor.execute("""
            INSERT INTO users_new (id, name, email, hashed_password, role, wedding_date, is_active, created_at)
            SELECT id_uuid, name, email, hashed_password, role, wedding_date, is_active, created_at
            FROM users
        """)
        
        # Copy admins
        cursor.execute("""
            INSERT INTO admins_new (id, name, email, hashed_password, role, is_active, created_at)
            SELECT id_uuid, name, email, hashed_password, role, is_active, created_at
            FROM admins
        """)
        
        # Copy events
        cursor.execute("""
            INSERT INTO events_new (id, user_id, event_name, wedding_date, location, google_maps_link, custom_invitation_url, custom_invitation_file, is_active, created_at)
            SELECT id, user_id_uuid, event_name, wedding_date, location, google_maps_link, custom_invitation_url, custom_invitation_file, is_active, created_at
            FROM events
        """)
        
        print("✅ Copied all data to new tables")
        
        # Step 6: Drop old tables and rename new ones
        print("\n📝 Step 6: Replacing old tables...")
        
        cursor.execute("DROP TABLE users")
        cursor.execute("DROP TABLE admins")
        cursor.execute("DROP TABLE events")
        
        cursor.execute("RENAME TABLE users_new TO users")
        cursor.execute("RENAME TABLE admins_new TO admins")
        cursor.execute("RENAME TABLE events_new TO events")
        
        print("✅ Replaced old tables with new UUID-based tables")
        
        # Commit all changes
        connection.commit()
        print("\n🎉 Migration completed successfully!")
        
        # Print summary
        print(f"\n📊 Migration Summary:")
        print(f"   • Migrated {len(users)} users to UUID")
        print(f"   • Migrated {len(admins)} admins to UUID")
        print(f"   • Updated {len(events)} events with new user UUID references")
        print(f"   • All foreign key relationships preserved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()
        print("🔒 Database connection closed")

if __name__ == "__main__":
    print("🚀 MySQL UUID Migration Script (Direct)")
    print("=" * 50)
    
    # Create backup first
    print("Creating database backup...")
    if not backup_database():
        print("❌ Cannot proceed without backup. Exiting.")
        sys.exit(1)
    
    # Run migration directly
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Please restart your application to use the new UUID system.")
    else:
        print("\n❌ Migration failed!")
        print("💡 Your original database is backed up. You can restore it if needed.")
        sys.exit(1)