#!/usr/bin/env python3
"""
Database initialization script for WedCraft
This script creates the database tables and populates them with initial data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, User, Admin, Event, RSVPResponse, get_password_hash
from datetime import datetime

# Database configuration
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/wedcrafts"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database with tables and sample data"""
    print("🚀 Initializing WedCraft Database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create default admin if not exists
        admin = db.query(Admin).filter(Admin.email == "admin@wedcraft.com").first()
        if not admin:
            admin = Admin(
                name="WedCraft Admin",
                email="admin@wedcraft.com",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
            print("✅ Default admin created: admin@wedcraft.com / admin123")
        else:
            print("ℹ️  Default admin already exists")
        
        # Create sample users if not exist
        sample_users = [
            {
                "name": "John & Sarah Smith",
                "email": "john.sarah@example.com",
                "password": "password123",
                "role": "user",
                "wedding_date": "2024-06-15"
            },
            {
                "name": "Michael Johnson",
                "email": "michael@example.com",
                "password": "user123",
                "role": "user",
                "wedding_date": "2024-08-20"
            },
            {
                "name": "Emma Wilson",
                "email": "emma@example.com",
                "password": "user123",
                "role": "user",
                "wedding_date": "2024-10-12"
            }
        ]
        
        for user_data in sample_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    wedding_date=user_data["wedding_date"]
                )
                db.add(user)
                print(f"✅ Sample user created: {user_data['email']} / {user_data['password']}")
        
        # Create sample events
        user = db.query(User).filter(User.email == "john.sarah@example.com").first()
        if user:
            existing_event = db.query(Event).filter(Event.user_id == user.id).first()
            if not existing_event:
                event = Event(
                    user_id=user.id,
                    bride_name="Sarah Johnson",
                    groom_name="John Smith",
                    wedding_date="2024-06-15",
                    location="Grand Palace Hotel, Mumbai",
                    invitation_message="We would be honored to have you celebrate this special day with us as we begin our journey together as husband and wife."
                )
                db.add(event)
                print("✅ Sample wedding event created")
                
                # Create sample RSVP responses
                sample_rsvps = [
                    {
                        "family_name": "The Johnson Family",
                        "attendance": "Yes",
                        "members_count": 4,
                        "food_preference": "veg"
                    },
                    {
                        "family_name": "The Brown Family",
                        "attendance": "Yes",
                        "members_count": 2,
                        "food_preference": "non-veg"
                    },
                    {
                        "family_name": "The Davis Family",
                        "attendance": "Maybe",
                        "members_count": 3,
                        "food_preference": "veg"
                    }
                ]
                
                db.commit()  # Commit to get event ID
                db.refresh(event)
                
                for rsvp_data in sample_rsvps:
                    rsvp = RSVPResponse(
                        event_id=event.id,
                        family_name=rsvp_data["family_name"],
                        attendance=rsvp_data["attendance"],
                        members_count=rsvp_data["members_count"],
                        food_preference=rsvp_data["food_preference"]
                    )
                    db.add(rsvp)
                
                print("✅ Sample RSVP responses created")
        
        # Commit all changes
        db.commit()
        print("✅ Database initialization completed successfully!")
        
        # Print summary
        print("\n📊 Database Summary:")
        print(f"   👥 Users: {db.query(User).count()}")
        print(f"   🛡️  Admins: {db.query(Admin).count()}")
        print(f"   💒 Events: {db.query(Event).count()}")
        print(f"   📝 RSVP Responses: {db.query(RSVPResponse).count()}")
        
        print("\n🔐 Login Credentials:")
        print("   Admin: admin@wedcraft.com / admin123")
        print("   User: john.sarah@example.com / password123")
        print("   User: planner@example.com / planner123")
        print("   User: vendor@example.com / vendor123")
        print("   User: michael@example.com / user123")
        print("   User: emma@example.com / user123")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()