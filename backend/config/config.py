import os
from datetime import timedelta
from decouple import config

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
    DEBUG = config('DEBUG', default=False, cast=bool)
    
    # Database settings
    DATABASE_URL = config('DATABASE_URL', default='sqlite:///health_monitor.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # External API keys
    OPENWEATHERMAP_API_KEY = config('OPENWEATHERMAP_API_KEY', default='')
    AIRVISUAL_API_KEY = config('AIRVISUAL_API_KEY', default='')
    
    # ML Model settings
    MODEL_CACHE_DIR = config('MODEL_CACHE_DIR', default='./ml_models/cache')
    
    # Redis settings (for caching and task queue)
    REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    
    # Security settings
    BCRYPT_LOG_ROUNDS = config('BCRYPT_LOG_ROUNDS', default=12, cast=int)
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = config('RATELIMIT_STORAGE_URL', default='redis://localhost:6379/1')
    
    # Federated learning settings
    FL_AGGREGATION_ROUNDS = config('FL_AGGREGATION_ROUNDS', default=10, cast=int)
    FL_MIN_CLIENTS = config('FL_MIN_CLIENTS', default=5, cast=int)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = config('UPLOAD_FOLDER', default='./uploads')
    
    # Logging settings
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')
    LOG_FILE = config('LOG_FILE', default='health_monitor.log')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """Get configuration based on environment."""
    env = config('FLASK_ENV', default='development')
    return config_by_name.get(env, DevelopmentConfig)