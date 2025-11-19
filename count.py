import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeddingAnalytics:
    def __init__(self, db_path: str = "wedcraft.db"):
        self.db_path = db_path
        self.model = None
        self._train_model()
    
    def _train_model(self):
        """Train ML model with dummy historical data for predictions"""
        np.random.seed(42)
        N = 800  # number of past weddings samples
        
        data = pd.DataFrame({
            "yes": np.random.randint(50, 300, N),
            "no": np.random.randint(10, 100, N),
            "maybe": np.random.randint(10, 120, N),
            "veg": np.random.randint(30, 200, N),
            "nonveg": np.random.randint(20, 150, N),
            "children": np.random.randint(0, 50, N),
        })
        
        # Actual attendance = yes + some of maybe - some cancellations
        data["actual_attendance"] = (
            data["yes"]
            + (data["maybe"] * np.random.uniform(0.25, 0.65))
            - np.random.randint(0, 10)
        ).astype(int)
        
        X = data[["yes", "no", "maybe", "veg", "nonveg", "children"]]
        y = data["actual_attendance"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=300, random_state=42)
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        print(f"🔹 Model trained successfully! MAE: {mae:.2f}")
    
    def fetch_rsvp_data(self, event_id: Optional[int] = None) -> Dict[str, Any]:
        """Fetch RSVP data from database and process it"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if event_id:
                query = "SELECT * FROM rsvp_responses WHERE event_id = ?"
                cursor.execute(query, (event_id,))
            else:
                query = "SELECT * FROM rsvp_responses"
                cursor.execute(query)
            
            rsvp_data = cursor.fetchall()
            
            # Process RSVP data
            yes_count = 0
            no_count = 0
            maybe_count = 0
            veg_count = 0
            nonveg_count = 0
            total_members = 0
            children_count = 0  # Estimate based on family size
            
            family_responses = []
            
            for row in rsvp_data:
                # row structure: (id, event_id, family_name, attendance, members_count, food_preference, created_at)
                attendance = row[3]
                members_count = row[4] or 0
                food_preference = row[5]
                
                family_responses.append({
                    "family_name": row[2],
                    "attendance": attendance,
                    "members_count": members_count,
                    "food_preference": food_preference
                })
                
                if attendance == "Yes":
                    yes_count += members_count
                    total_members += members_count
                    # Estimate children as 20% of family members
                    children_count += max(0, int(members_count * 0.2))
                    
                    if food_preference == "Vegetarian":
                        veg_count += members_count
                    elif food_preference == "Non-Vegetarian":
                        nonveg_count += members_count
                elif attendance == "No":
                    no_count += members_count
                elif attendance == "Maybe":
                    maybe_count += members_count
            
            return {
                "yes": yes_count,
                "no": no_count,
                "maybe": maybe_count,
                "veg": veg_count,
                "nonveg": nonveg_count,
                "children": children_count,
                "total_members": total_members,
                "family_responses": family_responses,
                "total_families": len(rsvp_data)
            }
            
        finally:
            conn.close()
    
    def fetch_form_responses(self, template_id: Optional[int] = None) -> Dict[str, Any]:
        """Fetch form response data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if template_id:
                query = "SELECT * FROM form_responses WHERE form_template_id = ?"
                cursor.execute(query, (template_id,))
            else:
                query = "SELECT * FROM form_responses"
                cursor.execute(query)
            
            form_data = cursor.fetchall()
            
            responses = []
            for row in form_data:
                # row structure: (id, form_template_id, response_data, submitted_by_email, submitted_by_name, ip_address, user_agent, created_at)
                try:
                    response_data = json.loads(row[2]) if row[2] else {}
                except json.JSONDecodeError:
                    response_data = {"raw_data": row[2]}
                
                responses.append({
                    "id": row[0],
                    "template_id": row[1],
                    "response_data": response_data,
                    "submitted_by": row[4] or "Anonymous",
                    "email": row[3],
                    "created_at": row[7]
                })
            
            return {
                "total_responses": len(responses),
                "responses": responses
            }
            
        finally:
            conn.close()
    
    def generate_analytics(self, event_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics for wedding data"""
        rsvp_data = self.fetch_rsvp_data(event_id)
        form_data = self.fetch_form_responses()
        
        # Prepare data for ML prediction
        live_data = {
            "yes": rsvp_data["yes"],
            "no": rsvp_data["no"],
            "maybe": rsvp_data["maybe"],
            "veg": rsvp_data["veg"],
            "nonveg": rsvp_data["nonveg"],
            "children": rsvp_data["children"]
        }
        
        # More realistic prediction calculation
        if self.model and any(live_data.values()) and rsvp_data["yes"] > 0:
            # Use ML model but cap it to reasonable bounds
            live_df = pd.DataFrame([live_data])
            X_live = live_df[["yes", "no", "maybe", "veg", "nonveg", "children"]]
            ml_prediction = int(self.model.predict(X_live)[0])
            
            # Cap ML prediction to be within reasonable bounds of actual data
            min_attendance = rsvp_data["yes"]  # At least confirmed attendees
            max_attendance = rsvp_data["yes"] + rsvp_data["maybe"]  # Maximum possible
            expected_attendance = max(min_attendance, min(ml_prediction, max_attendance + int(max_attendance * 0.2)))
        else:
            # Fallback calculation if no ML model or no data
            expected_attendance = rsvp_data["yes"] + int(rsvp_data["maybe"] * 0.4)
        
        # Food calculations with realistic estimates
        confirmed_attendees = rsvp_data["yes"]
        maybe_attendees = int(rsvp_data["maybe"] * 0.4)  # 40% of maybe responses typically attend
        total_expected = confirmed_attendees + maybe_attendees
        
        # If we have specific food preferences, use them with some buffer
        if rsvp_data["veg"] > 0 or rsvp_data["nonveg"] > 0:
            veg_required = rsvp_data["veg"] + int(maybe_attendees * 0.6)  # Assume 60% of maybe are veg
            nonveg_required = rsvp_data["nonveg"] + int(maybe_attendees * 0.4)  # Assume 40% of maybe are non-veg
        else:
            # If no specific preferences, estimate based on typical ratios
            veg_required = int(total_expected * 0.6)  # 60% vegetarian estimate
            nonveg_required = int(total_expected * 0.4)  # 40% non-vegetarian estimate
        
        # Additional analytics
        response_rate = (rsvp_data["total_families"] / max(1, rsvp_data["total_families"])) * 100
        attendance_rate = (rsvp_data["yes"] / max(1, rsvp_data["yes"] + rsvp_data["no"] + rsvp_data["maybe"])) * 100
        
        return {
            "rsvp_summary": rsvp_data,
            "form_summary": form_data,
            "predictions": {
                "expected_attendance": expected_attendance,
                "veg_required": veg_required,
                "nonveg_required": nonveg_required
            },
            "analytics": {
                "response_rate": round(response_rate, 2),
                "attendance_rate": round(attendance_rate, 2),
                "total_confirmed": rsvp_data["yes"],
                "total_declined": rsvp_data["no"],
                "total_pending": rsvp_data["maybe"]
            },
            "recommendations": self._generate_recommendations(rsvp_data, expected_attendance)
        }
    
    def _generate_recommendations(self, rsvp_data: Dict, expected_attendance: int) -> list:
        """Generate actionable recommendations based on data"""
        recommendations = []
        
        if rsvp_data["maybe"] > rsvp_data["yes"] * 0.3:
            recommendations.append("High number of 'Maybe' responses. Consider following up with these families.")
        
        if rsvp_data["veg"] > rsvp_data["nonveg"] * 2:
            recommendations.append("Vegetarian preference is significantly higher. Consider adjusting menu ratios.")
        
        if expected_attendance > rsvp_data["yes"] * 1.2:
            recommendations.append("Expected attendance is higher than confirmed. Prepare for additional guests.")
        
        if rsvp_data["children"] > expected_attendance * 0.25:
            recommendations.append("High number of children expected. Consider child-friendly arrangements.")
        
        return recommendations
    
    def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch and process all data from database tables"""
        logger.info("Fetching all data from database tables...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Fetch all table data
            data = {
                "users": self._fetch_users_data(cursor),
                "events": self._fetch_events_data(cursor),
                "rsvp_responses": self._fetch_all_rsvp_data(cursor),
                "form_responses": self._fetch_all_form_data(cursor),
                "analytics_summary": {}
            }
            
            # Process analytics for each event
            events_analytics = []
            for event in data["events"]:
                event_analytics = self.generate_analytics(event["id"])
                event_analytics["event_info"] = event
                events_analytics.append(event_analytics)
            
            data["analytics_summary"] = {
                "total_events": len(data["events"]),
                "total_users": len(data["users"]),
                "total_rsvp_responses": len(data["rsvp_responses"]),
                "total_form_responses": len(data["form_responses"]),
                "events_analytics": events_analytics,
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully processed data for {len(data['events'])} events")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching all data: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _fetch_users_data(self, cursor) -> List[Dict]:
        """Fetch users data"""
        cursor.execute("SELECT id, name, email, role, wedding_date, created_at FROM users")
        users = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "role": row[3],
                "wedding_date": row[4],
                "created_at": row[5]
            }
            for row in users
        ]
    
    def _fetch_events_data(self, cursor) -> List[Dict]:
        """Fetch events data"""
        cursor.execute("""
            SELECT id, user_id, bride_name, groom_name, wedding_date,
                   location, invitation_message, is_active, created_at
            FROM events
        """)
        events = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "bride_name": row[2],
                "groom_name": row[3],
                "wedding_date": row[4],
                "location": row[5],
                "invitation_message": row[6],
                "is_active": bool(row[7]),
                "created_at": row[8]
            }
            for row in events
        ]
    
    def _fetch_all_rsvp_data(self, cursor) -> List[Dict]:
        """Fetch all RSVP responses"""
        cursor.execute("""
            SELECT r.id, r.event_id, r.family_name, r.attendance,
                   r.members_count, r.food_preference, r.created_at,
                   e.bride_name, e.groom_name
            FROM rsvp_responses r
            LEFT JOIN events e ON r.event_id = e.id
        """)
        rsvps = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "event_id": row[1],
                "family_name": row[2],
                "attendance": row[3],
                "members_count": row[4],
                "food_preference": row[5],
                "created_at": row[6],
                "event_bride_name": row[7],
                "event_groom_name": row[8]
            }
            for row in rsvps
        ]
    
    def _fetch_all_form_data(self, cursor) -> List[Dict]:
        """Fetch all form responses"""
        cursor.execute("""
            SELECT fr.id, fr.form_template_id, fr.response_data,
                   fr.submitted_by_email, fr.submitted_by_name, fr.created_at,
                   ft.name as template_name
            FROM form_responses fr
            LEFT JOIN form_templates ft ON fr.form_template_id = ft.id
        """)
        forms = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "template_id": row[1],
                "response_data": json.loads(row[2]) if row[2] else {},
                "submitted_by_email": row[3],
                "submitted_by_name": row[4],
                "created_at": row[5],
                "template_name": row[6]
            }
            for row in forms
        ]
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics for dashboard"""
        logger.info("Generating real-time statistics...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get counts from all tables
            stats = {}
            
            # Users count
            cursor.execute("SELECT COUNT(*) FROM users")
            stats["total_users"] = cursor.fetchone()[0]
            
            # Events count
            cursor.execute("SELECT COUNT(*) FROM events")
            stats["total_events"] = cursor.fetchone()[0]
            
            # Active events count
            cursor.execute("SELECT COUNT(*) FROM events WHERE is_active = 1")
            stats["active_events"] = cursor.fetchone()[0]
            
            # RSVP responses count
            cursor.execute("SELECT COUNT(*) FROM rsvp_responses")
            stats["total_rsvp_responses"] = cursor.fetchone()[0]
            
            # Form responses count
            cursor.execute("SELECT COUNT(*) FROM form_responses")
            stats["total_form_responses"] = cursor.fetchone()[0]
            
            # Recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            cursor.execute("SELECT COUNT(*) FROM rsvp_responses WHERE created_at > ?", (week_ago,))
            stats["recent_rsvp_responses"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM form_responses WHERE created_at > ?", (week_ago,))
            stats["recent_form_responses"] = cursor.fetchone()[0]
            
            # Attendance summary
            cursor.execute("""
                SELECT attendance, COUNT(*) as count, SUM(members_count) as total_members
                FROM rsvp_responses
                GROUP BY attendance
            """)
            attendance_data = cursor.fetchall()
            
            stats["attendance_summary"] = {
                row[0]: {"families": row[1], "members": row[2] or 0}
                for row in attendance_data
            }
            
            # Food preference summary
            cursor.execute("""
                SELECT food_preference, COUNT(*) as count, SUM(members_count) as total_members
                FROM rsvp_responses
                WHERE attendance = 'Yes' AND food_preference IS NOT NULL
                GROUP BY food_preference
            """)
            food_data = cursor.fetchall()
            
            stats["food_summary"] = {
                row[0]: {"families": row[1], "members": row[2] or 0}
                for row in food_data
            }
            
            stats["generated_at"] = datetime.now().isoformat()
            
            logger.info("Real-time statistics generated successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating real-time stats: {str(e)}")
            raise
        finally:
            conn.close()

def print_analytics_report(analytics: Dict[str, Any]):
    """Print formatted analytics report"""
    print("========================================")
    print("        📊 WEDDING ANALYTICS REPORT      ")
    print("========================================")
    
    rsvp = analytics["rsvp_summary"]
    predictions = analytics["predictions"]
    stats = analytics["analytics"]
    
    print(f"Yes Responses        : {rsvp['yes']}")
    print(f"No Responses         : {rsvp['no']}")
    print(f"Maybe Responses      : {rsvp['maybe']}")
    print(f"Total Families       : {rsvp['total_families']}")
    print(f"Children Count       : {rsvp['children']}")
    print("----------------------------------------")
    print(f"👉 Expected Attendance: {predictions['expected_attendance']}")
    print(f"👉 Veg Required       : {predictions['veg_required']}")
    print(f"👉 Non-Veg Required   : {predictions['nonveg_required']}")
    print("----------------------------------------")
    print(f"📈 Attendance Rate    : {stats['attendance_rate']:.1f}%")
    print(f"📊 Response Rate      : {stats['response_rate']:.1f}%")
    
    if analytics["recommendations"]:
        print("----------------------------------------")
        print("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analytics["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    print("========================================")

# Main execution for testing
if __name__ == "__main__":
    analytics_engine = WeddingAnalytics()
    analytics = analytics_engine.generate_analytics()
    print_analytics_report(analytics)