from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import TimeEntry, CommonTimeUse, TimeEntryForm
from app.models import db  # Import db from the new module
from datetime import datetime

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    entries = TimeEntry.query.filter(
        TimeEntry.date.cast(db.Date) == date_filter
    ).order_by(TimeEntry.start_time).all()
    return render_template('home/list_entries.html', entries=entries)

@home_bp.route('/add', methods=['GET', 'POST'])
def add_entry():
    form = TimeEntryForm()
    # Populate common uses dropdown
    form.common_use.choices = [(0, '-- None --')] + [
        (use.id, use.description)
        for use in CommonTimeUse.query.order_by(CommonTimeUse.description).all()
    ]

    if form.validate_on_submit():
        entry = TimeEntry(
            date=datetime.strptime(form.date.data, '%Y-%m-%d'),
            start_time=form.start_time.data,
            duration=form.duration.data,
            description=form.description.data,
            common_use_id=form.common_use.data if form.common_use.data != 0 else None
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('home.index'))

    return render_template('home/add_entry.html', form=form)
