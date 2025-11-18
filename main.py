from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import os
from pathlib import Path

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./wedcraft.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # only 'user' role
    wedding_date = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    bride_name = Column(String, nullable=False)
    groom_name = Column(String, nullable=False)
    wedding_date = Column(String, nullable=False)
    location = Column(String, nullable=False)
    invitation_message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FormTemplate(Base):
    __tablename__ = "form_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    form_schema = Column(Text, nullable=False)  # JSON schema for form fields
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)  # Admin ID who created it
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class FormResponse(Base):
    __tablename__ = "form_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    form_template_id = Column(Integer, nullable=False)
    response_data = Column(Text, nullable=False)  # JSON data of form responses
    submitted_by_email = Column(String, nullable=True)
    submitted_by_name = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Keep RSVPResponse for backward compatibility
class RSVPResponse(Base):
    __tablename__ = "rsvp_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    family_name = Column(String, nullable=False)
    attendance = Column(String, nullable=False)  # 'Yes', 'No', 'Maybe'
    members_count = Column(Integer, nullable=True)
    food_preference = Column(String, nullable=True)  # 'veg', 'non-veg'
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
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
    bride_name: str
    groom_name: str
    wedding_date: str
    location: str
    invitation_message: Optional[str] = None

class FormTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    form_schema: str  # JSON string containing form field definitions
    
class FormTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    form_schema: Optional[str] = None
    is_active: Optional[bool] = None

class FormResponseCreate(BaseModel):
    form_template_id: int
    response_data: str  # JSON string containing form responses
    submitted_by_email: Optional[str] = None
    submitted_by_name: Optional[str] = None

class RSVPCreate(BaseModel):
    event_id: int
    family_name: str
    attendance: str
    members_count: Optional[int] = None
    food_preference: Optional[str] = None

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

