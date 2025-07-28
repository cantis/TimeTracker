from datetime import datetime

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from werkzeug.wrappers.response import Response
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Optional

from app.models import TimeEntry, db

home_bp = Blueprint('home', __name__)


def parse_time_to_minutes(value) -> int:
    """Converts a time value to minutes past midnight."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        if ':' in value:
            try:
                hour, minute = map(int, value.split(':'))
                return hour * 60 + minute
            except (ValueError, IndexError):
                return 0
    return 0


def format_time_for_display(value) -> str:
    """Converts a time value to display format (e.g., '8:45 AM')."""
    minutes = parse_time_to_minutes(value)

    # Convert minutes past midnight to hours and minutes
    hours = minutes // 60
    mins = minutes % 60

    # Convert to 12-hour format
    display_hour = hours % 12
    if display_hour == 0:
        display_hour = 12

    am_pm = 'AM' if hours < 12 else 'PM'

    return f'{display_hour}:{mins:02d} {am_pm}'


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
    try:
        operating_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        operating_date = datetime.now().date()

    entries = (
        TimeEntry.query.filter(db.func.date(TimeEntry.activity_date) == operating_date).order_by('from_time').all()
    )

    # Add formatted times to each entry for display
    for entry in entries:
        entry.from_time_display = format_time_for_display(entry.from_time)
        entry.to_time_display = format_time_for_display(entry.to_time)

        # Calculate duration in minutes for display
        from_minutes = parse_time_to_minutes(entry.from_time)
        to_minutes = parse_time_to_minutes(entry.to_time)
        entry.duration_minutes = to_minutes - from_minutes

    form = AddTimeEntryForm()
    return render_template(
        'home/main_entry.html',
        entries=entries,
        operating_date=operating_date,
        form=form,
        activity_options=['Meeting', 'Development', 'Break'],
    )


@home_bp.route('/entry/<int:entry_id>', methods=['GET'])
def get_entry(entry_id: int):
    """Get a specific time entry by ID."""
    entry = TimeEntry.query.get_or_404(entry_id)

    # Format times as HH:MM for the form
    def minutes_to_time_string(minutes):
        """Convert minutes past midnight to HH:MM format."""
        if isinstance(minutes, str) and ':' in minutes:
            return minutes  # Already in HH:MM format
        if isinstance(minutes, int):
            hours = minutes // 60
            mins = minutes % 60
            return f'{hours}:{mins:02d}'  # No leading zero for hours to match dropdown format
        return '0:00'

    from_time = minutes_to_time_string(entry.from_time)
    to_time = minutes_to_time_string(entry.to_time)

    # Format date as YYYY-MM-DD
    activity_date = entry.activity_date.strftime('%Y-%m-%d')

    return jsonify(
        {
            'id': entry.id,
            'activity_date': activity_date,
            'from_time': from_time,
            'to_time': to_time,
            'activity': entry.activity,
            'time_out': 1 if entry.time_out else 0,
        }
    )


@home_bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id: int):
    """Delete a time entry by ID."""
    entry = TimeEntry.query.get_or_404(entry_id)

    try:
        # Save date for redirect
        activity_date = entry.activity_date.strftime('%Y-%m-%d')

        # Delete the entry
        db.session.delete(entry)
        db.session.commit()

        flash('Time entry deleted successfully.', 'success')
        return jsonify({'success': True, 'redirect': url_for('home.index', date=activity_date)})
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))


@home_bp.route('/add', methods=['POST'])
def add_entry() -> Response:
    """Create or update a time entry."""
    form = AddTimeEntryForm()
    operating_date = request.form.get('operating_date')
    entry_id = request.form.get('entry_id')

    try:
        if form.validate_on_submit():
            checkbox_value = request.form.get('time_out')

            if entry_id:
                entry = TimeEntry.query.get_or_404(int(entry_id))
                if operating_date:
                    entry.activity_date = datetime.strptime(operating_date, '%Y-%m-%d')
                entry.from_time = parse_time_to_minutes(request.form.get('from_time'))
                entry.to_time = parse_time_to_minutes(request.form.get('to_time'))
                entry.activity = request.form.get('activity')
                entry.time_out = bool(checkbox_value)
                flash('Time entry updated successfully.', 'success')
            else:
                if operating_date:
                    entry = TimeEntry(
                        activity_date=datetime.strptime(operating_date, '%Y-%m-%d'),
                        from_time=parse_time_to_minutes(request.form.get('from_time') or '0'),
                        to_time=parse_time_to_minutes(request.form.get('to_time') or '0'),
                        activity=request.form.get('activity'),
                        time_out=bool(checkbox_value),
                    )
                    db.session.add(entry)
                    flash('Time entry added successfully.', 'success')

            db.session.commit()
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
            return redirect(url_for('home.index', date=operating_date))
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving entry: {str(e)}', 'danger')

    return redirect(url_for('home.index', date=operating_date))


@home_bp.route('/entries', methods=['GET'])
def get_entries() -> str:
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    entries = TimeEntry.query.filter(db.func.date(TimeEntry.activity_date) == date_filter).order_by('from_time').all()
    return render_template('home/entries.html', entries=entries)
