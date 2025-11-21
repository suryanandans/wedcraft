#!/usr/bin/env python3
"""
Database migration script to convert user IDs from integers to UUIDs
This script will:
1. Create new UUID columns
2. Generate UUIDs for existing users and admins
3. Update all foreign key references
4. Drop old integer columns
5. Rename UUID columns to replace the old ones
"""

import sqlite3
import uuid
import sys
from datetime import datetime

def generate_uuid():
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def migrate_database():
    """Main migration function"""
    print("Starting UUID migration...")
    
    # Connect to the database
    try:
        conn = sqlite3.connect('wedcraft.db')
        cursor = conn.cursor()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        # Step 1: Add new UUID columns to users and admins tables
        print("\n📝 Step 1: Adding UUID columns...")
        
        cursor.execute("ALTER TABLE users ADD COLUMN id_uuid TEXT")
        cursor.execute("ALTER TABLE admins ADD COLUMN id_uuid TEXT")
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
            cursor.execute("UPDATE users SET id_uuid = ? WHERE id = ?", (new_uuid, old_id))
        
        print(f"✅ Generated UUIDs for {len(users)} users")
        
        # Get all existing admins
        cursor.execute("SELECT id FROM admins")
        admins = cursor.fetchall()
        
        admin_id_mapping = {}
        for (old_id,) in admins:
            new_uuid = generate_uuid()
            admin_id_mapping[old_id] = new_uuid
            cursor.execute("UPDATE admins SET id_uuid = ? WHERE id = ?", (new_uuid, old_id))
        
        print(f"✅ Generated UUIDs for {len(admins)} admins")
        
        # Step 3: Add UUID column to events table and update foreign keys
        print("\n📝 Step 3: Updating events table...")
        
        cursor.execute("ALTER TABLE events ADD COLUMN user_id_uuid TEXT")
        
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
                cursor.execute("UPDATE events SET user_id_uuid = ? WHERE id = ?", (new_uuid, event_id))
            else:
                print(f"⚠️  Warning: Could not find UUID mapping for user_id {old_user_id} in event {event_id}")
        
        print(f"✅ Updated {len(events)} events with new UUIDs")
        
        # Step 4: Create new tables with UUID primary keys
        print("\n📝 Step 4: Creating new tables with UUID primary keys...")
        
        # Create new users table
        cursor.execute("""
            CREATE TABLE users_new (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                wedding_date TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create new admins table
        cursor.execute("""
            CREATE TABLE admins_new (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create new events table
        cursor.execute("""
            CREATE TABLE events_new (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_name TEXT NOT NULL,
                wedding_date TEXT NOT NULL,
                location TEXT NOT NULL,
                google_maps_link TEXT,
                custom_invitation_url TEXT,
                custom_invitation_file TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        cursor.execute("ALTER TABLE admins_new RENAME TO admins")
        cursor.execute("ALTER TABLE events_new RENAME TO events")
        
        print("✅ Replaced old tables with new UUID-based tables")
        
        # Step 7: Create indexes
        print("\n📝 Step 7: Creating indexes...")
        
        cursor.execute("CREATE INDEX idx_users_id ON users(id)")
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX idx_admins_id ON admins(id)")
        cursor.execute("CREATE INDEX idx_admins_email ON admins(email)")
        cursor.execute("CREATE INDEX idx_events_user_id ON events(user_id)")
        
        print("✅ Created indexes")
        
        # Commit all changes
        conn.commit()
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
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("🔒 Database connection closed")

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    
    try:
        backup_name = f"wedcraft_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('wedcraft.db', backup_name)
        print(f"✅ Database backed up to: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

if __name__ == "__main__":
    print("🚀 UUID Migration Script")
    print("=" * 50)
    
    # Create backup first
    print("Creating database backup...")
    if not backup_database():
        print("❌ Cannot proceed without backup. Exiting.")
        sys.exit(1)
    
    # Ask for confirmation
    response = input("\n⚠️  This will modify your database structure. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Please restart your application to use the new UUID system.")
    else:
        print("\n❌ Migration failed!")
        print("💡 Your original database is backed up. You can restore it if needed.")
        sys.exit(1)