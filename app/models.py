import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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
