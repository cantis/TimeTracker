from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.routes.home import home_bp
from app.models import Base
import os

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)

    # Database configuration
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'timetrack.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Create database tables
    with app.app_context():
        Base.metadata.create_all(db.engine)

    # Register blueprints
    app.register_blueprint(home_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)