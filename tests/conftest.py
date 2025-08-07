import pytest

from app.app import create_app
from app.models import db


@pytest.fixture
def app():
    """Create test Flask application with in-memory database."""
    # Set environment variable to skip default admin creation and use test mode
    import os

    os.environ['SKIP_DEFAULT_ADMIN'] = 'True'
    os.environ['TESTING'] = 'True'

    # Create app with test configuration overrides
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
        'SKIP_DEFAULT_ADMIN': True,
    }

    app = create_app(config_overrides=test_config)

    with app.app_context():
        # Create all tables in the in-memory database
        db.create_all()

    yield app

    # Cleanup after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

    # Clean up environment variable
    os.environ.pop('SKIP_DEFAULT_ADMIN', None)


@pytest.fixture
def client(app):
    """Create test client for Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner for Flask app."""
    return app.test_cli_runner()
