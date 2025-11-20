"""
Script to remove unused form_templates and form_responses tables
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

def remove_form_tables():
    """Remove form_templates and form_responses tables"""
    connection = None
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Connected to database successfully")
        
        # Check if form_responses table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'form_responses'
        """)
        form_responses_exists = cursor.fetchone()[0] > 0
        
        # Check if form_templates table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'form_templates'
        """)
        form_templates_exists = cursor.fetchone()[0] > 0
        
        # Drop form_responses table first (due to foreign key dependency)
        if form_responses_exists:
            print("Dropping form_responses table...")
            cursor.execute("DROP TABLE IF EXISTS form_responses")
            print("✓ form_responses table removed successfully")
        else:
            print("✓ form_responses table doesn't exist")
        
        # Drop form_templates table
        if form_templates_exists:
            print("Dropping form_templates table...")
            cursor.execute("DROP TABLE IF EXISTS form_templates")
            print("✓ form_templates table removed successfully")
        else:
            print("✓ form_templates table doesn't exist")
        
        # Commit changes
        connection.commit()
        print("\n✓ Database cleanup completed successfully!")
        
        # Show remaining tables
        print("\nRemaining tables in database:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
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
    print("Remove Unused Form Templates Tables Script")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        remove_form_tables()
        print("\n" + "=" * 60)
        print("Cleanup completed successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("Cleanup failed!")
        print("=" * 60)
        print(f"Error: {e}")