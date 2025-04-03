"""Configuration module for TimeTracker app."""

import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Configuration settings for the application."""
    
    # Database config with Docker-aware path handling
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if db_uri and db_uri.startswith('sqlite:///'):
        # Make relative paths absolute for Docker environment
        db_path = db_uri.replace('sqlite:///', '')
        if not db_path.startswith('/'):
            # If path is not absolute, make it relative to app root
            db_uri = f'sqlite:///{BASE_DIR / db_path}'
    
    SQLALCHEMY_DATABASE_URI = db_uri or 'sqlite:///instance/timetrack.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-only-for-development')
    
    # Application settings
    DAY_START_TIME = int(os.getenv('DAY_START_TIME', '08:30').split(':')[0]) * 60 + int(os.getenv('DAY_START_TIME', '08:30').split(':')[1])
    DAY_END_TIME = int(os.getenv('DAY_END_TIME', '17:00').split(':')[0]) * 60 + int(os.getenv('DAY_END_TIME', '17:00').split(':')[1])