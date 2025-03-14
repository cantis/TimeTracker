import os

from dotenv import load_dotenv
from flask import Flask

from app.models import db
from app.routes.home import home_bp

load_dotenv()


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Load start and end times
    app.config['DAY_START_TIME'] = int(os.getenv('DAY_START_TIME', '08:00').split(':')[0]) * 60 + int(os.getenv('DAY_START_TIME', '08:00').split(':')[1])
    app.config['DAY_END_TIME'] = int(os.getenv('DAY_END_TIME', '17:00').split(':')[0]) * 60 + int(os.getenv('DAY_END_TIME', '17:00').split(':')[1])

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(home_bp)

    return app
