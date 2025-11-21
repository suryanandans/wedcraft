import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wedcrafts',
    'charset': 'utf8mb4'
}

def check_database():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("=== Users Table Structure ===")
        cursor.execute("DESCRIBE users")
        for row in cursor.fetchall():
            print(row)
        
        print("\n=== Sample User Data ===")
        cursor.execute("SELECT id, name, email FROM users LIMIT 3")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
        
        print("\n=== Admins Table Structure ===")
        cursor.execute("DESCRIBE admins")
        for row in cursor.fetchall():
            print(row)
        
        print("\n=== Sample Admin Data ===")
        cursor.execute("SELECT id, name, email FROM admins LIMIT 3")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
        
        print("\n=== Events Table Structure ===")
        cursor.execute("DESCRIBE events")
        for row in cursor.fetchall():
            print(row)
        
        print("\n=== Sample Event Data ===")
        cursor.execute("SELECT id, user_id, event_name FROM events LIMIT 3")
        for row in cursor.fetchall():
            print(f"Event ID: {row[0]}, User ID: {row[1]}, Event Name: {row[2]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()