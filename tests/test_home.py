from datetime import datetime
from app.models import TimeEntry, CommonTimeUse
from app.app import db

def test_index_route(client):
    # Test empty list
    response = client.get('/')
    assert response.status_code == 200
    assert b'Time Entries' in response.data

    # Add test entry and verify it appears
    entry = TimeEntry(
        date=datetime.now(),
        start_time=540,  # 9:00 AM
        duration=30,
        description='Test entry'
    )
    db.session.add(entry)
    db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'Test entry' in response.data
    assert b'30 minutes' in response.data

def test_add_entry_get(client):
    response = client.get('/add')
    assert response.status_code == 200
    assert b'Add Time Entry' in response.data
    assert b'form' in response.data

def test_add_entry_post_success(client):
    # Test adding a new time entry
    data = {
        'date': '2023-08-01',
        'start_time': 540,  # 9:00 AM
        'duration': 30,
        'description': 'Test entry',
        'common_use': 0
    }

    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200

    # Verify entry was added to database
    entry = TimeEntry.query.filter_by(description='Test entry').first()
    assert entry is not None
    assert entry.duration == 30
    assert entry.start_time == 540

def test_add_entry_post_with_common_use(client):
    # Test adding entry with common use
    common_use = CommonTimeUse.query.filter_by(description='Meeting').first()

    data = {
        'date': '2023-08-01',
        'start_time': 600,  # 10:00 AM
        'duration': 45,
        'description': '',
        'common_use': common_use.id
    }

    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200

    # Verify entry was added with common use
    entry = TimeEntry.query.filter_by(start_time=600).first()
    assert entry is not None
    assert entry.common_use.description == 'Meeting'
    assert entry.duration == 45

def test_add_entry_validation(client):
    # Test with invalid data
    data = {
        'date': 'invalid-date',
        'start_time': 'not-a-number',
        'duration': -15,
        'description': '',
        'common_use': 0
    }

    response = client.post('/add', data=data)
    assert response.status_code == 200
    assert b'Add Time Entry' in response.data  # Should stay on form page

    # Verify no entry was added
    entries = TimeEntry.query.all()
    assert len(entries) == 0
