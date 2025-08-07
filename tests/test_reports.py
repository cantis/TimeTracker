"""Tests for the weekly_report route in reports.py."""

from datetime import date, datetime

from app.models import TimeEntry, db


# Arrange: Setup a test client and test data
def login(client):
    """Helper function to log in the test client."""
    return client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)


def test_weekly_report_get(client, app):
    """Test GET request to /reports/weekly returns the settings page with correct defaults loaded."""
    # Arrange
    with app.app_context():
        # Create admin user for login
        from app.service.user_service import UserService

        admin_user, _ = UserService.create_user('admin', 'admin@test.com', 'admin123', is_admin=True)
        assert admin_user is not None

    login(client)

    # Act
    response = client.get('/reports/weekly')

    # Assert
    assert response.status_code == 200
    assert b'Weekly Report Settings' in response.data or b'Weekly Report' in response.data


def test_weekly_report_post(client, app):
    """Test POST request to /reports/weekly returns the report page with correct entries."""

    # Arrange
    with app.app_context():
        # Create admin user for login
        from app.service.user_service import UserService

        admin_user, _ = UserService.create_user('admin', 'admin@test.com', 'admin123', is_admin=True)
        assert admin_user is not None

    login(client)
    start_date = date(2025, 5, 18)
    end_date = date(2025, 5, 24)

    with app.app_context():
        entry = TimeEntry(
            activity_date=datetime.combine(start_date, datetime.min.time()),
            from_time=480,  # 8:00 AM
            to_time=540,  # 9:00 AM
            activity='Test Activity',
        )
        db.session.add(entry)
        db.session.commit()

    # Act
    response = client.post(
        '/reports/weekly',
        data={
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        },
        follow_redirects=True,
    )

    # Assert
    assert response.status_code == 200
    assert b'Test Activity' in response.data
    assert b'2025-05-18' in response.data
