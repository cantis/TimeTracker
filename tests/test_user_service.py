"""Updated tests for user_service.py functionality using exception-based approach."""

import os
from unittest.mock import patch

import pytest

from app.service.user_service import (
    CreateUserError,
    DeleteUserError,
    UpdateUserError,
    authenticate_user,
    create_default_admin,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user,
)


class TestUserService:
    """Test class for user service module functions."""

    # region create_user tests

    def test_create_user_success(self, app):
        """Test successful user creation."""
        with app.app_context():
            # Arrange
            username = 'testuser'
            email = 'test@example.com'
            password = 'password123'
            is_admin = False
            is_active = True

            # Act
            user = create_user(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin,
                is_active=is_active,
            )

            # Assert
            assert user is not None
            assert user.username == username
            assert user.email == email
            assert user.is_admin == is_admin
            assert user.is_active == is_active
            assert user.check_password(password)

    def test_create_user_with_admin_privileges(self, app):
        """Test creating user with admin privileges."""
        with app.app_context():
            # Act
            user = create_user('admin', 'admin@example.com', 'password123', is_admin=True)

            # Assert
            assert user is not None
            assert user.is_admin is True
            assert user.username == 'admin'

    def test_create_user_with_inactive_status(self, app):
        """Test creating user with inactive status."""
        with app.app_context():
            # Act
            user = create_user('testuser', 'test@example.com', 'password123', is_active=False)

            # Assert
            assert user is not None
            assert user.is_active is False

    def test_create_user_duplicate_username_raises_exception(self, app):
        """Test creating user with existing username raises CreateUserError."""
        with app.app_context():
            # Arrange
            create_user('existinguser', 'existing@example.com', 'password123')

            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('existinguser', 'new@example.com', 'password123')
            assert exc_info.value.message == 'Username already exists'

    def test_create_user_duplicate_email_raises_exception(self, app):
        """Test creating user with existing email raises CreateUserError."""
        with app.app_context():
            # Arrange
            create_user('existinguser', 'existing@example.com', 'password123')

            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('newuser', 'existing@example.com', 'password123')
            assert exc_info.value.message == 'Email already exists'

    def test_create_user_short_username_raises_exception(self, app):
        """Test creating user with short username raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('ab', 'test@example.com', 'password123')
            assert exc_info.value.message == 'Username must be at least 3 characters long'

    def test_create_user_invalid_email_raises_exception(self, app):
        """Test creating user with invalid email raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('testuser', 'invalid-email', 'password123')
            assert exc_info.value.message == 'Invalid email address'

    def test_create_user_short_password_raises_exception(self, app):
        """Test creating user with short password raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('testuser', 'test@example.com', '12345')
            assert exc_info.value.message == 'Password must be at least 6 characters long'

    def test_create_user_empty_username_raises_exception(self, app):
        """Test creating user with empty username raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('', 'test@example.com', 'password123')
            assert exc_info.value.message == 'Username must be at least 3 characters long'

    def test_create_user_empty_email_raises_exception(self, app):
        """Test creating user with empty email raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('testuser', '', 'password123')
            assert exc_info.value.message == 'Invalid email address'

    def test_create_user_empty_password_raises_exception(self, app):
        """Test creating user with empty password raises CreateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('testuser', 'test@example.com', '')
            assert exc_info.value.message == 'Password must be at least 6 characters long'

    @patch('app.service.user_service.db.session.commit')
    def test_create_user_database_error_raises_exception(self, mock_commit, app):
        """Test database error during user creation raises CreateUserError."""
        with app.app_context():
            # Arrange
            from sqlalchemy.exc import IntegrityError

            mock_commit.side_effect = IntegrityError('test', 'test', 'test')

            # Act & Assert
            with pytest.raises(CreateUserError) as exc_info:
                create_user('testuser', 'test@example.com', 'password123')
            assert exc_info.value.message == 'Database error: User creation failed'

    # endregion

    # region get_user tests

    def test_get_user_by_id_success(self, app):
        """Test retrieving user by ID."""
        with app.app_context():
            # Arrange
            created_user = create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = get_user_by_id(created_user.id)

            # Assert
            assert found_user is not None
            assert found_user.id == created_user.id
            assert found_user.username == 'testuser'
            assert found_user.email == 'test@example.com'

    def test_get_user_by_id_not_found(self, app):
        """Test retrieving non-existent user by ID returns None."""
        with app.app_context():
            # Act
            found_user = get_user_by_id(999)

            # Assert
            assert found_user is None

    def test_get_user_by_username_success(self, app):
        """Test retrieving user by username."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = get_user_by_username('testuser')

            # Assert
            assert found_user is not None
            assert found_user.username == 'testuser'
            assert found_user.email == 'test@example.com'

    def test_get_user_by_username_not_found(self, app):
        """Test retrieving non-existent user by username returns None."""
        with app.app_context():
            # Act
            found_user = get_user_by_username('nonexistent')

            # Assert
            assert found_user is None

    def test_get_user_by_email_success(self, app):
        """Test retrieving user by email."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = get_user_by_email('test@example.com')

            # Assert
            assert found_user is not None
            assert found_user.username == 'testuser'
            assert found_user.email == 'test@example.com'

    def test_get_user_by_email_not_found(self, app):
        """Test retrieving non-existent user by email returns None."""
        with app.app_context():
            # Act
            found_user = get_user_by_email('nonexistent@example.com')

            # Assert
            assert found_user is None

    def test_get_all_users_empty(self, app):
        """Test retrieving all users when none exist."""
        with app.app_context():
            # Act
            users = get_all_users()

            # Assert
            assert len(users) == 0

    def test_get_all_users_multiple(self, app):
        """Test retrieving all users in sorted order."""
        with app.app_context():
            # Arrange
            create_user('zebra', 'zebra@example.com', 'password123')
            create_user('apple', 'apple@example.com', 'password123')
            create_user('banana', 'banana@example.com', 'password123')

            # Act
            users = get_all_users()

            # Assert
            assert len(users) == 3
            usernames = [user.username for user in users]
            assert usernames == ['apple', 'banana', 'zebra']

    # endregion

    # region update_user tests

    def test_update_user_username_success(self, app):
        """Test updating user's username."""
        with app.app_context():
            # Arrange
            user = create_user('oldname', 'test@example.com', 'password123')

            # Act
            updated_user = update_user(user.id, username='newname')

            # Assert
            assert updated_user is not None
            assert updated_user.username == 'newname'
            assert updated_user.id == user.id

    def test_update_user_email_success(self, app):
        """Test updating user's email."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'old@example.com', 'password123')

            # Act
            updated_user = update_user(user.id, email='new@example.com')

            # Assert
            assert updated_user is not None
            assert updated_user.email == 'new@example.com'

    def test_update_user_password_success(self, app):
        """Test updating user's password."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'oldpassword')

            # Act
            updated_user = update_user(user.id, password='newpassword123')

            # Assert
            assert updated_user is not None
            assert updated_user.check_password('newpassword123')
            assert not updated_user.check_password('oldpassword')

    def test_update_user_admin_status_success(self, app):
        """Test updating user's admin status."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'password123', is_admin=False)

            # Act
            updated_user = update_user(user.id, is_admin=True)

            # Assert
            assert updated_user is not None
            assert updated_user.is_admin is True

    def test_update_user_active_status_success(self, app):
        """Test updating user's active status."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'password123', is_active=True)

            # Act
            updated_user = update_user(user.id, is_active=False)

            # Assert
            assert updated_user is not None
            assert updated_user.is_active is False

    def test_update_user_multiple_fields_success(self, app):
        """Test updating multiple user fields at once."""
        with app.app_context():
            # Arrange
            user = create_user('oldname', 'old@example.com', 'oldpassword', is_admin=False, is_active=True)

            # Act
            updated_user = update_user(
                user.id,
                username='newname',
                email='new@example.com',
                password='newpassword123',
                is_admin=True,
                is_active=False,
            )

            # Assert
            assert updated_user is not None
            assert updated_user.username == 'newname'
            assert updated_user.email == 'new@example.com'
            assert updated_user.check_password('newpassword123')
            assert updated_user.is_admin is True
            assert updated_user.is_active is False

    def test_update_user_not_found_raises_exception(self, app):
        """Test updating non-existent user raises UpdateUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(UpdateUserError) as exc_info:
                update_user(999, username='newname')
            assert exc_info.value.message == 'User not found'
            assert exc_info.value.user_id == 999

    def test_update_user_duplicate_username_raises_exception(self, app):
        """Test updating user with existing username raises UpdateUserError."""
        with app.app_context():
            # Arrange
            create_user('existinguser', 'existing@example.com', 'password123')
            user = create_user('testuser', 'test@example.com', 'password123')

            # Act & Assert
            with pytest.raises(UpdateUserError) as exc_info:
                update_user(user.id, username='existinguser')
            assert exc_info.value.message == 'Username already exists'
            assert exc_info.value.user_id == user.id

    def test_update_user_duplicate_email_raises_exception(self, app):
        """Test updating user with existing email raises UpdateUserError."""
        with app.app_context():
            # Arrange
            create_user('existinguser', 'existing@example.com', 'password123')
            user = create_user('testuser', 'test@example.com', 'password123')

            # Act & Assert
            with pytest.raises(UpdateUserError) as exc_info:
                update_user(user.id, email='existing@example.com')
            assert exc_info.value.message == 'Email already exists'
            assert exc_info.value.user_id == user.id

    def test_update_user_short_password_raises_exception(self, app):
        """Test updating user with short password raises UpdateUserError."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'password123')

            # Act & Assert
            with pytest.raises(UpdateUserError) as exc_info:
                update_user(user.id, password='12345')
            assert exc_info.value.message == 'Password must be at least 6 characters long'
            assert exc_info.value.user_id == user.id

    # endregion

    # region delete_user tests

    def test_delete_user_success(self, app):
        """Test successful user deletion."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'password123')
            user_id = user.id

            # Act
            delete_user(user_id)

            # Assert - user should no longer exist
            deleted_user = get_user_by_id(user_id)
            assert deleted_user is None

    def test_delete_user_not_found_raises_exception(self, app):
        """Test deleting non-existent user raises DeleteUserError."""
        with app.app_context():
            # Act & Assert
            with pytest.raises(DeleteUserError) as exc_info:
                delete_user(999)
            assert exc_info.value.message == 'User not found'
            assert exc_info.value.user_id == 999

    def test_delete_last_admin_raises_exception(self, app):
        """Test deleting last admin user raises DeleteUserError."""
        with app.app_context():
            # Arrange - create only one admin user
            admin_user = create_user('admin', 'admin@example.com', 'password123', is_admin=True)

            # Act & Assert
            with pytest.raises(DeleteUserError) as exc_info:
                delete_user(admin_user.id)
            assert exc_info.value.message == 'Cannot delete the last admin user'
            assert exc_info.value.user_id == admin_user.id

    def test_delete_user_with_multiple_admins_success(self, app):
        """Test deleting admin user when multiple admins exist."""
        with app.app_context():
            # Arrange
            admin1 = create_user('admin1', 'admin1@example.com', 'password123', is_admin=True)
            admin2 = create_user('admin2', 'admin2@example.com', 'password123', is_admin=True)

            # Act
            delete_user(admin1.id)

            # Assert
            deleted_user = get_user_by_id(admin1.id)
            assert deleted_user is None
            # Ensure other admin still exists
            remaining_admin = get_user_by_id(admin2.id)
            assert remaining_admin is not None

    @patch('app.service.user_service.db.session.delete')
    def test_delete_user_database_error_raises_exception(self, mock_delete, app):
        """Test database error during user deletion raises DeleteUserError."""
        with app.app_context():
            # Arrange
            user = create_user('testuser', 'test@example.com', 'password123')
            mock_delete.side_effect = Exception('Database error')

            # Act & Assert
            with pytest.raises(DeleteUserError) as exc_info:
                delete_user(user.id)
            assert exc_info.value.message == 'Error deleting user'
            assert exc_info.value.user_id == user.id

    # endregion

    # region authenticate_user tests

    def test_authenticate_user_by_username_success(self, app):
        """Test successful authentication using username."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = authenticate_user('testuser', 'password123')

            # Assert
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'

    def test_authenticate_user_by_email_success(self, app):
        """Test successful authentication using email."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = authenticate_user('test@example.com', 'password123')

            # Assert
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'

    def test_authenticate_user_wrong_password(self, app):
        """Test authentication with wrong password."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = authenticate_user('testuser', 'wrongpassword')

            # Assert
            assert authenticated_user is None

    def test_authenticate_user_inactive_user(self, app):
        """Test authentication with inactive user."""
        with app.app_context():
            # Arrange
            create_user('testuser', 'test@example.com', 'password123', is_active=False)

            # Act
            authenticated_user = authenticate_user('testuser', 'password123')

            # Assert
            assert authenticated_user is None

    def test_authenticate_user_nonexistent_user(self, app):
        """Test authentication with non-existent user."""
        with app.app_context():
            # Act
            authenticated_user = authenticate_user('nonexistent', 'password123')

            # Assert
            assert authenticated_user is None

    # endregion

    # region create_default_admin tests

    def test_create_default_admin_when_no_users(self, app):
        """Test creating default admin when no users exist."""
        with app.app_context():
            # Act
            admin_user = create_default_admin()

            # Assert
            assert admin_user is not None
            assert admin_user.username == 'admin'
            assert admin_user.email == 'admin@timetracker.local'
            assert admin_user.is_admin is True
            assert admin_user.is_active is True
            assert admin_user.check_password('admin123')

    def test_create_default_admin_when_users_exist(self, app):
        """Test that default admin is not created when users already exist."""
        with app.app_context():
            # Arrange
            create_user('existinguser', 'existing@example.com', 'password123')

            # Act
            admin_user = create_default_admin()

            # Assert
            assert admin_user is None

    @patch.dict(
        os.environ,
        {
            'DEFAULT_ADMIN_USERNAME': 'customadmin',
            'DEFAULT_ADMIN_EMAIL': 'custom@admin.com',
            'DEFAULT_ADMIN_PASSWORD': 'custompass123',
        },
    )
    def test_create_default_admin_with_custom_env_vars(self, app):
        """Test creating default admin with custom environment variables."""
        with app.app_context():
            # Act
            admin_user = create_default_admin()

            # Assert
            assert admin_user is not None
            assert admin_user.username == 'customadmin'
            assert admin_user.email == 'custom@admin.com'
            assert admin_user.check_password('custompass123')
            assert admin_user.is_admin is True

    # endregion
