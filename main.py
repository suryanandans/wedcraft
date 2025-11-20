from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import os
import shutil
import uuid
from pathlib import Path

# Database configuration
# MySQL connection string format: mysql+pymysql://username:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/wedcrafts"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # only 'user' role
    wedding_date = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_name = Column(String(255), nullable=True)  # New field for generic event names
    bride_name = Column(String(255), nullable=True)  # Made nullable for backward compatibility
    groom_name = Column(String(255), nullable=True)  # Made nullable for backward compatibility
    wedding_date = Column(String(20), nullable=False)
    location = Column(String(500), nullable=False)
    google_maps_link = Column(String(1000), nullable=True)
    custom_invitation_url = Column(String(1000), nullable=True)
    custom_invitation_file = Column(String(500), nullable=True)  # Path to custom invitation HTML file
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Keep RSVPResponse for backward compatibility
class RSVPResponse(Base):
    __tablename__ = "rsvp_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    family_name = Column(String(255), nullable=False)
    attendance = Column(String(20), nullable=False)  # 'Yes', 'No', 'Maybe'
    members_count = Column(Integer, nullable=True)
    food_preference = Column(String(50), nullable=True)  # 'veg', 'non-veg'
    created_at = Column(DateTime, default=datetime.utcnow)

# New detailed family member model
class FamilyMember(Base):
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True, index=True)
    rsvp_response_id = Column(Integer, nullable=False)  # Foreign key to RSVPResponse
    member_name = Column(String(255), nullable=False)
    food_preference = Column(String(20), nullable=False)  # 'Vegetarian', 'Non-Vegetarian'
    is_child = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Processed Analytics table
