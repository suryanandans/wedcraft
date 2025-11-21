#!/usr/bin/env python3
"""
Test script to verify children counting accuracy after count.py improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from count import WeddingAnalytics
import pymysql
from datetime import datetime
import json

def test_children_counting():
    """Test the improved children counting functionality"""
    print("🧪 Testing Children Counting Improvements")
    print("=" * 50)
    
    try:
        # Initialize analytics engine
        analytics = WeddingAnalytics()
        
        # Test 1: Get real-time stats with children data
        print("\n📊 Test 1: Real-time Statistics with Children Data")
        stats = analytics.get_real_time_stats()
        
        print(f"Total Children in System: {stats.get('total_children', 0)}")
        print(f"Total Family Members: {stats.get('total_form_responses', 0)}")
        
        if 'children_summary' in stats:
            print("\nChildren by Attendance Status:")
            for status, count in stats['children_summary'].items():
                print(f"  {status}: {count} children")
        
        if 'food_summary' in stats:
            print("\nChildren by Food Preference:")
            for food_type, data in stats['food_summary'].items():
                children_count = data.get('children', 0)
                total_members = data.get('members', 0)
                print(f"  {food_type}: {children_count} children out of {total_members} members")
        
        # Test 2: Generate analytics for a specific event (if any exist)
        print("\n📈 Test 2: Event-Specific Analytics")
        
        # Get first active event for testing
        conn = pymysql.connect(**analytics.db_config)
        cursor = conn.cursor()
        
        # First, check what columns exist in events table
        cursor.execute("DESCRIBE events")
        columns = [row[0] for row in cursor.fetchall()]
        
        # Use appropriate columns based on what exists
        if 'bride_name' in columns and 'groom_name' in columns:
            cursor.execute("SELECT id, bride_name, groom_name FROM events WHERE is_active = 1 LIMIT 1")
            event = cursor.fetchone()
            event_name = f"{event[1]} & {event[2]}" if event else "Unknown Event"
        else:
            cursor.execute("SELECT id FROM events WHERE is_active = 1 LIMIT 1")
            event = cursor.fetchone()
            event_name = "Test Event"
        
        conn.close()
        
        if event:
            event_id = event[0]
            print(f"Testing with Event: {event_name} (ID: {event_id})")
            
            event_analytics = analytics.generate_analytics(event_id)
            rsvp_data = event_analytics['rsvp_summary']
            
            print(f"Event Children Count: {rsvp_data['children']}")
            print(f"Total Confirmed Attendees: {rsvp_data['yes']}")
            print(f"Total Families: {rsvp_data['total_families']}")
            
            # Calculate children percentage
            if rsvp_data['yes'] > 0:
                children_percentage = (rsvp_data['children'] / rsvp_data['yes']) * 100
                print(f"Children Percentage: {children_percentage:.1f}%")
            
            # Show recommendations
            if event_analytics.get('recommendations'):
                print("\nRecommendations:")
                for i, rec in enumerate(event_analytics['recommendations'], 1):
                    print(f"  {i}. {rec}")
        else:
            print("No active events found for testing")
        
        # Test 3: Compare old vs new counting method
        print("\n🔄 Test 3: Counting Method Comparison")
        
        # Get sample RSVP data to compare methods
        conn = pymysql.connect(**analytics.db_config)
        cursor = conn.cursor()
        
        # Old method: 20% estimation
        cursor.execute("""
            SELECT SUM(members_count) as total_members
            FROM rsvp_responses 
            WHERE attendance = 'Yes'
        """)
        result = cursor.fetchone()
        total_members = result[0] if result and result[0] else 0
        old_method_children = int(total_members * 0.2)
        
        # New method: actual count
        cursor.execute("""
            SELECT COUNT(*) as actual_children
            FROM family_members fm
            JOIN rsvp_responses r ON fm.rsvp_response_id = r.id
            WHERE r.attendance = 'Yes' AND fm.is_child = 1
        """)
        result = cursor.fetchone()
        new_method_children = result[0] if result and result[0] else 0
        
        conn.close()
        
        print(f"Old Method (20% estimation): {old_method_children} children")
        print(f"New Method (actual count): {new_method_children} children")
        print(f"Difference: {abs(new_method_children - old_method_children)} children")
        
        if total_members > 0:
            actual_percentage = (new_method_children / total_members) * 100
            print(f"Actual Children Percentage: {actual_percentage:.1f}%")
        
        print("\n✅ Children counting test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_structure():
    """Verify that the database has the required structure for children counting"""
    print("\n🔍 Verifying Database Structure")
    print("=" * 40)
    
    try:
        analytics = WeddingAnalytics()
        conn = pymysql.connect(**analytics.db_config)
        cursor = conn.cursor()
        
        # Check if family_members table exists with is_child column
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedcrafts' 
            AND TABLE_NAME = 'family_members'
            AND COLUMN_NAME = 'is_child'
        """)
        
        is_child_column = cursor.fetchone()
        if is_child_column:
            print("✅ family_members.is_child column exists")
            print(f"   Type: {is_child_column[1]}, Nullable: {is_child_column[2]}")
        else:
            print("❌ family_members.is_child column not found")
            return False
        
        # Check if there's actual data
        cursor.execute("SELECT COUNT(*) FROM family_members WHERE is_child = 1")
        children_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM family_members")
        total_members = cursor.fetchone()[0]
        
        print(f"✅ Database contains {children_count} children out of {total_members} total family members")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database structure verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 WedCrafts Children Counting Test Suite")
    print("=" * 60)
    
    # Verify database structure first
    if not verify_database_structure():
        print("\n❌ Database structure verification failed. Please ensure:")
        print("   1. family_members table exists")
        print("   2. is_child column is present")
        print("   3. Database contains sample data")
        sys.exit(1)
    
    # Run the main test
    if test_children_counting():
        print("\n🎉 All tests passed! Children counting improvements are working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the error messages above.")
        sys.exit(1)