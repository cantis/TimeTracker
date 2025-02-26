from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Optional

from app.models import TimeEntry, db

home_bp = Blueprint('home', __name__)


# Forms
class AddTimeEntryForm(FlaskForm):
    """Form for creating and editing time entries."""

    operating_date = StringField('Date', validators=[DataRequired()])
    from_time = StringField('Start Time (Minutes Past Midnight)', validators=[DataRequired()])
    to_time = StringField('End Time (Minutes Past Midnight)', validators=[DataRequired()])
    activity = StringField('Activity', validators=[DataRequired()])
    time_out = IntegerField('Time Out', validators=[Optional()])


# Routes
@home_bp.route('/')
def index() -> str:
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    entries = TimeEntry.query.filter(TimeEntry.date.cast(db.Date) == date_filter).order_by(TimeEntry.from_time).all()
    operating_date = datetime.strptime(date_filter, '%Y-%m-%d')
    form = AddTimeEntryForm()
    try:
        return render_template('home/main_entry.html', entries=entries, operating_date=operating_date, form=form)
    except Exception as e:
        current_app.logger.error(f'Error fetching time entries: {e}')
        entries = []
        flash('An error occurred while fetching time entries. Please try again later.', 'danger')
        return render_template('home/main_entry.html', entries=entries, operating_date=operating_date, form=form)


@home_bp.route('/add', methods=['POST'])
def add_entry() -> str:
    form = AddTimeEntryForm()

    try:
        if form.validate_on_submit():
            entry = TimeEntry(
                operating_date=datetime.strptime(form.operating_date.data, '%Y-%m-%d'),
                from_time=form.from_time.data,
                to_time=form.to_time.data,
                activity=form.activity.data,
                time_out=form.time_out.data,
            )
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('home.index'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the entry. Please try again.', 'danger')
        current_app.logger.error(f'Error adding time entry: {e}')
        return render_template('home/main_entry.html', form=form, error=str(e))

    return render_template('home/main_entry.html', form=form)