class ProcessedAnalytics(Base):
    __tablename__ = "processed_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=True)
    total_families = Column(Integer, default=0)
    yes_responses = Column(Integer, default=0)
    no_responses = Column(Integer, default=0)
    maybe_responses = Column(Integer, default=0)
    predicted_attendance = Column(Integer, default=0)
    veg_required = Column(Integer, default=0)
    nonveg_required = Column(Integer, default=0)
    children_count = Column(Integer, default=0)
    attendance_rate = Column(String(10), default="0.0")
    response_rate = Column(String(10), default="0.0")
    recommendations = Column(Text, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class StandardRSVPSubmission(BaseModel):
    event_id: int
    family_name: str
    attendance: str  # Must be 'Yes', 'No', or 'Maybe'
    members_count: Optional[int] = None  # Required if attendance is 'Yes'
    food_preference: Optional[str] = None  # 'Vegetarian' or 'Non-Vegetarian' if attendance is 'Yes'

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    wedding_date: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class EventCreate(BaseModel):
    user_id: int
    event_name: Optional[str] = None  # New field for generic event names
    bride_name: Optional[str] = None  # Made optional for backward compatibility
    groom_name: Optional[str] = None  # Made optional for backward compatibility
    wedding_date: str
    location: str
    google_maps_link: Optional[str] = None
    custom_invitation_url: Optional[str] = None

class RSVPCreate(BaseModel):
    event_id: int
    family_name: str
    attendance: str
    members_count: Optional[int] = None
    food_preference: Optional[str] = None

# Enhanced RSVP models for individual family member preferences
class FamilyMemberData(BaseModel):
    member_name: str
    food_preference: str  # 'Vegetarian' or 'Non-Vegetarian'
    is_child: bool = False

class EnhancedRSVPSubmission(BaseModel):
    event_id: int
    family_name: str
    attendance: str  # Must be 'Yes', 'No', or 'Maybe'
    family_members: Optional[List[FamilyMemberData]] = None  # Required if attendance is 'Yes'

class Token(BaseModel):
    access_token: str
    token_type: str

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="WedCraft API", description="Wedding website builder API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Mount static files for the root directory to serve HTML files
app.mount("/static", StaticFiles(directory="."), name="static")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_admin(db: Session, email: str, password: str):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

# Initialize default admin
def create_default_admin(db: Session):
    admin = db.query(Admin).filter(Admin.email == "admin@wedcraft.com").first()
    if not admin:
        hashed_password = get_password_hash("admin123")
        admin = Admin(
            name="WedCraft Admin",
            email="admin@wedcraft.com",
            hashed_password=hashed_password,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("Default admin created: admin@wedcraft.com / admin123")

# API Routes

# Serve HTML files
@app.get("/")
async def read_root():
    return FileResponse(Path("login.html"), media_type="text/html")

@app.get("/login.html")
async def login_page():
    return FileResponse(Path("login.html"), media_type="text/html")

@app.get("/dashboard.html")
async def dashboard_page():
    return FileResponse(Path("dashboard.html"), media_type="text/html")

@app.get("/rsvp_form_sample.html")
async def rsvp_sample_page():
    return FileResponse(Path("rsvp_form_sample.html"), media_type="text/html")

@app.get("/invitation.html")
async def invitation_page():
    return FileResponse(Path("invitation.html"), media_type="text/html")

@app.get("/enhanced_rsvp_form.html")
async def enhanced_rsvp_form_page():
    return FileResponse(Path("enhanced_rsvp_form.html"), media_type="text/html")

# Authentication endpoints
@app.post("/api/login")
async def unified_login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Unified login endpoint that handles both admin and user authentication
    """
    # First try to authenticate as admin
    admin = authenticate_admin(db, user_login.email, user_login.password)
    if admin:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin.email, "type": "admin", "user_id": admin.id},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "role": "admin",
                "wedding_date": None,
                "user_type": "admin"
            },
            "redirect_to": "dashboard"
        }
    
    # If not admin, try to authenticate as regular user
    user = authenticate_user(db, user_login.email, user_login.password)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "type": "user", "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "wedding_date": user.wedding_date,
                "user_type": "user"
            },
            "redirect_to": "dashboard"
        }
    
    # If neither admin nor user authentication succeeded
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

# Keep the original endpoints for backward compatibility
@app.post("/api/user/login")
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "type": "user", "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "wedding_date": user.wedding_date
        }
    }

@app.post("/api/admin/login")
async def login_admin(admin_login: AdminLogin, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, admin_login.email, admin_login.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email, "type": "admin", "admin_id": admin.id},
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role
        }
    }

# User management endpoints
@app.post("/api/admin/create-user")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        wedding_date=user.wedding_date
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "success": True,
        "message": "User created successfully",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
            "wedding_date": db_user.wedding_date
        }
    }

@app.get("/api/admin/users")
async def get_users(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    # If user_id is provided, return only that specific user (for regular user access)
    if user_id:
        # First check regular users
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "success": True,
                "users": [{
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "wedding_date": user.wedding_date,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "user_type": "user"
                }]
            }
        
        # Check admin users (with offset)
        if user_id >= 10000:
            admin_id = user_id - 10000
            admin = db.query(Admin).filter(Admin.id == admin_id).first()
            if admin:
                return {
                    "success": True,
                    "users": [{
                        "id": admin.id + 10000,
                        "name": admin.name,
                        "email": admin.email,
                        "role": admin.role,
                        "wedding_date": None,
                        "is_active": admin.is_active,
                        "created_at": admin.created_at.isoformat(),
                        "user_type": "admin"
                    }]
                }
        
        return {"success": True, "users": []}
    
    # Admin access - return all users
    # Get regular users
    users = db.query(User).all()
    user_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "wedding_date": user.wedding_date,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "user_type": "user"
        }
        for user in users
    ]
    
    # Get admin users and add them to the list
    admins = db.query(Admin).all()
    admin_list = [
        {
            "id": admin.id + 10000,  # Offset admin IDs to avoid conflicts
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "wedding_date": None,  # Admins don't have wedding dates
            "is_active": admin.is_active,
            "created_at": admin.created_at.isoformat(),
            "user_type": "admin"
        }
        for admin in admins
    ]
    
    # Combine both lists
    all_users = user_list + admin_list
    
    return {
        "success": True,
        "users": all_users
    }

@app.get("/api/admin/admins")
async def get_admins(db: Session = Depends(get_db)):
    admins = db.query(Admin).all()
    return {
        "success": True,
        "admins": [
            {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "role": admin.role,
                "is_active": admin.is_active,
                "created_at": admin.created_at.isoformat()
            }
            for admin in admins
        ]
    }

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user (handles both regular users and admins)"""
    try:
        # First, try to find in regular users table
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if db_user:
            # This is a regular user
            # Check if user has associated events
            user_events = db.query(Event).filter(Event.user_id == user_id).count()
            if user_events > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete user. User has {user_events} associated events. Delete events first."
                )
            
            db.delete(db_user)
            db.commit()
            return {
                "success": True,
                "message": "User deleted successfully"
            }
        
        # If not found in users, check if this is an admin user (with offset)
        if user_id >= 10000:
            admin_id = user_id - 10000
            db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
            
            if db_admin:
                # Check if this is the last admin
                admin_count = db.query(Admin).count()
                if admin_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
                
                # Check if admin has associated events
                admin_events = db.query(Event).filter(Event.user_id == admin_id).count()
                if admin_events > 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot delete admin. Admin has {admin_events} associated events. Delete events first."
                    )
                
                db.delete(db_admin)
                db.commit()
                return {
                    "success": True,
                    "message": "Admin user deleted successfully"
                }
        
        # If not found in either table
        raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

