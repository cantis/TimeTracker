import os

from flask import Flask

from app.models import db
from app.routes.home import home_bp


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'timetrack.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(home_bp)

    return app
