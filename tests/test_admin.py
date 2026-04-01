"""Tests for admin routes."""

from app.models import User
from app.service.user_service import create_user


def _login_as_admin(client, app):
    """Helper: create an admin user and log in."""
    with app.app_context():
        admin = create_user('admin', 'admin@example.com', 'admin123', is_admin=True)
        admin_id = admin.id

    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_id)
        sess['_fresh'] = True

    return admin_id


def _login_as_regular_user(client, app):
    """Helper: create a regular user and log in."""
    with app.app_context():
        user = create_user('regular', 'regular@example.com', 'password123')
        user_id = user.id

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True

    return user_id


class TestAdminRequired:
    """Test admin_required decorator blocks non-admin users."""

    def test_user_list_requires_admin(self, client, app):
        """Non-admin users are redirected away from user list."""
        _login_as_regular_user(client, app)
        response = client.get('/admin/users', follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin privileges required' in response.data

    def test_add_user_requires_admin(self, client, app):
        """Non-admin users are redirected away from add user."""
        _login_as_regular_user(client, app)
        response = client.get('/admin/users/add', follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin privileges required' in response.data

    def test_unauthenticated_user_list_redirects(self, client):
        """Unauthenticated access to admin routes redirects to login."""
        response = client.get('/admin/users')
        assert response.status_code == 302
        assert '/auth/login' in response.location


class TestUserList:
    """Tests for the admin user list page."""

    def test_user_list_displays_users(self, client, app):
        """Admin can view the user list."""
        _login_as_admin(client, app)
        with app.app_context():
            create_user('anotheruser', 'another@example.com', 'password123')

        response = client.get('/admin/users')
        assert response.status_code == 200
        assert b'anotheruser' in response.data
        assert b'admin' in response.data


class TestAddUser:
    """Tests for the add user admin page."""

    def test_add_user_page_loads(self, client, app):
        """Admin can load the add user form."""
        _login_as_admin(client, app)
        response = client.get('/admin/users/add')
        assert response.status_code == 200

    def test_add_user_success(self, client, app):
        """Admin can create a new user."""
        _login_as_admin(client, app)

        response = client.post(
            '/admin/users/add',
            data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'is_active': 'on',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'created successfully' in response.data

        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert not user.is_admin

    def test_add_user_duplicate_username(self, client, app):
        """Adding a user with an existing username shows an error."""
        _login_as_admin(client, app)
        with app.app_context():
            create_user('duplicate', 'dup@example.com', 'password123')

        response = client.post(
            '/admin/users/add',
            data={
                'username': 'duplicate',
                'email': 'other@example.com',
                'password': 'password123',
                'is_active': 'on',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b'Error creating user' in response.data


class TestDeleteUser:
    """Tests for deleting users via admin."""

    def test_delete_user_success(self, client, app):
        """Admin can delete another user."""
        _login_as_admin(client, app)

        with app.app_context():
            target = create_user('target', 'target@example.com', 'password123')
            target_id = target.id

        response = client.post(f'/admin/users/{target_id}/delete', follow_redirects=True)
        assert response.status_code == 200

        with app.app_context():
            assert User.query.get(target_id) is None

    def test_delete_self_forbidden(self, client, app):
        """Admin cannot delete their own account."""
        admin_id = _login_as_admin(client, app)

        response = client.post(f'/admin/users/{admin_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        # Should report an error rather than deleting
        assert b'cannot' in response.data.lower() or b'error' in response.data.lower() or b'Error' in response.data
