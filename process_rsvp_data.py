import sqlite3
import json
from count import WeddingAnalytics
from datetime import datetime

def process_and_store_analytics():
    """Process RSVP data through count.py and store in processed_analytics table"""
    
    # Initialize analytics engine
    analytics_engine = WeddingAnalytics()
    
    conn = sqlite3.connect('wedcraft.db')
    cursor = conn.cursor()
    
    try:
        # Get all events
        cursor.execute("SELECT id FROM events")
        events = cursor.fetchall()
        
        print(f"Processing analytics for {len(events)} events...")
        
        # Clear existing processed data
        cursor.execute("DELETE FROM processed_analytics")
        
        for event_row in events:
            event_id = event_row[0]
            print(f"Processing event {event_id}...")
            
            # Generate analytics for this event
            analytics = analytics_engine.generate_analytics(event_id)
            
            # Extract data from analytics
            rsvp_summary = analytics["rsvp_summary"]
            predictions = analytics["predictions"]
            analytics_data = analytics["analytics"]
            recommendations = analytics.get("recommendations", [])
            
            # Insert processed data
            cursor.execute('''
                INSERT INTO processed_analytics (
                    event_id, total_families, yes_responses, no_responses, maybe_responses,
                    predicted_attendance, veg_required, nonveg_required, children_count,
                    attendance_rate, response_rate, recommendations, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                rsvp_summary["total_families"],
                rsvp_summary["yes"],
                rsvp_summary["no"],
                rsvp_summary["maybe"],
                predictions["expected_attendance"],
                predictions["veg_required"],
                predictions["nonveg_required"],
                rsvp_summary["children"],
                analytics_data["attendance_rate"],
                analytics_data["response_rate"],
                json.dumps(recommendations),
                datetime.now().isoformat()
            ))
            
            print(f"  ✅ Event {event_id}: {rsvp_summary['total_families']} families, {predictions['expected_attendance']} predicted attendance")
        
        conn.commit()
        print(f"\n🎉 Successfully processed analytics for {len(events)} events!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM processed_analytics")
        count = cursor.fetchone()[0]
        print(f"📊 Total processed records: {count}")
        
        # Show sample data
        cursor.execute("""
            SELECT event_id, total_families, predicted_attendance, veg_required, nonveg_required
            FROM processed_analytics
            LIMIT 3
        """)
        sample_data = cursor.fetchall()
        print("\n📋 Sample processed data:")
        for row in sample_data:
            print(f"  Event {row[0]}: {row[1]} families → {row[2]} predicted attendance (Veg: {row[3]}, Non-veg: {row[4]})")
            
    except Exception as e:
        print(f"❌ Error processing analytics: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    process_and_store_analytics()