from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class TimeEntry(Base):
    """Model for storing time tracking entries."""
    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    start_time = Column(Integer, nullable=False)  # Stored in minutes past midnight
    duration = Column(Integer, nullable=False)  # Stored in minutes, must be in 15-min increments
    description = Column(String, nullable=True)
    common_use_id = Column(Integer, ForeignKey('common_time_uses.id'), nullable=True)

    common_use = relationship('CommonTimeUse')

class CommonTimeUse(Base):
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
