from datetime import datetime
from app.models import TimeEntry, db

def test_index_route(client, app):
    with app.app_context():
        # Ensure test user exists
        from app.models import User
        if not User.query.filter_by(username='test').first():
            user = User(username='test')
            user.set_password('test')
            db.session.add(user)
            db.session.commit()
        # Log in as test user
        client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)
        # Test empty list
        response = client.get('/')
        assert response.status_code == 200

        # Add test entry and verify it appears
        entry = TimeEntry(
            activity_date=datetime.now(),
            from_time=540,  # 9:00 AM
            to_time=570,    # 9:30 AM
def test_add_entry_post_success(client, app):
    with app.app_context():
        # Ensure test user exists
        from app.models import User
        if not User.query.filter_by(username='test').first():
            user = User(username='test')
            user.set_password('test')
            db.session.add(user)
            db.session.commit()
        # Log in as test user
        client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)
        # arrange
        data = {
            'operating_date': '2023-08-01',
            'from_time': '9:00',
            'to_time': '9:30',
            'activity': 'Test entry',
            'time_out': 0
        }
def test_add_entry_validation_fail(client, app):
     with app.app_context():
        # Ensure test user exists
        from app.models import User
        if not User.query.filter_by(username='test').first():
            user = User(username='test')
            user.set_password('test')
            db.session.add(user)
            db.session.commit()
        # Log in as test user
        client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)
        # arrange
        data = {
            'operating_date': '',
            'from_time': '',
            'to_time': '',
            'activity': '',
            'time_out': 0
        }
def test_change_operating_date(client, app):
    with app.app_context():
        # Ensure test user exists
        from app.models import User
        if not User.query.filter_by(username='test').first():
            user = User(username='test')
            user.set_password('test')
            db.session.add(user)
            db.session.commit()
        # Log in as test user
        client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)
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
        entries = TimeEntry.query.all()
def test_change_operating_date(client, app):
    with app.app_context():
        # Log in as test user if authentication is required
        client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)
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
        response = client.get('/?date=2023-08-01')

        # Assert
        assert response.status_code == 200
        assert b'Test entry 1' in response.data
        assert b'Test entry 2' not in response.data
