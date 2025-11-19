import pymysql
from datetime import datetime

def create_analytics_table():
    """Create a table to store processed analytics data"""
    # MySQL connection configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'wedcrafts',
        'charset': 'utf8mb4'
    }
    
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Create processed_analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_analytics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT,
                total_families INT DEFAULT 0,
                yes_responses INT DEFAULT 0,
                no_responses INT DEFAULT 0,
                maybe_responses INT DEFAULT 0,
                predicted_attendance INT DEFAULT 0,
                veg_required INT DEFAULT 0,
                nonveg_required INT DEFAULT 0,
                children_count INT DEFAULT 0,
                attendance_rate VARCHAR(10) DEFAULT '0.0',
                response_rate VARCHAR(10) DEFAULT '0.0',
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
        cursor.execute("SHOW COLUMNS FROM processed_analytics")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_analytics_table()