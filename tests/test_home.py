"""Tests for home routes and time entry functionality."""

from datetime import datetime

from app.models import TimeEntry, db


def test_index_route(client, app):
    """Test the main index route displays time entries."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        login_response = client.post(
            '/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True
        )
        assert login_response.status_code == 200

        # Test empty list
        response = client.get('/')
        assert response.status_code == 200

        # Add some test time entries (times in minutes past midnight)
        today = datetime.now().date()
        entry1 = TimeEntry(
            activity_date=datetime.combine(today, datetime.min.time()),
            from_time=540,  # 9:00 AM (9 * 60 = 540 minutes)
            to_time=1020,  # 5:00 PM (17 * 60 = 1020 minutes)
            user_id=user.id,
            activity='Test task 1',
        )
        entry2 = TimeEntry(
            activity_date=datetime.combine(today, datetime.min.time()),
            from_time=600,  # 10:00 AM (10 * 60 = 600 minutes)
            to_time=1080,  # 6:00 PM (18 * 60 = 1080 minutes)
            user_id=user.id,
            activity='Test task 2',
        )
        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()

        # Test list with entries
        response = client.get('/')
        assert response.status_code == 200
        assert b'Test task 1' in response.data
        assert b'Test task 2' in response.data


def test_add_time_entry(client, app):
    """Test adding a new time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Add a time entry using the actual form structure
        today = datetime.now().strftime('%Y-%m-%d')
        response = client.post(
            '/add',
            data={
                'operating_date': today,
                'from_time': '9:00',  # This will be converted to 540 minutes
                'to_time': '17:00',  # This will be converted to 1020 minutes
                'activity': 'New test task',
                'time_out': '1',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'Time entry added successfully' in response.data

        # Verify the entry was added to database
        entry = TimeEntry.query.filter_by(activity='New test task').first()
        assert entry is not None
        assert entry.from_time == 540  # 9:00 AM in minutes
        assert entry.to_time == 1020  # 5:00 PM in minutes
        assert entry.activity == 'New test task'


def test_edit_time_entry(client, app):
    """Test editing an existing time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Create initial time entry using correct model fields
        today = datetime.now().date()
        entry = TimeEntry(
            activity_date=datetime.combine(today, datetime.min.time()),
            from_time=540,  # 9:00 AM in minutes
            to_time=1020,  # 5:00 PM in minutes
            user_id=user.id,
            activity='Original task',
        )
        db.session.add(entry)
        db.session.commit()

        # Edit the time entry using the actual form structure
        response = client.post(
            '/add',
            data={
                'entry_id': str(entry.id),
                'operating_date': today.strftime('%Y-%m-%d'),
                'from_time': '10:00',  # This will be converted to 600 minutes
                'to_time': '18:00',  # This will be converted to 1080 minutes
                'activity': 'Updated task',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'Time entry updated successfully' in response.data

        # Verify the entry was updated
        updated_entry = TimeEntry.query.get(entry.id)
        assert updated_entry is not None
        assert updated_entry.activity == 'Updated task'
        assert updated_entry.from_time == 600  # 10:00 AM in minutes
        assert updated_entry.to_time == 1080  # 6:00 PM in minutes


def test_delete_time_entry(client, app):
    """Test deleting a time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Create initial time entry using correct model fields
        today = datetime.now().date()
        entry = TimeEntry(
            activity_date=datetime.combine(today, datetime.min.time()),
            from_time=540,  # 9:00 AM in minutes
            to_time=1020,  # 5:00 PM in minutes
            user_id=user.id,
            activity='Task to delete',
        )
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id

        # Delete the time entry using the actual route
        response = client.post(f'/entry/{entry_id}/delete', follow_redirects=True)

        assert response.status_code == 200

        # Verify the entry was deleted
        deleted_entry = TimeEntry.query.get(entry_id)
        assert deleted_entry is None
