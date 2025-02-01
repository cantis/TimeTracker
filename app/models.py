import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional

db = SQLAlchemy()


class TimeEntry(db.Model):
    """Model for storing time tracking entries."""

    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    start_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    duration = Column(Integer, nullable=False)  # Stored in minutes, must be in 15-min increments
    description = Column(String, nullable=True)
    common_use_id = Column(Integer, ForeignKey('common_time_uses.id'), nullable=True)

    common_use = relationship('CommonTimeUse')


class CommonTimeUse(db.Model):
    """Model for storing predefined common time usage descriptions."""

    __tablename__ = 'common_time_uses'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False, unique=True)


class TimeEntryForm(FlaskForm):
    """Form for creating and editing time entries."""

    date = StringField('Date', validators=[DataRequired()])
    start_time = IntegerField('Start Time (Minutes Past Midnight)', validators=[DataRequired()])
    duration = IntegerField('Duration (Minutes, 15-min increments)', validators=[DataRequired()])
    common_use = SelectField('Common Use', coerce=int, validators=[Optional()])
    description = StringField('Custom Description', validators=[Optional()])
    submit = SubmitField('Save Entry')
