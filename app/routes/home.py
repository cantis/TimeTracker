from datetime import datetime

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.models import CommonTimeUse, TimeEntry, db

home_bp = Blueprint('home', __name__)


# Forms
class AddTimeEntryForm(FlaskForm):
    """Form for creating and editing time entries."""

    date = StringField('Date', validators=[DataRequired()])
    start_time = IntegerField('Start Time (Minutes Past Midnight)', validators=[DataRequired()])
    duration = IntegerField('Duration (Minutes, 15-min increments)', validators=[DataRequired()])
    common_use = SelectField('Common Use', coerce=int, validators=[Optional()])
    description = StringField('Custom Description', validators=[Optional()])
    submit = SubmitField('Save Entry')


# Routes
@home_bp.route('/')
def index() -> str:
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    entries = TimeEntry.query.filter(TimeEntry.date.cast(db.Date) == date_filter).order_by(TimeEntry.start_time).all()
    operating_date = datetime.strptime(date_filter, '%Y-%m-%d')
    form = AddTimeEntryForm()
    form.date.data = date_filter
    try:
        return render_template('home/main_entry.html', entries=entries, operating_date=operating_date, form=form)
    except Exception as e:
        current_app.logger.error(f"Error fetching time entries: {e}")
        entries = []



@home_bp.route('/add', methods=['GET', 'POST'])
def add_entry() -> str:
    form = AddTimeEntryForm()
    # Populate common uses dropdown
    form.common_use.choices = [(0, '-- None --')] + [
        (use.id, use.description) for use in CommonTimeUse.query.order_by(CommonTimeUse.description).all()
    ]

    # Default the date entry box to today's date
    if request.method == 'GET':
        form.date.data = datetime.now().strftime('%Y-%m-%d')

        # Default the start time to be the end of the most recent entry for today
        today = datetime.now().strftime('%Y-%m-%d')
        latest_entry = (
            TimeEntry.query.filter(TimeEntry.date.cast(db.Date) == today).order_by(TimeEntry.start_time.desc()).first()
        )
        if latest_entry:
            form.start_time.data = latest_entry.start_time + latest_entry.duration
        else:
            form.start_time.data = current_app.config['DAY_START_TIME']

    try:
        if form.validate_on_submit():
            entry = TimeEntry(
                date=datetime.strptime(form.date.data, '%Y-%m-%d'),
                start_time=form.start_time.data,
                duration=form.duration.data,
                description=form.description.data,
                common_use_id=form.common_use.data if form.common_use.data != 0 else None,
            )
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('home.index'))
    except Exception as e:
        db.session.rollback()
        return render_template('home/add_entry.html', form=form, error=str(e))

    return render_template('home/add_entry.html', form=form)
