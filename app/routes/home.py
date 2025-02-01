from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for
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
    return render_template('home/list_entries.html', entries=entries)


@home_bp.route('/add', methods=['GET', 'POST'])
def add_entry() -> str:
    form = AddTimeEntryForm()
    # Populate common uses dropdown
    form.common_use.choices = [(0, '-- None --')] + [
        (use.id, use.description) for use in CommonTimeUse.query.order_by(CommonTimeUse.description).all()
    ]

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

    return render_template('home/add_entry.html', form=form)
