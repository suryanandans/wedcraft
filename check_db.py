import sqlite3

def check_database():
    conn = sqlite3.connect('wedcraft.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check RSVP responses data
    cursor.execute("SELECT COUNT(*) FROM rsvp_responses;")
    rsvp_count = cursor.fetchone()[0]
    print(f"RSVP Responses count: {rsvp_count}")
    
    if rsvp_count > 0:
        cursor.execute("SELECT * FROM rsvp_responses LIMIT 3;")
        rsvp_samples = cursor.fetchall()
        print("Sample RSVP data:", rsvp_samples)
    
    # Check form responses data
    cursor.execute("SELECT COUNT(*) FROM form_responses;")
    form_count = cursor.fetchone()[0]
    print(f"Form Responses count: {form_count}")
    
    conn.close()

if __name__ == "__main__":
    check_database()