# Event management endpoints
@app.post("/api/admin/create-event")
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    # Validate that user exists (check both regular users and admins with offset)
    user_exists = None
    actual_user_id = event.user_id
    
    if event.user_id >= 10000:
        # This is an admin user (with offset)
        admin_id = event.user_id - 10000
        user_exists = db.query(Admin).filter(Admin.id == admin_id).first()
        # For events, we'll store the actual admin ID without offset
        actual_user_id = admin_id
    else:
        # This is a regular user
        user_exists = db.query(User).filter(User.id == event.user_id).first()
    
    if not user_exists:
        raise HTTPException(status_code=400, detail=f"User with ID {event.user_id} not found")
    
    # Validate that event date is not before today
    event_date = datetime.strptime(event.wedding_date, "%Y-%m-%d").date()
    today = datetime.utcnow().date()
    
    if event_date < today:
        raise HTTPException(status_code=400, detail="Event date cannot be before today")
    
    # Validate that either event_name is provided OR both bride_name and groom_name are provided
    if not event.event_name and not (event.bride_name and event.groom_name):
        raise HTTPException(status_code=400, detail="Either event_name or both bride_name and groom_name must be provided")
    
    try:
        db_event = Event(
            user_id=actual_user_id,
            event_name=event.event_name,
            bride_name=event.bride_name,
            groom_name=event.groom_name,
            wedding_date=event.wedding_date,
            location=event.location,
            google_maps_link=event.google_maps_link,
            custom_invitation_url=event.custom_invitation_url
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        return {
            "success": True,
            "message": "Event created successfully",
            "event": {
                "id": db_event.id,
                "user_id": db_event.user_id,
                "event_name": db_event.event_name,
                "bride_name": db_event.bride_name,
                "groom_name": db_event.groom_name,
                "wedding_date": db_event.wedding_date,
                "location": db_event.location,
                "google_maps_link": db_event.google_maps_link,
                "custom_invitation_url": db_event.custom_invitation_url
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating event: {str(e)}")

@app.get("/api/admin/events")
async def get_events(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    # If user_id is provided, return only events for that specific user
    if user_id:
        events = db.query(Event).filter(Event.user_id == user_id).all()
    else:
        # Admin access - return all events
        events = db.query(Event).all()
    
    events_with_users = []
    
    for event in events:
        # Try to find user in regular users table first
        user = db.query(User).filter(User.id == event.user_id).first()
        user_name = None
        user_email = None
        user_role = None
        
        if user:
            user_name = user.name
            user_email = user.email
            user_role = user.role
        else:
            # Try to find in admins table
            admin = db.query(Admin).filter(Admin.id == event.user_id).first()
            if admin:
                user_name = admin.name
                user_email = admin.email
                user_role = admin.role
        
        events_with_users.append({
            "id": event.id,
            "user_id": event.user_id,
            "user_name": user_name or f"User ID: {event.user_id}",
            "user_email": user_email,
            "user_role": user_role,
            "event_name": event.event_name,
            "bride_name": event.bride_name,
            "groom_name": event.groom_name,
            "wedding_date": event.wedding_date,
            "location": event.location,
            "google_maps_link": event.google_maps_link,
            "custom_invitation_url": event.custom_invitation_url,
            "is_active": event.is_active,
            "created_at": event.created_at.isoformat()
        })
    
    return {
        "success": True,
        "events": events_with_users
    }

@app.get("/api/admin/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        })
    
    return {
        "success": True,
        "users": users_data
    }

@app.delete("/api/admin/events/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    # Find the event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    try:
        # First, delete all RSVP responses associated with this event
        db.query(RSVPResponse).filter(RSVPResponse.event_id == event_id).delete()
        
        # Then delete the event itself
        db.delete(event)
        db.commit()
        
        return {
            "success": True,
            "message": "Event and associated RSVP responses deleted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

# Custom invitation endpoints
@app.post("/api/admin/events/{event_id}/upload-invitation")
async def upload_custom_invitation(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Find the event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Validate file type
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Only HTML files are allowed")
    
    try:
        # Create unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"event_{event_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = f"custom_invitations/{unique_filename}"
        
        # Save file
        os.makedirs("custom_invitations", exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update event record
        event.custom_invitation_file = file_path
        db.commit()
        
        return {
            "success": True,
            "message": "Custom invitation uploaded successfully",
            "file_path": file_path
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload invitation: {str(e)}")

@app.get("/api/invitation/{event_id}")
async def get_custom_invitation(event_id: int, db: Session = Depends(get_db)):
    # Find the event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if custom invitation exists
    if event.custom_invitation_file and os.path.exists(event.custom_invitation_file):
        return FileResponse(
            path=event.custom_invitation_file,
            media_type="text/html",
            filename=f"invitation_event_{event_id}.html"
        )
    else:
        # Return default invitation page
        return FileResponse(
            path="invitation.html",
            media_type="text/html"
        )

@app.delete("/api/admin/events/{event_id}/invitation")
async def delete_custom_invitation(event_id: int, db: Session = Depends(get_db)):
    # Find the event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    try:
        # Delete file if exists
        if event.custom_invitation_file and os.path.exists(event.custom_invitation_file):
            os.remove(event.custom_invitation_file)
        
        # Update event record
        event.custom_invitation_file = None
        db.commit()
        
        return {
            "success": True,
            "message": "Custom invitation deleted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete invitation: {str(e)}")

# RSVP endpoints
@app.post("/api/rsvp/submit")
async def submit_rsvp(rsvp: RSVPCreate, db: Session = Depends(get_db)):
    db_rsvp = RSVPResponse(
        event_id=rsvp.event_id,
        family_name=rsvp.family_name,
        attendance=rsvp.attendance,
        members_count=rsvp.members_count,
        food_preference=rsvp.food_preference
    )
    db.add(db_rsvp)
    db.commit()
    db.refresh(db_rsvp)
    
    return {
        "success": True,
        "message": "RSVP submitted successfully",
        "rsvp": {
            "id": db_rsvp.id,
            "family_name": db_rsvp.family_name,
            "attendance": db_rsvp.attendance,
            "members_count": db_rsvp.members_count,
            "food_preference": db_rsvp.food_preference
        }
    }

# Standardized RSVP Form Submission Endpoint
@app.post("/api/rsvp/standard-submit")
async def submit_standard_rsvp(rsvp: StandardRSVPSubmission, db: Session = Depends(get_db)):
    """
    Standardized RSVP submission endpoint that ensures consistent data format
    regardless of how the form questions are worded.
    
    Standard format:
    1. family_name: String (required)
    2. attendance: 'Yes', 'No', or 'Maybe' (required)
    3. members_count: Integer (required if attendance is 'Yes')
    4. food_preference: 'Vegetarian' or 'Non-Vegetarian' (required if attendance is 'Yes')
    """
    
    # Validate attendance value
    valid_attendance = ['Yes', 'Maybe']
    if rsvp.attendance not in valid_attendance:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attendance value. Must be one of: {', '.join(valid_attendance)}"
        )
    
    # Validate required fields for 'Yes' attendance
    if rsvp.attendance == 'Yes':
        if not rsvp.members_count or rsvp.members_count <= 0:
            raise HTTPException(
                status_code=400,
                detail="Members count is required and must be greater than 0 when attendance is 'Yes'"
            )
        
        if not rsvp.food_preference:
            raise HTTPException(
                status_code=400,
                detail="Food preference is required when attendance is 'Yes'"
            )
        
        # Validate food preference
        valid_food_prefs = ['Vegetarian', 'Non-Vegetarian']
        if rsvp.food_preference not in valid_food_prefs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid food preference. Must be one of: {', '.join(valid_food_prefs)}"
            )
    
    # Check if event exists
    event = db.query(Event).filter(Event.id == rsvp.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check for duplicate RSVP from same family for same event
    existing_rsvp = db.query(RSVPResponse).filter(
        RSVPResponse.event_id == rsvp.event_id,
        RSVPResponse.family_name == rsvp.family_name
    ).first()
    
    if existing_rsvp:
        raise HTTPException(
            status_code=400,
            detail="RSVP already submitted for this family and event"
        )
    
    # Create standardized RSVP response
    db_rsvp = RSVPResponse(
        event_id=rsvp.event_id,
        family_name=rsvp.family_name.strip(),
        attendance=rsvp.attendance,
        members_count=rsvp.members_count if rsvp.attendance == 'Yes' else None,
        food_preference=rsvp.food_preference if rsvp.attendance == 'Yes' else None
    )
    
    db.add(db_rsvp)
    db.commit()
    db.refresh(db_rsvp)
    
    return {
        "success": True,
        "message": "RSVP submitted successfully",
        "rsvp": {
            "id": db_rsvp.id,
            "event_id": db_rsvp.event_id,
            "family_name": db_rsvp.family_name,
            "attendance": db_rsvp.attendance,
            "members_count": db_rsvp.members_count,
            "food_preference": db_rsvp.food_preference,
            "submitted_at": db_rsvp.created_at.isoformat()
        }
    }

# Enhanced RSVP Form Submission Endpoint with Individual Member Details
@app.post("/api/rsvp/enhanced-submit")
async def submit_enhanced_rsvp(rsvp: EnhancedRSVPSubmission, db: Session = Depends(get_db)):
    """
    Enhanced RSVP submission endpoint that handles individual family member details
    including food preferences and child status for each member.
    """
    
    # Validate attendance value
    valid_attendance = ['Yes', 'Maybe']
    if rsvp.attendance not in valid_attendance:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attendance value. Must be one of: {', '.join(valid_attendance)}"
        )
    
    # Validate required fields for 'Yes' and 'Maybe' attendance
    if rsvp.attendance == 'Yes' or rsvp.attendance == 'Maybe':
        if not rsvp.family_members or len(rsvp.family_members) == 0:
            raise HTTPException(
                status_code=400,
                detail="Family members details are required when attendance is 'Yes' or 'Maybe'"
            )
        
        # Validate each family member
        for member in rsvp.family_members:
            if not member.member_name.strip():
                raise HTTPException(
                    status_code=400,
                    detail="All family members must have a name"
                )
            
            valid_food_prefs = ['Vegetarian', 'Non-Vegetarian']
            if member.food_preference not in valid_food_prefs:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid food preference. Must be one of: {', '.join(valid_food_prefs)}"
                )
    
    # Check if event exists
    event = db.query(Event).filter(Event.id == rsvp.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check for duplicate RSVP from same family for same event
    existing_rsvp = db.query(RSVPResponse).filter(
        RSVPResponse.event_id == rsvp.event_id,
        RSVPResponse.family_name == rsvp.family_name
    ).first()
    
    if existing_rsvp:
        raise HTTPException(
            status_code=400,
            detail="RSVP already submitted for this family and event"
        )
    
    try:
        # Create main RSVP response
        members_count = len(rsvp.family_members) if rsvp.family_members else 0
        
        # Calculate overall food preference summary for backward compatibility
        food_preference_summary = None
        if (rsvp.attendance == 'Yes' or rsvp.attendance == 'Maybe') and rsvp.family_members:
            veg_count = sum(1 for member in rsvp.family_members if member.food_preference == 'Vegetarian')
            nonveg_count = len(rsvp.family_members) - veg_count
            
            if veg_count > 0 and nonveg_count > 0:
                food_preference_summary = "Mixed"
            elif veg_count > 0:
                food_preference_summary = "Vegetarian"
            else:
                food_preference_summary = "Non-Vegetarian"
        
        db_rsvp = RSVPResponse(
            event_id=rsvp.event_id,
            family_name=rsvp.family_name.strip(),
            attendance=rsvp.attendance,
            members_count=members_count if (rsvp.attendance == 'Yes' or rsvp.attendance == 'Maybe') else None,
            food_preference=food_preference_summary if (rsvp.attendance == 'Yes' or rsvp.attendance == 'Maybe') else None
        )
        
        db.add(db_rsvp)
        db.flush()  # Get the ID without committing
        
        # Create individual family member records
        family_members_data = []
        if (rsvp.attendance == 'Yes' or rsvp.attendance == 'Maybe') and rsvp.family_members:
            for member in rsvp.family_members:
                db_member = FamilyMember(
                    rsvp_response_id=db_rsvp.id,
                    member_name=member.member_name.strip(),
                    food_preference=member.food_preference,
                    is_child=member.is_child
                )
                db.add(db_member)
                family_members_data.append({
                    "member_name": db_member.member_name,
                    "food_preference": db_member.food_preference,
                    "is_child": db_member.is_child
                })
        
        db.commit()
        db.refresh(db_rsvp)
        
        return {
            "success": True,
            "message": "Enhanced RSVP submitted successfully",
            "rsvp": {
                "id": db_rsvp.id,
                "event_id": db_rsvp.event_id,
                "family_name": db_rsvp.family_name,
                "attendance": db_rsvp.attendance,
                "members_count": db_rsvp.members_count,
                "food_preference_summary": db_rsvp.food_preference,
                "family_members": family_members_data,
                "submitted_at": db_rsvp.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit RSVP: {str(e)}")

@app.get("/api/admin/rsvp-responses")
async def get_rsvp_responses(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if user_id:
        # Filter RSVP responses for specific user's events
        responses = db.query(RSVPResponse).join(Event, RSVPResponse.event_id == Event.id).filter(Event.user_id == user_id).all()
    else:
        # Admin view - all responses
        responses = db.query(RSVPResponse).all()
    
    # Build response list with event information
    response_list = []
    for response in responses:
        # Get event information for each response
        event = db.query(Event).filter(Event.id == response.event_id).first()
        event_name = None
        if event:
            event_name = f"{event.bride_name} & {event.groom_name}"
        
        response_list.append({
            "id": response.id,
            "event_id": response.event_id,
            "event_name": event_name,
            "family_name": response.family_name,
            "attendance": response.attendance,
            "members_count": response.members_count,
            "food_preference": response.food_preference,
            "message": None,  # RSVPResponse model doesn't have message field
            "created_at": response.created_at.isoformat()
        })
    
    return {
        "success": True,
        "responses": response_list
    }

# Enhanced RSVP responses with family member details
@app.get("/api/admin/enhanced-rsvp-responses")
async def get_enhanced_rsvp_responses(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get RSVP responses with detailed family member information"""
    if user_id:
        # Filter RSVP responses for specific user's events
        responses = db.query(RSVPResponse).join(Event, RSVPResponse.event_id == Event.id).filter(Event.user_id == user_id).all()
    else:
        # Admin view - all responses
        responses = db.query(RSVPResponse).all()
    
    # Build response list with event and family member information
    response_list = []
    for response in responses:
        # Get event information for each response
        event = db.query(Event).filter(Event.id == response.event_id).first()
        event_name = None
        if event:
            event_name = f"{event.bride_name} & {event.groom_name}" if event.bride_name and event.groom_name else event.event_name
        
        # Get family members for this RSVP
        family_members = db.query(FamilyMember).filter(FamilyMember.rsvp_response_id == response.id).all()
        family_members_data = []
        
        for member in family_members:
            family_members_data.append({
                "member_name": member.member_name,
                "food_preference": member.food_preference,
                "is_child": member.is_child
            })
        
        response_list.append({
            "id": response.id,
            "event_id": response.event_id,
            "event_name": event_name,
            "family_name": response.family_name,
            "attendance": response.attendance,
            "members_count": response.members_count,
            "food_preference_summary": response.food_preference,
            "family_members": family_members_data,
            "created_at": response.created_at.isoformat()
        })
    
    return {
        "success": True,
        "responses": response_list
    }

# Processed Analytics endpoints
@app.get("/api/admin/processed-analytics")
async def get_processed_analytics(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get processed analytics data from count.py processing"""
    try:
        if user_id:
            # Filter processed analytics for specific user's events
            analytics = db.query(ProcessedAnalytics).join(Event, ProcessedAnalytics.event_id == Event.id).filter(Event.user_id == user_id).all()
        else:
            # Admin view - all processed analytics
            analytics = db.query(ProcessedAnalytics).all()
        
        # Build response list with event information
        analytics_list = []
        for analytic in analytics:
            # Get event information
            event = db.query(Event).filter(Event.id == analytic.event_id).first()
            event_name = None
            if event:
                event_name = f"{event.bride_name} & {event.groom_name}"
            
            # Parse recommendations JSON
            recommendations = []
            if analytic.recommendations:
                try:
                    import json
                    recommendations = json.loads(analytic.recommendations)
                except:
                    recommendations = []
            
            analytics_list.append({
                "id": analytic.id,
                "event_id": analytic.event_id,
                "event_name": event_name,
                "total_families": analytic.total_families,
                "yes_responses": analytic.yes_responses,
                "no_responses": analytic.no_responses,
                "maybe_responses": analytic.maybe_responses,
                "predicted_attendance": analytic.predicted_attendance,
                "veg_required": analytic.veg_required,
                "nonveg_required": analytic.nonveg_required,
                "children_count": analytic.children_count,
                "attendance_rate": float(analytic.attendance_rate) if analytic.attendance_rate else 0.0,
                "response_rate": float(analytic.response_rate) if analytic.response_rate else 0.0,
                "recommendations": recommendations,
                "processed_at": analytic.processed_at.isoformat()
            })
        
        return {
            "success": True,
            "analytics": analytics_list
        }
        
    except Exception as e:
        print(f"Error fetching processed analytics: {e}")
        return {
            "success": False,
            "error": str(e),
            "analytics": []
        }

@app.post("/api/admin/process-analytics")
async def trigger_analytics_processing(db: Session = Depends(get_db)):
    """Trigger processing of RSVP data through count.py"""
    try:
        # Import and run the processing script
        from process_rsvp_data import process_and_store_analytics
        process_and_store_analytics()
        
        return {
            "success": True,
            "message": "Analytics processing completed successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process analytics"
        }

# Dashboard stats endpoint
@app.get("/api/admin/stats")
async def get_dashboard_stats(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if user_id:
        # User-specific stats
        total_users = 1  # Only the user themselves
        total_events = db.query(Event).filter(Event.user_id == user_id).count()
        total_rsvps = db.query(RSVPResponse).join(Event, RSVPResponse.event_id == Event.id).filter(Event.user_id == user_id).count()
        active_events = db.query(Event).filter(Event.user_id == user_id, Event.is_active == True).count()
    else:
        # Admin stats (all data)
        total_users = db.query(User).count()
        total_events = db.query(Event).count()
        total_rsvps = db.query(RSVPResponse).count()
        active_events = db.query(Event).filter(Event.is_active == True).count()
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "total_events": total_events,
            "total_rsvps": total_rsvps,
            "active_events": active_events
        }
    }

# Analytics endpoint using count.py
@app.get("/api/analytics/wedding-data")
async def get_wedding_analytics(event_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get comprehensive wedding analytics using count.py processing"""
    try:
        # Import the analytics engine from count.py
        from count import WeddingAnalytics
        
        # Initialize analytics engine
        analytics_engine = WeddingAnalytics()
        
        # Generate analytics for specific event or all events
        analytics_data = analytics_engine.generate_analytics(event_id)
        
        return {
            "success": True,
            "analytics": analytics_data,
            "message": "Wedding analytics generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analytics: {str(e)}"
        )

@app.get("/api/analytics/rsvp-summary")
async def get_rsvp_summary(event_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get RSVP summary data processed by count.py"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        rsvp_data = analytics_engine.fetch_rsvp_data(event_id)
        
        return {
            "success": True,
            "rsvp_data": rsvp_data,
            "message": "RSVP summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching RSVP summary: {str(e)}"
        )

@app.get("/api/analytics/form-responses")
async def get_form_analytics(template_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get form response analytics processed by count.py"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        form_data = analytics_engine.fetch_form_responses(template_id)
        
        return {
            "success": True,
            "form_data": form_data,
            "message": "Form analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching form analytics: {str(e)}"
        )

@app.get("/api/analytics/predictions")
async def get_attendance_predictions(event_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get ML-based attendance predictions from count.py"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        analytics_data = analytics_engine.generate_analytics(event_id)
        
        # Extract only prediction-related data
        predictions = {
            "expected_attendance": analytics_data["predictions"]["expected_attendance"],
            "veg_required": analytics_data["predictions"]["veg_required"],
            "nonveg_required": analytics_data["predictions"]["nonveg_required"],
            "attendance_rate": analytics_data["analytics"]["attendance_rate"],
            "recommendations": analytics_data["recommendations"]
        }
        
        return {
            "success": True,
            "predictions": predictions,
            "message": "Attendance predictions generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )

# New comprehensive analytics endpoints
@app.get("/api/analytics/dashboard-data")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get comprehensive dashboard analytics processed by count.py"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        
        # Get real-time stats for dashboard
        dashboard_stats = analytics_engine.get_real_time_stats()
        
        # Get comprehensive analytics data
        all_data = analytics_engine.fetch_all_data()
        
        return {
            "success": True,
            "dashboard_stats": dashboard_stats,
            "comprehensive_data": all_data,
            "message": "Dashboard analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard analytics: {str(e)}"
        )

@app.get("/api/analytics/real-time-stats")
async def get_real_time_stats(db: Session = Depends(get_db)):
    """Get real-time statistics for live dashboard updates"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        stats = analytics_engine.get_real_time_stats()
        
        return {
            "success": True,
            "stats": stats,
            "message": "Real-time statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching real-time stats: {str(e)}"
        )

@app.get("/api/analytics/comprehensive-report")
async def get_comprehensive_report(event_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get comprehensive analytics report with all processed data"""
    try:
        from count import WeddingAnalytics
        
        analytics_engine = WeddingAnalytics()
        
        if event_id:
            # Get analytics for specific event
            analytics_data = analytics_engine.generate_analytics(event_id)
            return {
                "success": True,
                "event_analytics": analytics_data,
                "message": f"Comprehensive report for event {event_id} generated successfully"
            }
        else:
            # Get all data
            all_data = analytics_engine.fetch_all_data()
            return {
                "success": True,
                "comprehensive_report": all_data,
                "message": "Comprehensive report generated successfully"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating comprehensive report: {str(e)}"
        )

# Startup event
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        create_default_admin(db)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)