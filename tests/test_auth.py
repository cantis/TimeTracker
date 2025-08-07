"""Tests for authentication routes."""

from app.models import User
from app.service.user_service import UserService


class TestAuthRoutes:
    """Test authentication routes."""

    def test_profile_page_authenticated(self, client, app):
        """Test profile page access when authenticated."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
            assert user is not None  # Type assertion

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            response = client.get('/auth/profile')
            assert response.status_code == 200
            assert b'User Profile' in response.data
            assert b'testuser' in response.data
            assert b'test@example.com' in response.data

    def test_profile_page_unauthenticated(self, client):
        """Test profile page redirects when not authenticated."""
        response = client.get('/auth/profile')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_change_password_page_authenticated(self, client, app):
        """Test change password page access when authenticated."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            response = client.get('/auth/change-password')
            assert response.status_code == 200
            assert b'Change Password' in response.data
            assert b'Current Password' in response.data
            assert b'New Password' in response.data

    def test_change_password_page_unauthenticated(self, client):
        """Test change password page redirects when not authenticated."""
        response = client.get('/auth/change-password')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_change_password_success(self, client, app):
        """Test successful password change."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            # Change password
            response = client.post(
                '/auth/change-password',
                data={
                    'current_password': 'password123',
                    'new_password': 'newpassword456',
                    'confirm_password': 'newpassword456',
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b'Password changed successfully' in response.data

            # Verify password was changed
            updated_user = User.query.get(user.id)
            assert updated_user.check_password('newpassword456')
            assert not updated_user.check_password('password123')

    def test_change_password_wrong_current(self, client, app):
        """Test password change with wrong current password."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            # Try to change password with wrong current password
            response = client.post(
                '/auth/change-password',
                data={
                    'current_password': 'wrongpassword',
                    'new_password': 'newpassword456',
                    'confirm_password': 'newpassword456',
                },
            )

            assert response.status_code == 200
            assert b'Current password is incorrect' in response.data

    def test_change_password_mismatch(self, client, app):
        """Test password change with mismatched new passwords."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            # Try to change password with mismatched confirmation
            response = client.post(
                '/auth/change-password',
                data={
                    'current_password': 'password123',
                    'new_password': 'newpassword456',
                    'confirm_password': 'differentpassword',
                },
            )

            assert response.status_code == 200
            assert b'New passwords do not match' in response.data

    def test_change_password_too_short(self, client, app):
        """Test password change with too short new password."""
        with app.app_context():
            # Create and login test user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            # Try to change password with too short new password
            response = client.post(
                '/auth/change-password',
                data={'current_password': 'password123', 'new_password': '12345', 'confirm_password': '12345'},
            )

            assert response.status_code == 200
            assert b'New password must be at least 6 characters long' in response.data
