from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
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


@home_bp.route('/entry/<int:entry_id>', methods=['GET'])
def get_entry(entry_id: int):
    """Get a specific time entry by ID."""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Format times as HH:MM for the form
    from_time = entry.from_time
    to_time = entry.to_time
    
    # Format date as YYYY-MM-DD
    activity_date = entry.activity_date.strftime('%Y-%m-%d')
    
    return jsonify({
        'id': entry.id,
        'activity_date': activity_date,
        'from_time': from_time,
        'to_time': to_time,
        'activity': entry.activity,
        'time_out': 1 if entry.time_out else 0
    })


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
        return jsonify({'success': False, 'error': str(e)}), 500


@home_bp.route('/add', methods=['POST'])
def add_entry() -> str:
    form = AddTimeEntryForm()
    operating_date = request.form.get('operating_date')
    entry_id = request.form.get('entry_id')
    
    try:
        if form.validate_on_submit():
            # Debug the checkbox value
            checkbox_value = request.form.get('time_out')
            
            # If entry_id exists, update existing entry
            if entry_id:
                entry = TimeEntry.query.get_or_404(int(entry_id))
                entry.activity_date = datetime.strptime(operating_date, '%Y-%m-%d')
                entry.from_time = request.form.get('from_time')
                entry.to_time = request.form.get('to_time')
                entry.activity = request.form.get('activity')
                # Use checkbox_value directly - checkbox is only in request.form if checked
                entry.time_out = 1 if checkbox_value else 0
                flash('Time entry updated successfully.', 'success')
            else:
                # Create new entry
                entry = TimeEntry(
                    activity_date=datetime.strptime(operating_date, '%Y-%m-%d'),
                    from_time=request.form.get('from_time'),
                    to_time=request.form.get('to_time'),
                    activity=request.form.get('activity'),
                    # Use checkbox_value directly
                    time_out=1 if checkbox_value else 0,
                )
                db.session.add(entry)
                flash('Time entry added successfully.', 'success')
                
            db.session.commit()
            return redirect(url_for('home.index', date=operating_date))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while saving the entry: {str(e)}', 'danger')
        return redirect(url_for('home.index', date=operating_date))  # Added date to redirect

    # If validation fails, redirect to the same date view
    return redirect(url_for('home.index', date=operating_date))  # Return to same date


@home_bp.route('/entries', methods=['GET'])
def get_entries() -> str:
    date_filter = request.args.get('date', datetime.now()).strftime('%Y-%m-%d')
    entries = TimeEntry.query.filter(db.func.date(TimeEntry.activity_date) == date_filter).order_by(TimeEntry.from_time).all()
    return render_template('home/entries.html', entries=entries)
