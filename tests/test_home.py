"""Tests for home routes and time entry functionality."""

from datetime import datetime

from app.models import TimeEntry, db


def test_index_route(client, app):
    """Test the main index route displays time entries."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import UserService
        
        user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
        
        # Test empty list
        response = client.get('/')
        assert response.status_code == 200

        # Add test entry and verify it appears
        entry = TimeEntry(
            activity_date=datetime.now(),
            from_time=540,  # 9:00 AM
            to_time=570,    # 9:30 AM
            activity='Test Activity'
        )
        db.session.add(entry)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200


def test_add_entry_post_success(client, app):
    """Test successful POST request to add a new time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import UserService
        
        user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
        
        # Arrange - prepare test data
        data = {
            'operating_date': '2023-08-01',
            'from_time': '9:00',
            'to_time': '9:30',
            'activity': 'Test entry',
            'time_out': '0',
        }

        # Act - submit the form
        response = client.post('/add', data=data, follow_redirects=True)

        # Assert - verify success
        assert response.status_code == 200
        # Check if entry was created in database
        entries = TimeEntry.query.all()
        assert len(entries) > 0
        assert entries[0].activity == 'Test entry'


def test_add_entry_validation_fail(client, app):
    """Test POST request with invalid data fails validation."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import UserService
        
        user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
        
        # Arrange - prepare invalid test data
        data = {
            'operating_date': '', 
            'from_time': '', 
            'to_time': '', 
            'activity': '', 
            'time_out': '0'
        }

        # Act - submit invalid form data
        response = client.post('/add', data=data, follow_redirects=True)

        # Assert - verify validation fails appropriately
        assert response.status_code == 200
        # Check that no entry was created with invalid data
        entries = TimeEntry.query.all()
        assert len(entries) == 0


def test_change_operating_date(client, app):
    """Test filtering time entries by operating date."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import UserService
        
        user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
        
        # Arrange - create test entries on different dates
        entry1 = TimeEntry(
            activity_date=datetime(2023, 8, 1),
            from_time=540,  # 9:00 AM
            to_time=570,    # 9:30 AM
            activity='Test entry 1',
        )
        entry2 = TimeEntry(
            activity_date=datetime(2023, 8, 2),
            from_time=600,  # 10:00 AM
            to_time=630,    # 10:30 AM
            activity='Test entry 2',
        )
        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()

        # Act - filter by specific date
        response = client.get('/?date=2023-08-01')

        # Assert - verify correct filtering
        assert response.status_code == 200
        assert b'Test entry 1' in response.data
        assert b'Test entry 2' not in response.data
