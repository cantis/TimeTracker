import datetime
from typing import Optional

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Model for storing user accounts."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    user_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    last_login = Column(DateTime, nullable=True)

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        is_active: bool = True,
    ):
        """Initialize User with proper type hints and password hashing."""
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_admin = is_admin
        self.user_active = is_active

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(str(self.password_hash), password)

    def get_id(self) -> str:
        """Return the user ID as a string for Flask-Login."""
        return str(self.id)

    @property
    def is_active(self) -> bool:
        """Return the user's active status for Flask-Login compatibility."""
        return bool(self.user_active)

    @property
    def role(self) -> str:
        """Return the user's role as a string."""
        return 'admin' if bool(self.is_admin) else 'user'

    def __repr__(self) -> str:
        """String representation of the user."""
        return f'<User {self.username}>'


class TimeEntry(db.Model):
    """Model for storing time tracking entries."""

    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_date = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    from_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    to_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    activity = Column(String, nullable=True)
    time_out = Column(Boolean, nullable=False)  # Indicates if the entry is a time-out entry (untracked time)

    user = relationship('User', backref='time_entries')

    def __init__(
        self,
        activity_date: datetime.datetime,
        from_time: int,
        to_time: int,
        user_id: int,
        activity: Optional[str] = None,
        time_out: bool = False,
    ):
        """Initialize TimeEntry with proper type hints for linters."""
        self.activity_date = activity_date
        self.from_time = from_time
        self.to_time = to_time
        self.user_id = user_id
        self.activity = activity
        self.time_out = time_out
