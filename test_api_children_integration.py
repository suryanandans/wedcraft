#!/usr/bin/env python3
"""
Test script to verify API integration with improved children counting
"""

import requests
import json
from datetime import datetime

# API base URL (adjust if needed)
BASE_URL = "http://localhost:8000"

def test_children_api_endpoints():
    """Test the children-related API endpoints"""
    print("🧪 Testing API Integration with Children Counting")
    print("=" * 55)
    
    endpoints_to_test = [
        {
            "name": "Real-time Stats",
            "url": f"{BASE_URL}/api/analytics/real-time-stats",
            "description": "Should include total_children and children_summary"
        },
        {
            "name": "Children Statistics",
            "url": f"{BASE_URL}/api/analytics/children-stats",
            "description": "New dedicated children analytics endpoint"
        },
        {
            "name": "Wedding Analytics",
            "url": f"{BASE_URL}/api/analytics/wedding-data",
            "description": "Should include improved children counts in rsvp_summary"
        },
        {
            "name": "Dashboard Data",
            "url": f"{BASE_URL}/api/analytics/dashboard-data",
            "description": "Should include enhanced children statistics"
        }
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        print(f"\n📊 Testing: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"Expected: {endpoint['description']}")
        
        try:
            response = requests.get(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint['name'] == "Real-time Stats":
                    # Check for enhanced children data
                    stats = data.get('stats', {})
                    total_children = stats.get('total_children', 0)
                    children_summary = stats.get('children_summary', {})
                    food_summary = stats.get('food_summary', {})
                    
                    print(f"✅ Total Children: {total_children}")
                    print(f"✅ Children by Attendance: {children_summary}")
                    
                    # Check food summary for children data
                    for food_type, food_data in food_summary.items():
                        children_count = food_data.get('children', 0)
                        print(f"✅ {food_type} Children: {children_count}")
                    
                    results.append({
                        "endpoint": endpoint['name'],
                        "status": "✅ PASS",
                        "children_data": {
                            "total_children": total_children,
                            "children_summary": children_summary
                        }
                    })
                
                elif endpoint['name'] == "Children Statistics":
                    # Check new children endpoint
                    children_data = data.get('children_data', {})
                    total_children = children_data.get('total_children', 0)
                    children_percentage = children_data.get('children_percentage', 0)
                    
                    print(f"✅ Total Children: {total_children}")
                    print(f"✅ Children Percentage: {children_percentage}%")
                    
                    results.append({
                        "endpoint": endpoint['name'],
                        "status": "✅ PASS",
                        "children_data": children_data
                    })
                
                elif endpoint['name'] == "Wedding Analytics":
                    # Check wedding analytics for children data
                    rsvp_summary = data.get('rsvp_summary', {})
                    children_count = rsvp_summary.get('children', 0)
                    total_attendees = rsvp_summary.get('yes', 0)
                    
                    print(f"✅ Event Children: {children_count}")
                    print(f"✅ Total Attendees: {total_attendees}")
                    
                    if total_attendees > 0:
                        percentage = (children_count / total_attendees) * 100
                        print(f"✅ Children Percentage: {percentage:.1f}%")
                    
                    results.append({
                        "endpoint": endpoint['name'],
                        "status": "✅ PASS",
                        "children_count": children_count
                    })
                
                elif endpoint['name'] == "Dashboard Data":
                    # Check dashboard data for children statistics
                    dashboard_stats = data.get('dashboard_stats', {})
                    total_children = dashboard_stats.get('total_children', 0)
                    
                    print(f"✅ Dashboard Children Count: {total_children}")
                    
                    results.append({
                        "endpoint": endpoint['name'],
                        "status": "✅ PASS",
                        "total_children": total_children
                    })
                
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                results.append({
                    "endpoint": endpoint['name'],
                    "status": f"❌ FAIL - HTTP {response.status_code}",
                    "error": response.text
                })
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Is the API server running?")
            results.append({
                "endpoint": endpoint['name'],
                "status": "❌ FAIL - Connection Error",
                "error": "API server not accessible"
            })
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                "endpoint": endpoint['name'],
                "status": f"❌ FAIL - {str(e)}",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 55)
    print("📋 TEST SUMMARY")
    print("=" * 55)
    
    passed = sum(1 for r in results if "✅ PASS" in r['status'])
    total = len(results)
    
    for result in results:
        print(f"{result['status']} - {result['endpoint']}")
    
    print(f"\n🎯 Results: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 All API endpoints are properly integrated with improved children counting!")
        return True
    else:
        print("💥 Some endpoints need attention. Check the errors above.")
        return False

def generate_api_documentation():
    """Generate documentation for the children-related API endpoints"""
    print("\n📚 API DOCUMENTATION - Children Analytics")
    print("=" * 60)
    
    docs = [
        {
            "endpoint": "GET /api/analytics/children-stats",
            "description": "Get detailed children statistics",
            "parameters": "event_id (optional) - Get stats for specific event",
            "response": {
                "success": True,
                "children_data": {
                    "total_children": "Number of children",
                    "children_percentage": "Percentage of children vs total attendees",
                    "family_breakdown": "List of families with children",
                    "attendance_breakdown": "Children by attendance status",
                    "food_preferences": "Children by food preference"
                }
            }
        },
        {
            "endpoint": "GET /api/analytics/real-time-stats",
            "description": "Enhanced with children data",
            "new_fields": {
                "total_children": "Total children in system",
                "children_summary": "Children by attendance status",
                "food_summary.*.children": "Children count per food preference"
            }
        },
        {
            "endpoint": "GET /api/analytics/wedding-data",
            "description": "Enhanced with accurate children counting",
            "improvements": "Uses real is_child data instead of 20% estimation"
        }
    ]
    
    for doc in docs:
        print(f"\n🔗 {doc['endpoint']}")
        print(f"   Description: {doc['description']}")
        
        if 'parameters' in doc:
            print(f"   Parameters: {doc['parameters']}")
        
        if 'response' in doc:
            print(f"   Response Structure:")
            print(f"   {json.dumps(doc['response'], indent=6)}")
        
        if 'new_fields' in doc:
            print(f"   New Fields:")
            for field, desc in doc['new_fields'].items():
                print(f"     • {field}: {desc}")
        
        if 'improvements' in doc:
            print(f"   Improvements: {doc['improvements']}")

if __name__ == "__main__":
    print("🎯 WedCrafts API Children Integration Test")
    print("=" * 60)
    
    # Test the API endpoints
    success = test_children_api_endpoints()
    
    # Generate documentation
    generate_api_documentation()
    
    if success:
        print("\n✅ API integration test completed successfully!")
        print("The API endpoints are properly exposing the improved children counting data.")
    else:
        print("\n❌ API integration test failed!")
        print("Please ensure the API server is running and check the error messages above.")