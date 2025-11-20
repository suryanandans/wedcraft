import mysql.connector
from mysql.connector import Error

def migrate_events():
    """
    Migrate all events to use event_name instead of bride_name/groom_name,
    then remove those columns from the database.
    """
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            database='wedcrafts',
            user='root',
            password='root'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Starting migration to remove bride_name and groom_name columns...")
            print("=" * 60)
            
            # Step 1: Migrate all events that have bride_name/groom_name but no event_name
            print("\nStep 1: Migrating events with bride_name/groom_name to event_name...")
            cursor.execute("""
                SELECT id, bride_name, groom_name, event_name 
                FROM events 
                WHERE event_name IS NULL OR event_name = ''
            """)
            events_to_migrate = cursor.fetchall()
            
            if events_to_migrate:
                print(f"Found {len(events_to_migrate)} events to migrate:")
                for event_id, bride_name, groom_name, event_name in events_to_migrate:
                    if bride_name and groom_name:
                        new_event_name = f"{bride_name} & {groom_name}'s Wedding"
                        cursor.execute("""
                            UPDATE events 
                            SET event_name = %s 
                            WHERE id = %s
                        """, (new_event_name, event_id))
                        print(f"  Event {event_id}: Set event_name to '{new_event_name}'")
                    elif bride_name:
                        new_event_name = f"{bride_name}'s Event"
                        cursor.execute("""
                            UPDATE events 
                            SET event_name = %s 
                            WHERE id = %s
                        """, (new_event_name, event_id))
                        print(f"  Event {event_id}: Set event_name to '{new_event_name}'")
                    elif groom_name:
                        new_event_name = f"{groom_name}'s Event"
                        cursor.execute("""
                            UPDATE events 
                            SET event_name = %s 
                            WHERE id = %s
                        """, (new_event_name, event_id))
                        print(f"  Event {event_id}: Set event_name to '{new_event_name}'")
                    else:
                        new_event_name = f"Event {event_id}"
                        cursor.execute("""
                            UPDATE events 
                            SET event_name = %s 
                            WHERE id = %s
                        """, (new_event_name, event_id))
                        print(f"  Event {event_id}: Set event_name to '{new_event_name}'")
                
                connection.commit()
                print(f"\nMigrated {len(events_to_migrate)} events successfully!")
            else:
                print("No events to migrate - all events already have event_name set.")
            
            # Step 2: Verify all events now have event_name
            print("\nStep 2: Verifying all events have event_name...")
            cursor.execute("SELECT COUNT(*) FROM events WHERE event_name IS NULL OR event_name = ''")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"WARNING: {count} events still don't have event_name!")
                return
            else:
                print("✓ All events have event_name set")
            
            # Step 3: Drop bride_name and groom_name columns
            print("\nStep 3: Removing bride_name and groom_name columns...")
            
            try:
                cursor.execute("ALTER TABLE events DROP COLUMN bride_name")
                print("✓ Dropped bride_name column")
            except Error as e:
                if "Can't DROP" in str(e):
                    print("  bride_name column already removed")
                else:
                    raise
            
            try:
                cursor.execute("ALTER TABLE events DROP COLUMN groom_name")
                print("✓ Dropped groom_name column")
            except Error as e:
                if "Can't DROP" in str(e):
                    print("  groom_name column already removed")
                else:
                    raise
            
            connection.commit()
            
            # Step 4: Verify final schema
            print("\nStep 4: Verifying final schema...")
            cursor.execute("DESCRIBE events")
            columns = cursor.fetchall()
            print("\nFinal events table structure:")
            for col in columns:
                print(f"  {col[0]}: {col[1]}")
            
            # Step 5: Show sample events
            print("\nStep 5: Sample migrated events:")
            cursor.execute("SELECT id, event_name, wedding_date FROM events LIMIT 5")
            sample_events = cursor.fetchall()
            for event_id, event_name, wedding_date in sample_events:
                print(f"  Event {event_id}: {event_name} ({wedding_date})")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("bride_name and groom_name columns have been removed.")
            print("All events now use event_name only.")
            print("=" * 60)

    except Error as e:
        print(f"Error during migration: {e}")
        if connection:
            connection.rollback()
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nDatabase connection closed.")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Event Schema Migration")
    print("Removing bride_name and groom_name columns")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Migrate all events to use event_name")
    print("2. Remove bride_name and groom_name columns")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
        migrate_events()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")