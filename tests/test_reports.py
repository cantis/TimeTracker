"""Tests for the weekly_report route in reports.py."""

from datetime import date, datetime, timedelta

from app.models import TimeEntry, db


# Arrange: Setup a test client and test data
def test_weekly_report_get(client):
    """Test GET request to /reports/weekly returns the settings page with correct defaults loaded."""
    # Arrange
    today = date.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)
    last_saturday = last_sunday + timedelta(days=6)

    # Act
    response = client.get('/reports/weekly')

    # Assert
    assert response.status_code == 200
    assert bytes(last_sunday.strftime('%Y-%m-%d'), 'utf-8') in response.data
    assert bytes(last_saturday.strftime('%Y-%m-%d'), 'utf-8') in response.data


def test_weekly_report_post(client, app):
    """Test POST request to /reports/weekly returns the report page with correct entries."""

    # Arrange
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
    )
    # Assert
    assert response.status_code == 200
    assert b'Test Activity' in response.data
    assert b'2025-05-18' in response.data
    assert b'1' in response.data  # duration in hours
