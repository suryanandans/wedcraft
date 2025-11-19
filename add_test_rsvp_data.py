import sqlite3
from datetime import datetime

def add_test_rsvp_data():
    """Add test RSVP data with more non-vegetarian than vegetarian responses"""
    
    conn = sqlite3.connect('wedcraft.db')
    cursor = conn.cursor()
    
    try:
        # Clear existing test data (keep original data but add more)
        print("Adding test RSVP data with more non-vegetarian responses...")
        
        # Test data with more non-veg than veg
        test_rsvps = [
            (2, 'Patel Family', 'Yes', 4, 'Non-Vegetarian'),
            (2, 'Kumar Family', 'Yes', 3, 'Non-Vegetarian'),
            (2, 'Singh Family', 'Yes', 5, 'Non-Vegetarian'),
            (2, 'Sharma Family', 'Yes', 2, 'Non-Vegetarian'),
            (2, 'Gupta Family', 'Yes', 3, 'Non-Vegetarian'),
            (2, 'Reddy Family', 'Yes', 4, 'Non-Vegetarian'),
            (2, 'Jain Family', 'Yes', 2, 'Vegetarian'),
            (2, 'Agarwal Family', 'Yes', 3, 'Vegetarian'),
            (2, 'Mehta Family', 'Maybe', 2, 'Vegetarian'),
            (2, 'Shah Family', 'No', 0, None),
            (1, 'Chopra Family', 'Yes', 4, 'Non-Vegetarian'),
            (1, 'Malhotra Family', 'Yes', 3, 'Non-Vegetarian'),
            (1, 'Kapoor Family', 'Yes', 2, 'Non-Vegetarian'),
            (1, 'Bansal Family', 'Yes', 3, 'Vegetarian'),
            (1, 'Mittal Family', 'Maybe', 2, 'Vegetarian'),
        ]
        
        # Insert test data
        for rsvp in test_rsvps:
            cursor.execute('''
                INSERT INTO rsvp_responses (event_id, family_name, attendance, members_count, food_preference, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (*rsvp, datetime.now().isoformat()))
        
        conn.commit()
        print(f"✅ Added {len(test_rsvps)} test RSVP responses")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM rsvp_responses")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total RSVP responses in database: {total_count}")
        
        # Show food preference breakdown
        cursor.execute("""
            SELECT food_preference, COUNT(*) as count, SUM(members_count) as total_members
            FROM rsvp_responses 
            WHERE attendance = 'Yes' AND food_preference IS NOT NULL
            GROUP BY food_preference
        """)
        food_stats = cursor.fetchall()
        print("\n🍽️ Food preference breakdown:")
        for stat in food_stats:
            print(f"  {stat[0]}: {stat[1]} families, {stat[2]} members")
            
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_test_rsvp_data()