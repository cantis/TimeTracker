"""Tests for the weekly_report route in reports.py."""

from datetime import date, datetime, timedelta

from app.models import TimeEntry, db


# Arrange: Setup a test client and test data
def login(client):
    """Helper function to log in the test client."""
    return client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)

def test_weekly_report_get(client):
    """Test GET request to /reports/weekly returns the settings page with correct defaults loaded."""
    # Arrange
    login(client)
    today = date.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)
    last_saturday = last_sunday + timedelta(days=6)

    # Act
    response = client.get('/reports/weekly')

    # Assert
def test_weekly_report_post(client, app):
    """Test POST request to /reports/weekly returns the report page with correct entries."""

    # Arrange
    login(client)
    start_date = date(2025, 5, 18)
    end_date = date(2025, 5, 24)
    with app.app_context():
        entry = TimeEntry(
            activity_date=datetime.combine(start_date, datetime.min.time()),
            from_time=480,
            to_time=540,
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
    assert b'1' in response.data  # duration in hours
    # Assert
    assert response.status_code == 200
    assert b'Test Activity' in response.data
    assert b'2025-05-18' in response.data
    assert b'1' in response.data  # duration in hours
