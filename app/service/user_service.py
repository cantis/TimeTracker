"""User management service for handling user operations."""

import os
from typing import List, Optional

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.models import User, db


class UpdateUserError(Exception):
    """Custom exception for user update operations."""

    def __init__(self, message: str, user_id: Optional[int] = None):
        """Initialize the exception with a message and optional user ID."""
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)


class CreateUserError(Exception):
    """Custom exception for user creation operations."""

    def __init__(self, message: str):
        """Initialize the exception with a message."""
        self.message = message
        super().__init__(self.message)


class DeleteUserError(Exception):
    """Custom exception for user deletion operations."""

    def __init__(self, message: str, user_id: Optional[int] = None):
        """Initialize the exception with a message and optional user ID."""
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)


def create_user(
    username: str,
    email: str,
    password: str,
    is_admin: bool = False,
    is_active: bool = True,
) -> User:
    """Create a new user."""
    try:
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            raise CreateUserError('Username already exists')

        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            raise CreateUserError('Email already exists')

        # Validate input
        if not username or len(username) < 3:
            raise CreateUserError('Username must be at least 3 characters long')

        if not email or '@' not in email:
            raise CreateUserError('Invalid email address')

        if not password or len(password) < 6:
            raise CreateUserError('Password must be at least 6 characters long')

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
        return user

    except CreateUserError:
        # Re-raise our custom exception
        db.session.rollback()
        raise
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error creating user {username}: {e}')
        raise CreateUserError('Database error: User creation failed') from e
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Unexpected error creating user {username}: {e}')
        raise CreateUserError('Unexpected error occurred') from e


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by their ID."""
    return User.query.get(user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by their username."""
    return User.query.filter_by(username=username).first()


def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by their email."""
    return User.query.filter_by(email=email).first()


def get_all_users() -> List[User]:
    """Get all users ordered by username."""
    return User.query.order_by(User.username).all()


def update_user(
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_admin: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> User:
    """
    Update an existing user.

    Args:
        user_id: ID of the user to update
        username: New username (optional)
        email: New email (optional)
        password: New password (optional)
        is_admin: New admin status (optional)
        is_active: New active status (optional)

    Returns:
        Updated User object

    Raises:
        UpdateUserError: If user update fails for any reason
    """
    try:
        current_app.logger.debug(
            f'Updating user {user_id} with username={username}, email={email}, '
            f'is_admin={is_admin}, is_active={is_active}'
        )

        user = User.query.get(user_id)
        if not user:
            raise UpdateUserError('User not found', user_id)

        # Check for conflicts if updating username or email
        if username and username != user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                raise UpdateUserError('Username already exists', user_id)
            user.username = username

        if email and email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                raise UpdateUserError('Email already exists', user_id)
            user.email = email

        if password:
            if len(password) < 6:
                raise UpdateUserError('Password must be at least 6 characters long', user_id)
            user.set_password(password)

        if is_admin is not None:
            user.is_admin = is_admin

        if is_active is not None:
            user.user_active = is_active

        db.session.commit()

        current_app.logger.info(f'Updated user: {user.username}')
        return user

    except UpdateUserError:
        # Re-raise our custom exception
        db.session.rollback()
        raise
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error updating user {user_id}: {e}')
        raise UpdateUserError('Database error: User update failed', user_id) from e
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Unexpected error updating user {user_id}: {e}')
        raise UpdateUserError('Unexpected error occurred', user_id) from e


def delete_user(user_id: int) -> None:
    """
    Delete a user.

    Args:
        user_id: ID of the user to delete

    Raises:
        DeleteUserError: If user deletion fails for any reason
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise DeleteUserError('User not found', user_id)

        # Don't allow deletion of the last admin user
        if user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                raise DeleteUserError('Cannot delete the last admin user', user_id)

        username = user.username
        db.session.delete(user)
        db.session.commit()

        current_app.logger.info(f'Deleted user: {username}')

    except DeleteUserError:
        # Re-raise our custom exception
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user {user_id}: {e}')
        raise DeleteUserError('Error deleting user', user_id) from e


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username/email and password.

    Returns:
        User object if authentication successful, None otherwise.
    """
    # Try to find user by username or email
    user = User.query.filter(db.or_(User.username == username, User.email == username)).first()

    if user and user.is_active and user.check_password(password):
        return user

    return None


def create_default_admin() -> Optional[User]:
    """Create a default admin user if no users exist."""
    user_count = User.query.count()
    if user_count == 0:
        # Read default admin settings from environment variables
        default_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@timetracker.local')
        default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')

        admin_user = User(
            username=default_username,
            email=default_email,
            password=default_password,
            is_admin=True,
            is_active=True,
        )
        db.session.add(admin_user)
        db.session.commit()
        current_app.logger.info(f'Created default admin user: {default_username}')
        return admin_user
    return None
