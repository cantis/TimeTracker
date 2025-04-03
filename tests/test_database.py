"""Tests for database configuration and connectivity."""

from datetime import datetime

from app.models import TimeEntry, db

def test_database_configuration(app):
    """Verify database URI is properly loaded from environment."""
    # Arrange & Act
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Assert
    assert db_uri is not None
    assert 'sqlite' in db_uri.lower() 

def test_database_write_and_read(app):
    """Verify database operations work correctly."""
    # Arrange
    with app.app_context():
        # Act - Create test entry
        entry = TimeEntry(
            activity_date=datetime.now(),
            from_time=540,  # 9:00 AM
            to_time=570,    # 9:30 AM
            activity='Test Database Connection'
        )
        db.session.add(entry)
        db.session.commit()
        
        # Assert - Record exists
        saved_entry = TimeEntry.query.filter_by(activity='Test Database Connection').first()
        assert saved_entry is not None
        assert saved_entry.from_time == 540
        assert saved_entry.to_time == 570
        
        # Clean up
        db.session.delete(saved_entry)
        db.session.commit()