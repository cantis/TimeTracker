"""Main application factory."""

import os

from dotenv import load_dotenv
from flask import Flask

from app.config import Config
from app.models import db
from app.routes.admin import admin_bp
from app.routes.home import home_bp
from app.routes.reports import reports_bp

# Load environment variables from .env file
load_dotenv()


def create_app() -> Flask:
    """Create and configure Flask application."""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    return app
