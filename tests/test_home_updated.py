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
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Test empty list
        response = client.get('/')
        assert response.status_code == 200
        assert b'Time Entries' in response.data

        # Add some test time entries
        entry1 = TimeEntry(
            start_time=datetime(2023, 1, 1, 9, 0),
            end_time=datetime(2023, 1, 1, 17, 0),
            task_description='Test task 1',
            user_id=user.id,
        )
        entry2 = TimeEntry(
            start_time=datetime(2023, 1, 2, 10, 0),
            end_time=datetime(2023, 1, 2, 18, 0),
            task_description='Test task 2',
            user_id=user.id,
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

        # Add a time entry
        response = client.post(
            '/add-entry',
            data={
                'start_time': '2023-01-01T09:00',
                'end_time': '2023-01-01T17:00',
                'task_description': 'New test task',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'Time entry added successfully' in response.data

        # Verify the entry was added to database
        entry = TimeEntry.query.filter_by(task_description='New test task').first()
        assert entry is not None
        assert entry.user_id == user.id
        assert entry.start_time.hour == 9
        assert entry.end_time.hour == 17


def test_edit_time_entry(client, app):
    """Test editing an existing time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Create initial time entry
        entry = TimeEntry(
            start_time=datetime(2023, 1, 1, 9, 0),
            end_time=datetime(2023, 1, 1, 17, 0),
            task_description='Original task',
            user_id=user.id,
        )
        db.session.add(entry)
        db.session.commit()

        # Edit the time entry
        response = client.post(
            f'/edit-entry/{entry.id}',
            data={
                'start_time': '2023-01-01T10:00',
                'end_time': '2023-01-01T18:00',
                'task_description': 'Updated task',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'Time entry updated successfully' in response.data

        # Verify the entry was updated
        updated_entry = TimeEntry.query.get(entry.id)
        assert updated_entry.task_description == 'Updated task'
        assert updated_entry.start_time.hour == 10
        assert updated_entry.end_time.hour == 18


def test_delete_time_entry(client, app):
    """Test deleting a time entry."""
    with app.app_context():
        # Create test user for authentication
        from app.service.user_service import create_user

        user = create_user('testuser', 'test@example.com', 'password123')
        assert user is not None

        # Log in as test user
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

        # Create initial time entry
        entry = TimeEntry(
            start_time=datetime(2023, 1, 1, 9, 0),
            end_time=datetime(2023, 1, 1, 17, 0),
            task_description='Task to delete',
            user_id=user.id,
        )
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id

        # Delete the time entry
        response = client.post(f'/delete-entry/{entry_id}', follow_redirects=True)

        assert response.status_code == 200
        assert b'Time entry deleted successfully' in response.data

        # Verify the entry was deleted
        deleted_entry = TimeEntry.query.get(entry_id)
        assert deleted_entry is None
