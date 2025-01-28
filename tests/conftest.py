import pytest
import os
from app.app import create_app, db
from app.models import Base, CommonTimeUse

@pytest.fixture
def app():
    # Use in-memory SQLite database for testing
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })

    with app.app_context():
        Base.metadata.create_all(db.engine)
        # Add some test common uses
        common_uses = [
            CommonTimeUse(description='Meeting'),
            CommonTimeUse(description='Development'),
            CommonTimeUse(description='Break')
        ]
        db.session.bulk_save_objects(common_uses)
        db.session.commit()

    yield app

    # Cleanup after tests
    with app.app_context():
        db.session.remove()
        Base.metadata.drop_all(db.engine)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
