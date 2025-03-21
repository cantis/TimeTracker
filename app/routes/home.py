from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
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
    try:
        operating_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        operating_date = datetime.now().date()

    entries = TimeEntry.query.filter(db.func.date(TimeEntry.activity_date) == operating_date).order_by(TimeEntry.from_time).all()
    form = AddTimeEntryForm()
    return render_template(
        'home/main_entry.html',
        entries=entries,
        operating_date=operating_date,
        form=form,
        activity_options=["Meeting", "Development", "Break"]
    )


@home_bp.route('/add', methods=['POST'])
def add_entry() -> str:
    form = AddTimeEntryForm()
    operating_date = request.form.get('operating_date')
    
    try:
        if form.validate_on_submit():
            entry = TimeEntry(
                activity_date=datetime.strptime(operating_date, '%Y-%m-%d'),
                from_time=request.form.get('from_time'),
                to_time=request.form.get('to_time'),
                activity=request.form.get('activity'),
                time_out=int(request.form.get('time_out', 0)) if request.form.get('time_out') else None,
            )
            db.session.add(entry)
            db.session.commit()
            flash('Time entry added successfully.', 'success')
            return redirect(url_for('home.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while adding the entry: {str(e)}', 'danger')
        redirect(url_for('index'))

    return render_template('home/main_entry.html', form=form)


@home_bp.route('/entries', methods=['GET'])
def get_entries() -> str:
    date_filter = request.args.get('date', datetime.now()).strftime('%Y-%m-%d')
    entries = TimeEntry.query.filter(db.func.date(TimeEntry.activity_date) == date_filter).order_by(TimeEntry.from_time).all()
    return render_template('home/entries.html', entries=entries)
