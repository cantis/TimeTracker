import pytest
from app.app import create_app
from app.models import db

@pytest.fixture
def app():
    """Create test Flask application with in-memory database."""
    # Use in-memory SQLite database for testing
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })

    with app.app_context():
        db.create_all()

    yield app

    # Cleanup after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client for Flask app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner for Flask app."""
    return app.test_cli_runner()
