from datetime import datetime
from app.models import TimeEntry, db

def test_index_route(client):
    # Test empty list
    response = client.get('/')
    assert response.status_code == 200

    # Add test entry and verify it appears
    entry = TimeEntry(
        activity_date=datetime.now(),
        from_time=540,  # 9:00 AM
        to_time=570,    # 9:30 AM
        activity='Test entry'
    )
    db.session.add(entry)
    db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'Test entry' in response.data

def test_add_entry_get(client):
    response = client.get('/add')
    assert response.status_code == 200
    assert b'Add Time Entry' in response.data
    assert b'form' in response.data

def test_add_entry_post_success(client):
    # Test adding a new time entry
    data = {
        'operating_date': '2023-08-01',
        'from_time': '9:00',
        'to_time': '9:30',
        'activity': 'Test entry',
        'time_out': 0
    }

    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200

    # Verify entry was added to database
    entry = TimeEntry.query.filter_by(activity='Test entry').first()
    assert entry is not None

def test_add_entry_validation(client):
    # Test with invalid data
    data = {
        'operating_date': '',
        'from_time': '',
        'to_time': '',
        'activity': '',
        'time_out': -15
    }

    response = client.post('/add', data=data)
    assert response.status_code == 200

    # Verify no entry was added
    entries = TimeEntry.query.all()
    assert len(entries) == 0
