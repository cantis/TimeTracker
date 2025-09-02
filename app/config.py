"""Configuration module for TimeTracker app."""

import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuration settings for the application."""

    # Use in-memory database for testing, otherwise use configured database
    if os.getenv('TESTING') == 'True':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        # Priority order for database configuration:
        # 1. DATABASE_URL (Render.com standard)
        # 2. SQLALCHEMY_DATABASE_URI (legacy support)
        # 3. Default SQLite fallback

        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Render.com provides DATABASE_URL, use it directly
            SQLALCHEMY_DATABASE_URI = database_url
        else:
            # Fallback to SQLALCHEMY_DATABASE_URI or SQLite default
            db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
            if db_uri and db_uri.startswith('sqlite:///'):
                # For SQLite, ensure database is in a writable location
                db_path = db_uri.replace('sqlite:///', '')
                if not db_path.startswith('/'):
                    # If path is not absolute, make it relative to app root
                    db_uri = f'sqlite:///{BASE_DIR / db_path}'
                else:
                    # For Docker paths like /app/instance/*, keep as-is
                    db_uri = f'sqlite:///{db_path}'

            SQLALCHEMY_DATABASE_URI = db_uri or f'sqlite:///{BASE_DIR / "instance" / "timetrack.db"}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-only-for-development')

    # Application settings
    start_time_env = os.getenv('DAY_START_TIME', '08:30')
    end_time_env = os.getenv('DAY_END_TIME', '17:00')

    DAY_START_TIME = int(start_time_env.split(':')[0]) * 60 + int(start_time_env.split(':')[1])
    DAY_END_TIME = int(end_time_env.split(':')[0]) * 60 + int(end_time_env.split(':')[1])
