"""Tests for user_service.py functionality."""

from unittest.mock import Mock

from app.service.user_service import UserService


class TestUserService:
    """Test class for UserService operations."""

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
            user, error = UserService.create_user(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin,
                is_active=is_active,
            )

            # Assert
            assert user is not None
            assert error == ''
            assert user.username == username  # type: ignore
            assert user.email == email  # type: ignore
            assert user.is_admin == is_admin  # type: ignore
            assert user.is_active == is_active  # type: ignore
            assert user.check_password(password)

    def test_create_user_duplicate_username(self, app):
        """Test user creation with duplicate username."""
        with app.app_context():
            # Arrange - create initial user
            UserService.create_user('testuser', 'test1@example.com', 'password123')

            # Act - try to create user with same username
            user, error = UserService.create_user('testuser', 'test2@example.com', 'password123')

            # Assert
            assert user is None
            assert error == 'Username already exists'

    def test_create_user_duplicate_email(self, app):
        """Test user creation with duplicate email."""
        with app.app_context():
            # Arrange - create initial user
            UserService.create_user('testuser1', 'test@example.com', 'password123')

            # Act - try to create user with same email
            user, error = UserService.create_user('testuser2', 'test@example.com', 'password123')

            # Assert
            assert user is None
            assert error == 'Email already exists'

    def test_create_user_invalid_username(self, app):
        """Test user creation with invalid username."""
        with app.app_context():
            # Act - username too short
            user, error = UserService.create_user('ab', 'test@example.com', 'password123')

            # Assert
            assert user is None
            assert error == 'Username must be at least 3 characters long'

    def test_create_user_invalid_email(self, app):
        """Test user creation with invalid email."""
        with app.app_context():
            # Act - email without @
            user, error = UserService.create_user('testuser', 'invalid-email', 'password123')

            # Assert
            assert user is None
            assert error == 'Invalid email address'

    def test_create_user_invalid_password(self, app):
        """Test user creation with invalid password."""
        with app.app_context():
            # Act - password too short
            user, error = UserService.create_user('testuser', 'test@example.com', '12345')

            # Assert
            assert user is None
            assert error == 'Password must be at least 6 characters long'

    def test_create_user_database_error(self, app):
        """Test user creation with database error."""
        with app.app_context():
            from unittest.mock import patch

            # Mock logger
            with patch('app.service.user_service.current_app') as mock_app:
                mock_app.logger = Mock()

                # Mock db.session.commit to raise IntegrityError
                with patch('app.service.user_service.db.session.commit') as mock_commit:
                    from sqlalchemy.exc import IntegrityError

                    mock_commit.side_effect = IntegrityError('test', 'test', Exception('test'))

                    # Act
                    user, error = UserService.create_user('testuser', 'test@example.com', 'password123')

                    # Assert
                    assert user is None
                    assert error == 'Database error: User creation failed'
                    mock_app.logger.error.assert_called()

    def test_get_user_by_id_success(self, app):
        """Test getting user by ID."""
        with app.app_context():
            # Arrange - create user
            created_user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = UserService.get_user_by_id(created_user.id)  # type: ignore

            # Assert
            assert found_user is not None
            assert found_user.id == created_user.id  # type: ignore
            assert found_user.username == 'testuser'  # type: ignore

    def test_get_user_by_id_not_found(self, app):
        """Test getting user by non-existent ID."""
        with app.app_context():
            # Act
            found_user = UserService.get_user_by_id(999)

            # Assert
            assert found_user is None

    def test_get_user_by_username_success(self, app):
        """Test getting user by username."""
        with app.app_context():
            # Arrange - create user
            UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = UserService.get_user_by_username('testuser')

            # Assert
            assert found_user is not None
            assert found_user.username == 'testuser'  # type: ignore

    def test_get_user_by_username_not_found(self, app):
        """Test getting user by non-existent username."""
        with app.app_context():
            # Act
            found_user = UserService.get_user_by_username('nonexistent')

            # Assert
            assert found_user is None

    def test_get_user_by_email_success(self, app):
        """Test getting user by email."""
        with app.app_context():
            # Arrange - create user
            UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            found_user = UserService.get_user_by_email('test@example.com')

            # Assert
            assert found_user is not None
            assert found_user.email == 'test@example.com'  # type: ignore

    def test_get_user_by_email_not_found(self, app):
        """Test getting user by non-existent email."""
        with app.app_context():
            # Act
            found_user = UserService.get_user_by_email('nonexistent@example.com')

            # Assert
            assert found_user is None

    def test_get_all_users(self, app):
        """Test getting all users."""
        with app.app_context():
            # Arrange - create multiple users
            UserService.create_user('user1', 'user1@example.com', 'password123')
            UserService.create_user('user2', 'user2@example.com', 'password123')
            UserService.create_user('user3', 'user3@example.com', 'password123')

            # Act
            users = UserService.get_all_users()

            # Assert
            assert len(users) == 3
            usernames = [user.username for user in users]
            assert 'user1' in usernames
            assert 'user2' in usernames
            assert 'user3' in usernames

    def test_update_user_success(self, app):
        """Test successful user update."""
        with app.app_context():
            # Arrange - create user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act - update user
            updated_user, error = UserService.update_user(
                user_id=user.id,  # type: ignore
                username='newusername',
                email='newemail@example.com',
                password='newpassword123',
                is_admin=True,
                is_active=False,
            )

            # Assert
            assert updated_user is not None
            assert error == ''
            assert updated_user.username == 'newusername'  # type: ignore
            assert updated_user.email == 'newemail@example.com'  # type: ignore
            assert updated_user.is_admin is True  # type: ignore
            assert updated_user.is_active is False  # type: ignore
            assert updated_user.check_password('newpassword123')

    def test_update_user_not_found(self, app):
        """Test updating non-existent user."""
        with app.app_context():
            # Act
            updated_user, error = UserService.update_user(user_id=999, username='newusername')

            # Assert
            assert updated_user is None
            assert error == 'User not found'

    def test_update_user_duplicate_username(self, app):
        """Test updating user with duplicate username."""
        with app.app_context():
            # Arrange - create two users
            user1, _ = UserService.create_user('user1', 'user1@example.com', 'password123')
            user2, _ = UserService.create_user('user2', 'user2@example.com', 'password123')

            # Act - try to update user2 with user1's username
            updated_user, error = UserService.update_user(
                user_id=user2.id,  # type: ignore
                username='user1',
            )

            # Assert
            assert updated_user is None
            assert error == 'Username already exists'

    def test_update_user_duplicate_email(self, app):
        """Test updating user with duplicate email."""
        with app.app_context():
            # Arrange - create two users
            user1, _ = UserService.create_user('user1', 'user1@example.com', 'password123')
            user2, _ = UserService.create_user('user2', 'user2@example.com', 'password123')

            # Act - try to update user2 with user1's email
            updated_user, error = UserService.update_user(
                user_id=user2.id,  # type: ignore
                email='user1@example.com',
            )

            # Assert
            assert updated_user is None
            assert error == 'Email already exists'

    def test_update_user_short_password(self, app):
        """Test updating user with too short password."""
        with app.app_context():
            # Arrange - create user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act - try to update with short password
            updated_user, error = UserService.update_user(
                user_id=user.id,  # type: ignore
                password='12345',
            )

            # Assert
            assert updated_user is None
            assert error == 'Password must be at least 6 characters long'

    def test_delete_user_success(self, app):
        """Test successful user deletion."""
        with app.app_context():
            # Arrange - create user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            success, error = UserService.delete_user(user.id)  # type: ignore

            # Assert
            assert success is True
            assert error == ''
            assert UserService.get_user_by_id(user.id) is None  # type: ignore

    def test_delete_user_not_found(self, app):
        """Test deleting non-existent user."""
        with app.app_context():
            # Act
            success, error = UserService.delete_user(999)

            # Assert
            assert success is False
            assert error == 'User not found'

    def test_delete_last_admin_user(self, app):
        """Test deleting the last admin user."""
        with app.app_context():
            # Arrange - create only one admin user
            admin_user, _ = UserService.create_user('admin', 'admin@example.com', 'password123', is_admin=True)

            # Act
            success, error = UserService.delete_user(admin_user.id)  # type: ignore

            # Assert
            assert success is False
            assert error == 'Cannot delete the last admin user'

    def test_delete_admin_when_others_exist(self, app):
        """Test deleting admin user when other admins exist."""
        with app.app_context():
            # Arrange - create two admin users
            admin1, _ = UserService.create_user('admin1', 'admin1@example.com', 'password123', is_admin=True)
            admin2, _ = UserService.create_user('admin2', 'admin2@example.com', 'password123', is_admin=True)

            # Act
            success, error = UserService.delete_user(admin1.id)  # type: ignore

            # Assert
            assert success is True
            assert error == ''
            assert UserService.get_user_by_id(admin1.id) is None  # type: ignore
            assert UserService.get_user_by_id(admin2.id) is not None  # type: ignore

    def test_authenticate_user_success_with_username(self, app):
        """Test successful authentication with username."""
        with app.app_context():
            # Arrange - create user
            UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = UserService.authenticate_user('testuser', 'password123')

            # Assert
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'  # type: ignore

    def test_authenticate_user_success_with_email(self, app):
        """Test successful authentication with email."""
        with app.app_context():
            # Arrange - create user
            UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = UserService.authenticate_user('test@example.com', 'password123')

            # Assert
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'  # type: ignore

    def test_authenticate_user_wrong_password(self, app):
        """Test authentication with wrong password."""
        with app.app_context():
            # Arrange - create user
            UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act
            authenticated_user = UserService.authenticate_user('testuser', 'wrongpassword')

            # Assert
            assert authenticated_user is None

    def test_authenticate_user_not_found(self, app):
        """Test authentication with non-existent user."""
        with app.app_context():
            # Act
            authenticated_user = UserService.authenticate_user('nonexistent', 'password123')

            # Assert
            assert authenticated_user is None

    def test_authenticate_inactive_user(self, app):
        """Test authentication with inactive user."""
        with app.app_context():
            # Arrange - create inactive user
            UserService.create_user('testuser', 'test@example.com', 'password123', is_active=False)

            # Act
            authenticated_user = UserService.authenticate_user('testuser', 'password123')

            # Assert
            assert authenticated_user is None

    def test_create_default_admin_when_no_users(self, app):
        """Test creating default admin when no users exist."""
        with app.app_context():
            from unittest.mock import patch

            # Mock logger
            with patch('app.service.user_service.current_app') as mock_app:
                mock_app.logger = Mock()

                # Act
                admin_user = UserService.create_default_admin()

                # Assert
                assert admin_user is not None
                assert admin_user.username == 'admin'  # type: ignore
                assert admin_user.email == 'admin@timetracker.local'  # type: ignore
                assert admin_user.is_admin is True  # type: ignore
                assert admin_user.is_active is True  # type: ignore
                assert admin_user.check_password('admin123')
                mock_app.logger.info.assert_called_with('Created default admin user')

    def test_create_default_admin_when_users_exist(self, app):
        """Test not creating default admin when users already exist."""
        with app.app_context():
            from unittest.mock import patch

            # Arrange - create a user first
            UserService.create_user('existinguser', 'existing@example.com', 'password123')

            with patch('app.service.user_service.current_app') as mock_app:
                mock_app.logger = Mock()

                # Act
                admin_user = UserService.create_default_admin()

                # Assert
                assert admin_user is None
                mock_app.logger.info.assert_not_called()

    def test_update_user_partial_update(self, app):
        """Test updating user with only some fields."""
        with app.app_context():
            # Arrange - create user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')
            original_email = user.email  # type: ignore
            original_password_hash = user.password_hash  # type: ignore

            # Act - update only username
            updated_user, error = UserService.update_user(
                user_id=user.id,  # type: ignore
                username='newusername',
            )

            # Assert
            assert updated_user is not None
            assert error == ''
            assert updated_user.username == 'newusername'  # type: ignore
            assert updated_user.email == original_email  # unchanged  # type: ignore
            assert updated_user.password_hash == original_password_hash  # unchanged  # type: ignore

    def test_update_user_same_values(self, app):
        """Test updating user with same values (no conflicts)."""
        with app.app_context():
            # Arrange - create user
            user, _ = UserService.create_user('testuser', 'test@example.com', 'password123')

            # Act - update with same username and email
            updated_user, error = UserService.update_user(
                user_id=user.id,  # type: ignore
                username='testuser',  # same as before
                email='test@example.com',  # same as before
                is_admin=True,
            )

            # Assert
            assert updated_user is not None
            assert error == ''
            assert updated_user.is_admin is True  # type: ignore
