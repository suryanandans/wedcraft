import sqlite3
from datetime import datetime

def create_analytics_table():
    """Create a table to store processed analytics data"""
    conn = sqlite3.connect('wedcraft.db')
    cursor = conn.cursor()
    
    try:
        # Create processed_analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                total_families INTEGER DEFAULT 0,
                yes_responses INTEGER DEFAULT 0,
                no_responses INTEGER DEFAULT 0,
                maybe_responses INTEGER DEFAULT 0,
                predicted_attendance INTEGER DEFAULT 0,
                veg_required INTEGER DEFAULT 0,
                nonveg_required INTEGER DEFAULT 0,
                children_count INTEGER DEFAULT 0,
                attendance_rate REAL DEFAULT 0.0,
                response_rate REAL DEFAULT 0.0,
                recommendations TEXT,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_analytics_event_id ON processed_analytics(event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_analytics_processed_at ON processed_analytics(processed_at)')
        
        conn.commit()
        print("✅ processed_analytics table created successfully!")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(processed_analytics)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_analytics_table()