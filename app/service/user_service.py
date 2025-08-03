"""User management service for handling user operations."""

from typing import List, Optional

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.models import User, db


class UserService:
    """Service class for user management operations."""

    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        is_active: bool = True,
    ) -> tuple[User | None, str]:
        """
        Create a new user.

        Returns:
            Tuple of (User, error_message). User is None if creation failed.
        """
        try:
            # Check if username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

            if existing_user:
                if existing_user.username == username:
                    return None, 'Username already exists'
                else:
                    return None, 'Email already exists'

            # Validate input
            if not username or len(username) < 3:
                return None, 'Username must be at least 3 characters long'

            if not email or '@' not in email:
                return None, 'Invalid email address'

            if not password or len(password) < 6:
                return None, 'Password must be at least 6 characters long'

            # Create new user
            user = User(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin,
                is_active=is_active,
            )

            db.session.add(user)
            db.session.commit()

            current_app.logger.info(f'Created new user: {username}')
            return user, ''

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Database error creating user {username}: {e}')
            return None, 'Database error: User creation failed'
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Unexpected error creating user {username}: {e}')
            return None, 'Unexpected error occurred'

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get a user by their username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by their email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users ordered by username."""
        return User.query.order_by(User.username).all()

    @staticmethod
    def update_user(
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_admin: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[User | None, str]:
        """
        Update an existing user.

        Returns:
            Tuple of (User, error_message). User is None if update failed.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None, 'User not found'

            # Check for conflicts if updating username or email
            if username and username != user.username:
                existing = User.query.filter_by(username=username).first()
                if existing:
                    return None, 'Username already exists'
                user.username = username

            if email and email != user.email:
                existing = User.query.filter_by(email=email).first()
                if existing:
                    return None, 'Email already exists'
                user.email = email

            if password:
                if len(password) < 6:
                    return None, 'Password must be at least 6 characters long'
                user.set_password(password)

            if is_admin is not None:
                user.is_admin = is_admin

            if is_active is not None:
                user.user_active = is_active

            db.session.commit()

            current_app.logger.info(f'Updated user: {user.username}')
            return user, ''

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Database error updating user {user_id}: {e}')
            return None, 'Database error: User update failed'
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Unexpected error updating user {user_id}: {e}')
            return None, 'Unexpected error occurred'

    @staticmethod
    def delete_user(user_id: int) -> tuple[bool, str]:
        """
        Delete a user.

        Returns:
            Tuple of (success, error_message).
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'

            # Don't allow deletion of the last admin user
            if user.is_admin:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    return False, 'Cannot delete the last admin user'

            username = user.username
            db.session.delete(user)
            db.session.commit()

            current_app.logger.info(f'Deleted user: {username}')
            return True, ''

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting user {user_id}: {e}')
            return False, 'Error deleting user'

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username/email and password.

        Returns:
            User object if authentication successful, None otherwise.
        """
        # Try to find user by username or email
        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if user and user.is_active and user.check_password(password):
            return user

        return None

    @staticmethod
    def create_default_admin() -> Optional[User]:
        """Create a default admin user if no users exist."""
        user_count = User.query.count()
        if user_count == 0:
            admin_user = User(
                username='admin',
                email='admin@timetracker.local',
                password='admin123',
                is_admin=True,
                is_active=True,
            )
            db.session.add(admin_user)
            db.session.commit()
            current_app.logger.info('Created default admin user')
            return admin_user
        return None