# Authentication endpoints
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
async def get_users(db: Session = Depends(get_db)):
    # Get regular users
    users = db.query(User).all()
    user_list = [
        {
            "id": f"user_{user.id}",
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "wedding_date": user.wedding_date,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]
    
    # Get admin users and add them to the list
    admins = db.query(Admin).all()
    admin_list = [
        {
            "id": f"admin_{admin.id}",
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "wedding_date": None,  # Admins don't have wedding dates
            "is_active": admin.is_active,
            "created_at": admin.created_at.isoformat()
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

# Event management endpoints
@app.post("/api/admin/create-event")
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(
        user_id=event.user_id,
        bride_name=event.bride_name,
        groom_name=event.groom_name,
        wedding_date=event.wedding_date,
        location=event.location,
        invitation_message=event.invitation_message
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
            "bride_name": db_event.bride_name,
            "groom_name": db_event.groom_name,
            "wedding_date": db_event.wedding_date,
            "location": db_event.location,
            "invitation_message": db_event.invitation_message
        }
    }

@app.get("/api/admin/events")
async def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return {
        "success": True,
        "events": [
            {
                "id": event.id,
                "user_id": event.user_id,
                "bride_name": event.bride_name,
                "groom_name": event.groom_name,
                "wedding_date": event.wedding_date,
                "location": event.location,
                "invitation_message": event.invitation_message,
                "is_active": event.is_active,
                "created_at": event.created_at.isoformat()
            }
            for event in events
        ]
    }

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

@app.get("/api/admin/rsvp-responses")
async def get_rsvp_responses(db: Session = Depends(get_db)):
    responses = db.query(RSVPResponse).all()
    return {
        "success": True,
        "responses": [
            {
                "id": response.id,
                "event_id": response.event_id,
                "family_name": response.family_name,
                "attendance": response.attendance,
                "members_count": response.members_count,
                "food_preference": response.food_preference,
                "created_at": response.created_at.isoformat()
            }
            for response in responses
        ]
    }

# Form Template Management APIs
@app.post("/api/admin/form-templates")
async def create_form_template(form_template: FormTemplateCreate, db: Session = Depends(get_db)):
    """Create a new form template"""
    db_form_template = FormTemplate(
        name=form_template.name,
        description=form_template.description,
        form_schema=form_template.form_schema,
        created_by=1  # Default admin ID, should be from JWT token in production
    )
    db.add(db_form_template)
    db.commit()
    db.refresh(db_form_template)
    
    return {
        "success": True,
        "message": "Form template created successfully",
        "form_template": {
            "id": db_form_template.id,
            "name": db_form_template.name,
            "description": db_form_template.description,
            "form_schema": db_form_template.form_schema,
            "is_active": db_form_template.is_active,
            "created_at": db_form_template.created_at.isoformat()
        }
    }

@app.get("/api/admin/form-templates")
async def get_form_templates(db: Session = Depends(get_db)):
    """Get all form templates"""
    templates = db.query(FormTemplate).all()
    return {
        "success": True,
        "templates": [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "form_schema": template.form_schema,
                "is_active": template.is_active,
                "created_by": template.created_by,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            }
            for template in templates
        ]
    }

@app.get("/api/admin/form-templates/{template_id}")
async def get_form_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific form template"""
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found")
    
    return {
        "success": True,
        "template": {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "form_schema": template.form_schema,
            "is_active": template.is_active,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
    }

@app.put("/api/admin/form-templates/{template_id}")
async def update_form_template(template_id: int, form_template: FormTemplateUpdate, db: Session = Depends(get_db)):
    """Update a form template"""
    db_template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Form template not found")
    
    if form_template.name is not None:
        db_template.name = form_template.name
    if form_template.description is not None:
        db_template.description = form_template.description
    if form_template.form_schema is not None:
        db_template.form_schema = form_template.form_schema
    if form_template.is_active is not None:
        db_template.is_active = form_template.is_active
    
    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    
    return {
        "success": True,
        "message": "Form template updated successfully"
    }

@app.delete("/api/admin/form-templates/{template_id}")
async def delete_form_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a form template"""
    db_template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Form template not found")
    
    db.delete(db_template)
    db.commit()
    
    return {
        "success": True,
        "message": "Form template deleted successfully"
    }

# Form Response Management APIs
@app.post("/api/forms/{template_id}/submit")
async def submit_form_response(template_id: int, form_response: FormResponseCreate, db: Session = Depends(get_db)):
    """Submit a form response (public endpoint)"""
    # Verify template exists and is active
    template = db.query(FormTemplate).filter(
        FormTemplate.id == template_id,
        FormTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found or inactive")
    
    db_response = FormResponse(
        form_template_id=template_id,
        response_data=form_response.response_data,
        submitted_by_email=form_response.submitted_by_email,
        submitted_by_name=form_response.submitted_by_name
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    
    return {
        "success": True,
        "message": "Form response submitted successfully",
        "response_id": db_response.id
    }

@app.get("/api/admin/form-responses")
async def get_all_form_responses(db: Session = Depends(get_db)):
    """Get all form responses"""
    responses = db.query(FormResponse).all()
    return {
        "success": True,
        "responses": [
            {
                "id": response.id,
                "form_template_id": response.form_template_id,
                "response_data": response.response_data,
                "submitted_by_email": response.submitted_by_email,
                "submitted_by_name": response.submitted_by_name,
                "created_at": response.created_at.isoformat()
            }
            for response in responses
        ]
    }

@app.get("/api/admin/form-responses/{template_id}")
async def get_form_responses_by_template(template_id: int, db: Session = Depends(get_db)):
    """Get all responses for a specific form template"""
    responses = db.query(FormResponse).filter(FormResponse.form_template_id == template_id).all()
    return {
        "success": True,
        "template_id": template_id,
        "responses": [
            {
                "id": response.id,
                "response_data": response.response_data,
                "submitted_by_email": response.submitted_by_email,
                "submitted_by_name": response.submitted_by_name,
                "created_at": response.created_at.isoformat()
            }
            for response in responses
        ]
    }

@app.get("/api/admin/form-responses/response/{response_id}")
async def get_form_response(response_id: int, db: Session = Depends(get_db)):
    """Get a specific form response"""
    response = db.query(FormResponse).filter(FormResponse.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Form response not found")
    
    return {
        "success": True,
        "response": {
            "id": response.id,
            "form_template_id": response.form_template_id,
            "response_data": response.response_data,
            "submitted_by_email": response.submitted_by_email,
            "submitted_by_name": response.submitted_by_name,
            "created_at": response.created_at.isoformat()
        }
    }

@app.delete("/api/admin/form-responses/{response_id}")
async def delete_form_response(response_id: int, db: Session = Depends(get_db)):
    """Delete a form response"""
    db_response = db.query(FormResponse).filter(FormResponse.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="Form response not found")
    
    db.delete(db_response)
    db.commit()
    
    return {
        "success": True,
        "message": "Form response deleted successfully"
    }

# Dashboard stats endpoint
@app.get("/api/admin/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_events = db.query(Event).count()
    total_rsvps = db.query(RSVPResponse).count()
    active_events = db.query(Event).filter(Event.is_active == True).count()
    total_form_templates = db.query(FormTemplate).count()
    total_form_responses = db.query(FormResponse).count()
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "total_events": total_events,
            "total_rsvps": total_rsvps,
            "active_events": active_events,
            "total_form_templates": total_form_templates,
            "total_form_responses": total_form_responses
        }
    }

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