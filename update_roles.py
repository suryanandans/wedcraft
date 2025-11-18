#!/usr/bin/env python3
"""
Update existing user roles to only 'user' role
This script updates the database to have only Admin and User roles
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./wedcraft.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_user_roles():
    """Update all user roles to 'user'"""
    print("🔄 Updating user roles...")
    
    db = SessionLocal()
    
    try:
        # Update all users to have 'user' role (except admins which are in separate table)
        result = db.execute(text("UPDATE users SET role = 'user' WHERE role != 'user'"))
        db.commit()
        
        print(f"✅ Updated {result.rowcount} user roles to 'user'")
        
        # Show current users
        users = db.execute(text("SELECT id, name, email, role FROM users")).fetchall()
        print("\n📊 Current Users:")
        for user in users:
            print(f"   ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Role: {user[3]}")
        
        # Show current admins
        admins = db.execute(text("SELECT id, name, email, role FROM admins")).fetchall()
        print("\n🛡️  Current Admins:")
        for admin in admins:
            print(f"   ID: {admin[0]}, Name: {admin[1]}, Email: {admin[2]}, Role: {admin[3]}")
            
    except Exception as e:
        print(f"❌ Error updating roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_roles()