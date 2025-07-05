from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import json

db = SQLAlchemy()

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    CHRONIC_DISEASE = "chronic_disease"
    ENVIRONMENTAL = "environmental"
    LIFESTYLE = "lifestyle"
    MENTAL_HEALTH = "mental_health"

class HealthRecord(db.Model):
    """Health record model for storing user health data."""
    
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vital signs
    heart_rate = db.Column(db.Integer)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    
    # Lifestyle data
    sleep_hours = db.Column(db.Float)
    exercise_minutes = db.Column(db.Integer)
    stress_level = db.Column(db.Integer)  # 1-10 scale
    
    # Dietary information (stored as JSON)
    dietary_data = db.Column(db.Text)  # JSON string
    
    # Medications
    current_medications = db.Column(db.Text)  # JSON string
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_dietary_data(self, data):
        """Set dietary data as JSON string."""
        self.dietary_data = json.dumps(data)
    
    def get_dietary_data(self):
        """Get dietary data as Python object."""
        return json.loads(self.dietary_data) if self.dietary_data else {}
    
    def set_medications(self, medications):
        """Set medications as JSON string."""
        self.current_medications = json.dumps(medications)
    
    def get_medications(self):
        """Get medications as Python object."""
        return json.loads(self.current_medications) if self.current_medications else []
    
    def to_dict(self):
        """Convert health record to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'heart_rate': self.heart_rate,
            'blood_pressure_systolic': self.blood_pressure_systolic,
            'blood_pressure_diastolic': self.blood_pressure_diastolic,
            'temperature': self.temperature,
            'weight': self.weight,
            'height': self.height,
            'sleep_hours': self.sleep_hours,
            'exercise_minutes': self.exercise_minutes,
            'stress_level': self.stress_level,
            'dietary_data': self.get_dietary_data(),
            'medications': self.get_medications(),
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SymptomReport(db.Model):
    """Symptom report model for storing user-reported symptoms."""
    
    __tablename__ = 'symptom_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Symptom description
    symptom_text = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Enum(SeverityLevel), nullable=False)
    
    # Processed symptom data
    processed_symptoms = db.Column(db.Text)  # JSON string of classified symptoms
    
    # Context information
    onset_date = db.Column(db.Date)
    duration_days = db.Column(db.Integer)
    
    # Environmental context
    location = db.Column(db.String(100))
    weather_conditions = db.Column(db.Text)  # JSON string
    air_quality_index = db.Column(db.Integer)
    
    # Timestamps
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_processed_symptoms(self, symptoms):
        """Set processed symptoms as JSON string."""
        self.processed_symptoms = json.dumps(symptoms)
    
    def get_processed_symptoms(self):
        """Get processed symptoms as Python object."""
        return json.loads(self.processed_symptoms) if self.processed_symptoms else []
    
    def set_weather_conditions(self, conditions):
        """Set weather conditions as JSON string."""
        self.weather_conditions = json.dumps(conditions)
    
    def get_weather_conditions(self):
        """Get weather conditions as Python object."""
        return json.loads(self.weather_conditions) if self.weather_conditions else {}
    
    def to_dict(self):
        """Convert symptom report to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symptom_text': self.symptom_text,
            'severity': self.severity.value,
            'processed_symptoms': self.get_processed_symptoms(),
            'onset_date': self.onset_date.isoformat() if self.onset_date else None,
            'duration_days': self.duration_days,
            'location': self.location,
            'weather_conditions': self.get_weather_conditions(),
            'air_quality_index': self.air_quality_index,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RiskAssessment(db.Model):
    """Risk assessment model for storing AI-generated risk predictions."""
    
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Risk details
    risk_category = db.Column(db.Enum(RiskCategory), nullable=False)
    risk_level = db.Column(db.Enum(SeverityLevel), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)  # 0-1 probability
    
    # Prediction details
    predicted_condition = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    
    # AI model information
    model_version = db.Column(db.String(50))
    model_type = db.Column(db.String(50))
    
    # Factors contributing to risk
    risk_factors = db.Column(db.Text)  # JSON string
    
    # Recommendations
    recommendations = db.Column(db.Text)  # JSON string
    
    # Timestamps
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_risk_factors(self, factors):
        """Set risk factors as JSON string."""
        self.risk_factors = json.dumps(factors)
    
    def get_risk_factors(self):
        """Get risk factors as Python object."""
        return json.loads(self.risk_factors) if self.risk_factors else []
    
    def set_recommendations(self, recommendations):
        """Set recommendations as JSON string."""
        self.recommendations = json.dumps(recommendations)
    
    def get_recommendations(self):
        """Get recommendations as Python object."""
        return json.loads(self.recommendations) if self.recommendations else []
    
    def to_dict(self):
        """Convert risk assessment to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'risk_category': self.risk_category.value,
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'predicted_condition': self.predicted_condition,
            'confidence_score': self.confidence_score,
            'model_version': self.model_version,
            'model_type': self.model_type,
            'risk_factors': self.get_risk_factors(),
            'recommendations': self.get_recommendations(),
            'assessed_at': self.assessed_at.isoformat() if self.assessed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EnvironmentalData(db.Model):
    """Environmental data model for storing external environmental factors."""
    
    __tablename__ = 'environmental_data'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Location
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Air quality
    air_quality_index = db.Column(db.Integer)
    pm25 = db.Column(db.Float)
    pm10 = db.Column(db.Float)
    co2 = db.Column(db.Float)
    pollen_count = db.Column(db.Integer)
    
    # Weather data
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    
    # Disease outbreak alerts
    outbreak_alerts = db.Column(db.Text)  # JSON string
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_outbreak_alerts(self, alerts):
        """Set outbreak alerts as JSON string."""
        self.outbreak_alerts = json.dumps(alerts)
    
    def get_outbreak_alerts(self):
        """Get outbreak alerts as Python object."""
        return json.loads(self.outbreak_alerts) if self.outbreak_alerts else []
    
    def to_dict(self):
        """Convert environmental data to dictionary."""
        return {
            'id': self.id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'air_quality_index': self.air_quality_index,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'co2': self.co2,
            'pollen_count': self.pollen_count,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'outbreak_alerts': self.get_outbreak_alerts(),
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }