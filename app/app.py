"""Main application factory."""

import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from app.config import Config
from app.models import User, db
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.home import home_bp
from app.routes.reports import reports_bp
from app.service.user_service import UserService

# Load environment variables from .env file
load_dotenv()


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure Flask application."""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Apply any configuration overrides (useful for testing)
    if config_overrides:
        app.config.update(config_overrides)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Load user by ID for Flask-Login."""
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    with app.app_context():
        db.create_all()
        # Create default admin user if no users exist (skip in tests)
        if not (app.config.get('SKIP_DEFAULT_ADMIN', False) or os.getenv('SKIP_DEFAULT_ADMIN')):
            UserService.create_default_admin()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    return app
