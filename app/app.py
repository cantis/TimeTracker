"""Main application factory."""

import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.models import User, db
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.home import home_bp
from app.routes.reports import reports_bp
from app.service.user_service import create_default_admin

# Load environment variables from .env file
load_dotenv()


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure Flask application. (application factory pattern)"""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)
    app.config['APPLICATION_ROOT'] = os.getenv('APPLICATION_ROOT', '/')

    # Apply any configuration overrides (useful for testing)
    if config_overrides:
        app.config.update(config_overrides)

    # Configure ProxyFix middleware for reverse proxy support
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize CSRF protection
    CSRFProtect(app)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    # Note: type ignore is used to suppress type checking issues with Flask-Login because of
    # an incompatibility between Flask-Login and Flask's type hints.
    login_manager: LoginManager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore[attr-defined]
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
            create_default_admin()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    # Register error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template(
            'error.html', error='403 Forbidden – You do not have permission to access this page.'
        ), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', error='404 Not Found – The page you requested does not exist.'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error.html', error='500 Internal Server Error – Something went wrong on our end.'), 500

    return app
