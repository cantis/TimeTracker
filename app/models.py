import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String

db = SQLAlchemy()


class TimeEntry(db.Model):
    """Model for storing time tracking entries."""

    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    activity_date = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    from_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    to_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    activity = Column(String, nullable=True)
    time_out = Column(Integer, nullable=True)  # Stored in minutes past midnight

    def __init__(
        self,
        activity_date: datetime.datetime,
        from_time: int,
        to_time: int,
        activity: Optional[str] = None,
        time_out: Optional[int] = None,
    ):
        """Initialize TimeEntry with proper type hints for linters."""
        self.activity_date = activity_date
        self.from_time = from_time
        self.to_time = to_time
        self.activity = activity
        self.time_out = time_out
