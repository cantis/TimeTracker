from datetime import datetime
from app.models import TimeEntry, db

def test_index_route(client, app):
    with app.app_context():
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

def test_add_entry_post_success(client, app):
    with app.app_context():
        # arrange
        data = {
            'operating_date': '2023-08-01',
            'from_time': '9:00',
            'to_time': '9:30',
            'activity': 'Test entry',
            'time_out': 0
        }

        # act
        response = client.post('/add', data=data, follow_redirects=True)
        assert response.status_code == 200

        # assert
        entry = TimeEntry.query.filter_by(activity='Test entry').first()
        assert entry is not None

def test_add_entry_validation_fail(client, app):
    with app.app_context():
        # arrange
        data = {
            'operating_date': '',
            'from_time': '',
            'to_time': '',
            'activity': '',
            'time_out': 0
        }

        # act
        response = client.post('/add', data=data)
        assert response.status_code == 200

        # assert 
        entries = TimeEntry.query.all()
        assert len(entries) == 0

def test_change_operating_date(client, app):
    with app.app_context():
        # Arrange
        entry1 = TimeEntry(
            activity_date=datetime(2023, 8, 1),
            from_time=540,  # 9:00 AM
            to_time=570,    # 9:30 AM
            activity='Test entry 1'
        )
        entry2 = TimeEntry(
            activity_date=datetime(2023, 8, 2),
            from_time=600,  # 10:00 AM
            to_time=630,    # 10:30 AM
            activity='Test entry 2'
        )
        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()

        # Act
        response = client.get('/?date=2023-08-01')

        # Assert
        assert response.status_code == 200
        assert b'Test entry 1' in response.data
        assert b'Test entry 2' not in response.data
