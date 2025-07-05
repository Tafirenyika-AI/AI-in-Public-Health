from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    USER = "user"
    HEALTH_PROFESSIONAL = "health_professional"
    PUBLIC_HEALTH_OFFICIAL = "public_health_official"
    ADMIN = "admin"

class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    location = db.Column(db.String(100))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    # Privacy settings
    data_sharing_consent = db.Column(db.Boolean, default=False)
    public_health_sharing = db.Column(db.Boolean, default=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    symptom_reports = db.relationship('SymptomReport', backref='user', lazy=True, cascade='all, delete-orphan')
    risk_assessments = db.relationship('RiskAssessment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'role': self.role.value,
            'data_sharing_consent': self.data_sharing_consent,
            'public_health_sharing': self.public_health_sharing,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'